SUBDIRS=. intl po

bin_PROGRAMS = apt-listchanges
mandir=$(prefix)/share/man/man1
datadir=$(prefix)/share/$(PACKAGE)
man_DATA = apt-listchanges.1
data_DATA = wrapper.sh

apt-listchanges: apt-listchanges.in

all-local:
	chmod +x apt-listchanges

clean-local:
	rm -f apt-listchanges.1

%.1: %.sgml
	docbook-to-man $< > $@
