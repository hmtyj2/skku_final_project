#-*- coding:utf-8 -*-
import json
import math
import urllib3
import requests
from khaiii import KhaiiiApi

Homepages=[]
total_Words={}
total_Pages=0
Api = KhaiiiApi('/home/hwang/khaiii/khaiii/build/lib/libkhaiii.so.0.4', '/home/hwang/khaiii/khaiii/build/share/khaiii')

def Etri_API(Q,P):
    openApiURL = "http://aiopen.etri.re.kr:8000/MRCServlet"
    accessKey="81b52b9a-adf3-489d-a244-44d67a74b2dd"
    requestJson = {
        "access_key": accessKey,
        "argument": {
            "question": Q,
            "passage": P
            }
        }
    http = urllib3.PoolManager()
    response = http.request(
    "POST",
    openApiURL,
    headers={"Content-Type": "application/json; charset=UTF-8"},
    body=json.dumps(requestJson))
    print(json.dumps(requestJson))
    print(len(json.dumps(requestJson)))
    print("[responseCode] " + str(response.status))
    print("[responBody]")
    print(str(response.data,"utf-8"))

def Adams_API(Q,P):
    openApiURL = "http://api.adams.ai/datamixiApi/mrcQa"
    accessKey="5203067209565929901"
    response = requests.get(openApiURL,params={"key": accessKey, "paragraph": P, "question": Q})
    response.raise_for_status()
    jsonResponse = response.json()
    print(jsonResponse["return_object"]["answer"])


def mk_Homepages():
    with open('DB.json') as json_file:
        json_data=json.load(json_file)
        for url in json_data.keys():
            Homepages.append(Homepage(url,json_data[url]))

def get_Qkeyword(str):
    ret=[]
    for word in Api.analyze(str):
        for morph in word.morphs:
            if 'NN' in morph.tag:
                if morph.lex not in ret:
                    ret.append(morph.lex)
    return ret

def get_targetPage(n,keywords):
    ret=[]
    for H in Homepages:
        scores=0
        for Key in keywords:
            if Key in H.keyword.keys():
                scores+=1/math.sqrt(H.keyword[Key])
            else:
                scores+=0
        ret.append([H.url,scores])
    ret.sort(key=lambda x:x[1],reverse=True)
    return ret[:n]

def mk_passage(targets,n):
    ret=""
    for T in targets:
        for H in Homepages:
            if T[0]==H.url:
                ret+=processing(H.context,n)
    return ret

def processing(str,n):
    str=str.replace("\n",".").replace("\t",".")
    if len(str)>n:
        return str[:n]
    return str

class Homepage():
    def __init__(self,url,context):
        self.url=url
        self.context=context

    def cal_Wordcount(self):
        self.words={}
        for word in Api.analyze(self.context):
            for morph in word.morphs:
                if 'NN' in morph.tag:
                    if morph.lex in self.words:
                        self.words[morph.lex]+=1
                    else:
                        self.words[morph.lex]=1
                        if morph.lex in total_Words:
                            total_Words[morph.lex]+=1
                        else:
                            total_Words[morph.lex]=1
        pass

    def cal_TFIDF(self):
        self.TFIDF={}
        for word in self.words.keys():
            self.TFIDF[word]=math.log(total_Pages/total_Words[word])*self.words[word]

    def cal_Keyword_rank(self):
        self.keyword={}
        rank=1
        for word in sorted(self.TFIDF,key=lambda K:self.TFIDF[K],reverse=True):
            self.keyword[word]=rank
            rank+=1
        pass


mk_Homepages()
for H in Homepages:
    H.cal_Wordcount()
    total_Pages+=1
for H in Homepages:
    H.cal_TFIDF()
    H.cal_Keyword_rank()

while(1):
    Q=input("Question: ")
    targets=get_targetPage(2,get_Qkeyword(Q))
    P=mk_passage(targets,500)
    print(P)
    Etri_API(Q,P)
    #Adams_API(Q,P)
