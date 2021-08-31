"""
File that runs all the things
"""

import os
import sys
import subprocess
import shutil

import tkinter as tk
from tkinter.filedialog import askdirectory

from modules import Steamcmd, SteamcmdException
import vdf

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

        # Steamcmd
        self.scmd = None

        # Stores entry labels for uploading
        self.usr =  tk.StringVar()
        self.pwd =  tk.StringVar()
        self.auth = tk.StringVar()

        # Window Stuff
        self['bg'] = '#5f7b4d'
        self.title('Steam Workshop Utility')

        self.gui_MainMenu()

    def gui_MainMenu(self):
        self.clear_frame()
        self.grn_btn(self, text="New Mod", command=self.gui_New).grid(row=0)
        self.grn_btn(self, text="Load Mod", command=self.load).grid(row=1)
        self.grn_btn(self, text="Exit", command=self.close).grid(row=2)
        self.geometry('100x120')

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

        # Workshop Desc
        tk.Label(text='Workshop Description', bg='#5f7b4d').place(x=10, y=10)
        modDesc = tk.Text(width=50, height=39)

        tk.Label(text='App-ID', bg='#5f7b4d').place(x=450, y=10)
        appID = tk.Entry()

        tk.Label(text='File ID', bg='#5f7b4d').place(x=450, y=55)
        fileID = tk.Entry()

        tk.Label(text='Title', bg='#5f7b4d').place(x=450, y=100)
        modTitle = tk.Entry(width=30)

        tk.Label(text='Visibility', bg='#5f7b4d').place(x=450, y=145)
        visibilityMenu = tk.OptionMenu(self, tk.StringVar(value=visval), *visibility_rev.keys(), command=upd_visval)

        tk.Label(text='Image Path', bg='#5f7b4d').place(x=450, y=200)
        previewPath = tk.Entry(width=30)

        tk.Label(text='Mod Path', bg='#5f7b4d').place(x=450, y=250)
        modPath = tk.Entry(width=30)

        self.data['description'] = modDesc
        self.data['appid'] = appID
        self.data['publishedfileid'] = fileID
        self.data['title'] = modTitle
        self.data['previewfile'] = previewPath
        self.data['contentfolder'] = modPath

        for key in self.data:
            obj = self.data[key]
            obj['bg'] = '#85a76f'
            obj['highlightbackground'] = '#86c45e'

        modDesc.insert('end', self.parsed['description'])
        appID.insert(0, self.parsed['appid'])
        fileID.insert(0, self.parsed['publishedfileid'])
        modTitle.insert(0, self.parsed['title'])
        previewPath.insert(0, self.parsed['previewfile'])
        modPath.insert(0, self.parsed['contentfolder'])

        visibilityMenu.config(width=20, bg='#5f7b4d', highlightbackground='#86c45e')

        modDesc.place(x=10, y=30)
        appID.place(x=450, y=30)
        fileID.place(x=450, y=75)
        modTitle.place(x=450, y=120)
        visibilityMenu.place(x=450, y=165)
        previewPath.place(x=450, y=225)
        modPath.place(x=450, y=270)

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

        backb = self.grn_btn(self, text="Back", command=self.gui_MainMenu)
        saveb = self.grn_btn(self, text="Save", command=save)
        uplb = self.grn_btn(self, text="Upload", command=savenup)

        backb.pack(side=tk.BOTTOM, anchor=tk.E)
        saveb.pack(side=tk.BOTTOM, anchor=tk.E)
        uplb.pack(side=tk.BOTTOM, anchor=tk.E)

        self.geometry('800x700')

    def gui_New(self):
        self.clear_frame()

        tk.Label(self, text='Mod Name', bg='#5f7b4d').grid(row=0,column=0)
        self.modname = tk.Entry(highlightbackground='#86c45e', bg='#85a76f')
        self.modname.grid(row=0,column=1)

        def create():
            _moddir = self.modname.get().strip(' ')
            os.mkdir(_moddir)
            shutil.copy('./vdf_template.vdf', f'{_moddir}/{_moddir}.vdf')
            self.vdfloc = f'{_moddir}/{_moddir}.vdf'
            self.gui_vdfEditor()

        self.grn_btn(self, text="Create", command=create).place(x=10, y=35)
        self.grn_btn(command=self.gui_vdfEditor, text='Back').place(x=85, y=35)
        self.geometry('260x80')

    def gui_Upload(self):
        self.clear_frame()
        self.scmd = Steamcmd('./')
        try:
            self.scmd.install()
        except SteamcmdException:
            print('SteamCMD Already Installed')

        tk.Label(self, text='Username', bg='#5f7b4d').grid(row=0)
        tk.Label(self, text='Password', bg='#5f7b4d').grid(row=1)
        tk.Label(self, text='Auth Code', bg='#5f7b4d').grid(row=2)
        tk.Entry(textvariable=self.usr, bg='#85a76f', highlightbackground='#86c45e').grid(row=0, column=1)
        tk.Entry(textvariable=self.pwd, show=False, bg='#85a76f', highlightbackground='#86c45e').grid(row=1, column=1)
        tk.Entry(textvariable=self.auth, bg='#85a76f', highlightbackground='#86c45e').grid(row=2, column=1)
        self.grn_btn(command=self.finish, text='Upload').grid(row=3)
        self.grn_btn(command=self.gui_vdfEditor, text='Back').grid(row=3, column=1)
        self.geometry('200x120')

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
        return tk.Button(*args, **kwargs, bg='#5f7b4d', highlightbackground='#72a84f')

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