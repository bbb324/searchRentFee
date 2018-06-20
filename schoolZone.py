import requests
import math
from bs4 import BeautifulSoup
import re # 正则
import time

link_list = [
    'http://www.szxuexiao.com/PrimarySchool/LuoHuShengYiJiXiaoXue.html',    # 罗湖学校列表
    'http://www.szxuexiao.com/PrimarySchool/FuTianShengYiJiXiaoXue.html',   # 福田学校列表
    'http://www.szxuexiao.com/PrimarySchool/NaShanShengYiJiXiaoXue.html',   # 南山学校列表
]

dist_list = [
        'http://bsy.sz.bendibao.com/bsyDetail/606150.html', #罗湖住房类表
        'http://bsy.sz.bendibao.com/bsyDetail/611764.html', #福田住房列表
        'http://bsy.sz.bendibao.com/bsyDetail/616443.html', #南山住房列表
]


# 获得省一级小学列表名单
def getTopElementrySchool(area):
    if area == 'luohu':
        url = link_list[0]
    elif area == 'futian':
        url = link_list[1]
    elif area == 'nanshan':
        url = link_list[2]

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    group = soup.find_all("div", {"class", "doc_list"})
    ul = group[0].find_all('ul', {'class', 'detail_nursery'})
    img = ul[0].find_all('img');
    info = []
    for item in ul:
        text = item.find_all('img')[0].attrs['alt']
        schoolList = regexGetSchoolName(text, area) # 字符串截取获取小学名称
        info.append(schoolList)  
    getLocationName(info, area)


def getLocationName(info, area):
    if area == 'luohu':
        url = dist_list[0]
    elif area == 'futian':
        url = dist_list[1]
    elif area == 'nanshan':
        url = dist_list[2]
   
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    group = soup.find_all("div", {"class", "checkbox1"})
    
    for name in info:
        for dist in group:
            titles = dist.find_all('strong')
            for title in titles:
            
                if name in title.text or ('石厦' in name and '石厦' in title.text):
                    print(name)
                    getCommunityName(title.parent.nextSibling)
                    print('-----------')
                               
    # for dist in group:
    #         titles = dist.find_all('strong')
    #         for title in titles:
    #             if '石厦小学' in title.text:
    #                 getCommunityName(title.parent.nextSibling)
    #             elif '石厦学校小学部' in title.text:
    #                 getCommunityName(title.parent.nextSibling)
                                   

# 获取学校真实名称
def regexGetSchoolName(text, area):
    if area == 'futian':
            schoolName = text;
            if '深圳福田' in text:
                schoolName = text.split('深圳福田')[1]
    return schoolName


def getCommunityName(ele):
    nameList = ele.find(id='s_list')
    
    if nameList != None:
        print(nameList.text.split('，'))
    elif ele != None and '学区划分' in ele.text:
        print(ele.text.split('：')[1].split('，'))
    # 荔园外语东校区
    elif ele.nextSibling != None and '学区划分' in ele.nextSibling.text:
        print(ele.nextSibling.text.split('：')[1].split('，'))    
    # 荔园小学西校区
    elif ele.nextSibling.nextSibling.nextSibling.find(id='s_list') != None:
        print(ele.nextSibling.nextSibling.nextSibling.find(id='s_list').text.split('，'))  
    else:
        print('no')



getTopElementrySchool('futian')
    