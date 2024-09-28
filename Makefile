SERVICE := missions
DESTDIR ?= dist_root
SERVICEDIR ?= /srv/$(SERVICE)

.PHONY: build install

build:
	echo nothing to build

install: build
	mkdir -p $(DESTDIR)$(SERVICEDIR)
	cp -r docker-compose-release.yml $(DESTDIR)$(SERVICEDIR)/docker-compose.yml
	cp -r cached  $(DESTDIR)$(SERVICEDIR)
	cp -r missiond  $(DESTDIR)$(SERVICEDIR)
	cp -r frontend  $(DESTDIR)$(SERVICEDIR)
	#echo "# censored" > $(DESTDIR)$(SERVICEDIR)/missiond/Dockerfile
	mkdir -p $(DESTDIR)/etc/systemd/system/faustctf.target.wants/
	ln -s /etc/systemd/system/docker-compose@.service $(DESTDIR)/etc/systemd/system/faustctf.target.wants/docker-compose@$(SERVICE).service

