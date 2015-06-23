import sys
import os
import codecs
import time
import json
import pprint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = '.'

def find_elem(browser, locator):
    
    if locator.startswith("#"):
        elem = browser.find_element_by_id(locator[1:]) 
    elif locator.startswith("."):            
        elem = browser.find_element_by_class_name(locator[1:])

    return elem

def run_tut(steps, config):
    
    wait_in_mili = tut_config["metadata"]["default_wait"]
    highlight_elem = tut_config["metadata"]

    chrome_driver_path = os.path.join(basedir,os.path.join('libs','chromedriver'))

    c_o = Options()
    c_o.binary_location = os.path.join(basedir,os.path.join('libs',"cefsimple.app/Contents/MacOS/cefsimple"))
    
    browser = webdriver.Chrome(executable_path=chrome_driver_path,chrome_options=c_o)

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

tut_config = json.load( open("configs/ow.tut") )

run_tut(tut_config["steps"], tut_config["metadata"])
