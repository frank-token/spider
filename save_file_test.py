#-*- coding:utf-8 -*-
__author__='lf'

from scrapy.spiders import Spider
from scrapy import FormRequest
from news_spider.MySQL_config import mysql_db
import requests
from datetime import *
import json
import re
import time
from hashlib import md5
import sys,os
reload(sys)
sys.setdefaultencoding('utf8')

today=date.today()
start_time = str(date(2017,8,28))
#start_time=str(today)
end_time = str(today)
def download_file(file_title,save_url):
    with open(file_title + '.pdf', 'w') as f0:
        with open(save_url, 'r') as f1:
            data = f1.read()
        f0.write(data)
    print('保存成功！')

class postnews(Spider):
    name='postnews'
    download_delay = 1
    custom_settings = {
        # 'DOWNLOAD_TIMEOUT': 20,
        'RETRY_TIMES': 4,  # 默认为2
    }
    def start_requests(self):
        global start_time
        global end_time
        base_url='http://www.neeq.com.cn/disclosureInfoController/infoResult.do?callback=%s'
        call_back_list={
             '9': 'jQuery18305971592945646758_1503970456426',
             #'9': 'jQuery183008474523168260006_1503916891699'
        }
        type_cate_list = [
            ('9', '关键字')
        ]
        for type_cate in type_cate_list:
            link_type = type_cate[0]
            cate = type_cate[1]
            callback = call_back_list[link_type]
            print('url:'+ base_url % callback)
            page_list=['0','1']
            for page in page_list:
                yield FormRequest(
                    url=base_url%callback,dont_filter=True,callback=self.parse,
                    meta={'callback': callback,'base_url': base_url,
                          'start_time': start_time, 'end_time': end_time},
                    formdata={
                        "disclosureType": link_type,  # 与callback有关,callback确定后无用
                        "page": page, #可设置
                        "companyCd": "公司名称/拼音/代码",
                        "keyword": cate,
                        "startTime": start_time,
                        "endTime": end_time,
                    }
                )
    def parse(self, response):
        resouce=response.body
        res=re.findall('\(.*\)',resouce)[0][2:-2]
        data=json.loads(res)
        info=data['listInfo']['content']
        for x in info:
            file_title=x['disclosureTitle']
            print(file_title)
            file_source='http://www.neeq.com.cn'+x['destFilePath']
            #print(file_source)
            s=md5()
            s.update(file_source+file_title)
            md5_name=s.hexdigest()
            publish_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(str(x['upDate']['time'])[:-3])))
            #print(publish_time)
            headers={
                #'Content-Length': '188',
                'Accept': 'text/javascript,application/javascript,application/ecmascript,application/x-ecmascript,*/*;q=0.01',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            }
            try:
                file_res=requests.get(file_source,headers=headers,timeout=3)
                path='/Users/qmp/Desktop/'
                file_type=x['destFilePath'][-4:]
                filelist=os.listdir(path)
                if (md5_name+file_type not in filelist):
                    print('保存新文件')
                    with open(path+md5_name+file_type,'w') as f:
                        f.write(file_res.content)
                    print('%s.pdf文件保存完成!'%file_title)

                    update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        sq0='INSERT INTO download_save(file_title,file_source,save_url,md5,update_time,publish_time) VALUES(%s,%s,%s,%s,%s,%s)'
                        mysql_db.execute_sql(sq0,[file_title,file_source,path+md5_name+'.pdf',md5_name,update_time,publish_time])
                        print('数据库操作完成!')
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

