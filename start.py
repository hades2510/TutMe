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

class TutApp:
    """TutApp is the entry point in the app
        
       It takes care of setting up selenium, chromium and chromedriver
       Points chromium to the landing page
    """
    
    def __init__(self):
        self._browser = None
        
    @property
    def browser(self):
        return self._browser
        
    @browser.setter
    def browser(self, value):
        self._browser = value
       
    def cef_location(self):
        """ OS independent location of cef """
        
        if platform.system() == "Windows":
            return os.path.join(basedir, "libs/win/cefsimple.exe")
        else:
            return os.path.join(basedir, os.path.join('libs','cefsimple.app/Contents/MacOS/cefsimple'))
        
    def chrome_driver_location(self):
        """ OS independent retrieval of chromedriver location """
        
        if platform.system() == "Windows":
            return os.path.join(basedir, "libs/win/chromedriver")
        else:
            return os.path.join(basedir, os.path.join('libs','chromedriver'))

    def find_elem(self, locator):
        """ Tries to find an elemend in the browser based on locator"""    
        
        print "looking for elem ", locator
            
        if locator.startswith("#"):
            elem = WebDriverWait(self.browser, 5).until( EC.presence_of_element_located( (By.ID, locator[1:]) ) )
        elif locator.startswith("."):            
            elem = WebDriverWait(self.browser, 5).until( EC.presence_of_element_located( (By.CLASS_NAME, locator[1:]) ) )
    
        print "found elem ", locator
    
        return elem

    def open_browser(self,url):
        """Opens the cef instance and the provide url"""
    
        chrome_driver_path = self.chrome_driver_location()
    
        c_o = Options()
        c_o.add_argument("--disable-web-security")

        #redirect webdriver output to null, this doesn't block the pipe
        #and stops a chromium freeze
        c_o.add_argument("--webdriver-logfile=%s" % os.devnull)
    
        #don't let chromium go to http://www.google.com, instead
        #point it to the landing page
        c_o.add_argument("--url=%s" % url)

        #custom browser location
        c_o.binary_location = self.cef_location()

        #redirect logs to null file
        service_args = ["--log-path=%s" % os.devnull]
    
        self.browser = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=c_o, service_args=service_args)
        self.browser.get(url)
    
        #wait for a recipe to be choosen
        elem = WebDriverWait( self.browser, 1000 ).until( EC.presence_of_element_located( (By.ID, "make_recipe")) )
        inputs = None
        try:
            inputs=json.loads(self.browser.find_element_by_id("make_recipe_input").get_attribute("value"))   
        except Exception as e:
            print e

        #load the recipe, this contains all the steps
        #and other config params
        tut_config = json.load( open( os.path.join(basedir, elem.get_attribute("value") ) ) )
 
        #run a tutorial
        self.run_tut(tut_config["steps"], tut_config["metadata"], inputs)

    def inject_css(self):
        """Injects the content of res/inject.css in the browser window"""
        
        print "injecting css"
        
        with open( os.path.join( basedir, "res/inject.css"), "r") as css_file:
            css_content = css_file.read()
   
        css_content = css_content.replace("\n","\\\n")
    
        css_injection_script = """var css_to_inject="%s";
                            var style = document.createElement("style");
                            style.appendChild( document.createTextNode( css_to_inject ) );
                            style.type = "text/css";
                            document.head.appendChild(style);""" % css_content
    
        self.browser.execute_script(css_injection_script)

    def inject_javascript(self):
        """Injects the content of res/inject.js in the browser window"""
        
        print "injecting js"
        
        with open( os.path.join(basedir, "res/inject.js") ) as js_file:
            js_content = js_file.read()
            
        self.browser.execute_script(js_content)
        
    def inject_templates(self):
        """Inject css and javascript into the browser for highlighting"""
        
        print "injecting templates"
        self.inject_css()
        self.inject_javascript()
    
    def highlight_element( self, locator, highlight_time ):
        self.browser.execute_script("TutMe.highlightElem('%s',%s);"%(locator, highlight_time))
        WebDriverWait(self.browser, 10).until( EC.presence_of_element_located( (By.ID, locator) ) )
        
    def run_tut(self, steps, config, inputs=None):
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
                self.browser.get(step["data"])
                print "loaded url ",step["data"]

                #inject custom css and javascript for
                #highlighting elements
                if highlight_elem:
                    self.inject_templates()

            #if text_input step, find the element
            #and enter the input, variable interpolation may happen
            if step["type"] == "text_input":

                data = step["data"]
                
                elem = self.find_elem(step["data"]["locator"])

                input_data = data["value"]
                
                if highlight_elem:
                    self.highlight_element( data["locator"], highlight_time )
             
                #maybe a var
                if input_data.startswith('$') :
                    print "interpolating variable ",input_data
                    input_data = inputs.get(input_data, input_data)            
     
                print "feeding input ", input_data            
                
                elem.send_keys(input_data)

            #button step, find the button and press it
            if step["type"] == "button_press":
                
                data = step["data"]
                
                elem = self.find_elem( data["locator"] )
                
                if highlight_elem:
                    self.highlight_element( data["locator"], highlight_time )
                
                print "pushing button ",data

                elem.click()

            #wait between steps, this is usefull for the user
            #comes from the config
            time.sleep(wait_in_mili/1000.0)

#start the app :)
app = TutApp()
app.open_browser("file://"+os.path.abspath(os.path.join(basedir,"configs/Recipes.html")))
