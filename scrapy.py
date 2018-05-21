import requests
import math
from bs4 import BeautifulSoup
import re # 正则
from bokeh.io import output_notebook, show # 引入初始化
from bokeh.plotting import figure #引入图表界面
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, LabelSet
from bokeh.models.annotations import Label # 引入备注
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.sampledata.commits import data
from bokeh.transform import factor_cmap

from bokeh.models.glyphs import VBar

import os # 操作系统
from openpyxl import Workbook
import datetime



# 爬取特定区域内挂牌7天以内的房源
def grab(url, last_day):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    g_data = soup.find_all("div", {"class", "info clear"})
    
    for item in g_data:
        day = item.contents[3].text.split('/ ')[2]
        if day == '刚刚发布' or int(re.match('\d+', day).group()) < last_day:
            try:
                yard = item.contents[1].find_all('a')[0].text
            except:
                pass
            try:
                price = item.contents[5].find_all('span')[1].text
            except:
                pass
            try:
                address = item.contents[4].find_all('span', {'class', 'subway'})[0].text
            except:
                pass
            try:
                time = item.contents[3].text.split('/ ')[2]
            except:
                pass
            print(yard+ '|' + price + '|' + time + '|') #打印出 小区，价格，地址

#先获取总页数，再以循环的方式获取列表
def getTotal(day):
    page = 5 # 爬的总页数
    count = 1
    area_list = [
        'https://sz.lianjia.com/ershoufang/luohuqu/pg', # 罗湖
        'https://sz.lianjia.com/ershoufang/futianqu/pg', # 福田
        'https://sz.lianjia.com/ershoufang/nanshanqu/pg', # 南山
        'https://sz.lianjia.com/ershoufang/baoanqu/pg'] # 宝安
    for link in area_list:
        while count<=page:
            href = link + str(count) +"co32a3a4/"
            print(href)
            grab(href, day)
            count += 1
        count = 1    

# 爬取 7天内 新上架的房源
#getTotal(7)



# 爬取特定区域的房源总数 （70~90，90~110 不考虑价格）
def grab_area_house_number():
    title = '各区房源数量'
    nums = []
    area_list = [
        'https://sz.lianjia.com/ershoufang/luohuqu/a3a4', # 罗湖
        'https://sz.lianjia.com/ershoufang/futianqu/a3a4', # 福田
        'https://sz.lianjia.com/ershoufang/nanshanqu/a3a4', # 南山
        'https://sz.lianjia.com/ershoufang/baoanqu/a3a4'] # 宝安
    
    for area in area_list:
        page = requests.get(area)
        soup = BeautifulSoup(page.content, 'lxml')
        total = soup.find('h2', {'class', 'total fl'})
        number = int(total.find('span').text)
        nums.append(number)
    
    label_name = ['罗湖','福田','南山','宝安']

    diagram = figure(x_range     = label_name, 
                    y_range      = [0, 2000], 
                    plot_height  = 250, 
                    title        = title, 
                    tools        = 'wheel_zoom',
                    y_axis_label = '房源数量')

    source = ColumnDataSource(data=dict(
        x     = label_name,
        top   = nums,
        names = nums,
        color = ['#67b7dc', '#b9783f','#84b761', '#cd82ad']))

    labels = LabelSet(source=source,
                        x           = 'x',
                        y           = 'top',
                        text        = 'names', 
                        level       = 'glyph', 
                        text_align  = 'center', 
                        render_mode = 'canvas')
    diagram.vbar(source=source, 
                    x      = 'x', 
                    top    = 'top', 
                    width  = 0.5, 
                    bottom =  0, 
                    color  = 'color')

    # 添加顶部具体数据
    diagram.add_layout(labels)
    

    show(diagram)
    

#grab_area_house_number()


# 30 天内的成交数据
def getDoneTransaction():
    url    = 'https://sz.lianjia.com/chengjiao/nanshanzhongxin/'
    r      = requests.get(url)
    soup   = BeautifulSoup(r.content, 'lxml')
    g_data = soup.find_all("ul", {"class", "listContent"})

    for item in g_data[0].find_all('li'):
        try:
            yard    = item.find_all('div', {'class', 'title'})[0].text
        except:
            pass
        try:
            href    = item.find_all('a')[0].attrs['href']
            result  = getTransactionDate(href)
        except:
            pass
        print(yard + '|' + result['total']+ '|' + result['date'])    



# 成交具体详情（小区，总价，日期）
def getTransactionDate(url):
    req         = requests.get(url)
    soup        = BeautifulSoup(req.content, 'lxml')
    detail      = soup.find_all("div", {"class", "wrapper"})[0]
    total_ele   = soup.find_all("span", {"class", "dealTotalPrice"})[0]


    date        = detail.find_all('span')[0].text.split(' ')[0] # 成交日期
    total_value = total_ele.find_all('i')[0].text + '万' # 成交金额

    return ({'total': total_value, 'date': date})




#getDoneTransaction()


def getUploadInfo(url):
    req         = requests.get(url)
    soup        = BeautifulSoup(req.content, 'lxml')
    priceInfo   = soup.find_all("div", {"class", "price"})[0]
    total       = priceInfo.find_all('span', {'class', 'total'})[0].text + '万'
    unit        = priceInfo.find_all('span', {'class', 'unitPriceValue'})[0].text
    
    # 房子信息
    houseInfo   = soup.find_all("div", {"class", "houseInfo"})[0]
    room        = houseInfo.find_all('div', {'class', 'mainInfo'})[0].text

    area        = soup.find_all('div', {'class', 'area'})[0]
    size        = area.find_all('div', {'class', 'mainInfo'})[0].text + '平米'
    age         = area.find_all('div', {'class', 'subInfo'})[0].text
    direction   = soup.find_all('div', {'class', 'type'})[0].find_all('div')[0].text

    geoInfo     = soup.find_all('div', {'class', 'aroundInfo'})[0]
    community   = geoInfo.find_all('a')[0].text

    
    return ({
                'total'     : total,      # 总价
                'unit'      : unit,       # 单价
                'room'      : room,       # 房屋结构
                'direction' : direction,  # 房屋朝向
                'community' : community,  # 房屋所属小区
                'age'       : age,        # 房龄
                'size'      : size        # 房屋大小
            })




# 获取福田区各位置新上房源，总价低于800万10套的
def getTotalTransactionByArea():
    area_list    = ['bagualing', 'baihua','chegongmian','chiwei','futianbaoshuiqu']
    baseUrl = 'https://sz.lianjia.com/ershoufang/'

    tmpUrl = 'https://sz.lianjia.com/ershoufang/baihua/co21'
    r      = requests.get(tmpUrl)
    soup   = BeautifulSoup(r.content, 'lxml')
    g_data = soup.find_all('div', {'class', 'info clear'})


    total = 800
    last_day = 30
   
    

    for item in g_data:
        price = int(item.contents[5].find_all('span')[0].text)
        if (price <= total):
            result  = getUploadInfo(item.find_all('a')[0].attrs['href'])
            result['link']       = item.find_all('a')[0].attrs['href']
            result['uploadTime'] = item.contents[3].text.split('/ ')[2]
            index = 1
            wb = Workbook()
            ws = wb.active
            ws['A' + str(index)] = result['total']
            ws['B' + str(index)] = result['unit']
            ws['C' + str(index)] = result['room']
            ws['D' + str(index)] = result['direction']
            ws['E' + str(index)] = result['community']
            ws['F' + str(index)] = result['age']
            ws['G' + str(index)] = result['size']
                
            index = index + 1
            wb.save('data.xlsx')    

            

getTotalTransactionByArea()  









def visualize():
    # 折线图画法
    p = figure(plot_width=800, plot_height=300, title="abc")
    p.multi_line(xs=[[1,2,3], [2,3,4]], ys=[[6,7,2], [4,5,7]], color=['red', 'black'])

    

    # 柱状图
    plot = figure(plot_width=800, plot_height=300, title='rect')
    plot.vbar(x=['a','b','c'], width=0.5, bottom=0, top=[1,2,3], color=['red', 'brown', 'navy'])

    # pandas, source 是坐标,可以直接引入外部数据通过 bokeh.sampledata.autompg
    source = ColumnDataSource(data={
        'x': [1,2,3,4],
        'y': [3,6,4,2],
        })
    p_panda = figure(plot_width=800, plot_height=300)
    p_panda.circle('x', 'y', source=source)
    
    # x轴为label的柱状图展示
    fruites=['a','b','c','d']
    p_fruits = figure(x_range=fruites, plot_height=250, title='fruit')
    p_fruits.vbar(x=fruites, top=[5,2,3,6], width=0.5)
    p_fruits.xgrid.grid_line_color= 'red'
    p_fruits.y_range.start = 0


    #点图加注释LabelSet
    source = ColumnDataSource(data=dict(
        temp=[166, 171, 172, 168, 174, 162],
        pressure=[165, 189, 220, 141, 260, 174],
        names=['A', 'B', 'C', 'D', 'E', 'F']))

    p_anotation = figure(x_range=(160, 175))
    p_anotation.scatter(x='temp', y='pressure', size=8, source=source)
    p_anotation.xaxis.axis_label = 'Temperature (C)'
    p_anotation.yaxis.axis_label = 'Pressure (lbs)'

    labels = LabelSet(x='temp', y='pressure', text='names', level='glyph',
                  x_offset=5, y_offset=5, source=source, render_mode='canvas')

    p_anotation.add_layout(labels)
    show(p_anotation)

#visualize() 

    # 按品种为单位，三年的数量柱状图
def groupChart():
    fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
    years = ['2015', '2016', '2017']
    data = {'fruits' : fruits,
            '2015'   : [2, 1, 4, 3, 2, 4],
            '2016'   : [5, 3, 3, 2, 4, 6],
            '2017'   : [3, 2, 4, 4, 5, 3]}

    # this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
    x = [ (fruit, year) for fruit in fruits for year in years ]
    counts = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), plot_height=250, title="Fruit Counts by Year")

    p.vbar(x='x', top='counts', width=0.9, source=source)

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    show(p)
#groupChart()

# 混合图形，包含柱状图，折线图，并且按“季度”为group展开，折线图为4季度平均值连线
def mixedCategory():
    factors = [("Q1", "jan"), ("Q1", "feb"), ("Q1", "mar"),
           ("Q2", "apr"), ("Q2", "may"), ("Q2", "jun"),
           ("Q3", "jul"), ("Q3", "aug"), ("Q3", "sep"),
           ("Q4", "oct"), ("Q4", "nov"), ("Q4", "dec")]
    p = figure(x_range=FactorRange(*factors), plot_height=250)
    x = [ 10, 12, 16, 9, 10, 8, 12, 13, 14, 14, 12, 16 ]
    p.vbar(x=factors, top=x, width=0.9, alpha=0.5)       
    qs, aves = ["Q1", "Q2", "Q3", "Q4"], [(10+12+16)/3, (9+10+8)/3, (12+13+14)/3, (14+12+16)/3]
    p.line(x=qs, y=aves, color="red", line_width=3)
    p.circle(x=qs, y=aves, line_color="red", fill_color="white", size=10)

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    show(p)
#mixedCategory()







def toExcel():
    wb = Workbook()
    ws = wb.active
    #ws['A1'] = 42
    #ws.append([1,2,3])
    area_list = [
        'https://sz.lianjia.com/ershoufang/luohuqu/a3a4', # 罗湖
        'https://sz.lianjia.com/ershoufang/futianqu/a3a4', # 福田
        'https://sz.lianjia.com/ershoufang/nanshanqu/a3a4', # 南山
        'https://sz.lianjia.com/ershoufang/baoanqu/a3a4'] # 宝安
    index = 1   
    for area in area_list:

        ws['A'+str(index)] = area
        index = index + 1
    
    wb.save('sample.xlsx')

#toExcel()




