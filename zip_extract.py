#!/usr/bin/env python

"""
.. module:: unzip
    :platform: Windows
    :synopsis: Simple script to setup the IAG Toolkit application

.. moduleauthor:: Alex Nelson <alex.nelson@aexp.com>

"""

# Imports
import os
import sys
import win32api
import zipfile

import win32com.client
import pythoncom

from win32com.shell import shell, shellcon


def unzip(zip_file, destination):
    """Extract the provided zip file to the destination

    Args:
        zip_file (path): The full path of the zip file to extract
        destination (path): The full path where the zip file will be extracted

    """

    zfile = zipfile.ZipFile(zip_file)
    for name in zfile.namelist():
        (dir_name, filename) = os.path.split(name)
        if filename == '':
            # directory
            new_dir = destination + '/' + dir_name
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        else:
            # file
            fd = open(destination + '/' + name, 'wb')
            print 'Extracting %s' % name
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()


def create_shortcut(target_dir, shortcut_name, shortcut_description=None):
    """Create a shortcut of the provided target path on the user's desktop

    Args:
        target_dir (path): The full path of the executable

    Kwargs:
        shortcut_description (str): A short description for the shortcut
    """

    #shortcut = pythoncom.CoCreateInstance(
     #   shell.CLSID_ShellLink,
      #  None,
     #   pythoncom.CLSCTX_INPROC_SERVER,
     #   shell.IID_IShellLink
    #)
    #shortcut.SetPath(target_dir)
    #shortcut.SetDescription(shortcut_description)
    #shortcut.SetIconLocation(sys.executable, 0)

    desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
    print desktop_path

    #persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    #print persist_file
    
    target = open (os.path.join(desktop_path, "IAG ToolKIT.bat"), 'w') ## a will append, w will over-write 
    target.write("START %s runserver" % target_dir)
    target.write("\n")
    target.write("ping 192.0.2.2 -n 1 -w 2000 > nul")
    target.write("\n")
    target.write("START http://127.0.0.1:8000")
    target.close()
    # persist_file.Save(os.path.join(desktop_path, "%s.lnk" % shortcut_name), 0)


if __name__ == '__main__':
    print 'Extracting files...'
    working_directory = os.getcwd()
    zip_path = os.path.join(working_directory, "pychamp.zip")
    dest_path = os.path.expanduser("~")
    
    unzip(zip_path, dest_path)

    print 'Creating shortcut...'
    target = os.path.join(dest_path, "pychamp", "toolkit.exe")
    
    description = "IAG MAP Management Toolkit written in Python"

    create_shortcut(target, "IAG Toolkit", shortcut_description=description)

    win32api.MessageBox(0, "Have fun...", 'Setup complete')