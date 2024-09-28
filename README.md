# CI Example for a service using docker-compose

The .gitlab-ci.yml in this repo builds and pushes all possible images (docker-compose.yml is parsed and used to call kaniko).

In the vulnbox build process, the compose file is used to pull all images and include them in the vm.

## SPOILER

There are multiple dockers involved
- missiond / dockername: webapp Port 5000
	- simple flask webapp
	- provides login etc.
- varnish (9090)
	- queries webapp (5000)
- frontend (3000)
	- nuxt
	- no idea why
	
## Vulnerability & Attack
The varnish cache is intended to cache images starting with `/imgs`, but `~ /imgs` is a `contains` matching and not a `startswith` matching. This causes also the endpoint `/userinfo/imgsxxx` to be cached for specifically created usernames.

**Attack**
1. Create a user `imgsxxx`
2. Request the userinfo `/userinfo/imgsxxx`, this caches your own cookie into to response
3. wait
	- the bot will iterate all users and request their info page
	- the cached response will cause the bot to take over the cookie of your account
	- the bot adds a note to your account
4. Query the data of your account
