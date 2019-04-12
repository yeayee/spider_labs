#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Zhi
# @Date  : 2019/3/21

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome(executable_path="C:/chrome/chromedriver.exe")  # 打开浏览器
driver.maximize_window()  # 浏览器最大化
driver.get("https://www.yuanrenxue.com")  # 打开猿人学首页
time.sleep(3)  # 人工预留加载时间

driver.find_element_by_class_name("search-show").click()  # 通过class定位页面元素，并点击
search = driver.find_element_by_id("isearch")  # 通过id定位元素
search.send_keys(u"python教程")  # 输入，只能是 Unicode
time.sleep(10)
search.send_keys(Keys.ENTER)  # 回车
time.sleep(10)
driver.quit()
