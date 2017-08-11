#coding:utf-8
import urllib.request
import re
import requests
url="https://en.wikipedia.org/wiki/Machine_translation"
url1="https://www.seebug.org/"
proxy = {'http': 'http://113.107.112.210:8101'}
response = requests.get(url, proxies=proxy)
html=response.text
#data= urllib.request.urlopen(url1)
#html=data.read().decode('utf-8')
print(html)
with open('mt.xml','w') as f:
    f.write(str(html.encode('utf-8')))
print('mt.html写入结束')
word_dic={}
with open('mt.xml') as files:
    info=files.read()
    s=info.replace('\n',"")
    word_info=re.findall('<p>(.*)</p>',s)
    for x in word_info:
        word_info=re.findall('[a-z]{1,22}',x)
    word_set=list(set(word_info))

    for i in word_set:
        count=0
        for j in word_info:
            if j==i:
                count+=1
        word_dic[i]=count
    word_dic=sorted(word_dic.items(),key=lambda x:x[1],reverse=True)#按照单词出现频率降序排列
    #print('word dict:',word_dic)

    f0 = open('mt_word.txt', 'w')
    for x in word_dic:
        f0.write(x[0] +'\t'+str(x[1])+'\n')
    f0.close()
    print('word save ok!')


    year_info=re.findall('[1-2][0-9]{3}',s)
    year_info=sorted(list(set(year_info)))
    f1 = open('mt_year.txt', 'w')
    for x in year_info:
        f1.write(x+'\n')
    f1.close()
    print('year save ok!')
