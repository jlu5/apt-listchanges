# This can go away with python 2.2
from __future__ import nested_scopes
import DebianControlParser
import apt_pkg
import ConfigParser
import getopt
import string
import os
import re
import sys
import gettext
import email.Message
import email.Header
import locale
from socket import gethostname

# TODO:
# newt-like frontend, or maybe some GUI bit
# keep track of tar/dpkg-deb errors like in pre-2.0

locale.setlocale(locale.LC_ALL,'')
try:
    _ = gettext.translation('apt-listchanges').gettext
except IOError:
    _ = lambda str: str

def changelog_variations(filename):
    formats = ['usr/doc/\\*/%s.gz',
               'usr/share/doc/\\*/%s.gz',
               'usr/doc/\\*/%s',
               'usr/share/doc/\\*/%s',
               './usr/doc/\\*/%s.gz',
               './usr/share/doc/\\*/%s.gz',
               './usr/doc/\\*/%s',
               './usr/share/doc/\\*/%s']
    return map(lambda format: format % filename, formats)

def numeric_urgency(u):
    u = string.lower(u)
    if u == 'low':
        return 4
    elif u == 'medium':
        return 3
    elif u == 'high':
        return 2
    elif u == 'emergency' or u == 'critical':
        return 1
    else:
        return 0

changelog_header = re.compile('^\S+ \((?P<version>.*)\) .*;.*urgency=(?P<urgency>\w+).*')
def extract_changelog(deb, version=None):
    """Extract changelog entries later than version from deb.
    returns (text, urgency) where urgency is the highest urgency
    of the entries selected"""
    
    parser = DebianControlParser.DebianControlParser()
    parser.readdeb(deb)
    pkgdata = parser.stanzas[0]
    
    binpackage = pkgdata.Package
    srcpackage = pkgdata.source()

    changelog_filenames = changelog_variations('changelog.Debian')
    changelog_filenames_nodebian = changelog_variations('changelog')

    found = 0
    changes = None
    urgency = numeric_urgency('low')
    for filenames in [changelog_filenames, changelog_filenames_nodebian]:
         extract_command = "dpkg-deb --fsys-tarfile %s \
         | tar -xO --exclude '*/doc/*/*/*' -f - %s 2>/dev/null \
         | zcat -f" % (deb, string.join(filenames))

         if (found > 0): break

         changes = ''
         for line in os.popen(extract_command).readlines():
             if line.startswith('tar:') or line.startswith('dpkg-deb'):
                 # XXX, keep track of errors
                 continue

             found = 1

             if version:
                 match = changelog_header.match(line)
                 if match:
                     if apt_pkg.VersionCompare(match.group('version'),
                                              version) > 0:
                         urgency = min(numeric_urgency(match.group('urgency')),
                                       urgency)
                     else:
                         break
             changes += line

    return (changes, urgency)

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
                "all", "headers", "save_seen=", "debug", "version", "help"])
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
    try:
        subject = email.Header.Header(subject,
                                      locale.nl_langinfo(locale.CODESET))
    except UnicodeError:
        subject = email.Header.Header(subject, 'US-ASCII')
    except LookupError:
        subject = email.Header.Header(subject, 'UTF-8')

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
        pass

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
    
    def update_progress(self):
        self.progress += 1
        sys.stdout.write(_("Reading changelogs") + "... %d%%\r" %
                         (self.progress * 100 / self.packages))
        sys.stdout.flush()

    def progress_done(self):
        sys.stdout.write(_("Reading changelogs") + "... " + _("Done") + "\n")

class pager(ttyconfirm,fancyprogress):
    pager = 'sensible-pager'
    
    def __init__(self,packages):
        apply(fancyprogress.__init__, (self,packages))

    def display_output(self, text):
        pipe = os.popen(self.pager, 'w')
        try:
            pipe.write(text)
            pipe.close()
        except IOError:
            # Broken pipe is OK
            pass

class xterm(ttyconfirm,fancyprogress):
    def __init__(self,packages):
        apply(fancyprogress.__init__, (self,packages))
    
    def display_output(self,text):
        # Fork immediately so that we can get on with installation
        pid = os.fork()
        if pid == 0:
            (read,write) = os.pipe()
            pid = os.fork()
            if pid == 0:
                os.close(write)
                os.execlp('x-terminal-emulator',
                          'x-terminal-emulator','-title','apt-listchanges',
                          '-e','sh','-c','%s <&%d' % (self.pipecommand,read))
                sys.exit(1)
            else:
                os.close(read)
                try:
                    os.write(write,text)
                    os.close(write)
                except IOError:
                    # Broken pipe is OK
                    pass
                (junk,status) = os.waitpid(pid,0)
                if status != 0:
                    sys.stderr.write(_("%s exited with status %d")
                                     % ('xterm',status))
                    sys.exit(1)
                sys.exit(0)

class xterm_pager(xterm):
    pipecommand = 'sensible-pager'

class html:
    bug_re = re.compile('(?P<linktext>#(?P<bugnum>[1-9]\d+))', re.IGNORECASE)
    # regxlib.com
    email_re = re.compile(r'([a-zA-Z0-9_\-\.]+)@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)')

    def htmlify(self,text):
        htmltext = '''<html>
        <head>
        <title>apt-listchanges output</title>
        </head>

        <body>
        <pre>
'''
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
            htmltext += line + '\n'
        htmltext += '''</body>
        </pre>
'''

        # With python 2.2...
        #super(html,self).display_output(htmltext)
        return htmltext

    def display_output(self,text):
        # One day, this will create a temporary file to allow use with
        # any browser
        pass

class browser(pager,html):
    pager = '/usr/lib/apt-listchanges/browser-pipe'

    def display_output(self,text):
        pager.display_output(self,self.htmlify(text))

class xterm_browser(html,xterm_pager):
    pipecommand = '/usr/lib/apt-listchanges/browser-pipe'

    def display_output(self,text):
        xterm.display_output(self,self.htmlify(text))
