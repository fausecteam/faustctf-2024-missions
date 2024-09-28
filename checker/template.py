#!/usr/bin/env python3

from ctf_gameserver import checkerlib

import utils
import requests
import random
import logging
import string
import time
import urllib3
import json

from comm import *
COOKIE_NAME = "session"
# TODO make it look like a normal browser

def rnd_name():
	r = random.randint(1, 3)
	if r == 1:
		return "Test_" + str(random.randint(1, 125123))
	elif r == 2:
		return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
	elif r == 3:
		return "Investigate Mr. " + "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
	return None

def rnd_pwd():
	return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(20))

class TemplateChecker(checkerlib.BaseChecker):

	def place_flag(self, tick):
		try:
			FLAG = checkerlib.get_flag(tick)
			BASE = f"http://[{self.ip}]:9090"
			s_victim = requests.Session()
			name = rnd_name()
			# create
			try:
				pwd = create(BASE, s_victim, name, "Nothing to see here")
			except json.JSONDecodeError:
				logging.error(f"Service did not return JSON")
				return checkerlib.CheckResult.FAULTY
			checkerlib.store_state(str(tick), {
				"name": name,
				"pwd": pwd
			})
			login(BASE, s_victim, name, pwd)
			try:
				c = s_victim.cookies[COOKIE_NAME]
				logging.info(f"My own cookie is: {c}")
			except KeyError:
				logging.info("No cookie")
			# Victim loads missionlist
			try:
				missions = get_missionlist(BASE, s_victim)
			except json.JSONDecodeError as e:
				logging.error(f"while running get_missionlist: JSONDecodeError: {e}")
				return checkerlib.CheckResult.FAULTY
			# Iterate missions, verify cookies after each one and send the post request
			# The POST request will add the notes to the mission of the victim user, unless the cookie got replaced by a recently cached response
			for mission in missions[-100:]:
				name = mission["name"]
				logging.info(f"\t.. getting missioninfo for {name}")
				get_missioninfo(BASE, s_victim, name)
				try:
					c = s_victim.cookies[COOKIE_NAME]
					if name.startswith("imgs"):
						logging.info(f"This will probably be cached and we will get their cookie: {c}")
					else:
						logging.info(f"Should be the same cookie as before: {c}")
				except KeyError:
					logging.info("No cookie found")
				#	assert s_victim.cookies[COOKIE_NAME] != cookie_victim
				#else:
				#	assert s_victim.cookies[COOKIE_NAME] == cookie_victim
				# POST
				add_data(BASE, s_victim, f"Status update: {FLAG}</br>")
			logout(BASE, s_victim)
		except (urllib3.exceptions.MaxRetryError, TimeoutError):
			return checkerlib.CheckResult.DOWN
		return checkerlib.CheckResult.OK

	def check_service(self):
		try:
			# TODO: Implement (maybe use `utils.generate_message()`)
			BASE = f"http://[{self.ip}]:9090"
			n1 = rnd_name()
			t = int(time.time())
			qs = [
				f"{BASE}/imgs/{n1}.png",
				f"{BASE}/imgs/{n1}.png", # Identical
				f"{BASE}/imgs/{n1}.png?t={t}", # Cache Buster
				f"{BASE}/imgs/{n1}.png?t={t}", # Cache Buster again
			]
			ergs = []
			for q in qs:
				r = requests.get(q, proxies = proxies)
				if r.status_code != 200:
					logging.warning(f"Image {q} did not return successfully but with code {r.status_code}")
					return checkerlib.CheckResult.FAULTY
				ergs.append(r.content)
				
			if ergs[0] != ergs[1]: # should be cached
				logging.info("Identical images 0 and 1 are not identical (probably not cached)")
				return checkerlib.CheckResult.FAULTY
			if ergs[2] != ergs[3]: # should be cached
				logging.info("Identical images 2 and 3 are not identical (probably not cached)")
				return checkerlib.CheckResult.FAULTY
			if ergs[1] == ergs[2]: # with cachebuster
				logging.info("Different images are identical")
				return checkerlib.CheckResult.FAULTY
			# TODO: test remaining functionaility
			# Check if they allow to create users starting with imgs
			s_victim = requests.Session()
			name = "imgs" + rnd_name()[5:]
			try:
				pwd = create(BASE, s_victim, name, "Nothing to see here")
				rnd_data = rnd_pwd()
				add_data(BASE, s_victim, rnd_data)
				data = get_data(BASE, s_victim, pwd)
				if data != rnd_data:
					logging.error(f"Data in newly placed information is {data}, but we put {rnd_data}")
					return checkerlib.CheckResult.FAULTY
			except json.JSONDecodeError:
				logging.error(f"Service did not return JSON")
				return checkerlib.CheckResult.FAULTY
		except (urllib3.exceptions.MaxRetryError, TimeoutError):
			return checkerlib.CheckResult.DOWN
		return checkerlib.CheckResult.OK

	def check_flag(self, tick):
		try:
			BASE = f"http://[{self.ip}]:9090"
			expect_flag = checkerlib.get_flag(tick)
			logging.info("Checking flag %s for tick %d" % (expect_flag, tick))
			# get data and delete sign values (prepare for load game state)
			tickdata = checkerlib.load_state(str(tick))
			if tickdata == None:
				logging.error("No checker state exists for tick %d" % tick)
				return checkerlib.CheckResult.FLAG_NOT_FOUND

			s = requests.Session()
			l = login(BASE, s, tickdata["name"], tickdata["pwd"])
			if l.status_code != 200:
				logging.error("Login failed with old user")
				return checkerlib.CheckResult.FLAG_NOT_FOUND
			data = get_data(BASE, s, tickdata["pwd"])
			if not data or expect_flag not in data:
				logging.error(f"Missing flag, only got {data}")
				return checkerlib.CheckResult.FLAG_NOT_FOUND
			return checkerlib.CheckResult.OK
		except SystemExit as e:
			logging.error("Failed checking the flag. Probably service died?")
			logging.error(e)
			return checkerlib.CheckResult.FLAG_NOT_FOUND
		except (urllib3.exceptions.MaxRetryError, TimeoutError):
			return checkerlib.CheckResult.DOWN

if __name__ == '__main__':

	checkerlib.run_check(TemplateChecker)
