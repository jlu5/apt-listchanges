import re
import sys, os, os.path
import tempfile
import gzip
import errno
import glob
import shutil

import gettext, locale

# TODO:
# indexed lookups by package at least, maybe by arbitrary field

locale.setlocale(locale.LC_ALL, '')
try:
    _ = gettext.translation('apt-listchanges').lgettext
except IOError:
    _ = lambda str: str

def numeric_urgency(u):
    urgency_map = { 'low' : 1,
                    'medium' : 2,
                    'high' : 3,
                    'emergency' : 4,
                    'critical' : 4 }

    return urgency_map.get(u.lower(), 5)

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

class Package:
    changelog_header = re.compile('^\S+ \((?P<version>.*)\) .*;.*urgency=(?P<urgency>\w+).*')

    def __init__(self, path):
        self.path = path

        parser = ControlParser()
        parser.readdeb(self.path)
        pkgdata = parser.stanzas[0]

        self.binary = pkgdata.Package
        self.source = pkgdata.source()
        self.source_version = pkgdata.sourceversion()

    def extract_changes(self, which, since_version=None):
        '''Extract changelog entries, news or both from the package.
        If since_version is specified, only return entries later than the specified version.
        returns a sequence of Changes objects.'''

        news_filenames = self._changelog_variations('NEWS.Debian')
        changelog_filenames = self._changelog_variations('changelog.Debian')
        changelog_filenames_native = self._changelog_variations('changelog')

        filenames = []
        if which == 'both' or which == 'news':
            filenames.extend(news_filenames)
        if which == 'both' or which == 'changelogs':
            filenames.extend(changelog_filenames)
            filenames.extend(changelog_filenames_native)

        tempdir = self.extract_contents(filenames)

        find_first = lambda acc, fname: acc or self.read_changelog(os.path.join(tempdir, fname), since_version)

        news       = reduce(find_first, news_filenames, None)
        changelog  = reduce(find_first, changelog_filenames + changelog_filenames_native, None)

        shutil.rmtree(tempdir, 1)

        return (news, changelog)

    def extract_contents(self, filenames):
        tempdir = tempfile.mkdtemp(prefix='apt-listchanges')

        extract_command = 'dpkg-deb --fsys-tarfile %s | tar xf - --wildcards -C %s %s 2>/dev/null' % (
            self.path, tempdir,
            ' '.join(["'" + x + "'" for x in filenames])
        )

        # tar exits unsuccessfully if _any_ of the files we wanted
        # were not available, so we can't do much with its status
        os.system(extract_command)

        return tempdir

    def read_changelog(self, filename, since_version):
        filenames = glob.glob(filename)

        fd = None
        for filename in filenames:
            try:
                if os.path.isdir(filename):
                    print >> sys.stderr, _("Ignoring `%s' (seems to be a directory !)") % filename
                elif filename.endswith('.gz'):
                    fd = gzip.GzipFile(filename)
                else:
                    fd = open(filename)
                break
            except IOError, e:
                if e.errno == errno.ENOENT:
                    pass
                else:
                    raise

        if not fd:
            return None

        urgency = numeric_urgency('low')
        changes = ''
        is_debian_changelog = 0
        for line in fd.readlines():
            match = self.changelog_header.match(line)
            if match:
                is_debian_changelog = 1
                if since_version:
                    if apt_pkg.VersionCompare(match.group('version'),
                                              since_version) > 0:
                        urgency = max(numeric_urgency(match.group('urgency')),
                                      urgency)
                    else:
                        break
            changes += line

        if not is_debian_changelog:
            return None

        return Changes(self.source, changes, urgency)

    def _changelog_variations(self, filename):
        formats = ['usr/doc/*/%s.gz',
                   'usr/share/doc/*/%s.gz',
                   'usr/doc/*/%s',
                   'usr/share/doc/*/%s',
                   './usr/doc/*/%s.gz',
                   './usr/share/doc/*/%s.gz',
                   './usr/doc/*/%s',
                   './usr/share/doc/*/%s']
        return [x % filename for x in formats]

class Changes:
    def __init__(self, package, changes, urgency):
        self.package = package
        self.changes = changes
        self.urgency = urgency

__all__ = [ 'ControlParser', 'Package' ]
