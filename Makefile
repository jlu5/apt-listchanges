DESTDIR=/usr/local
TARGETS=apt-listchanges.1

all: $(TARGETS)

install:
	install -d $(DESTDIR)/bin $(DESTDIR)/share/man/man1
	install -m 755 apt-listchanges $(DESTDIR)/bin
	install -m 644 apt-listchanges.1 $(DESTDIR)/share/man/man1

clean:
	rm -f $(TARGETS)

%.1: %.sgml
	docbook-to-man $< > $@

