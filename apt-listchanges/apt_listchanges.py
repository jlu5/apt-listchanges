#vim:set fileencoding=utf-8:

import apt_pkg
import ConfigParser
import getopt
import sys, os, os.path
import re
import gettext
import locale
import email.Message
import email.Header
import email.Charset
import cStringIO
import tempfile

# TODO:
# newt-like frontend, or maybe some GUI bit
# keep track of tar/dpkg-deb errors like in pre-2.0

locale.setlocale(locale.LC_ALL, '')
try:
    _ = gettext.translation('apt-listchanges').lgettext
except IOError:
    _ = lambda str: str

class Config:
    def __init__(self):
        # Defaults
        self.frontend = 'pager'
        self.email_address = None
        self.verbose = False
        self.quiet = 0
        self.show_all = False
        self.confirm = False
        self.headers = False
        self.debug = False
        self.save_seen = None
        self.apt_mode = False
        self.profile = None
        self.which = 'both'
        self.allowed_which = ('both', 'news', 'changelogs')

    def read(self, file):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(file)

    def expose(self):
        if self.parser.has_section(self.profile):
            for option in self.parser.options(self.profile):
                value = None
                if self.parser.has_option(self.profile, option):
                    if option in ('confirm', 'run', 'show_all', 'headers', 'verbose'):
                        value = self.parser.getboolean(self.profile, option)
                    else:
                        value = self.parser.get(self.profile, option)
                setattr(self, option, value)

    def get(self, option, defvalue=None):
        return getattr(self, option, defvalue)

    def usage(self, exitcode):
        if exitcode == 0:
            fh = sys.stdout
        else:
            fh = sys.stderr

        fh.write(_("Usage: apt-listchanges [options] {--apt | filename.deb ...}\n"))
        sys.exit(exitcode)


    def getopt(self, argv):
        try:
            (optlist, args) = getopt.getopt(argv[1:], 'vf:s:cah', [
                "apt", "verbose", "frontend=", "email-address=", "confirm",
                "all", "headers", "save_seen=", "debug", "which=", "help",
                "profile="])
        except getopt.GetoptError:
            return None

        # Determine mode and profile before processing other options
        for opt, arg in optlist:
            if opt == '--profile':
                self.profile = arg
            elif opt == '--apt':
                self.apt_mode = True

        # Provide a default profile if none has been specified
        if self.profile is None:
            if self.apt_mode:
                self.profile = 'apt'
            else:
                self.profile = 'cmdline'

        # Expose defaults from config file
        self.expose()

        # Environment variables override config file
        self.frontend = os.getenv('APT_LISTCHANGES_FRONTEND', self.frontend)

        # Command-line options override environment and config file
        for opt, arg in optlist:
            if opt == '--help':
                self.usage(0)
            elif opt in ('-v', '--verbose'):
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
                if arg in self.allowed_which:
                    self.which = arg
                else:
                    print _('Unknown option %s for --which.  Allowed are: %s.') % \
                        (arg, ', '.join(self.allowed_which))
                    sys.exit(1)
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
        line = sys.stdin.readline().rstrip()
        if not line:
            break

        if line.startswith('quiet='):
            config.quiet = int(line[len('quiet='):])

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

def mail_changes(address, changes, subject):
    print "apt-listchanges: " + _("Mailing %s: %s") % (address, subject)

    charset = email.Charset.Charset('utf-8')
    charset.body_encoding = '8bit'
    charset.header_encoding = email.Charset.QP
    message = email.Message.Message()
    message.set_charset(charset)
    message['Subject'] = subject
    message['To'] = address
    message.set_payload(changes)

    fh = os.popen('/usr/sbin/sendmail -oi -t', 'w')
    fh.write(message.as_string())
    fh.close()

def make_frontend(name, packages, config):
    frontends = { 'text' : text,
                  'pager' : pager,
                  'mail' : mail,
                  'browser' : browser,
                  'xterm-pager' : xterm_pager,
                  'xterm-browser' : xterm_browser }

    if name in ('newt', 'w3m', 'xterm-w3m'):
        sys.stderr.write((_("The %s frontend is deprecated, using pager") + '\n') % name)
        name = 'pager'

    if not frontends.has_key(name):
        return None
    return frontends[name](packages, config)

class frontend:
    def __init__(self, packages, config):
        self.packages = packages
        self.config = config

    def update_progress(self):
        pass

    def progress_done(self):
        pass

    def display_output(self, text):
        pass

    def _render(self, text):
        newtext = []
        for line in text.split('\n'):
            try:
                # changelogs are supposed to be in UTF-8
                uline = line.decode('utf-8')
            except UnicodeError:
                # ... but handle gracefully if they aren't.
                # (That's also the reason we do it line by line.)
                # This is possibly wrong, but our best guess.
                uline = line.decode('iso8859-1')
            newtext.append(uline.encode(locale.getlocale()[1] or 'ascii', 'replace'))
        return '\n'.join(newtext)

    def confirm(self):
        return 1

class ttyconfirm:
    def confirm(self):
        try:
            tty = open('/dev/tty', 'r+')
        except IOError, e:
            return -1
        tty.write('apt-listchanges: ' + _('Do you want to continue? [Y/n]? '))
        tty.flush()
        response = tty.readline()
        return response == '\n' or re.search(locale.nl_langinfo(locale.YESEXPR),
                                             response)

class simpleprogress:
    def update_progress(self):
        if self.config.quiet > 1:
            return

        if not hasattr(self, 'message_printed'):
            self.message_printed = 1
            sys.stderr.write(_("Reading changelogs") + "...\n")

    def progress_done(self):
        pass

class mail(simpleprogress, frontend):
    pass

class text(simpleprogress, ttyconfirm, frontend):
    def display_output(self, text):
        sys.stdout.write(text)

class fancyprogress:
    def update_progress(self):
        if not hasattr(self, 'progress'):
            # First call
            self.progress = 0
            self.line_length = 0

        self.progress += 1
        line = _("Reading changelogs") + "... %d%%" % (self.progress * 100 / self.packages)
        self.line_length = len(line)
        sys.stdout.write(line + '\r')
        sys.stdout.flush()

    def progress_done(self):
        if hasattr(self, 'line_length'):
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
        shellcommand = self.get_command() + ' ' + tmp.name

        status = os.spawnl(os.P_WAIT, '/bin/sh', 'sh', '-c', shellcommand)
        if status != 0:
            raise OSError('Subprocess ' + shellcommand + ' exited with status ' + str(status))

        if self.mode == os.P_NOWAIT:
            # We are a child; exit
            sys.exit(0)

    def get_command(self):
        return self.command

class pager(runcommand, ttyconfirm, fancyprogress, frontend):
    def __init__(self, *args):
        apply(frontend.__init__, [self] + list(args))
        self.command = self.config.get('pager', 'sensible-pager')

class xterm(runcommand, ttyconfirm, fancyprogress, frontend):
    def __init__(self, *args):
        apply(frontend.__init__, [self] + list(args))
        self.mode = os.P_NOWAIT
        self.xterm = self.config.get('xterm', 'x-terminal-emulator')

    def get_command(self):
        return self.xterm + ' -T apt-listchanges -e ' + self.xterm_command

class xterm_pager(xterm):
    def __init__(self, *args):
        apply(xterm.__init__, [self] + list(args))
        self.xterm_command = self.config.get('pager', 'sensible-pager')

class html:
    suffix = '.html'

    bug_stanza_re = re.compile(r'(?:closes:\s*(?:bug)?\#?\s?\d+(?:,\s*(?:bug)?\#?\s?\d+)*|#\d+)', re.I)
    bug_re        = re.compile('(?P<linktext>#?(?P<bugnum>\d+))', re.I)
    bug_fmt       = r'<a href="http://bugs.debian.org/\g<bugnum>">\g<linktext></a>'
    # regxlib.com
    email_re = re.compile(r'([a-zA-Z0-9_\-\.]+)@(([[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)')

    def _render(self, text):
        htmltext = cStringIO.StringIO()
        htmltext.write('''<html>
        <head>
        <title>apt-listchanges output</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        </head>

        <body>
        <pre>''')

        for line in text.split('\n'):
            try:
                # changelogs are supposed to be in UTF-8
                uline = line.decode('utf-8')
            except UnicodeError:
                # ... but handle gracefully if they aren't.
                # This is possibly wrong, but our best guess.
                uline = line.decode('iso8859-1')
            line = uline.encode('utf-8').replace(
                '&', '&amp;').replace(
                '<', '&lt;').replace(
                '>', '&gt;')
            line = self.bug_stanza_re.sub(lambda m: self.bug_re.sub(self.bug_fmt, m.group(0)), line)
            line = self.email_re.sub(r'<a href="mailto:\g<0>">\g<0></a>', line)
            htmltext.write(line + '\n')
        htmltext.write('</pre></body></html>')

        return htmltext.getvalue()

class browser(html, pager):
    def __init__(self, *args):
        apply(pager.__init__, [self] + list(args))
        self.command = self.config.get('browser', 'sensible-browser')

class xterm_browser(html, xterm):
    def __init__(self, *args):
        apply(xterm.__init__, [self] + list(args))
        self.xterm_command = self.config.get('browser', 'sensible-browser')


