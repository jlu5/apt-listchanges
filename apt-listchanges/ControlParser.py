import os, re

# TODO:
# indexed lookups by package at least, maybe by arbitrary field

class ControlStanza:
    sourceversionre = re.compile('\((?P<version>.*).*\)')

    def __init__(self, str):
        field = None

        for line in str.split('\n'):
            if not line:
                break
            if line[0] in (' ', '\t'):
                if field:
                    setattr(self, field, getattr(self, field) + '\n' + line)
            else:
                field, value = line.split(':', 1)
                setattr(self, field, value.lstrip())

    def source(self):
        return getattr(self, 'Source', self.Package).split(' ')[0]

    def sourceversion(self):
        if hasattr(self, 'Source'):
            m = self.sourceversionre.search(self.Source)
            if m:
                return m.group('version')
        return getattr(self, 'Version', None)

    def installed(self):
        return hasattr(self, 'Status') and self.Status.split(' ')[2] == 'installed'


class ControlParser:
    def __init__(self):
        self.stanzas = []
        self.index = {}

    def makeindex(self, field):
        self.index[field] = {}
        for stanza in self.stanzas:
            self.index[field][getattr(stanza, field)] = stanza

    def readfile(self, file):
        self.stanzas += [ControlStanza(x) for x in open(file, 'r').read().split('\n\n') if x]

    def readdeb(self, deb):
        fh = os.popen('dpkg-deb -f %s' % deb)
        self.stanzas.append(ControlStanza(fh.read()))

    def find(self, field, value):
        if self.index.has_key(field):
            if self.index[field].has_key(value):
                return self.index[field][value]
            else:
                return None
        else:
            for stanza in self.stanzas:
                if hasattr(stanza, field) and getattr(stanza, field) == value:
                    return stanza
        return None

__all__ = [ 'ControlParser' ]
