#!/usr/bin/env python3

# (c) 2020 Srevin Saju <srevin03@gmail.com> 
#
# JupyterLabs Activity for Sugar
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

import os
import sys
import shlex
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

try:
    from gi.repository import WebKit2 as WebKit
except ModuleNotFoundError:
    from gi.repository import WebKit

from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.activity.widgets import DescriptionItem

from subprocess import Popen, PIPE

class Jupyter:
    def __init__(self, ip='localhost', port='4444'):
        self.path = self.get_jupyter_path()
        self.set_ip(ip)
        self.set_port(port)
        self.serve()
        self.url = None
        
        pass
    
    def get_url(self):
        return self.uri
    
    def get_jupyter_path(self):
        
        for i in [os.path.expanduser('~/.local/bin/jupyter'), os.path.expanduser('~/bin/jupyter'), 
                  '/usr/bin/jupyter', '/usr/local/bin/jupyter']:
            if os.path.exists(i):
                return i
        else:
            path = None
            print("Jupyter is not installed")
            print("Quitting")
            sys.exit(0)
        
    
    def serve(self):
        print("Starting jupyter labs server")
        cmd = self.path + " lab -y --no-browser --ip={ip} --port={port} --port-retries=0".format(ip=self._ip, port=self._port)
        args = shlex.split(cmd)
        try:
            jserver_output = Popen(args)
            self.url="http://{}:{}".format(self._ip, self._port)
            print("Loaded ", self.url)
            return True
        except Exception as e:
            print("Error {e} has occured.".format(e=e))
            return False
    
    def set_port(self, port):
        self._port = port
    
    def set_ip(self, ip):
        self._ip = ip
        
    def install_jupyter(self):
        print('#'*50)
        print(" INSTALLING JUPYTER ")
        print('#'*50)
        os.system('pip3 install jupyter --user')
        print("Install complete")
        pass
    
    def shutdown(self):
        os.system("jupyter notebook stop {}".format(self._port))


class JupyterActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.jupy = Jupyter()
        # For now, collaboration is disabled.
        self.max_participants = 1
        self.build_toolbar()
        
        self._web_view = WebKit.WebView()
        # self._web_view.set_full_content_zoom(True)

        _scrolled_window = Gtk.ScrolledWindow()
        _scrolled_window.add(self._web_view)
        _scrolled_window.show()
        self.set_canvas(_scrolled_window)
        self._web_view.show()

        while not self.jupy.url:
            if self.jupy.url:
                
                self._web_view.load_uri(self.jupy.url)
                break

    def build_toolbar(self):
        toolbar_box = ToolbarBox()

        activity_button = ActivityButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        title_entry = TitleEntry(self)
        toolbar_box.toolbar.insert(title_entry, -1)
        title_entry.show()

        description_item = DescriptionItem(self)
        toolbar_box.toolbar.insert(description_item, -1)
        description_item.show()

        share_button = ShareButton(self)
        toolbar_box.toolbar.insert(share_button, -1)
        share_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()
        

    def launch_jupyter_server(self):
        pass

    def can_close(self):
        self.jupy.shutdown()
        return True
