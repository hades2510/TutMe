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
    """ OS independent location of cef """
    
    if platform.system() == "Windows":
        return os.path.join(basedir, "libs/win/cefsimple.exe")
    else:
        return os.path.join(basedir, os.path.join('libs','cefsimple.app/Contents/MacOS/cefsimple'))
        
def get_chrome_driver_location():
    """ OS independent retrieval of chromedriver location """
    
    if platform.system() == "Windows":
        return os.path.join(basedir, "libs/win/chromedriver")
    else:
        return os.path.join(basedir, os.path.join('libs','chromedriver'))

def find_elem(browser, locator):
    """ Tries to find an elemend in the browser based on locator"""    
    
    print "looking for elem ", locator
            
    if locator.startswith("#"):
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.ID, locator[1:]) ) )
    elif locator.startswith("."):            
        elem = WebDriverWait(browser, 5).until( EC.presence_of_element_located( (By.CLASS_NAME, locator[1:]) ) )
    
    print "found elem ", locator
    
    return elem

    
def get_null_file():
    """ Returns a system dependent file path similar to POSIX /dev/null """
    
    if platform.system() == "Windows":
        return "NUL"
    else:
        return "/dev/null"

def open_browser(url):
    """Opens the cef instance and the provide url"""
    
    chrome_driver_path = get_chrome_driver_location()
    
    c_o = Options()
    c_o.add_argument("--disable-web-security")

    #redirect webdriver output to null, this doesn't block the pipe
    #and stops a chromium freeze
    c_o.add_argument("--webdriver-logfile=%s" % get_null_file())
    
    #don't let chromium go to http://www.google.com, instead
    #point it to the landing page
    c_o.add_argument("--url=%s" % url)

    #custom browser location
    c_o.binary_location = get_cef_location()

    #redirect logs to null file
    service_args = ["--log-path=%s" % get_null_file()]
    
    browser = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=c_o, service_args=service_args)
    browser.get(url)
    inject_templates(browser)
    
    #wait for a recipe to be choosen
    elem = WebDriverWait( browser, 1000 ).until( EC.presence_of_element_located( (By.ID, "make_recipe")) )
    inputs = None
    try:
        inputs=json.loads(browser.find_element_by_id("make_recipe_input").get_attribute("value"))   
    except Exception as e:
        print e

    #load the recipe, this contains all the steps
    #and other config params
    tut_config = json.load( open( os.path.join(basedir, elem.get_attribute("value") ) ) )
 
    #run a tutorial
    run_tut(browser, tut_config["steps"], tut_config["metadata"], inputs)

def inject_css(browser):
    """Injects the content of res/inject.css in the browser window"""
    
    with open("res/inject.css","r") as css_file:
        css_content = css_file.read()
   
    css_content=css_content.replace("\n","\\\n")
    print css_content 
    css_injection_script = """var css_to_inject="%s";
                            var head = document.getElementsByTagName("head")[0];
                            var style = document.createElement("link");
                            style.rel = "stylesheet";
                            style.innerHTML = css_to_inject;
                            head.appendChild(style);""" % css_content
    print css_injection_script
    browser.execute_script(css_injection_script)

def inject_javascript(browser):
    pass

def inject_templates(browser):
    """Inject css and javascript into the browser for highlighting"""
    
    inject_css(browser)
    inject_javascript(browser)
    
def run_tut(browser, steps, config, inputs=None):
    """ Runs a tutorial
    
        Runs a given tutorial in the provided browser. The run consists
        of running all the steps, interpolating the variables based on
        the recipe and on the inputs proided.
        
        Configs related to delay between steps, highlighting elements and
        other options are available.
    """    
    
    wait_in_mili = config["default_wait"]
    highlight_elem = config["highlight_element"]
    highlight_time = config["highlight_time"]

    for step in steps:
        
        #if url step point the browser to that url
        if step["type"] == "url":
            print "going to url ",step["data"]
            browser.get(step["data"])
            print "loaded url ",step["data"]

            #inject custom css and javascript for
            #highlighting elements
            if highlight_elem:
                inject_templates(browser)

        #if text_input step, find the element
        #and enter the input, variable interpolation may happen
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

        #button step, find the button and press it
        if step["type"] == "button_press":
            
            data = step["data"]
            
            elem = find_elem(browser, data["locator"])
            
            print "pushing button ",data

            elem.click()

        #wait between steps, this is usefull for the user
        #comes from the config
        time.sleep(wait_in_mili/1000.0)

#start the app :)
open_browser("file://"+os.path.abspath(os.path.join(basedir,"configs/Recipes.html")))
