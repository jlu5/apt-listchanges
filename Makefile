PYLIBDIR := /usr/lib/$(shell pyversions -d)/site-packages

all:
	docbook-to-man apt-listchanges.sgml > apt-listchanges.1
	docbook-to-man apt-listchanges.es.sgml > apt-listchanges.es.1
	docbook-to-man apt-listchanges.fr.sgml > apt-listchanges.fr.1
	make -C po

install: all
	install -d $(DESTDIR)/usr/bin
	install -m 755 apt-listchanges $(DESTDIR)/usr/bin
	install -d $(DESTDIR)$(PYLIBDIR)/apt_listchanges
	install -m 644 apt_listchanges/* $(DESTDIR)$(PYLIBDIR)/apt_listchanges
	install -d $(DESTDIR)/etc/apt/apt.conf.d
	install -m 644 debian/apt.conf $(DESTDIR)/etc/apt/apt.conf.d/20listchanges
	for man in apt-listchanges*.1; do \
	    lang=`echo $$man | sed -e 's/apt-listchanges\.*// ; s/\.*1//'`; \
	    install -d $(DESTDIR)/usr/share/man/$$lang/man1;                \
	    install -m 644 $$man $(DESTDIR)/usr/share/man/$$lang/man1/apt-listchanges.1; \
	done
	$(MAKE) -C po install

clean:
	rm -f apt-listchanges.1
	make -C po clean
