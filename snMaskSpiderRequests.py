import os
import time
import random
from snlogger import logger
import urllib
import urllib.request
from lxml import etree
import pickle
import json
from PIL import Image
from util import parse_json
from util import get_random_useragent

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class SnMaskSpider(object):
    def __init__(self):
        # 初始化信息
        # self.curPartNumber = global_config.getRaw('config', 'curPartNumber')
        #self.seckill_init_info = dict()
        #self.seckill_url = dict()
        #self.seckill_order_data = dict()
        #self.timers = Timer()
        # self.default_user_agent = global_config.getRaw('config', 'DEFAULT_USER_AGENT')

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
        options.add_argument('--user-agent="{}"'.format(get_random_useragent()))
        driver = webdriver.Chrome(executable_path=executable_path, options=options)

        self.login = Login(driver)

    def reserve(self):
        self.login.loginByQrCode()
        return
         

class Login(object):
    #  扫码登录
    def __init__(self, driver):
        """
        初始化扫码登录
        大致流程：
            1、访问登录二维码页面，获取Token
            2、使用Token获取票据
            3、校验票据
        :param spider_session:
        """
        self.driver = driver
        self.driver.get("https://passport.suning.com/ids/login")

        self. _getCookie()

        self.isLogin = False
        self.refreshLoginStatus()

    # 刷新是否登录状态
    def refreshLoginStatus(self):
        self.isLogin = self._validateCookies()

    #获取cookies保存到文件
    def _saveCookie(self):
        cookiesFile = '{}{}.cookies'.format("cookies/", "sn")
        directory = os.path.dirname(cookiesFile)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        dictCookies = self.driver.get_cookies()
        with open(cookiesFile, 'wb') as f:
            pickle.dump(dictCookies, f)

    #读取文件中的cookie
    def _getCookie(self):
        self.driver.delete_all_cookies()
        cookiesFile = '{}{}.cookies'.format("cookies/", "sn")

        if not os.path.exists(cookiesFile):
            return False

        with open(cookiesFile, 'rb') as f:
            listCookies = pickle.load(f)

        for cookie in listCookies:
            self.driver.add_cookie(cookie)


    def _validateCookies(self):
        """
        验证cookies是否有效（是否登陆）
        通过访问用户订单列表页进行判断：若未登录，将会重定向到登陆页面。
        :return: cookies是否有效 True/False 
        """
        url = 'https://order.suning.com/order/orderList.do'
        self.driver.get(url)
        print(self.driver.session_id)
        if (self.driver.title == "我的订单"):
            logger.info('Cookis登录成功')
            return True
        else:
            logger.info('Cookis登录失败')
            return False

    # 缓存并展示登录二维码
    def _getQrcode(self):
        self.driver.get("https://passport.suning.com/ids/login")
        time.sleep(1)
        #driver.save_screenshot("all.png")
        element = self.driver.find_element_by_xpath("//img[contains(@class,\"qrCodesId\")]")
        element.screenshot("qr.png")
        print(self.driver.session_id)

        logger.info('二维码获取成功，请打开苏宁APP扫描')

        return True

    def _validateQrCode(self):
        url = "https://passport.suning.com/ids/qrLoginStateProbe?callback=jQuery{}_{}"
        self.driver.get(url.format(random.randint(1000000, 9999999), str(int(time.time() * 1000))))

        resp = parse_json(self.driver.page_source)
        if resp["state"] != '2':
            logger.info('请扫描二维码,state:{}'.format(resp["state"]))
            return None
        else:
            logger.info('已完成手机客户端确认')
            return True

    def loginByQrCode(self):
        """
        二维码登陆
        :return:
        """
        
        self.isLogin = self._validateCookies()

        # 未登录获取二维码
        if not self.isLogin:
            self._getQrcode()

        ticket = None
        retry_times = 85
        for _ in range(retry_times):
            ticket = self._validateQrCode()
            if ticket:
                break
            time.sleep(2)
        else:
            logger.info('二维码过期，请重新获取扫描')
            return

        while True:
            if not self.isLogin:
                self.isLogin = self._validateCookies()
            else:
               self._saveCookie()
               break 

        logger.info('二维码登录成功')
       
