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

import gi

from viewtoolbar import ViewToolbar

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
import logging
import os
import sys
import shlex

from gi.repository import GObject
from sugar3.graphics.toolbutton import ToolButton
from gi.repository import Gtk, GLib, Gio
try:
    from gi.repository import WebKit2 as WebKit
except ModuleNotFoundError:
    from gi.repository import WebKit  # for backward compatibility
from gettext import gettext as _
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox, ToolbarButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
os.chdir(activity.get_bundle_path())
from subprocess import Popen, PIPE


def get_index_uri(loader='installer'):
    """ Returns static/installer.html if jupyter doesn't exist, else loads static/init.html """
    os.chdir(activity.get_bundle_path())
    index_path = os.path.join(activity.get_bundle_path(), 'static/{}.html'.format(loader))
    if not os.path.isfile(index_path):
        index_path = os.path.join(
            activity.get_bundle_path(), 'static/{}.html'.format(loader))
    return 'file://' + index_path


def get_path(path):
    """ Checks path exists, if yes, returns path, else returns False  """
    for i in [os.path.expanduser('~/.local/bin/{}'.format(path)), os.path.expanduser('~/bin/{}'.format(path)),
              '/usr/bin/{}'.format(path), '/usr/local/bin/{}'.format(path)]:
        if os.path.exists(i):
            return i
    else:
        return False


def check_path(exe):
    """ Checks path exists, if yes, returns path, else raises FileNotFoundError """
    path = get_path(exe)
    if path:
        return path
    else:
        if exe=='pip3':
            msg = '{e} is not a valid executable. Please check if {e} is installed and is on PATH'.format(e=exe)
            logging.error(msg)
            return False
        else:
            msg = '{e} is not a valid executable. Please check if {e} is installed and is on PATH'.format(e=exe)
            logging.error(msg)
            raise FileNotFoundError(msg)


class Jupyter:
    """
    Jupyter Loader
    Jupyter object which handles
    (i) Installation
    (ii) Server
    (iii) Data Management
    (iv) Path definitions
    (v) Destroy
    """
    def __init__(self, parent, ip='localhost', port='4444'):
        """
        Initiate variables
        :param parent: the caller of Jupyter Class
        :param ip: IP address where a user would like to host Jupyter Activity
        :param port: Port where Jupyter would serve
        """

        # set ports and IP address, and url
        self._port = port
        self._ip = ip
        self.url = None

        self.parent = parent
        sys.path.append('.')

        # save file to notebooks to get_activity_root()
        if not os.path.exists(os.path.join(activity.get_activity_root(), 'notebooks')):
            os.makedirs(os.path.join(activity.get_activity_root(), 'notebooks'))
        # os.chdir(os.path.join(activity.get_activity_root(), 'notebooks'))

        # install ip, port
        self.set_ip(ip)
        self.set_port(port)
        self.path = None

    def bootstrap(self):
        """
        Start jupyter-lab, if it exists, else raise FileNotFoundError.
        :return: None
        """
        self.path = check_path('jupyter-lab')
        logging.warning(self.path)
        if self.serve():
            return True
        else:
            self.parent.web_view.load_uri(get_index_uri('failed'))

    def get_url(self):
        """
        Gets URL of the jupyter server with token
        :return: URL after Jupyter lab server is initated
        """
        return self.url

    def set_url(self, url):
        """
        Update the object variable declaration of URL, with a valid URL
        :param url: Jupyter Server URL
        :return: True if valid url, else false
        """
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
        """
        Starts Jupyter labs.
        Using subprocess module, serve method reads for terminal output until
        valid URL with token- is given.
        Try executing jupyter-labs to check sample output.

        :return: True, if URL is valid, server started successfully , else False
        """
        logging.debug("Starting jupyter labs server")
        cmd = self.path + " -y --no-browser --ip={ip} --port={port}".format(ip=self._ip, port=self._port)
        args = shlex.split(cmd)
        try:
            os.chdir(os.path.join(activity.get_activity_root(), 'notebooks'))
            jupyter_server_output = Popen(args, stdout=PIPE, stderr=PIPE)
            tmp_output = jupyter_server_output.stderr.readline().decode()
            while ('http' not in tmp_output) and ('token' not in tmp_output):
                tmp_output = jupyter_server_output.stderr.readline().decode()
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
        """
        Safely shutdown jupyter labs server.
        Jupyter Labs server can use CPU cycles if left unhandled.
        :return: None
        """
        Gio.Subprocess.new(shlex.split("jupyter-notebook stop {}".format(self._port)), 0)


class JupyterActivity(activity.Activity):
    """
    JupyterActivity Class is an edited helpactivity.py from sugarlabs
    """
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        # init Jupyter Object
        self.jupy = Jupyter(self)

        self.props.max_participants = 1

        self.web_view = WebKit.WebView()

        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.add(self.web_view)
        self._scrolled_window.show()
        self.build_toolbar()
        self.set_canvas(self._scrolled_window)
        self.web_view.show()
        jupyter_path = get_path('jupyter-lab')   # returns path if exists, else false
        if jupyter_path:
            loader = 'init'  # need to call init on OLPCs with slow CPU cycle. Server might start slow
        else:
            loader = 'installer'
        self.web_view.load_uri(get_index_uri(loader))
        if jupyter_path:
            self.load_jupyter()
        else:
            self.install_jupyter()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        viewtoolbar = ViewToolbar(self)
        viewbutton = ToolbarButton(page=viewtoolbar,
                                   icon_name='toolbar-view')
        toolbar_box.toolbar.insert(viewbutton, -1)
        viewbutton.show()

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        # lets reuse the code below
        navtoolbar = Toolbar(self.web_view, self)

        toolitem = Gtk.ToolItem()
        navtoolbar._home.reparent(toolitem)
        toolbar_box.toolbar.insert(toolitem, -1)
        navtoolbar._home.show()
        toolitem.show()

        toolitem = Gtk.ToolItem()
        navtoolbar._back.reparent(toolitem)
        toolbar_box.toolbar.insert(toolitem, -1)
        navtoolbar._back.show()
        toolitem.show()

        toolitem = Gtk.ToolItem()
        navtoolbar._forward.reparent(toolitem)
        toolbar_box.toolbar.insert(toolitem, -1)
        navtoolbar._forward.show()
        toolitem.show()

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

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

    def install_jupyter(self):
        """
        Install Jupyter
        This method should not be moved to Jupyter Object.
        This method uses Gio.subprocess to check if pip3 install jupyter installation completed
        Gio.subprocess removes the hassle of threading, this provides a smooth experience
        for the user, who wouldn't want to install anything

        :return:True if installation was called, False if pip3 was not installs
        """
        logging.debug("Installing Jupyter")
        pip3_path = check_path('pip3')
        if pip3_path:
            pass
        else:
            self.web_view.load_uri(get_index_uri('nopip3'))
            return False
        pip_installer = Gio.Subprocess.new(
            shlex.split("{} install jupyter notebook jupyterlab --user".format(pip3_path)), 0)
        pip_installer.wait_check_async(None, self._on_update_finished)
        return True

    def _on_update_finished(self, process, result):
        process.wait_check_finish(result)
        self.load_jupyter()

    def load_jupyter(self):
        self.jupy.bootstrap()
        self.web_view.load_uri(self.jupy.get_url())

    def read_file(self, file_path):
        # JupyterLabs have their own configuration file system, and opens the last modified
        # file when its loaded. So basically, we would not like to mess with it.
        pass

    def write_file(self, file_path):
        pass

    def can_close(self):
        # Jupyter doesn't need to save files using write_file or the read_file
        # Jupyter has its own configuration file which loads the
        # last edited file.
        # It is safer to let Jupyter handle its stuff.
        try:
            self.jupy.shutdown()
        except FileExistsError:
            logging.warning("LOG: jupyter-notebook is not installed. Server might not be shutdown")
            pass
        return True


class Toolbar(Gtk.Toolbar):
    """
    Modified HelpActivity Toolbar Class Object (c) SugarLabs
    """
    def __init__(self, web_view, parent):
        GObject.GObject.__init__(self)
        self.parent = parent
        self.web_view = web_view

        self._back = ToolButton('go-previous-paired')
        self._back.set_tooltip(_('Back'))
        self._back.props.sensitive = False
        self._back.connect('clicked', self._go_back_cb)
        self.insert(self._back, -1)
        self._back.show()

        self._forward = ToolButton('go-next-paired')
        self._forward.set_tooltip(_('Forward'))
        self._forward.props.sensitive = False
        self._forward.connect('clicked', self._go_forward_cb)
        self.insert(self._forward, -1)
        self._forward.show()

        self._home = ToolButton('go-home')
        self._home.set_tooltip(_('Home'))
        self._home.connect('clicked', self._go_home_cb)
        self.insert(self._home, -1)
        self._home.show()

        self.web_view.connect('notify::uri', self._uri_changed_cb)

    def _uri_changed_cb(self, progress_listener, uri):
        self.update_navigation_buttons()

    def _loading_stop_cb(self, progress_listener):
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self._back.props.sensitive = self.web_view.can_go_back()
        self._forward.props.sensitive = self.web_view.can_go_forward()

    def _go_back_cb(self, button):
        self.web_view.go_back()

    def _go_forward_cb(self, button):
        self.web_view.go_forward()

    def _go_home_cb(self, button):
        """
        Changes the web_view to static/init.html, if homebutton pressed while installation in progress
        Else change it to Jupyter.url
        """
        jupyter_url = self.parent.jupy.get_url()
        if jupyter_url:
            self.web_view.load_uri(jupyter_url)
        else:
            self.web_view.load_uri(get_index_uri('init'))
