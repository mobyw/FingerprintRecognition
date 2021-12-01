#
# 支持 CLI 和 GUI 执行方式
# 可通过输入 -h 参数查看帮助
# Author: Xiaohei
# Updatetime: 2021-12-01
#

import argparse
from pathlib import Path
import sys
import subprocess
import shlex
import threading
import tkinter as tk

from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import ttk

from myapp import *

DEFAULT_DATA_PATH = "./data/"
CONFIG_UNSET = "Not set"

# Indexed on feature name, tuple contains the C file, the H file and the Cmake project name for the feature
GUI_TEXT = 0
C_FILE = 1
H_FILE = 2
LIB_NAME = 3

DEFINES = 0
INITIALISERS = 1

configuration_dictionary = list(dict())


class Parameters:
    def __init__(self, _img, _data, gui):
        self.imgPath = _img
        self.dataPath = _data
        self.wantGUI = gui


def GetBackground():
    return 'white'


def GetButtonBackground():
    return 'white'


def GetTextColour():
    return 'black'


def GetButtonTextColour():
    return '#c51a4a'


def RunGUI(_args):
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('default')

    ttk.Style().configure("TButton", padding=6, relief="groove", border=2, foreground=GetButtonTextColour(),
                          background=GetButtonBackground())
    ttk.Style().configure("TLabel", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TCheckbutton", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TRadiobutton", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TLabelframe", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TLabelframe.Label", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TCombobox", foreground=GetTextColour(), background=GetBackground())
    ttk.Style().configure("TListbox", foreground=GetTextColour(), background=GetBackground())

    app = ProjectWindow(root, _args)

    app.configure(background=GetBackground())

    root.mainloop()
    sys.exit(0)


def RunWarning(message):
    mb.showwarning('Fingerprint Recognization', message)
    sys.exit(0)


def ShowResult(message):
    mb.showinfo('Fingerprint Recognization', message)


class ChecklistBox(tk.Frame):
    def __init__(self, parent, entries):
        tk.Frame.__init__(self, parent)

        self.vars = []
        for c in entries:
            # This var will be automatically updated by the checkbox
            # The checkbox fills the var with the "onvalue" and "offvalue" as
            # it is clicked on and off
            var = tk.StringVar(value='')  # Off by default for the moment
            self.vars.append(var)
            cb = ttk.Checkbutton(self, var=var, text=c,
                                 onvalue=c, offvalue="",
                                 width=20)
            cb.pack(side="top", fill="x", anchor="w")

    def getCheckedItems(self):
        values = []
        for var in self.vars:
            value = var.get()
            if value:
                values.append(value)
        return values


def thread_function(text, command, ok):
    l = shlex.split(command)
    proc = subprocess.Popen(l, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(proc.stdout.readline, ''):
        if not line:
            if ok:
                ok["state"] = tk.NORMAL
            return
        text.insert(tk.END, line)
        text.see(tk.END)


# Function to run an OS command and display the output in a new modal window
class DisplayWindow(tk.Toplevel):
    def __init__(self, parent, title):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.text = None
        self.OKButton = None
        self.init_window(title)

    def init_window(self, title):
        self.title(title)

        frame = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame.pack(fill=tk.X, expand=True, side=tk.TOP)

        scrollbar = tk.Scrollbar(frame)
        self.text = tk.Text(frame, bg='gray14', fg='gray99')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=scrollbar.set)

        frame1 = tk.Frame(self, borderwidth=1)
        frame1.pack(fill=tk.X, expand=True, side=tk.BOTTOM)
        self.OKButton = ttk.Button(frame1, text="OK", command=self.OK)
        self.OKButton["state"] = tk.DISABLED
        self.OKButton.pack()

        # make dialog modal
        self.transient(self.parent)
        self.grab_set()

    def OK(self):
        self.destroy()


def RunCommandInWindow(parent, command):
    w = DisplayWindow(parent, command)
    x = threading.Thread(target=thread_function, args=(w.text, command, w.OKButton))
    x.start()
    parent.wait_window(w)


class EditBoolWindow(sd.Dialog):

    def __init__(self, parent, configitem, current):
        self.parent = parent
        self.config_item = configitem
        self.current = current
        sd.Dialog.__init__(self, parent, "Edit boolean configuration")

    def body(self, master):
        self.configure(background=GetBackground())
        ttk.Label(self, text=self.config_item['name']).pack()
        self.result = tk.StringVar()
        self.result.set(self.current)
        ttk.Radiobutton(master, text="True", variable=self.result, value="True").pack(anchor=tk.W)
        ttk.Radiobutton(master, text="False", variable=self.result, value="False").pack(anchor=tk.W)
        ttk.Radiobutton(master, text=CONFIG_UNSET, variable=self.result, value=CONFIG_UNSET).pack(anchor=tk.W)

    def get(self):
        return self.result.get()


class EditIntWindow(sd.Dialog):

    def __init__(self, parent, configitem, current):
        self.parent = parent
        self.config_item = configitem
        self.current = current
        self.input = None
        sd.Dialog.__init__(self, parent, "Edit integer configuration")

    def body(self, master):
        self.configure(background=GetBackground())
        _str = self.config_item['name'] + "  Max = " + self.config_item['max'] + "  Min = " + self.config_item['min']
        ttk.Label(self, text=_str).pack()
        self.input = tk.Entry(self)
        self.input.pack(pady=4)
        self.input.insert(0, self.current)
        ttk.Button(self, text=CONFIG_UNSET, command=self.unset).pack(pady=5)

    def validate(self):
        self.result = self.input.get()
        # Check for numeric entry
        return True

    def unset(self):
        self.result = CONFIG_UNSET
        self.destroy()

    def get(self):
        return self.result


class EditEnumWindow(sd.Dialog):
    def __init__(self, parent, configitem, current):
        self.parent = parent
        self.config_item = configitem
        self.current = current
        self.input = None
        sd.Dialog.__init__(self, parent, "Edit Enumeration configuration")

    def body(self, master):
        # self.configure(background=GetBackground())
        values = self.config_item['enumvalues'].split('|')
        values.insert(0, 'Not set')
        self.input = ttk.Combobox(self, values=values, state='readonly')
        self.input.set(self.current)
        self.input.pack(pady=12)

    def validate(self):
        self.result = self.input.get()
        return True

    def get(self):
        return self.result


def _get_filepath(filename):
    return os.path.join(os.path.dirname(__file__), filename)


# Our main window
class ProjectWindow(tk.Frame):

    def __init__(self, parent, _args):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.help = None
        self.logo = None
        self.imgPath = None
        self.dataPath = None
        self.init_window()

    def init_window(self):
        self.master.title("Fingerprint Recognization")
        self.master.configure(bg=GetBackground())
        mainFrame = tk.Frame(self, bg=GetBackground()).grid(row=0, column=0, columnspan=6, rowspan=12)

        # Need to keep a reference to the image or it will not appear.
        self.logo = tk.PhotoImage(file=_get_filepath("logo.png"))
        logowidget = ttk.Label(mainFrame, image=self.logo, borderwidth=0, relief="solid").grid(row=0, column=0,
                                                                                               columnspan=5, pady=10)

        # Set image path
        imglbl = ttk.Label(mainFrame, text='Image path:').grid(row=2, column=0, sticky=tk.E)
        self.imgPath = tk.StringVar()
        self.imgPath.set(os.getcwd())
        imgEntry = ttk.Entry(mainFrame, textvariable=self.imgPath).grid(row=2, column=1, columnspan=3,
                                                                        sticky=tk.W + tk.E, padx=5)
        imgBrowse = ttk.Button(mainFrame, text='Browse', command=self.browseImgPath).grid(row=2, column=4)

        # Set data path
        datalbl = ttk.Label(mainFrame, text='Data path:').grid(row=3, column=0, sticky=tk.E)
        self.dataPath = tk.StringVar()
        self.dataPath.set(os.getcwd())
        dataEntry = ttk.Entry(mainFrame, textvariable=self.dataPath).grid(row=3, column=1, columnspan=3,
                                                                          sticky=tk.W + tk.E, padx=5)
        dataBrowse = ttk.Button(mainFrame, text='Browse', command=self.browseDataPath).grid(row=3, column=4)

        # OK, Cancel, Help section
        # creating buttons
        QuitButton = ttk.Button(mainFrame, text="Quit", command=self.quit).grid(row=5, column=4)
        OKButton = ttk.Button(mainFrame, text="OK", command=self.OK).grid(row=5, column=3)

        # TODO help not implemented yet
        # HelpButton = ttk.Button(mainFrame, text="Help", command=self.help).grid(row=5, column=0, pady=5)

        # You can set a default path here, replace the string with whereever you want.
        self.imgPath.set('./image/101_1.tif')
        self.dataPath.set('./data/')

    def quit(self):
        # TODO Check if we want to exit here
        sys.exit(0)

    def OK(self):
        # OK, grab all the settings from the page, then call the generators
        _imgPath = self.imgPath.get()
        _dataPath = self.dataPath.get()

        p = Parameters(_img=Path(_imgPath), _data=Path(_dataPath), gui=True)

        DoEverything(self, p)

    def browseImgPath(self):
        name = fd.askopenfilename(initialdir="./image/",
                                  title="Select image file",
                                  filetypes=[
                                      ("TIFF files", ".tiff .tif"),
                                      ("Windows bitmaps", ".bmp .dib"),
                                      ("JPEG files", ".jpeg .jpg .jpe"),
                                      ("JPEG 2000 files", ".jp2"),
                                      ("Portable Network Graphics", ".png"),
                                      ("WebP", ".webp"),
                                      ("Portable image format", ".pbm .pgm .ppm .pxm .pnm"),
                                      ("PFM files", ".pfm"),
                                      ("Sun rasters", ".sr .ras"),
                                      ("OpenEXR Image files", ".exr"),
                                      ("Radiance HDR", ".hdr .pic"),
                                      ("All files", ".*")
                                  ])
        self.imgPath.set(name)

    def browseDataPath(self):
        name = fd.askdirectory(initialdir="./data/",
                               title="Select data folder",)
        self.dataPath.set(name)

    def help(self):
        self.help = None
        print("Help TODO")


def CheckImgPath(gui, _img):
    _imgPath = os.path.exists(Path(_img))

    if _imgPath is None:
        m = 'Unable to locate the image file.'
        if gui:
            RunWarning(m)
        else:
            print(m)
    elif not os.path.isfile(Path(_img)):
        m = 'Unable to locate the image file, --image does not point to a file.'
        if gui:
            RunWarning(m)
        else:
            print(m)
        _imgPath = None

    return _imgPath


def CheckDataPath(gui, _data):
    _dataPath = os.path.exists(Path(_data))

    if _dataPath is None:
        m = 'Unable to locate the data folder.'
        if gui:
            RunWarning(m)
        else:
            print(m)
    elif not os.path.isdir(Path(_data)):
        m = 'Unable to locate the data folder, --data does not point to a folder.'
        if gui:
            RunWarning(m)
        else:
            print(m)
        _dataPath = None

    return _dataPath


def ParseCommandLine():
    parser = argparse.ArgumentParser(description='Fingerprint Recognization')
    parser.add_argument("-d", "--data", help="Select an alternative data folder", default="./data/")
    parser.add_argument("-i", "--image", help="Select a fingerprint image to recognize")
    parser.add_argument("-g", "--gui", action='store_true', help="Run a GUI version of the fingerprint recognization")

    return parser.parse_args()


def LoadDataDir(path):
    address_lst = os.listdir(path)
    name_lst = list(address_lst)
    return name_lst


def DoEverything(parent, params):
    if (not os.path.exists(params.dataPath)) and os.path.isdir(params.dataPath):
        if params.wantGUI:
            mb.showerror('Fingerprint Recognization', 'Invalid data path. Select a valid path and try again!')
            return
        else:
            print('Invalid data path!\n')
            sys.exit(-1)

    name_lst = LoadDataDir(params.dataPath)

    # print("img: ")
    # print(params.imgPath)
    # print("data: ")
    # print(params.dataPath)
    print("name_lst: ")
    print(name_lst)

    flag, name = run_app(str(params.imgPath), str(params.dataPath))

    if flag:
        m = 'Fingerprint matches: {}'.format(name)
        if params.wantGUI:
            ShowResult(m)
        else:
            print(m)
    elif not name == "None":
        m = 'Fingerprint does not match. Most likely: {}'.format(name)
        if params.wantGUI:
            ShowResult(m)
        else:
            print(m)
    else:
        m = 'Empty database.'
        if params.wantGUI:
            ShowResult(m)
        else:
            print(m)


###################################################################################
# main execution starteth here

args = ParseCommandLine()

# TODO Do both warnings in the same error message so user does have to keep coming back to find still more to do

if args.image is None and not args.gui:
    print("No image path specfied.\n")
    sys.exit(-1)

if args.gui:
    RunGUI(args)  # does not return, only exits

img = CheckImgPath(args.gui, args.image)

if img is None:
    sys.exit(-1)

imgPath = Path(args.image)

data = CheckDataPath(args.gui, args.data)

if data is None:
    if not os.path.isdir(Path(DEFAULT_DATA_PATH)):
        os.mkdir(Path(DEFAULT_DATA_PATH))
    dataPath = Path(DEFAULT_DATA_PATH)
else:
    dataPath = Path(args.data)

p = Parameters(_img=imgPath, _data=dataPath, gui=False)

DoEverything(None, p)
