SUBDIRS=. intl po

bin_SCRIPTS = apt-listchanges
mandir=$(prefix)/share/man/man1
man_DATA = apt-listchanges.1

all-local:
	chmod +x apt-listchanges

clean-local:
	rm -f apt-listchanges.1

%.1: %.sgml
	docbook-to-man $< > $@
