# Makefile for program source directory in GNU NLS utilities package.
# Copyright (C) 1995-1997, 2000, 2001 by Ulrich Drepper <drepper@gnu.ai.mit.edu>
#
# This file file be copied and used freely without restrictions.  It can
# be used in projects which are not available under the GNU Public License
# but which still want to provide support for the GNU gettext functionality.
# Please note that the actual code is *not* freely available.

PACKAGE = apt-listchanges
prefix = /usr
exec_prefix = ${prefix}
datadir = $(prefix)/share
localedir = $(datadir)/locale
gettextsrcdir = $(prefix)/share/gettext/po
subdir = po
srcdir = .

INSTALL = /usr/bin/install -c
INSTALL_DATA = ${INSTALL} -m 644
MKINSTALLDIRS = ../mkinstalldirs

CC = gcc
GENCAT = gencat
MSGFMT = /usr/bin/msgfmt --statistics
XGETTEXT = /usr/share/doc/python2.2/examples/Tools/i18n/pygettext.py
MSGMERGE = msgmerge

POFILES =  $(wildcard *.po)
MOFILES =  $(patsubst %.po,%.mo,$(POFILES))

POTFILES = ../apt-listchanges ../apt_listchanges.py ../DebianControlParser.py

all: $(PACKAGE).pot $(MOFILES)

.SUFFIXES: .po .mo

.po.mo:
	$(MSGFMT) -o $@ $<

# Note: Target 'all' must not depend on target '$(srcdir)/$(PACKAGE).pot',
# otherwise packages like GCC can not be built if only parts of the source
# have been downloaded.

$(PACKAGE).pot: $(POTFILES)
	if test -f $(XGETTEXT); then \
		$(XGETTEXT) --default-domain=$(PACKAGE) \
			--keyword=_ $(POTFILES); \
	else \
		touch $@; \
	fi

install: all
	for file in $(MOFILES); do \
                lang=`echo $$file | sed 's/\.mo//'`; \
                install -d $(DESTDIR)$(localedir)/$$lang/LC_MESSAGES/; \
                install -m 0644 $$file $(DESTDIR)$(localedir)/$$lang/LC_MESSAGES/$(PACKAGE).mo; \
        done

mostlyclean:
	rm -f core core.* *.pox $(PACKAGE).po *.new.po
	rm -fr *.o

clean: mostlyclean

distclean: clean
	rm -f *.mo $(PACKAGE).pot

update-po: Makefile
	$(MAKE) $(PACKAGE).pot
	if test "$(PACKAGE)" = "gettext"; then PATH=`pwd`/../src:$$PATH; fi; \
        cd $(srcdir); \
        catalogs='$(MOFILES)'; \
        for cat in $$catalogs; do \
          cat=`basename $$cat`; \
          lang=`echo $$cat | sed 's/\.mo$$//'`; \
          echo "$$lang:"; \
          if $(MSGMERGE) $$lang.po $(PACKAGE).pot -o $$lang.new.po; then \
            mv -f $$lang.new.po $$lang.po; \
          else \
            echo "msgmerge for $$cat failed!"; \
            rm -f $$lang.new.po; \
          fi; \
        done

