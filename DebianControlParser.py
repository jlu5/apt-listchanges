import os
import string
import re

# TODO:
# indexed lookups by package at least, maybe by arbitrary field

class DebianControlParser:
    def __init__(self):
        self.stanzas = []
        self.index = {}

    def makeindex(self,field):
        self.index[field] = {}
        for stanza in self.stanzas:
            self.index[field][getattr(stanza,field)] = stanza
            
    class DebianControlStanza:
        sourceversionre = re.compile('\((?P<version>.*).*\)')
        
        def __init__(self,str):
            field = None

            for line in str.split('\n'):
                if not line:
                    break
                if line[0] == ' ':
                    if not field:
                        # XXX, raise an exception
                        pass
                    else:
                        setattr(self, field,
                                getattr(self, field) + '\n' + line)
                else:
                    colon = line.find(':')
                    field = line[:colon]
                    value = line[colon+1:].lstrip()
                    setattr(self, field, value)

        def source(self):
            if hasattr(self, 'Source'):
                return self.Source.split(' ')[0]
            else:
                return self.Package

        def sourceversion(self):
            if hasattr(self, 'Source'):
                m = self.sourceversionre.search(self.Source)
                if m:
                    return m.group('version')
            if hasattr(self, 'Version'):
                return self.Version
            return None

        def installed(self):
            if hasattr(self, 'Status'):
                return self.Status.split(' ')[2] == 'installed'
            return 0

    def readfile(self,file):
        for chunk in open(file, 'r').read().split('\n\n'):
            if chunk:
                self.stanzas.append(self.DebianControlStanza(chunk))
    
    def readdeb(self,deb):
        fh=os.popen('dpkg-deb -f %s' % deb)
        self.stanzas.append(self.DebianControlStanza(fh.read()))
                            
    def find(self,field,value):
        if self.index.has_key(field):
            return self.index[field][value]
        else:
            for stanza in self.stanzas:
                if hasattr(stanza,field) and getattr(stanza,field) == value:
                    return stanza
        return None
