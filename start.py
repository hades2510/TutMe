import sys
import os
import codecs
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

if getattr(sys, 'frozen', False):
	basedir = sys._MEIPASS
else:
	basedir = '.'

chrome_driver_path = os.path.join(basedir,os.path.join('libs','chromedriver'))

c_o = Options()
c_o.binary_location = os.path.join(basedir,"cefsimple.app/Contents/MacOS/cefsimple")

browser = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=c_o)
browser.get("http://dev01.owpdev.com:8080/owp")

time.sleep(1)

pas = browser.find_element_by_id("pw")
pas.send_keys("secret")

uname = browser.find_element_by_id("un")
uname.send_keys("admin")
uname.send_keys(Keys.RETURN)

