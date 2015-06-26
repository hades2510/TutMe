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
		return os.path.join(basedir, "libs/win/cefsimple.exe")
	else:
		return os.path.join(basedir, os.path.join('libs','cefsimple.app/Contents/MacOS/cefsimple'))
		
def get_chrome_driver_location():
	if platform.system() == "Windows":
		return os.path.join(basedir, "libs/win/chromedriver")
	else:
		return os.path.join(basedir, os.path.join('libs','chromedriver'))

def find_elem(browser, locator):
    
    print "looking for elem ", locator
            
    if locator.startswith("#"):
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.ID, locator[1:]) ) )
    elif locator.startswith("."):            
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.CLASS_NAME, locator[1:]) ) )
    
    print "found elem ", locator
    
    return elem
    
def get_null_file():
    
    if platform.system() == "Windows":
        return "NUL"
    else:
        return "/dev/null"

def open_browser(url):
    chrome_driver_path = get_chrome_driver_location()
	
    c_o = Options()
    c_o.add_argument("--disable-web-security")
    c_o.add_argument("--webdriver-logfile=NUL")
    c_o.binary_location = get_cef_location()

    service_args = ["--log-path=%s" % get_null_file()]
    
    browser = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=c_o, service_args=service_args)
    browser.get(url)
    
    #wait for a recipe to be choosen
    elem = WebDriverWait( browser, 1000 ).until( EC.presence_of_element_located( (By.ID, "make_recipe")) )
    inputs = None
    try:
        inputs=json.loads(browser.find_element_by_id("make_recipe_input").get_attribute("value"))   
    except Exception as e:
        print e

    tut_config = json.load( open( os.path.join(basedir, elem.get_attribute("value") ) ) )
 
    run_tut(browser, tut_config["steps"], tut_config["metadata"], inputs)
	
def run_tut(browser, steps, config, inputs=None):
    
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

            input_data = data["value"]
            
            #maybe a var
            if input_data.startswith('$') :
                print "interpolating variable ",input_data
                input_data = inputs.get(input_data, input_data)            
 
            print "feeding input ", input_data            
            
            elem.send_keys(input_data)

        if step["type"] == "button_press":
            
            data = step["data"]
            
            elem = find_elem(browser, data["locator"])
            
            print "pushing button ",data

            elem.click()

        time.sleep(wait_in_mili/1000.0)

open_browser("file://"+os.path.abspath(os.path.join(basedir,"configs/Recipes.html")))
