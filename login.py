from selenium import webdriver
import time
driver = webdriver.Chrome()
# driver.get('https://login.alibaba.com')

# driver.find_element_by_id('fm-login-id').send_keys('cqycgs')
# passwd = driver.find_element_by_id('fm-login-password')
# passwd.send_keys('hello1234')

# inputspan = driver.find_element_by_id('fm-login-submit')
# inputspan.click();
driver.get('https://baidu.com')
driver.find_element_by_id('kw').send_keys('你好')
driver.find_element_by_id('su').click()