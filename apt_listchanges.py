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
from socket import gethostname

# TODO:
# newt-like frontend, or maybe some GUI bit
# keep track of tar/dpkg-deb errors like in pre-2.0

try:
    _ = gettext.translation('apt-listchanges').gettext
except IOError:
    def gettext_null(str): return str
    _ = gettext_null

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
    if u == 'low':
        return 3
    elif u == 'medium':
        return 2
    elif u == 'high':
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
    urgency = 0
    for filenames in [changelog_filenames, changelog_filenames_nodebian]:
         extract_command = "dpkg-deb --fsys-tarfile %s \
         | tar -xO --exclude '*/doc/*/*/*' -f - %s 2>/dev/null \
         | zcat -f" % (deb, string.join(filenames))

         if (found > 0): break

         changes = ''
         for line in os.popen(extract_command).readlines():
             if line[:4] == 'tar:' or line[:8] == 'dpkg-deb':
                 # XXX, keep track of errors
                 continue

             found = 1

             if version:
                 match = changelog_header.match(line)
                 if match:
                     if apt_pkg.VersionCompare(match.group('version'),
                                              version) > 0:
                         urgency = max(numeric_urgency(match.group('urgency')),
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
    fh = os.popen('/usr/sbin/sendmail -t', 'w')
    subject = _("apt-listchanges output for %s") % hostname
    fh.write("To: %s\nSubject: %s\n\n%s" % (address,subject,changes))
    fh.close()

def make_frontend(name, packages):
    frontends = { 'text' : text,
                  'pager' : pager,
                  'mail' : mail,
                  'xterm-pager' : xterm_pager }
    
    if name == 'newt':
        sys.stderr.write(_("The newt frontend is deprecated, using pager"))
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
        if response and (response[0] == 'n' or response[0] == 'N'):
            return 0
        return 1

class simpleprogress:
    def __init__(self,packages):
        sys.stderr.write(_("Reading changelogs") + "...")

    def update_progress(self):
        pass

    def progress_done(self):
        sys.stdout.write('\n')

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
        sys.stdout.write(_("Reading changelogs") + "...%d%%\r" %
                         (self.progress * 100 / self.packages))
        sys.stdout.flush()

    def progress_done(self):
        sys.stdout.write(_("Reading changelogs") + "..." + _("Done") + "\n")

class pager(ttyconfirm,fancyprogress):
    def __init__(self,packages):
        apply(fancyprogress.__init__, (self,packages))

    def display_output(self, text):
        pipe = os.popen('sensible-pager', 'w')
        try:
            pipe.write(text)
            pipe.close()
        except IOError:
            # Broken pipe is OK
            pass

class xterm_pager(ttyconfirm,fancyprogress):
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
                os.execlp('xterm',
                          'xterm','-title','apt-listchanges',
                          '-e','sh','-c','less <&%d' % read)
                sys.exit(1)
            else:
                os.close(read)
                os.write(write,text)
                os.close(write)
                (junk,status) = os.waitpid(pid,0)
                if status != 0:
                    sys.stderr.write(_("%s exited with status %d")
                                     % ('xterm',status))
                    sys.exit(1)
                sys.exit(0)
