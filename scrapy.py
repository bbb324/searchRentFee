import requests

from bs4 import BeautifulSoup

url = "https://sz.lianjia.com/ershoufang/nanshanqu/l3a3p4/"
count = 0

def grab(url):
	global count #使用全局变量
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'lxml')
	g_data = soup.find_all("div", {"class", "info clear"})
	
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
		
		print(yard+ '|' + price + '|' +address) #打印出 小区，价格，地址



for page in range(1, 5):
	url = "https://sz.lianjia.com/ershoufang/nanshanqu/pg"+str(page)+"l3a3p4/"
	grab(url)

print('共'+str(count)+'条')
	

		