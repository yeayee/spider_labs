#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Zhi
# @Date  : 2019/3/21

# 隐式等待是一个全局设置，设置后所有的元素定位都会等待给定的时间，直到元素出现为止，等待规定时间元素没出现就报错。

from selenium import webdriver

driver = webdriver.Chrome(executable_path="C:/chrome/chromedriver.exe")  # 打开浏览器
driver.implicitly_wait(5)

driver.get('https://www.yuanrenxue.com')
driver.find_element_by_class_name("slide-left").click()
driver.quit()
