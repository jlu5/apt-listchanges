import DebianControlParser
import apt_pkg
import ConfigParser
import getopt
import os
import re
import sys
import gettext
import email.Message
import email.Header
import locale
import cStringIO
import tempfile
import shutil
import gzip
import errno
import glob
from socket import gethostname

# TODO:
# newt-like frontend, or maybe some GUI bit
# keep track of tar/dpkg-deb errors like in pre-2.0

locale.setlocale(locale.LC_ALL,'')
try:
    _ = gettext.translation('apt-listchanges').gettext
except IOError:
    _ = lambda str: str

def numeric_urgency(u):
    urgency_map = { 'low' : 1,
                    'medium' : 2,
                    'high' : 3,
                    'emergency' : 4,
                    'critical' : 4 }

    return urgency_map.get(u.lower(), 5)

class Package:
    changelog_header = re.compile('^\S+ \((?P<version>.*)\) .*;.*urgency=(?P<urgency>\w+).*')

    def __init__(self, path):
        self.path = path
        
        parser = DebianControlParser.DebianControlParser()
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
        if which == 'both' or which == 'changelog':
            filenames.extend(changelog_filenames)
            filenames.extend(changelog_filenames_native)

        tempdir = self.extract_contents(filenames)

        news = None
        for filename in news_filenames:
            news = self.read_changelog(os.path.join(tempdir,filename),
                                       since_version)
            if news:
                break

        changelog = None
        for batch in (changelog_filenames, changelog_filenames_native):
            for filename in batch:
                changelog = self.read_changelog(os.path.join(tempdir,filename),
                                                since_version)
                if changelog:
                    break
            if changelog:
                break

        shutil.rmtree(tempdir,1)
        
        return (news, changelog)
        
    def extract_contents(self, filenames):
        try:
            tempdir = tempfile.mkdtemp(prefix='apt-listchanges')
        except AttributeError:
            tempdir = tempfile.mktemp()
            os.mkdir(tempdir)

        extract_command = 'dpkg-deb --fsys-tarfile %s |tar xf - -C %s %s 2>/dev/null' % (
            self.path,
            tempdir,
            ' '.join(map(lambda x: "'%s'" % x, filenames))
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
                if filename.endswith('.gz'):
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
                    is_debian_changelog = 1
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

    def _changelog_variations(self,filename):
        formats = ['usr/doc/*/%s.gz',
                   'usr/share/doc/*/%s.gz',
                   'usr/doc/*/%s',
                   'usr/share/doc/*/%s',
                   './usr/doc/*/%s.gz',
                   './usr/share/doc/*/%s.gz',
                   './usr/doc/*/%s',
                   './usr/share/doc/*/%s']
        return map(lambda format: format % filename, formats)

class Changes:
    def __init__(self, package, changes, urgency):
        self.package = package
        self.changes = changes
        self.urgency = urgency

class Config:
    def __init__(self):
        # Defaults
        self.frontend = 'pager'
        self.email_address = None
        self.verbose = 0
        self.quiet = 0
        self.show_all = 0
        self.confirm = 0
        self.headers = 0
        self.debug = 0
        self.save_seen = None
        self.mode = 'cmdline'
        self.which = 'both'

    def read(self,file):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(file)

    def expose(self):
        if self.parser.has_section(self.mode):
            for option in self.parser.options(self.mode):
                value = None
                if self.parser.has_option(self.mode,option):
                    if option in ('confirm','run','show_all','headers','verbose'):
                        value = self.parser.getboolean(self.mode,option)
                    else:
                        value = self.parser.get(self.mode,option)
                setattr(self, option, value)

    def usage(self,exitcode):
        if exitcode == 0:
            fh = sys.stdout
        else:
            fh = sys.stderr
            
        fh.write("Usage: apt-listchanges [options] {--apt | filename.deb ...}\n")
        sys.exit(exitcode)


    def getopt(self,argv):
        try:
            (optlist, args) = getopt.getopt(argv[1:], 'vf:s:cah', [
                "apt", "verbose", "frontend=", "email-address=", "confirm",
                "all", "headers", "save_seen=", "debug", "which", "version", "help"])
        except getopt.GetoptError:
            return None

        # Determine mode before processing other options
        for opt, arg in optlist:
            if opt == '--apt':
                self.mode = 'apt'

        # Expose defaults from config file
        self.expose()

        # Override with environment variables
        self.frontend = os.getenv('APT_LISTCHANGES_FRONTEND', self.frontend)

        # Override with command-line options
        for opt, arg in optlist:
            if opt == '--help':
                self.usage(0)
            if opt == '--version':
                print "apt-listchanges version 2.0"
                sys.exit(0)
            if opt in ('-v', '--verbose'):
                self.verbose = 1
            elif opt in ('-f', '--frontend'):
                self.frontend = arg
            elif opt == '--email-address':
                self.email_address = arg
            elif opt in ('-c', '--confirm'):
                self.confirm = 1
            elif opt in ('-a', '--all'):
                self.show_all = 1
            elif opt in ('-h', '--headers'):
                self.headers = 1
            elif opt == '--save_seen':
                self.save_seen = arg
            elif opt == '--which':
                self.which = arg
            elif opt == '--debug':
                self.debug = 1

        if self.email_address == 'none':
            self.email_address = None
        if self.save_seen == 'none':
            self.save_seen = None

        return args

def read_apt_pipeline(config):
    version = sys.stdin.readline().rstrip()
    if version != "VERSION 2":
        sys.stderr.write(_('''Wrong or missing VERSION from apt pipeline
(is Dpkg::Tools::Options::/usr/bin/apt-listchanges::Version set to 2?)
'''))
        sys.exit(1)

    while 1:
        aptconfig = sys.stdin.readline()
        if not aptconfig or aptconfig == '\n':
            break

        (option, value) = aptconfig.rstrip().split('=', 1)
        
        if option == 'quiet':
            config.quiet = value

    filenames = {}
    order = []
    for pkgline in sys.stdin.readlines():
        if not pkgline:
            break
        
        (pkgname, oldversion, compare, newversion, filename) = pkgline.split()
        if compare != '<' or oldversion == '-':
            continue

        if filename == '**CONFIGURE**':
            order.append(pkgname)
        elif filename == '**REMOVE**':
            continue
        else:
            filenames[pkgname] = filename

    # Sort by configuration order.  THIS IS IMPORTANT.  Sometimes, a
    # situation exists where package X contains changelog.gz (upstream
    # changelog) and depends on package Y which contains
    # changelog.Debian.gz (Debian changelog).  Until we have a more
    # reliable method for determining whether a package is Debian
    # native, this allows things to work, since Y will always be
    # configured first.
    
    return map(lambda pkg: filenames[pkg], order)

def mail_changes(address, changes):
    print "apt-listchanges: " + _("Mailing changelogs to %s") % address

    hostname = gethostname()
    message = email.Message.Message()
    subject = _("apt-listchanges output for %s") % hostname
# this way lies madness -mdz, 2003/06/29
#     try:
#         subject = email.Header.Header(subject,
#                                       locale.nl_langinfo(locale.CODESET))
#     except:
#         subject = email.Header.Header(subject, 'UTF-8')

    message['Subject'] = subject
    message['To'] = address
    message.set_payload(changes, 'utf-8')

    fh = os.popen('/usr/sbin/sendmail -t', 'w')
    fh.write(message.as_string())
    fh.close()

def make_frontend(name, packages):
    frontends = { 'text' : text,
                  'pager' : pager,
                  'mail' : mail,
                  'browser' : browser,
                  'xterm-pager' : xterm_pager,
                  'xterm-browser' : xterm_browser }
    
    if name in ('newt','w3m','xterm-w3m'):
        sys.stderr.write((_("The %s frontend is deprecated, using pager") + '\n') % name)
        name = 'pager'
        
    if not frontends.has_key(name):
        return None
    return frontends[name](packages)
         
class frontend:
    def __init__(self,packages):
        self.packages = packages

    def update_progress(self):
        pass

    def progress_done(self):
        pass

    def display_output(self,text):
        self._display_output(self._render(text))

    def _render(self,text):
        return text

    def confirm(self):
        return 1

class ttyconfirm:
    def confirm(self):
        tty = open('/dev/tty', 'r+')
        tty.write('apt-listchanges: ' +
                       _('Do you want to continue? [Y/n]? '))
        tty.flush()
        response = tty.readline()
        if response == '\n' or re.search(locale.nl_langinfo(locale.YESEXPR),
                                         response):
            return 1
#         if re.match(locale.nl_langinfo(locale.NOEXPR),response[0]):
#             return 0
        return 0

class simpleprogress:
    def __init__(self,packages):
        # XXX Should omit progress indication entirely if stdout not a
        # terminal
        sys.stderr.write(_("Reading changelogs") + "...\n")

    def update_progress(self):
        pass

    def progress_done(self):
        pass

class mail(frontend,simpleprogress):
    def __init__(self,packages):
        apply(simpleprogress.__init__, (self,packages))

class text(ttyconfirm,simpleprogress):
    def __init__(self,packages):
        apply(simpleprogress.__init__, (self,packages))

    def display_output(self,text):
        sys.stdout.write(text)

class fancyprogress(frontend):
    def __init__(self,packages):
        apply(frontend.__init__, (self,packages))
        self.progress = 0
        self.line_length = 0
    
    def update_progress(self):
        self.progress += 1
        line = _("Reading changelogs") + "... %d%%" % (self.progress * 100 / self.packages)
        self.line_length = len(line)
        sys.stdout.write(line + '\r')
        sys.stdout.flush()

    def progress_done(self):
        sys.stdout.write(' ' * self.line_length + '\r')
        sys.stdout.write(_("Reading changelogs") + "... " + _("Done") + "\n")
        sys.stdout.flush()

class runcommand:
    mode = os.P_WAIT
    suffix = ''
    
    def display_output(self, text):
        if self.mode == os.P_NOWAIT:
            if os.fork() != 0:
                return

        tmp = tempfile.NamedTemporaryFile(suffix=self.suffix)
        tmp.write(self._render(text))
        tmp.flush()
        shellcommand = self.command + ' ' + tmp.name
    
        status = os.spawnl(os.P_WAIT, '/bin/sh', 'sh', '-c', shellcommand)
        if status != 0:
            raise OSError('Subprocess ' + shellcommand + ' exited with status ' + str(status))

class pager(runcommand,ttyconfirm,fancyprogress):
    command = 'sensible-pager'

    def __init__(self,packages):
        apply(fancyprogress.__init__, (self,packages))

class xterm(runcommand,ttyconfirm,fancyprogress):
    def __init__(self,packages):
        apply(fancyprogress.__init__, (self,packages))
        self.mode = os.P_NOWAIT
        self.command = 'x-terminal-emulator -T apt-listchanges -e ' + self.xterm_command

class xterm_pager(xterm):
    xterm_command = 'sensible-pager'

class html:
    suffix = '.html'
    
    bug_re = re.compile('(?P<linktext>#(?P<bugnum>[1-9]\d+))', re.IGNORECASE)
    # regxlib.com
    email_re = re.compile(r'([a-zA-Z0-9_\-\.]+)@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)')

    def _render(self,text):
        htmltext = cStringIO.StringIO()
        htmltext.write('''<html>
        <head>
        <title>apt-listchanges output</title>
        </head>

        <body>
        <pre>
''')
        for line in text.split('\n'):
            line = line.replace(
                '&', '&amp;').replace(
                '<', '&lt;').replace(
                '>','&gt;')
            line = re.sub(self.bug_re,
                          r'<a href="http://bugs.debian.org/\g<bugnum>">\g<linktext></a>',
                          line)
            line = re.sub(self.email_re,
                          r'<a href="mailto:\g<0>">\g<0></a>',
                          line)
            htmltext.write(line + '\n')
        htmltext.write('''</body>
        </pre>
''')

        return htmltext.getvalue()

class browser(html,pager):
    command = 'sensible-browser'

class xterm_browser(html,xterm):
    xterm_command = 'sensible-browser'

