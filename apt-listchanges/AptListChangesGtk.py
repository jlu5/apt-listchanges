# check if gtk is avialable

from apt_listchanges import frontend

import gi
gi.require_version('Gtk', '3.0')
import gettext

from gi.repository import Gtk
from gi.repository import GObject
# import Gtk.glade

from ALChacks import *

# set the i18n dirs
gettext.bindtextdomain("apt-listchanges", "/usr/share/locale")
gettext.textdomain("apt-listchanges")

class gtk2(frontend):
    def flush_interface(self):
        while Gtk.events_pending():
            Gtk.main_iteration()

    def cb_close(self, widget):
        if self.button_close.get_property("sensitive") == False:
            # window manager was used to close before the parsing was complete
            sys.exit()
        Gtk.main_quit()

    def __init__(self, packages, config):
        frontend.__init__(self,packages, config)
        try:
            file("apt-listchanges/apt-listchanges.ui").close()
            self.builder = Gtk.Builder()
            self.builder.add_from_file("apt-listchanges/apt-listchanges.ui")
            self.builder.connect_signals(self)
        except:
            self.builder.add_from_file("/usr/share/apt-listchanges/apt-listchanges.ui")
        self.window_main = self.builder.get_object("window_main")
        self.window_main.connect("destroy", self.cb_close)
        handlers = {
            "on_button_close_clicked": self.cb_close
        }
        self.progressbar_main = self.builder.get_object("progressbar_main")
        self.button_close = self.builder.get_object("button_close")
        self.builder.connect_signals(handlers)
        self.flush_interface()

    def display_output(self,text):
        self.button_close.set_sensitive(True)
        buf = self.builder.get_object("textview_main").get_buffer()
        buf.set_text(self._render(text))
        Gtk.main()

    def update_progress(self):
        if not hasattr(self,'progress'):
            # First call
            self.progress = 0.0
            self.progressbar_main.show()
        self.progress += 1.0
        self.progressbar_main.set_fraction(self.progress / self.packages)
        self.progressbar_main.set_text(("%i%%" % (self.progress*100 / self.packages)))
        self.flush_interface()

    def progress_done(self):
        self.progressbar_main.hide()
        self.flush_interface()

    def confirm(self):
        m = Gtk.MessageDialog(self.window_main,
                              Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.YES_NO)
        m.set_default_response(Gtk.ResponseType.YES)
        m.set_markup("<big><b>%s</b></big>\n\n%s" % (_("Continue Installation?"), _("You can abort the installation if you select 'no'.")))
        if m.run() == Gtk.ResponseType.NO:
            return False
        return True
