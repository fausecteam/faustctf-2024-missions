import requests
import json

proxies = {
#	"http": "http://localhost:8080"
}

def login(BASE, session, mission, secret):
	r = session.post(
		f"{BASE}/api/authenticate",
		json = {
			"mission": mission,
			"secret": secret
		}, proxies = proxies, headers={'Connection':'close'})
	return r
		
def create(BASE, session, mission, short):
	r = session.post(
		f"{BASE}/api/create",
		json = {
			"name": mission,
			"short": short
		}, proxies = proxies, headers={'Connection':'close'})
	try:
		j = r.json()
		return j["secret"]
	except KeyError:
		return None
	except json.JSONDecodeError:
		print("Error converting to json. got: ", r.content)
		return None

def logout(BASE, session):
	session.get(
		f"{BASE}/api/logout"
		, proxies = proxies)

def get_missioninfo(BASE, session, mission):
	session.get(
		f"{BASE}/api/missioninfo/{mission}"
		, proxies = proxies)

def get_missionlist(BASE, session):
	return session.get(
		f"{BASE}/api/missions"
	, proxies = proxies).json()

def add_data(BASE, session, data):
	r = session.post(
		f"{BASE}/api/add_data",
		json = {
			"data": data
		}, proxies = proxies, headers={'Connection':'close'})
	print(r.content)

def get_data(BASE, session, secret = None):
	j = {}
	if secret != None:
		j["secret"] = secret
	r = session.post(
		f"{BASE}/api/get_data"
		, json = j
		, proxies = proxies, headers={'Connection':'close'})
	try:
		j = r.json()
		return j["data"]
	except KeyError:
		return None
	except json.JSONDecodeError:
		print("Error converting to json in get_data(). got: ", r.content)
		return None

"""not implemented in backend
def remove(BASE, session, secret):
	session.post(
		f"{BASE}/api/remove",
		json = {
			"secret": secret
		}, proxies = proxies)"""
