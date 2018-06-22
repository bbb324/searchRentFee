import requests
import math
from bs4 import BeautifulSoup
import re # 正则
import time
from blacklist import blacklist

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
def getTopElementrySchool(area, range):
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
    getLocationName(info, area, range)


def getLocationName(info, area, range):
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
                    dicts = {
                        'area': area,
                        'name': name,
                        'community': getCommunityName(title.parent.nextSibling)
                    }
                    getApartmentInfo(dicts, range)

# 获取学校真实名称
def regexGetSchoolName(text, area):
    if area == 'futian':
            schoolName = text;
            if '深圳福田' in text:
                schoolName = text.split('深圳福田')[1]
    return schoolName

# 获取对应学校所包含的小区信息
def getCommunityName(ele):
    nameList = ele.find(id='s_list')
    
    if nameList != None:
        return nameList.text.split('，')
    elif ele != None and '学区划分' in ele.text:
        return ele.text.split('：')[1].split('，')
    # 荔园外语东校区
    elif ele.nextSibling != None and '学区划分' in ele.nextSibling.text:
        return ele.nextSibling.text.split('：')[1].split('，')
    # 荔园小学西校区
    elif ele.nextSibling.nextSibling.nextSibling.find(id='s_list') != None:
        return ele.nextSibling.nextSibling.nextSibling.find(id='s_list').text.split('，')
    else:
        print('no')

# 获取每个小区的价格
def getApartmentInfo(param, range):
    communities = param['community']
    for unit in communities:
        url = 'https://sz.lianjia.com/ershoufang/bp'+str(range[0]) + 'ep'+str(range[1])+'rs'+ unit
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        # 打印学校名称和对应小区名称
        print(param['name'], unit)
        group = soup.find("h2", {"class", "total fl"})
        if group == None:
            print('不存在页面')
        elif blacklist.nameList(unit):
            print('不存在房源')
        # 出现拼写错误时，取第一个跳转链接
        elif len(soup.find_all('div', {'class','spellcheck'})) != 0:
            print('跳转')
            # spellGuess = soup.find_all('div', {'class','spellcheck'})[0]
            # ele = spellGuess.find_all('a')[0]
            # getApartmentInfo(ele.attrs['data-el'])
        # 找到0套待售房源    
        elif group.find_all('span')[0].text.strip(' ') == '0':
            print('无')
        else:
            g_data = soup.find_all('div', {'class': 'info clear'})
            formatInfo(g_data, unit)

# 格式化返回房源信息
def formatInfo(g_data, community):
    houseInfo = {}
    for item in g_data:
        if community in item.find_all('a')[1].text:
            houseInfo['detail'] = item.find('div', {'class': 'houseInfo'}).text
            houseInfo['price'] = item.find('div', {'class': 'priceInfo'}).text    
            houseInfo['href'] = item.find('a').attrs['href']
            print(houseInfo)

getTopElementrySchool('futian', [400, 550])
    




