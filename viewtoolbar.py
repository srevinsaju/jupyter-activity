# Copyright (C) 2007, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# this is an edited version of help-activity/view-toolbar.py

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import GObject

from sugar3.graphics.toolbutton import ToolButton


class ViewToolbar(Gtk.Toolbar):
    def __init__(self, activity):
        GObject.GObject.__init__(self)

        self._activity = activity

        self._browser = self._activity.web_view

        self.separator = Gtk.SeparatorToolItem()
        self.separator.set_draw(True)
        self.insert(self.separator, -1)
        self.separator.show()

        self.fullscreen = ToolButton('view-fullscreen')
        self.fullscreen.set_tooltip(_('Fullscreen'))
        self.fullscreen.connect('clicked', self.__fullscreen_clicked_cb)
        self.insert(self.fullscreen, -1)
        self.fullscreen.show()

    def __zoomin_clicked_cb(self, button):
        self._browser.zoom_in()

    def __zoomout_clicked_cb(self, button):
        self._browser.zoom_out()

    def __fullscreen_clicked_cb(self, button):
        self._activity.fullscreen()