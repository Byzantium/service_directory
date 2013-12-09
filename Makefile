SHELL = /bin/bash
PRGNAM = service_directory
MODORDER = 001-
VERSION = $(shell git rev-parse --short HEAD)
DESTDIR?=$(BUILDDIR)/$(PRGNAM)
## Variables that should be inherited from the parent Makefile or the environment
# MODULEDIR - the directory where finished modules should but stored
# ARCH - from the build environment
# BYZBUILD - Byzantium build version
# MODEXT - module extension (should be '.xzm')
##

WEBDIR=/srv/httpd/htdocs
SERVICEDIR=/opt/byzantium/services

# high level targets
.PHONY : init build module install clean dist-clean


opt :
	$(INSTALL_EXEC) $@ $(DESTDIR)$(SERVICEDIR)

rc.service_directory :
	$(INSTALL_EXEC) $@ $(DESTDIR)etc/rc.d/$@

build : rc.service_directory opt

module : build
	dir2xzm $(DESTDIR) $(MODULEDIR)/$(MODORDER)$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)

clean :
	@# Do *not* remove $(DESTDIR)! If the build is for a monolithic module that will remove everything from every build.

dist-clean : clean
	$(CLEAN) $(MODULEDIR)/$(MODORDER)$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)
