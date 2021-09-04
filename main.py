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

from modules import Steamcmd, SteamcmdException
import vdf

try:
    from PIL import Image, ImageTk
    PILMODE = TRUE
except ModuleNotFoundError:
    PILMODE = False

class GUI(tk.Tk):
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

        # Window Stuff
        self['bg'] = '#637e94'
        self.title('Steam Workshop Utility')

        # Stored to prevent GC by Tk
        self.img = None

        self.gui_MainMenu()

    def gui_MainMenu(self):
        self.clear_frame()
        self.grn_btn(self, text="New Mod", width=10, command=self.gui_New).grid(row=0)
        self.grn_btn(self, text="Load Mod", width=10, command=self.load).grid(row=1)
        self.grn_btn(self, text="Exit", width=10, command=self.close).grid(row=2)
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
        tk.Label(text='Workshop Description', bg='#637e94').place(x=5, y=150)
        modDesc = tk.Text(width=78, height=15)

        tk.Label(text='App-ID', bg='#637e94').place(x=5, y=10)
        appID = tk.Entry()

        tk.Label(text='File ID', bg='#637e94').place(x=5, y=70)
        fileID = tk.Entry()

        tk.Label(text='Title', bg='#637e94').place(x=250, y=10)
        modTitle = tk.Entry(width=30)

        tk.Label(text='Visibility', bg='#637e94').place(x=250, y=70)
        visibilityMenu = tk.OptionMenu(self, tk.StringVar(value=visval), *visibility_rev.keys(), command=upd_visval)

        tk.Label(text='Image Path', bg='#637e94').place(x=490, y=10)
        previewPath = tk.Entry(width=30)

        tk.Label(text='Mod Path', bg='#637e94').place(x=490, y=70)
        modPath = tk.Entry(width=30)

        self.imgetn = previewPath
        self.modetn = modPath

        self.data['description'] = modDesc
        self.data['appid'] = appID
        self.data['publishedfileid'] = fileID
        self.data['title'] = modTitle
        self.data['previewfile'] = previewPath
        self.data['contentfolder'] = modPath

        for key in self.data:
            obj = self.data[key]
            obj['bg'] = '#ccdae6'
            obj['highlightbackground'] = '#7598b6'

        modDesc.insert('end', self.parsed['description'])
        appID.insert(0, self.parsed['appid'])
        fileID.insert(0, self.parsed['publishedfileid'])
        modTitle.insert(0, self.parsed['title'])
        previewPath.insert(0, self.parsed['previewfile'])
        modPath.insert(0, self.parsed['contentfolder'])

        visibilityMenu.config(width=24, bg='#ccdae6', highlightbackground='#7598b6')


        self.imgbtn = self.grn_btn(self, text='Browse', width=3, command=saveimg)
        self.modbtn = self.grn_btn(self, text='Browse', width=3, command=savemod)
        self.imgbtn.place(x=490, y=35)
        self.modbtn.place(x=490, y=95)

        # Tkinter will GC it if it's not stored
        try:
            if self.parsed['previewfile'] and PILMODE:
                self.img = ImageTk.PhotoImage(Image.open(self.parsed['previewfile']).resize((144, 144), Image.ANTIALIAS))
                tk.Button(image=self.img, width=144, height=144).place(x=638, y=170)
        except FileNotFoundError:
            pass # Ignore and dont render it

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

        backb = self.grn_btn(self, text="Back", width=6, command=self.gui_MainMenu)
        saveb = self.grn_btn(self, text="Save", width=6,command=save)
        uplb = self.grn_btn(self, text="Upload", width=15, command=savenup)

        backb.place(x=636, y=400)
        saveb.place(x=708, y=400)
        uplb.place(x=636, y=370)

        self.geometry('790x435')

    def gui_New(self):
        self.clear_frame()

        tk.Label(self, text='Mod Name', bg='#637e94').place(x=5, y=5)
        self.modname = tk.Entry(highlightbackground='#7598b6', bg='#ccdae6')
        self.modname.place(x=90, y=5)

        def create():
            _moddir = self.modname.get().strip(' ')
            os.mkdir(_moddir)
            shutil.copy('./vdf_template.vdf', f'{_moddir}/{_moddir}.vdf')
            self.vdfloc = f'{_moddir}/{_moddir}.vdf'
            self.gui_vdfEditor()

        self.grn_btn(self, text="Create", command=create, width=12).place(x=5, y=35)
        self.grn_btn(command=self.gui_MainMenu, text='Back', width=12).place(x=128, y=35)
        self.geometry('260x70')

    def gui_Upload(self):
        self.clear_frame()
        self.scmd = Steamcmd('./')
        try:
            self.scmd.install()
        except SteamcmdException:
            print('SteamCMD Already Installed')

        tk.Label(self, text='Username', bg='#637e94').place(x=5, y=5)
        tk.Label(self, text='Password', bg='#637e94').place(x=5, y=30)
        tk.Label(self, text='Auth Code', bg='#637e94').place(x=5, y=55)
        tk.Entry(textvariable=self.usr, bg='#ccdae6', highlightbackground='#7598b6').place(x=80, y=5)
        tk.Entry(textvariable=self.pwd, show=False, bg='#ccdae6', highlightbackground='#7598b6').place(x=80, y=30)
        tk.Entry(textvariable=self.auth, bg='#ccdae6', highlightbackground='#7598b6').place(x=80, y=55)
        self.grn_btn(command=self.finish, text='Upload', width=15).place(x=5, y=80)
        self.grn_btn(command=self.gui_vdfEditor, text='Back', width=8).place(x=150, y=80)
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

    def close(self):
        exit()

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

    def grn_btn(self, *args, **kwargs):
        return tk.Button(*args, **kwargs, bg='#5a8db8', highlightbackground='#3581c1')

    def clear_frame(self):
        for obj in self.winfo_children():
            obj.destroy()

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

GUI().mainloop()