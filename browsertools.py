from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from PIL import Image
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
import random, time, email, imaplib, string, os

def wait(min=1, max=3):
    if min > max:
        max = min + 1
    time.sleep(round(random.uniform(min, max), 2))
    
def generateData(length=10, digits=True, letters=True, characters=False, upper=True, lower=True):
    source = ""
    if digits == True:
        source += string.digits
    if letters == True:
        if upper == True:
            source += string.ascii_uppercase
        if lower == True:
            source += string.ascii_lowercase
    if characters == True:
        source += """!@#$%^&*()_+-="'[],./;':"""
    output = ""
    for i in range(length):
        output += random.choice(source)
    return output
        

class Browser:
    def __init__(self):
        self.profile = webdriver.FirefoxProfile()
        self.driver = None
        self.prefs = {}
        self.captchaAPI = {"text": "", "recaptcha": ""}
        
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
    
    def getSiteKey(self):
        return self.driver.find_element_by_class_name("g-recaptcha").get_attribute('data-sitekey')
    
    def solveTextCaptcha(self, captcha, length="", digits=True, letters=True, characters=True, lower=True, upper=True):
        captchafile = generateData(16) + ".jpg"
        self.savePic(captcha, captchafile)
        
    
    def solveReCaptcha(self, api):
        sitekey = self.getSiteKey()
        client = AnticaptchaClient(api)
        task = NoCaptchaTaskProxylessTask(self.driver.current_url, sitekey)
        job = client.createTask(task)
        job.join()
        code = job.get_solution_response()        
        self.inject("g-recaptcha-response", code, "id")
        
    def setUseragent(self, value):
        self.setPref('general.useragent.override', value)
        self.useragent = value

    def randomType(self, target, value, min=0.1, max=1.1):
        for eachChar in value:
            target.send_keys(eachChar)
            wait(min, max)
              
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
        self.driver.save_screenshot(output)
        image = Image.open(output)
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        image.save(output, 'jpeg')        
        
    def select(self, elem, by, value):
        pass
    
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
        
def readEmail(server, username, password):
    mail = imaplib.IMAP4_SSL(MAIL_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.list()
    mail.select('inbox')
    result, data = mail.uid('search', None, "UNSEEN")  # (ALL/UNSEEN)
    i = len(data[0].split())
    x = i - 1
    latest_email_uid = data[0].split()[x]
    result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = email_data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    # Header Details
    date_tuple = email.utils.parsedate_tz(email_message['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
        local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))

    email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
    email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
    subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
    # Body details
    otpCode = ""

if __name__ == "__main__":
    b = Browser()
    b.startDriver()

def solveTextCaptcha():
    while True:
        wait(min=1)
        if captchaservice == 'deathbycaptcha':
            if True:
                balance = client.get_balance()
                captcha = client.decode('captcha.jpeg', 34)
                if captcha:
                    """if len(captcha["text"]) != 5:
                        client.report(captcha["captcha"])
                        return solve_captcha(element)
                    else:
                        try:
                            val = int(captcha["text"])
                        except:
                            client.report(captcha["captcha"])
                            return solve_captcha(element) """                           
                    os.remove('captcha.jpeg')
                    return captcha["text"], captcha["captcha"]  
