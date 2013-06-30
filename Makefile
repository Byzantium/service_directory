.EXPORT_ALL_VARIABLES

SHELL = /bin/sh
INSTALL_DIR=$(INSTALL) -D 
INSTALL_EXEC=$(INSTALL) -m 755 
CLEAN=-rm -rf
WEBDIR=/srv/httpd/htdocs
SERVICEDIR=/opt/byzantium/services
## Variables that should be inherited from the parent Makefile or the environment
# MODULEDIR - the directory where finished modules should but stored
# PRGNAM - module name
# VERSION - module/software version (use the short hash of the git commit if you aren't sure)
# ARCH - from the build environment
# BYZBUILD - Byzantium build version
# MODEXT - module extension (should be '.xzm')
##

# high level targets
.PHONY : init build module install clean dist-clean web web-clean rc rc-clean backend backend-clean 

web: index.html static tmpl
	$(INSTALL_DIR) $@ $(DESTDIR)/$(WEBDIR)

web-clean: index.html static tmpl
	$(CLEAN) $(DESTDIR)/$(WEBDIR)/$@

rc: rc.avahiclient
	$(INSTALL_EXEC) $@ $(DESTDIR)/etc/rc.d

rc-clean: rc.avahiclient
	$(CLEAN) $(DESTDIR)/etc/rc.d/$@

backend: rc.avahiclient *.py avahiclient.sh
	$(INSTALL_EXEC) $@ $(DESTDIR)/$(SERVICEDIR)

backend-clean: rc.avahiclient *.py avahiclient.sh
	$(CLEAN) $(DESTDIR)/$(SERVICEDIR)/$@

init:
	echo 'init is a noop in this Makefile'

build: init
	echo 'build is a noop in this Makefile'

install: build web rc backend

module: install
	dir2xzm $(DESTDIR) $(MODULEDIR)/$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)

clean: web-clean backend-clean
	# Do *not* remove $(DESTDIR)! If the build is for a monolithic module that will remove everything from every build.

dist-clean: clean
	$(CLEAN) $(MODULEDIR)/$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)
