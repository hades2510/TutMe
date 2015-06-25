import sys
import os
import codecs
import time
import json
import pprint
import platform

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = '.'
	
def get_cef_location():
	if platform.system() == "Windows":
		return os.path.join(basedir, "libs/win/cefsimple")
	else:
		return os.path.join(basedir, os.path.join('libs','cefsimple.app/Contents/MacOS/cefsimple'))
		
def get_chrome_driver_location():
	if platform.system() == "Windows":
		return os.path.join(basedir, "libs/win/chromedriver")
	else:
		return os.path.join(basedir, os.path.join('libs','chromedriver'))

def find_elem(browser, locator):
    
    if locator.startswith("#"):
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.ID, locator[1:]) ) )
    elif locator.startswith("."):            
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.CLASS_NAME, locator[1:]) ) )

    return elem

def open_browser(url):
    chrome_driver_path = get_chrome_driver_location()
	
    c_o = Options()
    c_o.binary_path = get_cef_location()
        
    browser = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=c_o)
    browser.get(url)
    
    #wait for a recipe to be choosen
    elem = WebDriverWait( browser, 1000 ).until( EC.presence_of_element_located( (By.ID, "make_recipe")) )
    
    tut_config = json.load( open( os.path.join(basedir, elem.get_attribute("value") ) ) )
    
    run_tut(browser, tut_config["steps"], tut_config["metadata"])
	
def run_tut(browser, steps, config):
    
    wait_in_mili = config["default_wait"]
    highlight_elem = config

    for step in steps:
        if step["type"] == "url":
            print "going to url ",step["data"]
            browser.get(step["data"])
            print "loaded url ",step["data"]

        if step["type"] == "text_input":

            data = step["data"]

            elem = find_elem(browser, step["data"]["locator"])
            
            print "feeding input ",data            
            
            elem.send_keys(data["value"])

        if step["type"] == "button_press":
            
            data = step["data"]
            
            elem = find_elem(browser, data["locator"])
            
            print "pushing button ",data

            elem.click()

        time.sleep(wait_in_mili/1000.0)

open_browser("file://"+os.path.abspath(os.path.join(basedir,"configs/Recipes.html")))
