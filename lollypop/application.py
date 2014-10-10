#!/usr/bin/python
# Copyright (c) 2014 Cedric Bellegarde <gnumdk@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# Many code inspiration from gnome-music at the GNOME project

from gi.repository import Gtk, Gio, GLib, Gdk, Notify
from gettext import gettext as _
from lollypop.window import Window
from lollypop.database import Database
from lollypop.player import Player
from lollypop.mpris import MediaPlayer2Service
from lollypop.notification import NotificationManager

class Application(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self,
					 application_id='org.gnome.Lollypop',
					 flags=Gio.ApplicationFlags.FLAGS_NONE)
		GLib.set_application_name(_("Lollypop"))
		GLib.set_prgname('lollypop')

		cssProviderFile = Gio.File.new_for_uri('resource:///org/gnome/Lollypop/application.css')
		cssProvider = Gtk.CssProvider()
		cssProvider.load_from_file(cssProviderFile)
		screen = Gdk.Screen.get_default()
		styleContext = Gtk.StyleContext()
		styleContext.add_provider_for_screen(screen, cssProvider,
						     Gtk.STYLE_PROVIDER_PRIORITY_USER)

		self._db = Database()
		self._player = Player(self._db)
		self._window = None

	def build_app_menu(self):
		builder = Gtk.Builder()

		builder.add_from_resource('/org/gnome/Lollypop/app-menu.ui')

		menu = builder.get_object('app-menu')
		self.set_app_menu(menu)

		aboutAction = Gio.SimpleAction.new('about', None)
		aboutAction.connect('activate', self.about)
		self.add_action(aboutAction)

		quitAction = Gio.SimpleAction.new('quit', None)
		quitAction.connect('activate', self.quit)
		self.add_action(quitAction)


	def about(self, action, param):
        	builder = Gtk.Builder()
        	builder.add_from_resource('/org/gnome/Lollypop/AboutDialog.ui')
        	about = builder.get_object('about_dialog')
        	about.set_transient_for(self._window)
        	about.connect("response", self.about_response)
        	about.show()

	def about_response(self, dialog, response):
		dialog.destroy()

	def do_startup(self):
		Gtk.Application.do_startup(self)
		Notify.init(_("Lollypop"))
		self.build_app_menu()

	def quit(self, action=None, param=None):
		self._window.destroy()

	def do_activate(self):
		if not self._window:
			self._window = Window(self, self._db, self._player)
			self._service = MediaPlayer2Service(self._db, self._player)
			self._notifications = NotificationManager(self._player, self._db)

		self._window.present()

