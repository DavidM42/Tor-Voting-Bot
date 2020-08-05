import socket
from time import sleep
from datetime import datetime
from random import randint
import requests
import re
import sys
import tempfile
# from os.path import join
# import tbselenium.common as cm
import socks  # PySocks module
import stem.process
from stem import Signal
from stem.control import Controller
# worked on basis of https://github.com/DemonicCroissant/Jugendwort-des-Jahres-Bot/blob/master/Jugendwort%20des%20Jahres.py

# General values
done_string = '\033[1mFertig\033[0m'
survey_url  = 'https://www.surveymonkey.com/r/7JZRVLJ?embedded=1'
age_groups  = [
    ("3067519627", "10 bis 15 Jahre"),
    ("3067519628", "16 bis 20 Jahre"),
    ("3067519629", "21 bis 30 Jahre"),
    ("3067519630", "über 30 Jahre")
]


# User-defined values, tweak as you wish
VOTE_WORD          = 'Schabernack' # The word to submit
get_submit_wait = 7         # The approximate time between receiving data and sending it 
dual_vote_interval = 30     # the approximate time between double votes by one person withouth changing ips in between
ip_change_time_interval = 10           # The approximate time interval between submissions of different ips in seconds
chosen_age_group = age_groups[1]  # age group to vote as





SOCKS_PORT = 7000
CONTROL_PORT = 7001
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)  #TODO this line needed? or just for setting all request proxy
request_proxy = dict(
                    http='socks5://127.0.0.1:' + str(SOCKS_PORT),
                    https='socks5://127.0.0.1:' + str(SOCKS_PORT)
                )
# sends all traffic from this script through proxy
# would work normally for requests and so on but breaks access to tor controller
# socket.socket = socks.socksocket

def get_setup_survey_data():
    """
        Gets setup survey data WITHOUT using proxy as this step is blocked in tor ips
        Would return captcha which is unsolvable by bot
    """

    # Setup could also be done everytime to be more human like
    # but could also trigger some bot warnings
    # print("Beziehe Daten vom Server...")
    sys.stdout.flush()
    print("Getting setup survey data without proxy use via real ip...")
    r = requests.get(survey_url)

    data = re.search(r'survey_data" value="(.*?)" />', r.text)
    if not data:
        print("\033[1mFailed to get setup survey data as even non tor ip is blocked. Will give up...\033[0m")
        return False

    survey_data = data.group(1)
    return survey_data

def get_reponse_quality_data(secondVote):
    """
        Calculate some random times it took and started and replicate normal reponse quality values to use
    """
    randomTimeSpentMs = randint(33364 , 240123)

    now = datetime.now()
    now_ms = int(now.timestamp()* 1000.00)
    start_time_ms = now_ms - randomTimeSpentMs

    # got basic object from network tab of legit vote in browser and will variate it a bit
    # don't know what most of it means so hope for the best in terms of bot detection
    return {
            "question_info": {
                "qid_463803414": {
                    "number":1,
                    "type":"dropdown",
                    "option_count":5,
                    "has_other": False,
                    "other_selected": None,
                    "relative_position":[[2,0]],
                    "dimensions":[5,1],
                    "input_method": None,
                    "is_hybrid": False
                },
                "qid_463803684": {
                    "number":2,
                    "type":"open_ended",
                    "option_count": None,
                    "has_other":False,
                    "other_selected": None,
                    "relative_position": None,
                    "dimensions": None,
                    "input_method":"text_typed",
                    "is_hybrid": True
                },
                "qid_483089934": {
                    "number":3,
                    "type":"multiple_choice_vertical",
                    "option_count":1,
                    "has_other": False,
                    "other_selected": None,
                    "relative_position":[[0,0]],
                    "dimensions":[1,1],
                    "input_method": None,
                    "is_hybrid": False
                }
            },
            "start_time": start_time_ms,
            "end_time": now_ms + 15, # emulate sending delay after calculation
            "time_spent": randomTimeSpentMs,
            "previous_clicked": secondVote,
            "has_backtracked": False, #TODO maybe variate between true and false?
            "bi_voice":{}
        }

def submitVote(survey_data, secondVote):
    """
        Submits one vote for the word of the year
    """

    post_data = {
        '463803414'  : "",
        '463803684'  : VOTE_WORD,
        '483089934[]': '3189794655',
        'is_previous': 'false',
        'survey_data': survey_data,
        'disable_survey_buttons_on_submit': '',
        'response_quality_data': get_reponse_quality_data(secondVote)
    }
    print(done_string)

    # Set age group to the one choosen at top for next submission
    age_key = chosen_age_group[0]
    age_string = chosen_age_group[1]
    post_data["463803414"] = age_key
    
    # Wait the specified amount of time
    print("Warte etwa " + str(get_submit_wait) + " Sekunden vor dem absenden...")
    sys.stdout.flush()
    waitTimeWithNoise(get_submit_wait)
    print(done_string)
    
    # Submit survey
    print("Stimme ab mit der Altersgruppe " + age_string + "...")
    sys.stdout.flush()
    # if you remove the tor proxy from here the request works but any repeated votes from the same ip are probably ignored from the start
    post_resp = requests.post(survey_url, data=post_data, proxies=request_proxy)
    # print(post_resp.text) #debuggin show result html of poll post
    # print("\033[1mFailed to submit vote as ip is blocked. Moving on...\033[0m")

    print(done_string)

def waitTimeWithNoise(timeS):
    """
        Waits random time between given time minus 2 seconds and time given +2 seconds
        timeS is the time in seconds to be approximately waited for
    """
    minimum = timeS - 2
    if minimum <= 0:
        minimum = 0.3
    randomTime = randint(minimum , timeS + 2)
    # print("Waiting for " + str(randomTime) + " seconds")
    sleep(randomTime)

def display_ip_info():
    """
        Displays current ip and a guess from which country it is to the console
    """
    resp = requests.get("https://api.myip.com/", proxies=request_proxy) # sadly not working more verbose api "https://ipapi.co/json/"
    if resp:
        ip_info = resp.json()
        print("Info on new ip:")
        print(ip_info)


def change_tor_nodes():
    # signal TOR for a new connection
    # thanks to https://boredhacking.com/tor-webscraping-proxy/
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

    display_ip_info()


# TBB_PATH = "/home/david/tools/tor-browser_en-US/"
tor_data_dir = tempfile.mkdtemp()
# tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)


tor_process = stem.process.launch_tor_with_config(
    # tor_cmd=tor_binary,
    config = {
        'ControlPort': str(CONTROL_PORT),
        'SocksPort': str(SOCKS_PORT),
        'DataDirectory': tor_data_dir,
        # 'ExitNodes': '{de}', # only exit from german ips for now for anti bot detection purposes
        # not needed since tor hopping still doesn't help to trick surveymonkey
    },
)

try:
    survey_data = get_setup_survey_data()
    if survey_data is not None and survey_data is not False:

        display_ip_info()
        while True:
            voteWorked = submitVote(survey_data, False)

            # Vote twice sometimes without changing ip sometimes only one vote per ip
            voteTwiceNumber = randint(0 , 1)
            if voteTwiceNumber == 1 and voteWorked is not False:
                print("Voting a second time with existing ip this time")
                waitTimeWithNoise(dual_vote_interval)
                submitVote(survey_data, True)

            change_tor_nodes()
            waitTimeWithNoise(ip_change_time_interval)

            # at this point connect to new tor exit node connection
            # break

except IOError as e:
    print(e)
finally:
    tor_process.kill()  # stops tor