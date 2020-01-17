#!/usr/bin/env python3
"""
Copyright (c) 2020 Srevin Saju <srevin03@gmail.com>
JupyterLabs Activity for Sugar, MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import shlex


import gi
from sugar3.graphics.toolbutton import ToolButton

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

try:
    from gi.repository import WebKit2 as WebKit
except ModuleNotFoundError:
    from gi.repository import WebKit

from gettext import gettext as _

from sugar3.activity import activity
from sugar3.datastore import datastore
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.activity.widgets import DescriptionItem

from subprocess import Popen, PIPE


# Import Webactivity from Sugar's Built In Brownse Activity

browse_path = None
try:
    from sugar3.activity.activity import get_bundle
    browse_bundle = get_bundle('org.sugarlabs.WebActivity')
    browse_path = browse_bundle.get_path()
except:
    if os.path.exists('../Browse.activity'):
        browse_path = '../Browse.activity'
    elif os.path.exists('/usr/share/sugar/activities/Browse.activity'):
        browse_path = '/usr/share/sugar/activities/Browse.activity'
    elif os.path.exists(os.path.expanduser('~/Activities/Browse.activity')):
        browse_path = os.path.expanduser('~/Activities/Browse.activity')

if browse_path is None:
    print('This activity need a Browser activity installed to run')

sys.path.append(browse_path)
import webactivity

class Jupyter:
    def __init__(self, ip='localhost', port='4444'):
        # Add the current path to PATH to access modules
        sys.path.append('.')
        # Change directory to activity_root so that the ipynb files are saved to
        # the cwd, i.e. activity_root
        if not os.path.exists(os.path.join(activity.get_activity_root(), 'notebooks')):
            os.makedirs(os.path.join(activity.get_activity_root(), 'notebooks'))
        os.chdir(os.path.join(activity.get_activity_root(), 'notebooks'))
        self.path = self.get_jupyter_path()
        self.set_ip(ip)
        self.set_port(port)
        self.serve()
    
    def get_url(self):
        return self.url

    def set_url(self, url):
        if url.startswith('http'):
            self.url = url
            return True
        else:
            print("ERR: Badly formatted URL")
            return False
    
    def get_jupyter_path(self):
        
        for i in [os.path.expanduser('~/.local/bin/jupyter'), os.path.expanduser('~/bin/jupyter'), 
                  '/usr/bin/jupyter', '/usr/local/bin/jupyter']:
            if os.path.exists(i):
                return i
        else:
            path = None
            print("Jupyter is not installed")
            print("Trying to install")
            # FIXME Add offline support too
            os.system("pip3 install jupyter jupyterlab --user")
            if self.get_jupyter_path():
                return True
            else:
                sys.exit(0)
        
    
    def serve(self):
        print("Starting jupyter labs server")
        cmd = self.path + " lab -y --no-browser --ip={ip} --port={port}".format(ip=self._ip, port=self._port)
        args = shlex.split(cmd)
        httpfound = False
        try:
            jserver_output = Popen(args, stdout=PIPE, stderr=PIPE)
            tmp_output = jserver_output.stderr.readline().decode()
            while 'http' not in tmp_output:
                if httpfound:
                    break
                tmp_output = jserver_output.stderr.readline().decode()
            else:
                httpfound = True
                url = tmp_output[tmp_output.find('http'):tmp_output.find(' ', tmp_output.find('http'))]
                print("Loading URL:", url)
                self.set_url(url)
                self.set_port(url.split(":")[2][:url.split(':')[2].find('/')])
                self.set_ip(url.split(":")[1][url.split(':')[1].find('/')+2:])
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
        Popen(shlex.split("jupyter notebook stop {}".format(self._port)))


class JupyterActivity(webactivity.WebActivity):
    def __init__(self, handle):
        self.jupy = Jupyter()
        self.url = self.jupy.get_url()
        # set URL to serve dir
        handle.uri = self.url
        webactivity.WebActivity.__init__(self, handle)
        self.browser = self._get_browser()
        # For now, collaboration is disabled.
        self.max_participants = 1
        self.build_toolbar()

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

    def _get_browser(self):
        if hasattr(self, '_browser'):
            # Browse < 109
            return self._browser
        else:
            return self._tabbed_view.props.current_browser

    def _go_home_button_cb(self, button):
        home_url = 'http://%s:%s%s' % (
            self.confvars['ip'], self.confvars['port'],
            self.confvars['home_page'])
        browser = self._get_browser()
        browser.load_uri(home_url)

    def launch_jupyter_server(self):
        pass

    def can_close(self):
        # Jupyter doesn't need to save files using write_file or the read_file
        # Jupyter has its own configuration file which loads the
        # last edited file.
        # It is safer to let Jupyter handle its stuff.
        self.jupy.shutdown()
        return True




