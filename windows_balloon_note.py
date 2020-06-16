from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# #############################################################################
# ########## Libraries #############
# ##################################
# standard library
import logging
import threading
from os import path
import os
from time import sleep
from pkg_resources import Requirement
from pkg_resources import resource_filename

# 3rd party modules
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER, WM_RBUTTONUP, WM_RBUTTONDOWN
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS
from win32gui import PumpMessages

# Magic constants
PARAM_DESTROY = 1028
PARAM_CLICKED = 1029

# ############################################################################
# ########### Classes ##############
# ##################################


class WindowsBalloonNote(object):
    """Create a Windows 10  toast notification.

    from: https://github.com/jithurjacob/Windows-10-Toast-Notifications
    """

    def __init__(self):
        """Initialize."""
        self._thread = None
        self.classAtom = None

    @staticmethod
    def _decorator(func, callback=None):
        """
        :param func: callable to decorate
        :param callback: callable to run on mouse click within notification window
        :return: callable
        """
        def inner(*args, **kwargs):
            kwargs.update({'callback': callback})
            func(*args, **kwargs)
        return inner


    def _show_toast(self, title, msg,
                    icon_path, duration,
                    cbFunc=None, cbArgs=None):
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        self.user_cbFunc = cbFunc
        self.user_cbArgs = cbArgs
        
        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("PythonTaskbar" + os.urandom(24).hex())  # must be a string
        self.wc.lpfnWndProc = self._decorator(self.wnd_proc, self.user_cbFunc)  # could also specify a wndproc.
        try:
             self.classAtom = RegisterClass(self.wc)
        except:
            pass #not sure of this
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, CW_USEDEFAULT,
                                 CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
            icon_flags = LR_LOADFROMFILE 
            try:
                hicon = LoadImage(self.hinst, icon_path,
                              IMAGE_ICON, 0, 0, icon_flags)
            except Exception as e:
                logging.error("Some trouble with the icon ({}): {}"
                              .format(icon_path, e))
                hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,
                                      WM_USER + 20,
                                      hicon, "Balloon Tooltip", msg, 200,
                                      title))
        PumpMessages()
        # take a rest then destroy
        sleep(duration)
        DestroyWindow(self.hwnd)
        UnregisterClass(self.wc.lpszClassName, None)
        return None

    def show_toast(self, title="Notification", msg="Here comes the message",
                    icon_path=None, duration=5, threaded=False, cbFunc=None, cbArgs=None):
        """Notification settings.

        :title: notification title
        :msg: notification message
        :icon_path: path to the .ico file to custom notification
        :duration: delay in seconds before notification self-destruction
        """
        if not threaded:
            self._show_toast(title, msg, icon_path, duration, cbFunc, cbArgs)
        else:
            if self.notification_active():
                # We have an active notification, let is finish so we don't spam them
                return False

            self._thread = threading.Thread(target=self._show_toast,
                                            args=(title, msg, icon_path, duration, cbFunc, cbArgs))
            self._thread.start()
        return True

    def notification_active(self):
        """See if we have an active notification showing"""
        if self._thread != None and self._thread.is_alive():
            # We have an active notification, let is finish we don't spam them
            return True

        return False

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """Clean after notification ended.

        :hwnd:
        :msg:
        :wparam:
        :lparam:
        """

        # Give time to read
        sleep(10)
        
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

        return None

    def wnd_proc(self, hwnd, msg, wparam, lparam, **kwargs):
        """Messages handler method"""
        if lparam == PARAM_CLICKED:
            # callback goes here
            if kwargs.get('callback'):
                kwargs.pop('callback')(self.user_cbArgs)
                self.on_destroy(hwnd, msg, wparam, lparam)
        elif lparam == PARAM_DESTROY:
            self.on_destroy(hwnd, msg, wparam, lparam)
