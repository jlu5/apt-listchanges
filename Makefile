all:
	docbook-to-man apt-listchanges.sgml > apt-listchanges.1
	docbook-to-man apt-listchanges.es.sgml > apt-listchanges.es.1
	docbook-to-man apt-listchanges.fr.sgml > apt-listchanges.fr.1
	make -C po

install: all
	install -d $(DESTDIR)/usr/bin
	install -m 755 apt-listchanges $(DESTDIR)/usr/bin
	install -d $(DESTDIR)/usr/lib/site-python
	install -m 644 DebianControlParser.py apt_listchanges.py \
		$(DESTDIR)/usr/lib/site-python
	install -d $(DESTDIR)/etc/apt/apt.conf.d
	install -m 644 debian/apt.conf \
		$(DESTDIR)/etc/apt/apt.conf.d/20listchanges
	install -d $(DESTDIR)/usr/share/man/man1 $(DESTDIR)/usr/share/man/es/man1 $(DESTDIR)/usr/share/man/fr/man1
	install -m 644 apt-listchanges.1 $(DESTDIR)/usr/share/man/man1
	install -m 644 apt-listchanges.es.1 $(DESTDIR)/usr/share/man/es/man1/apt-listchanges.1
	install -m 644 apt-listchanges.fr.1 $(DESTDIR)/usr/share/man/fr/man1/apt-listchanges.1
	$(MAKE) -C po install

clean:
	rm -f apt-listchanges.1 apt-listchanges.es.1 apt-listchanges.fr.1
	make -C po clean
