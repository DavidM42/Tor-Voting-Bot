from stem.control import Controller
from stem import CircStatus
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from selenium.webdriver.common.utils import free_port
import tempfile
from os.path import join
from time import sleep
from selenium.common.exceptions import NoSuchElementException

# Tried to create votes by browser automation with selenium and tor browser
# But captcha prevented this

from torHelpers import print_tor_circuits
# got from https://github.com/webfp/tor-browser-selenium/blob/master/examples/stem_adv.py
# country exit nodes config tip from here https://stem.torproject.org/tutorials/to_russia_with_love.html#using-pycurl

TBB_PATH = "/home/david/tools/tor-browser_en-US/"
VOTE_WORD = "Schabernack"


def submitWord(driver):
    vote_url = "https://www.langenscheidt.com/jugendwort-des-jahres"

    driver.load_url(vote_url, wait_on_page=2)
    vote_iframe_elem = driver.find_element_by_css_selector("iframe[src^='https://www.surveymonkey.com/']")
    driver.switch_to.frame(vote_iframe_elem)
    print(vote_iframe_elem)

    try:
        # TODO make random time
        sleep(6)
        surveymonkey_captcha_element = driver.find_element_by_css_selector("iframe[src^='https://captcha-challenge.immun.io/surveymonkey.html']")
        print(surveymonkey_captcha_element)
        driver.switch_to.frame(surveymonkey_captcha_element)

        recaptcha_iframe_element = driver.find_element_by_css_selector("iframe[src^='https://www.google.com/recaptcha/api2']")
        print(recaptcha_iframe_element)
        driver.switch_to.frame(recaptcha_iframe_element)

        recaptcha_element = driver.find_element_by_css_selector('span#recaptcha-anchor')
        print(recaptcha_element)

        recaptcha_element.click()
        sleep(4) #TODO random
        driver.switch_to.frame(vote_iframe_elem)

    except NoSuchElementException as e:
        print(e)

    while True:
        pass

    h4Containers = driver.find_elements_by_css_selector('h4.question-title-container')

    for container in h4Containers:
        task = container.find_element_by_css_selector('span.user-generated').text
        print("Task is: " + task)

        if (task == "Wie alt bis du?"):
            fieldset_element = container.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')

            select =  fieldset_element.find_element_by_css_selector('select')
            option_value = select.find_elements_by_css_selector('option')[3].value
            select.value = option_value

        


    # print(driver.find_element_by("h1.on").text)
    # print(driver.find_element_by(".content > p").text)




def launch_tb_with_custom_stem(tbb_dir):
    socks_port = free_port()
    control_port = free_port()
    tor_data_dir = tempfile.mkdtemp()
    tor_binary = join(tbb_dir, cm.DEFAULT_TOR_BINARY_PATH)
    print("SOCKS port: %s, Control port: %s" % (socks_port, control_port))

    torrc = {
            'ControlPort': str(control_port),
            'SOCKSPort': str(socks_port),
            'DataDirectory': tor_data_dir,
            # 'ExitNodes': '{de}', # TODO only connect to german exit nodes for anti bot
        }
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir, torrc=torrc,
                                        tor_binary=tor_binary)
    with Controller.from_port(port=control_port) as controller:
        controller.authenticate()
        with TorBrowserDriver(tbb_dir, socks_port=socks_port,
                            control_port=control_port,
                            tor_cfg=cm.USE_STEM) as driver:
            
            submitWord(driver)

            # driver.load_url("https://check.torproject.org", wait_on_page=3)
            # print(driver.find_element_by("h1.on").text)
            # print(driver.find_element_by(".content > p").text)
        
        
        print_tor_circuits(controller)
    # tor_process.kill()


if __name__ == '__main__':
    launch_tb_with_custom_stem(TBB_PATH)
