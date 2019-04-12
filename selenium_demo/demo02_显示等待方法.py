#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Zhi
# @Date  : 2019/3/21

# 就是设置一个等待时间，直到这个元素出现就停止等待，如果没出现就抛出异常。

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome(executable_path="C:/chrome/chromedriver.exe")  # 打开浏览器
driver.maximize_window()  # 浏览器最大化
driver.get("https://www.yuanrenxue.com")  # 打开猿人学首页

wait_time = 10
try:
    element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "search-show")))
    element.click()
finally:
    time.sleep(10)
    driver.quit()
