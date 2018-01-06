import requests,re,time,json,random,pymongo,threading
from getcookies import Getcookies
from values import USER_AGENTS
from lxml import etree
cookies={}
import json

import xlrd
import xlwt


try:
    cookiefile = open('cookies.json', 'r', encoding='utf-8')
except FileNotFoundError:
    Getcookies()
    cookiefile = open('cookies.json', 'r', encoding='utf-8')
for cookie in json.load(cookiefile)["cookies"]:
    cookies[cookie["name"]] = cookie["value"]
cookiefile.close()
class wbrelation():


    def getrequest(self,url):
        #使用随机的user-agent
        self.headers["User-Agent"] = (random.choice(USER_AGENTS))
        try:
            r = requests.get(url, cookies=cookies, headers=self.headers)
            if r.content ==b'':
                print("网络错误")
                time.sleep(20)
                r = self.getrequest(url)
            if(r.status_code==414):
                print("60错误！")
                time.sleep(120)
                r = self.getrequest(url)
            print("requested from:" + url)
            return r
        except requests.exceptions.ConnectionError:
            print("连接无响应，1秒后自动重试")
            time.sleep(1)
            r = self.getrequest(url)
            return r
    def getnum(self,user_id):
        self.follows=[]
        #self.follow_num=0
        self.headers={"User-Agent":""}
        self.follow_num=0
        self.fans_num=0
        self.headers["User-Agent"] = (random.choice(USER_AGENTS))

        url="https://weibo.cn/%s"%(user_id)
        #print (url)
        r=self.getrequest(url)
        #r=requests.get(url,cookies=cookies,headers=self.headers).content
        doc_tree = etree.HTML(r.content)
        follownum=doc_tree.xpath("//*[@class='tip2']/a[1]/text()")
        self.follow_num=re.findall("\d+",str(follownum))[0]

        fansnum = doc_tree.xpath("//*[@class='tip2']/a[2]/text()")
        self.fans_num = re.findall("\d+", str(fansnum))[0]

        print("关注数：" +self.follow_num)
        print("粉丝数: " +self.fans_num)



    def getfollow(self,user_id):
        self.follow=[]
        self.headers = {"User-Agent": ""}
        self.headers["User-Agent"] = (random.choice(USER_AGENTS))
        url = "https://weibo.cn/%s/follow"%(user_id)
        r = self.getrequest(url)
        #r = requests.get(url, cookies=cookies, headers=self.headers).content
        #print(r)
        doc_tree = etree.HTML(r.content)

        page_num=doc_tree.xpath(".//div[@id='pagelist']/form/div/input[1]/@value")
        if (len(page_num)!=0):
           page=int(page_num[0])
           for i in range(1,page+1):
              url = 'https://weibo.cn/%s/follow?page=%d' % (user_id,i)
              #print(url)
              r = self.getrequest(url)
              #r = requests.get(url, cookies=cookies, headers=self.headers).content
              # print(r)
              doc_tree = etree.HTML(r.content)

              cmt = doc_tree.xpath('.//td[@valign="top"]/a[2]/@href')
             #print(cmt)

              for c in cmt:
                  follow_uid = re.findall('\d{10}', str(c))
                  if follow_uid:
                      fans_id = follow_uid[0]
                      self.follow.append(fans_id)
           print(self.follow)
        else:
            url = 'https://weibo.cn/%s/follow?page=1' % (user_id)
            #print(url)
            #r = requests.get(url, cookies=cookies, headers=self.headers).content
            # print(r)
            r=self.getrequest(url)
            doc_tree = etree.HTML(r.content)


            cmt = doc_tree.xpath('.//td[@valign="top"]/a[2]/@href')
            # print(cmt)

            for c in cmt:
                follow_uid = re.findall('\d{10}', str(c))
                if follow_uid:
                    fans_id = follow_uid[0]
                    self.follow.append(fans_id)
            print(self.follow)

    def getfans(self,user_id):
        self.fans=[]
        self.headers = {"User-Agent": ""}
        self.headers["User-Agent"] = (random.choice(USER_AGENTS))
        url = "https://weibo.cn/%s/fans"%(user_id)
        #print(url)
        r = self.getrequest(url)
        #r = requests.get(url, cookies=cookies, headers=self.headers).content
        #print(r)
        doc_tree = etree.HTML(r.content)

        page_num=doc_tree.xpath(".//div[@id='pagelist']/form/div/input[1]/@value")
        if len(page_num)!=0:
          page=int(page_num[0])
          for i in range(1,page+1):
              url = 'https://weibo.cn/%s/fans?page=%d' % (user_id,i)
              #print(url)
              r = self.getrequest(url)
              #r = requests.get(url, cookies=cookies, headers=self.headers).content
              doc_tree = etree.HTML(r.content)

              cmt = doc_tree.xpath('//*[@valign="top"]/a[2]/@href')
             #print(cmt)

              for c in cmt:
                  fans_uid= re.findall('\d{10}', str(c))
                  if fans_uid:
                    fans_id=fans_uid[0]
                    self.fans.append(fans_id)
          print(self.fans)
        else:
            url = 'https://weibo.cn/%s/fans?page=1' % (user_id)
            #print(url)
            r = self.getrequest(url)
            #r = requests.get(url, cookies=cookies, headers=self.headers).content
            doc_tree = etree.HTML(r.content)

            cmt = doc_tree.xpath('//*[@valign="top"]/a[2]/@href')

            for c in cmt:

                fans_uid = re.findall('\d{10}', str(c))
                if fans_uid:
                    fans_id = fans_uid[0]
                    self.fans.append(fans_id)
            # print(cmt)
            print(self.fans)
    def updatetxt(self):
        myfile = open('relation.txt', 'a')
        myfile.write('\n' + user_id + '\n' + 'follow' + ' ')
        for line in self.follow:
            myfile.write(line + ' ')
        myfile = open('relation.txt', 'a')
        myfile.write('\n' + 'fans' + ' ')

        for line in self.fans:
            myfile.write(line + ' ')
    def updatedb(self):

            client = pymongo.MongoClient('127.0.0.1:27017')
            db = client['WeiboTV']
            db['Relation'].insert(
                {"author": self.author,
                 "content": self.content,
                 "id": self.id,
                 "url": re.findall('[A-Za-z0-9]{9}', self.url)[0],
                 "comments_num": self.comments_num,
                 "likes_num": self.likes_num,
                 "forwards_num": self.forwards_num,
                 "comments": self.comments,
                 "forwards": self.forwards,
                 }
            )
run=wbrelation()
with open('userid.txt', 'r') as f0:
    lines = f0.readlines()
    for line in lines:

        user_id = line.strip()
        run.getnum(user_id)
        run.getfollow(user_id)
        run.getfans(user_id)
        run.updatetxt()






