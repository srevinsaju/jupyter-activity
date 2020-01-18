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
import logging
import os
import sys
import shlex
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, GLib, Gio
try:
    from gi.repository import WebKit2 as WebKit
except ModuleNotFoundError:
    from gi.repository import WebKit
import server
from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.activity.widgets import DescriptionItem
os.chdir(activity.get_bundle_path())
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
    logging.warning('This activity need a Browser activity installed to run')

sys.path.append(browse_path)

import webactivity


def get_path(path):
    for i in [os.path.expanduser('~/.local/bin/{}'.format(path)), os.path.expanduser('~/bin/{}'.format(path)),
              '/usr/bin/{}'.format(path), '/usr/local/bin/{}'.format(path)]:
        if os.path.exists(i):
            return i
    else:
        return False


def check_path(exe):
    path = get_path(exe)
    if path:
        return path
    else:
        msg = '{e} is not a valid executable. Please check if {e} is installed and is on PATH'.format(e=exe)
        logging.warning(msg)
        raise FileNotFoundError(msg)


class Jupyter:
    def __init__(self, parent, ip='localhost', port='4444'):

        # set ports and IP address, and url
        self._port = port
        self._ip = ip
        self.url = None

        # Add the current path to PATH to access modules
        self.parent = parent
        # sys.path.append('.')

        # save file to notebooks to get_activity_root()
        if not os.path.exists(os.path.join(activity.get_activity_root(), 'notebooks')):
            os.makedirs(os.path.join(activity.get_activity_root(), 'notebooks'))
        # os.chdir(os.path.join(activity.get_activity_root(), 'notebooks'))

        # install ip, port
        self.set_ip(ip)
        self.set_port(port)
        self.path = None

    def bootstrap(self):
        self.path = check_path('jupyter-lab')
        logging.warning(self.path)
        self.serve()

    def get_url(self):
        return self.url

    def set_url(self, url):
        if url.startswith('http'):
            self.url = url
            return True
        else:
            logging.warning("ERR: Badly formatted URL")
            return False

    def set_port(self, port):
        self._port = port

    def set_ip(self, ip):
        self._ip = ip

    def serve(self):
        logging.debug("Starting jupyter labs server")
        cmd = self.path + " -y --no-browser --ip={ip} --port={port}".format(ip=self._ip, port=self._port)
        args = shlex.split(cmd)
        try:
            os.chdir(activity.get_activity_root())
            jserver_output = Popen(args, stdout=PIPE, stderr=PIPE)
            tmp_output = jserver_output.stderr.readline().decode()
            while ('http' not in tmp_output) and ('token' not in tmp_output):
                tmp_output = jserver_output.stderr.readline().decode()
            else:
                url = tmp_output[tmp_output.find('http'):tmp_output.find(' ', tmp_output.find('http'))]
                logging.debug("Loading URL:", url)
                self.set_url(url)
                self.set_port(url.split(":")[2][:url.split(':')[2].find('/')])
                self.set_ip(url.split(":")[1][url.split(':')[1].find('/')+2:])
                return True

        except Exception as e:
            logging.error("Error {e} has occurred.".format(e=e))
            return False

    def shutdown(self):
        Gio.Subprocess.new(shlex.split("jupyter-notebook stop {}".format(self._port)), 0)


class JupyterActivity(webactivity.WebActivity):
    def __init__(self, handle):
        # For now, collaboration is disabled.
        # init Jupyter
        self.jupy = Jupyter(self)
        # TODO, doesn't work atm, sugar-activity3 works on cwd works

        if not get_path('jupyter-lab'):
            os.chdir(activity.get_bundle_path())
            handle.uri = "file://{}/static/sugar.html".format(activity.get_bundle_path())
            logging.debug(handle.uri)
        else:
            self.jupy.bootstrap()
            handle.uri = self.jupy.get_url()

        webactivity.WebActivity.__init__(self, handle)

        # set URL to serve dir
        self.browser = self._get_browser()
        self.max_participants = 1
        self.build_toolbar()

        if not get_path('jupyter-lab'):
            self.install_jupyter()

    def install_jupyter(self):
        # install jupyter
        logging.debug("Installing Jupyter")
        pip3_path = check_path('pip3')
        pip_installer = Gio.Subprocess.new(
            shlex.split("{} install jupyter notebook jupyterlab --user".format(pip3_path)), 0)
        pip_installer.wait_check_async(None, self._on_update_finished)
        return True

    def _on_update_finished(self, process, result):
        process.wait_check_finish(result)
        self.load_jupyter()

    def load_jupyter(self):
        self.jupy.bootstrap()
        self.browser.load_uri(self.jupy.get_url())

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

    def __new_tab_cb(self, browser, url):
        new_browser = self.add_tab(next_to_current=True)
        new_browser.load_uri(url)
        new_browser.grab_focus()

    def _go_home_button_cb(self, button):
        self.browser.load_uri(self.jupy.get_url())

    def can_close(self):
        # Jupyter doesn't need to save files using write_file or the read_file
        # Jupyter has its own configuration file which loads the
        # last edited file.
        # It is safer to let Jupyter handle its stuff.
        try:
            self.jupy.shutdown()
        except FileExistsError:
            logging.warning("LOG: jupyter-notebook is not installed. Quitting")
            pass
        return True

