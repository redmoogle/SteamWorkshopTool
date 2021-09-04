"""
File that runs all the things
"""

import os
import sys
import subprocess
import shutil

import tkinter as tk
from tkinter.constants import TRUE
from tkinter.filedialog import askdirectory, askopenfile
import modules.GUIBackend as GUI

from modules import Steamcmd, SteamcmdException
import vdf

# Used for rendering preview images for Tk
try:
    from PIL import Image, ImageTk
    PILMODE = TRUE
except ModuleNotFoundError:
    PILMODE = False

class SteamWorkshop(GUI.GUI):
    def __init__(self):
        super().__init__()

        # Name of the new mod
        self.modname = None

        # GUI Storage
        self.data = {}    # To be read

        # VDF Data
        self.vdfloc = ''   # Location
        self.vdf = None    # Workshop Data
        self.parsed = None # Full VDF Data

        # Paths
        self.modent = None
        self.imgent = None

        self.modfile = ''
        self.imgfile = ''

        # Steamcmd
        self.scmd = None

        # Stores entry labels for uploading
        self.usr =  tk.StringVar()
        self.pwd =  tk.StringVar()
        self.auth = tk.StringVar()

        # Stored to prevent GC by Tk
        self.img = None

        self.gui_MainMenu()

    def gui_MainMenu(self):
        self.clear_frame()
        GUI.Button(self, text="New Mod", width=10, command=self.gui_New).grid(row=0)
        GUI.Button(self, text="Load Mod", width=10, command=self.load).grid(row=1)
        GUI.Button(self, text="Exit", width=10, command=self.close).grid(row=2)
        self.geometry('112x93')

    def gui_vdfEditor(self):
        self.clear_frame()
        self.data = {}

        visibility = {0:"Public", 1:"Friends Only", 2: "Private"}
        visibility_rev = {"Public": 0, "Friends Only": 1, "Private": 2}

        with open(self.vdfloc) as vdffile:
            self.vdf = vdf.parse(vdffile)
            self.parsed = self.vdf['workshopitem']

        visval = visibility[int(self.parsed['visibility'])]
        def upd_visval(selection):
            visval = visibility_rev[selection]
            self.parsed['visibility'] = visval

        def saveimg():
            self.imgfile = askopenfile(filetypes=[('JPEG Files', '.jpg')]).name
            self.imgetn.delete(0, tk.END)
            self.imgetn.insert(0, self.imgfile)

        def savemod():
            self.modfile = askopenfile(filetypes=[('Mod File', '*')]).name
            self.modent.delete(0, tk.END)
            self.modetn.insert(0, self.modfile)

        # Workshop Desc
        GUI.Label(text='Workshop Description').place(x=5, y=150)
        modDesc = GUI.Text(self.parsed['description'], width=78, height=15)

        GUI.Label(text='App-ID').place(x=5, y=10)
        appID = GUI.Entry(self.parsed['appid'])

        GUI.Label(text='File ID').place(x=5, y=70)
        fileID = GUI.Entry(self.parsed['publishedfileid'])

        GUI.Label(text='Title').place(x=250, y=10)
        modTitle = GUI.Entry(self.parsed['title'], width=30)

        GUI.Label(text='Visibility').place(x=250, y=70)
        visibilityMenu = tk.OptionMenu(self, tk.StringVar(value=visval), *visibility_rev.keys(), command=upd_visval)

        GUI.Label(text='Image Path').place(x=490, y=10)
        previewPath = GUI.Entry(self.parsed['previewfile'], width=30)

        GUI.Label(text='Mod Path').place(x=490, y=70)
        modPath = GUI.Entry(self.parsed['contentfolder'], width=30)

        self.imgetn = previewPath
        self.modetn = modPath

        self.data['description'] = modDesc
        self.data['appid'] = appID
        self.data['publishedfileid'] = fileID
        self.data['title'] = modTitle
        self.data['previewfile'] = previewPath
        self.data['contentfolder'] = modPath

        visibilityMenu.config(width=24, bg='#ccdae6', highlightbackground='#7598b6')


        self.imgbtn = GUI.Button(self, text='Browse', width=3, command=saveimg)
        self.modbtn = GUI.Button(self, text='Browse', width=3, command=savemod)
        self.imgbtn.place(x=490, y=35)
        self.modbtn.place(x=490, y=95)

        # Tkinter will GC it if it's not stored
        try:
            if self.parsed['previewfile'] and PILMODE:
                self.img = ImageTk.PhotoImage(Image.open(self.parsed['previewfile']).resize((144, 144), Image.ANTIALIAS))
                GUI.Button(image=self.img, width=144, height=144).place(x=638, y=170)
        except FileNotFoundError:
            pass # Ignore and dont render it; Should put something here in its place

        modDesc.place(x=5, y=170)
        appID.place(x=5, y=35, height=30, width=220)
        fileID.place(x=5, y=95, height=30, width=220)
        modTitle.place(x=250, y=35, height=30, width=220)
        visibilityMenu.place(x=250, y=95, height=30, width=220)
        previewPath.place(x=545, y=35, height=30, width=220)
        modPath.place(x=545, y=95, height=30, width=220)

        def save():
            for dataobj in self.data:
                obj = self.data[dataobj]
                if isinstance(obj, tk.Text):
                    dat = self.data[dataobj].get('1.0', tk.END)
                else:
                    dat = self.data[dataobj].get()
                self.parsed[dataobj] = dat
            with open(self.vdfloc, mode='w+') as vdffile:
                self.vdf['workshopitem'] = self.parsed
                vdf.dump(self.vdf, vdffile, pretty=False, escaped=False)
            print('Saved VDF')
            self.gui_vdfEditor()

        def savenup():
            save()
            self.gui_Upload()

        backb = GUI.Button(self, text="Back", width=6, command=self.gui_MainMenu)
        saveb = GUI.Button(self, text="Save", width=6,command=save)
        uplb = GUI.Button(self, text="Upload", width=15, command=savenup)

        backb.place(x=636, y=400)
        saveb.place(x=708, y=400)
        uplb.place(x=636, y=370)

        self.geometry('790x435')

    def gui_New(self):
        self.clear_frame()

        GUI.Label(self, text='Mod Name').place(x=5, y=5)
        self.modname = GUI.Entry()
        self.modname.place(x=90, y=5)

        def create():
            _moddir = self.modname.get().strip(' ')
            os.mkdir(_moddir)
            shutil.copy('./vdf_template.vdf', f'{_moddir}/{_moddir}.vdf')
            self.vdfloc = f'{_moddir}/{_moddir}.vdf'
            self.gui_vdfEditor()

        GUI.Button(self, text="Create", command=create, width=12).place(x=5, y=35)
        GUI.Button(command=self.gui_MainMenu, text='Back', width=12).place(x=128, y=35)
        self.geometry('260x70')

    def gui_Upload(self):
        self.clear_frame()
        self.scmd = Steamcmd('./')
        try:
            self.scmd.install()
        except SteamcmdException:
            print('SteamCMD Already Installed')

        GUI.Label(self, text='Username').place(x=5, y=5)
        GUI.Label(self, text='Password').place(x=5, y=30)
        GUI.Label(self, text='Auth Code').place(x=5, y=55)
        GUI.Entry(textvariable=self.usr).place(x=80, y=5)
        GUI.Entry(textvariable=self.pwd, show=False).place(x=80, y=30)
        GUI.Entry(textvariable=self.auth).place(x=80, y=55)
        GUI.Button(command=self.finish, text='Upload', width=15).place(x=5, y=80)
        GUI.Button(command=self.gui_vdfEditor, text='Back', width=8).place(x=150, y=80)
        self.geometry('255x115')

    def finish(self):
        subprocess.run([
            self.scmd.steamcmd_exe,
            f'+login {self.usr.get()} {self.pwd.get()} {self.auth.get()}',
            '+workshop_build_item',
            self.vdfloc,
            '+quit'
        ])
        print('Finished Upload')
        self.gui_MainMenu()

    def load(self):
        fdir = askdirectory(title='Open Mod Folder', initialdir=".")
        vdf = None
        for file in os.listdir(fdir):
            if file.endswith('.vdf'):
                vdf = file
                break
        else:
            print('No VDF Found')
            return

        self.vdfloc = f'{fdir}/{vdf}'
        print(f'VDF Located: {self.vdfloc}')
        self.gui_vdfEditor()

OSTypes = {
    'WINDOWS': 'win32',
    'LINUX': 'linux',
}

platform = sys.platform
detected_platform = None
root = os.path.abspath("./")

for OS in OSTypes:
    if platform == OSTypes[OS]:
        detected_platform = OS
        print(f'Detected OS: {OS}')
    
if detected_platform == None:
    # FreeBSD Cygwin Aix MacOS
    print(f'Unsupported OS: {sys.platform}')
    exit()

SteamWorkshop().mainloop()