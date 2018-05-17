import requests
import math
from bs4 import BeautifulSoup

from bokeh.io import output_notebook, show # 引入初始化
from bokeh.plotting import figure #引入图表界面
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, LabelSet
from bokeh.models.annotations import Label # 引入备注
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.sampledata.commits import data
from bokeh.transform import factor_cmap

from bokeh.models.glyphs import VBar


url = "https://sz.lianjia.com/ershoufang/nanshanqu/l3a3p4/"
count = 0

def grab(url):
    global count #使用全局变量
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    g_data = soup.find_all("div", {"class", "info clear"})
    print(g_data[0].contents)
    for item in g_data:
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
        count +=1

        print(yard+ '|' + price + '|') #打印出 小区，价格，地址


#先获取总页数，再以循环的方式获取列表
def getTotal(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    total = soup.find('h2', {'class', 'total fl'})
    number = int(total.find('span').text)
    page = math.ceil(number/30)
    count = 1
    while count<=page:
        grab("https://sz.lianjia.com/ershoufang/nanshanqu/pg"+str(count)+"l3a3p4/")
        count += 1

# 爬取特定条件下的房源
#grab(url)

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
                    plot_height  = 250, 
                    y_range      = [0, 2000], 
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
    

grab_area_house_number()













