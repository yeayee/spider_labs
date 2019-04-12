#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Zhi
# @Date  : 2019/3/21

import time
import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chrome_path = "C:/chrome/chromedriver.exe"


def save_cookies(cookies, file_to_save):
    with open(file_to_save, "wb") as f:
        pickle.dump(cookies, f)


def login_auto(login_url, username, password, username_xpath, password_xpath, submit_xpath, cookies_file, browser=None):
    if browser is None:
        browser = webdriver.Chrome(executable_path=chrome_path)
    browser.maximize_window()
    browser.get(login_url)
    time.sleep(10)  # 等待登录页面加载
    browser.find_element_by_xpath(username_xpath).send_keys(username)
    browser.find_element_by_xpath(password_xpath).send_keys(password)
    browser.find_element_by_xpath(submit_xpath).send_keys(Keys.ENTER)
    time.sleep(10)  # 等待登录完成页面加载
    cookies = browser.get_cookies()
    print(cookies)
    save_cookies(cookies, cookies_file)
    browser.quit()


def login_manually(login_url, cookies_file, browser=None):
    if browser is None:
        browser = webdriver.Chrome(executable_path=chrome_path)
    browser.get(login_url)
    time.sleep(60)  # 一分钟填写账号密码验证码
    cookies = browser.get_cookies()
    print(cookies)
    save_cookies(cookies, cookies_file)
    browser.quit()


def load_cookies_to_browser(cookies_file, browser=None):
    with open(cookies_file, "rb") as f:
        cookies = pickle.load(f)
    if browser is None:
        browser = webdriver.Chrome()
    for cookie in cookies:
        browser.add_cookie(cookie)
    return browser


def load_cookies_to_requests(cookies_file, session=None):
    with open(cookies_file, "rb") as f:
        cookies = pickle.load(f)
    if session is None:
        session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])


def load_to_requests(cookies_file, session=None):
    with open(cookies_file, 'rb') as f:
        cookies = pickle.load(f)
    if session is None:
        session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])


if __name__ == '__main__':
    method = "auto"

    if method == "manually":
        url = "https://passport.bilibili.com/login"
        login_manually(url, "bilibili.cookies")
    elif method == "auto":
        url = "https://weibo.com/"
        username_xpath = '//input[@id="loginname"]'
        password_xpath = '//input[@name="password"]'
        submit_xpath = '//a[@action-type="btn_submit"]'
        username = "name"
        password = "***"
        login_auto(url, username, password, username_xpath, password_xpath, submit_xpath, "weibo.cookies")
    else:
        print("need choice auto/manually")
