SHELL = /bin/bash
PRGNAM = service_directory
MODORDER = 001-
VERSION = -$(shell git rev-parse --short HEAD)
DESTDIR ?= $(BUILDDIR)/$(PRGNAM)-package
## Variables that should be inherited from the parent Makefile or the environment
# MODULEDIR - the directory where finished modules should but stored
# ARCH - from the build environment
# BYZBUILD - Byzantium build version
# MODEXT - module extension (should be '.xzm')
# MKDIR - make a directory
# INSTALL_* - install commands
# CLEAN - clean files from build environment
##

SERVICESRC ?= opt/

SERVICEDIR ?= $(DESTDIR)
RCDIR ?= $(DESTDIR)etc/rc.d/

RCSCRIPTS = rc.$(PRGNAM)

RC_TARGETS = $(foreach rcscript, $(RCSCRIPTS), $(RCDIR)$(rcscript))
SERVICE_TARGETS = $(foreach servicefile, $(shell find $(SERVICESRC)), $(SERVICEDIR)$(servicefile))

# high level targets
.PHONY : init build module install clean dist-clean service-clean rc-clean

DIRS = $(DESTDIR) $(RCDIR) $(SERVICEDIR)

init : $(DIRS)

build : init

install : build $(RC_TARGETS) $(SERVICE_TARGETS)

module : install $(MODULEDIR)$(MODORDER)$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)

clean : rc-clean service-clean

dist-clean : clean
	@# Do *not* remove $(DESTDIR)! If the build is for a monolithic module that will remove everything from every build.
	$(CLEAN) $(MODULEDIR)$(MODORDER)$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT)

rc-clean :
	$(CLEAN) $(RC_TARGETS)

service-clean :
	$(CLEAN) $(SERVICE_TARGETS)

$(DIRS) :
	$(MKDIR) $@

$(RC_TARGETS) :
	$(INSTALL_EXEC) $(notdir $@) $@

$(SERVICE_TARGETS) :
	$(MKDIR) $@
	$(CP) $(wildcard $(SERVICESRC)*) $@

$(MODULEDIR)$(MODORDER)$(PRGNAM)$(VERSION)-$(ARCH)-$(BYZBUILD).$(MODEXT): $(MODULEDIR)
	$(MAKEMODULE) $@
	@#$(DESTDIR) $@

