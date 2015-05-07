# -*- coding: UTF-8 -*- 
import requests
from bs4 import BeautifulSoup
import os
import re

def getname(url):
        url = url[::-1]
        name = []
        for i in url:
            if i == '/':
                break
            name.append(i)
        strs = ''
        strs = strs.join(name)
        strs = strs[::-1]
        return strs

def getmax(page):
	souplist = BeautifulSoup(page)
	for i in souplist.select('input[name="mp"]'):
		return int(i["value"])

def gettap(page):
	pass

def downp(url,path):
	h = requests.get(url)
	name = getname(url)
	fp = open(path+name,'w')
	fp.write(h.content)
	fp.close

class WeiBo(object):
	def __init__(self,mail,password):
		self.session = requests.session()
		WEIBO_RAND_URL = 'http://login.weibo.cn/login/'  
		WEIBO_LOGIN_PREFIX = 'http://login.weibo.cn/login/'  

		h = self.session.post(WEIBO_RAND_URL,data = {})
		page = h.text
		soup = BeautifulSoup(page)
		rand = soup.form["action"]
		self.url = WEIBO_LOGIN_PREFIX+rand
		for v in soup.select('input[name="vk"]'):
			vk = v["value"]
		for p in soup.select('input[type="password"]'):
			passwordrand = p["name"]

		self.data = {'mobile': mail,
				passwordrand: password,  
				'remember': 'on',  
				'backURL': 'http://weibo.cn/',  
				'backTitle': '新浪微博',  
				'vk': vk,  
				'submit': '登录',  
				'encoding': 'utf-8'}
		page = self.session.post(self.url,self.data)
		soup = BeautifulSoup(page.text)
		print "login successful!"
		self.id = soup.find("div","tip2").a["href"].split('/')[1]

	def getlist(self):
		print "loding get list!"
		followurl = "http://weibo.cn/"+self.id+"/follow?vt=4"
		followpage = self.session.get(followurl)
		name = []
		href = []
		num = getmax(followpage.text)
		lenurl = range(1,num)
		for n in lenurl:
			followurl = "http://weibo.cn/"+self.id+"/follow?page="+str(n)
			if n != 1:
				followpage = self.session.get(followurl)
			souplist = BeautifulSoup(followpage.text)
			for tag in souplist.find_all("tr"):
				name.append(tag.td.next_sibling.a["href"])
				href.append(tag.td.next_sibling.a.string)
		return zip(name,href)

	def downloadall(self,pathin):
		usrlist = self.getlist()
		for h,n in usrlist:
			print "downloading",n
			path = pathin+n
			if not os.path.exists(path):
				os.mkdir(path)
			path = path +"/"
			usrpage = self.session.get(h)
			num = getmax(usrpage.text)
			numlist = range(1,num)
			for n in numlist:
				print "downloading",n,"pages"
				hurl = h.replace("?vt=4","")+"?page="+str(n)
				print hurl
				if n != 1:
					usrpage = self.session.get(hurl)
				soup = BeautifulSoup(usrpage.text)
				for tag in soup.find_all("img","ib"):
					picallurl = tag.parent["href"].replace("pic","picAll")
					print picallurl
					picpage = self.session.get(picallurl)
					picsoup = BeautifulSoup(picpage.text)
					for tag in picsoup.find_all("img"):
						print tag["src"]
						picurl = "http://ww3.sinaimg.cn/large/"+getname(tag["src"])
						if os.path.isfile(path+getname(tag["src"])):
							break
						downp(picurl,path)
