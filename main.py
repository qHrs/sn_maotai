import os
import sys
import time
import random
import json
from selenium import webdriver
from snMaskSpiderRequests import SnMaskSpider

from bs4 import BeautifulSoup
from util import parse_json

if __name__ == '__main__':
    ''''''
    snMaskSpider = SnMaskSpider();
    snMaskSpider.reserve();
    
    '''
    # 浏览器地址
    executable_path = "webdriver/chromedriver.exe"

    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    options.add_argument('window-size=1920x1080')  # 指定浏览器分辨率
    options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    #options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    options.add_argument('log-level=3')  # 只输出失败信息
    options.add_argument('User-Agent:')  # 只输出失败信息
    driver = webdriver.Chrome(executable_path=executable_path, options=options)

    driver.get("https://passport.suning.com/ids/login")
    time.sleep(1)
    url = "https://passport.suning.com/ids/qrLoginStateProbe?callback=jQuery{}_{}"
    retry_times = 85
    for _ in range(retry_times):
        url = url.format('172026256123645663143', str(int(time.time() * 1000)))
        print(url)
        driver.get(url)
        
        html = driver.page_source
        resp_json = parse_json(html)
        print(resp_json)
    
    driver.save_screenshot("all.png")
    element = driver.find_element_by_xpath("//img[contains(@class,\"qrCodesId\")]")
    element.screenshot("qr.png")
    #driver.get("https://passport.suning.com/ids/qrLoginUuidGenerate.htm?image=true&yys={0}".format(str(int(time.time() * 1000))))
    #driver.save_screenshot("qr.png")
    time.sleep(10)
    driver.get("https://order.suning.com/order/orderList.do")
    print(driver.title)
    '''