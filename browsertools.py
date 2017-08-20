from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import random, time
from PIL import Image

class Browser:
    def __init__(self):
        self.profile = webdriver.FirefoxProfile()
        self.driver = None
        self.prefs = {}
        
    def wait(min=1, max=3):
        self.sleep=True
        if min > max:
            max = min + 1
        time.sleep(round(random.uniform(min, max), 2))
        self.sleep=False
        return True
        
    def startDriver(self, browser='Firefox', profile=None):
        browser = browser.lower()
        if browser == 'firefox':
            if profile != None:
                self.driver = webdriver.Firefox(profile)
            else:
                self.driver = webdriver.Firefox()
        return self.driver
    
    def setPref(self, target, value):
        if self.driver == None and self.profile != None:
            self.profile.set_preference(target, value)
        elif self.driver != None:
            ac = ActionChains(self.driver)
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
            ac.send_keys('pref set {} {}'.format(target, str(value))).perform()
            ac.send_keys(Keys.ENTER).perform()
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
            ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
        else:
            return False
        self.prefs[str(target)] = value
    
    def setProxy(self, proxy, types=["http", "https", "ftp", "socks", "ssl"]):
        self.proxy, self.proxyp = proxy.split(':')
        self.setPref("network.proxy.type", 1)
        for eachType in types:
            proxystring = 'network.proxy.' + eachType
            self.setPref(proxystring, self.proxy)
            self.setPref(proxystring + '_port', int(self.proxyp))
    
    def getScrollPosition(self, axis='y'):
        return self.driver.execute_script("return window.page{}Offset;".format(axis.upper()))
        
        
    def setUseragent(self, value):
        self.setPref('general.useragent.override', value)
        self.useragent = value

    def randomType(self, target, value, min=0.1, max=1.1):
        for eachChar in value:
            target.send_keys(eachChar)
            self.wait(min, max)
              
    def get(self, url):
        finished = 0
        i = 0
        while finished == 0:
            if i > 5:
                return False
            try:
                self.driver.get(url)
                finished = 1
            except:
                wait()
                i += 1
        return True
    
    def savePic(self, elem, output):
        location = elem.location
        size = elem.size
        offset = self.getScrollPosition()
        location['y'] += offset
        driver.save_screenshot(output)
        image = Image.open(output)
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        image.save(output, 'jpeg')        
    
    def scrollTo(self, elem='', y='', x=''):
        if elem:
            self.driver.execute_script("return arguments[0].scrollIntoView();", elem)
            self.driver.execute_script("window.scrollBy(0, -150);")
        if y:
            self.driver.execute_script("window.scrollTo(" + str(y) + ", Y)")
        if x:
            self.driver.execute_script("window.scrollTo(" + str(x) + ", X)")
    
    def hide(self):
        self.driver.set_window_position(-3000, 0)
        self.hidden = True
    
    def unhide(self):
        self.driver.set_window_position(0, 0)
        self.hidden = False
        
    def inject(self, target, value, elemtype='id'):
        elemtype = elemtype.lower()
        getelemstring = "getElementBy{}"
        if elemtype == 'id':
            getelemstring.format('Id')
        self.driver.execute_script('document.' + getelemstring + '(' + target + ').value = "' + value + '"')