"""
File that runs all the things
"""

import os
import sys
from threading import Timer
import subprocess
import shutil

import tkinter as tk
from tkinter.filedialog import askdirectory

from modules import Steamcmd, SteamcmdException
import vdf

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Steam Workshop Utility')
        self.objects = []
        self.gui_MainMenu()
        self.vdfloc = ''
        self.data = {}
        self.parsed = None
        self.vdf = None
        self.usr = tk.StringVar()
        self.pwd = tk.StringVar()
        self.auth = tk.StringVar()
        self.scmd = None

        self['bg'] = '#5f7b4d'

        self.modname = None

    def gui_MainMenu(self):
        self.clear_frame()
        self.objects.append(self.grn_btn(self, text="New Mod", command=self.gui_New, highlightbackground='#72a84f'))
        self.objects.append(self.grn_btn(self, text="Load Mod", command=self.load, highlightbackground='#72a84f'))
        self.objects.append(self.grn_btn(self, text="Exit", command=self.close, highlightbackground='#72a84f'))
        self.render(size='100x120')

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

        modDesc.place(x=10, y=30)
        appID.place(x=450, y=30)
        fileID.place(x=450, y=75)
        modTitle.place(x=450, y=120)
        visibilityMenu.config(width=20, bg='#5f7b4d', highlightbackground='#86c45e')
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


        self.render(size='800x700')

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
        self.render(size='260x80')

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
        self.render(size='200x120')

    def finish(self):
        subprocess.run([self.scmd.steamcmd_exe, f'+login {self.usr.get()} {self.pwd.get()} {self.auth.get()}', '+workshop_build_item', self.vdfloc, '+quit'])
        print('Finished Upload')
        self.gui_MainMenu()

    def close(self):
        exit()

    def load(self):
        file = askdirectory(title='Open Mod Folder', initialdir=".")
        _file = file # IDK WTF HAPPENS
        contents = os.listdir(file)
        vdf = None
        for file in contents:
            if file.endswith('.vdf'):
                vdf = file
        
        if vdf == None:
            print('No VDF Found')
            widg = tk.Label(text="Failed to locate VDF File", fg="Red", font=("Helvetica", 18))
            widg.pack()
            Timer(3, widg.destroy).start()

        else:
            print(f'VDF Located: {_file}/{vdf}')
            self.vdfloc = f'{_file}/{vdf}'
            self.gui_vdfEditor()

    def grn_btn(self, *args, **kwargs):
        return tk.Button(*args, **kwargs, bg='#5f7b4d')

    def render(self, size='800x1000'):
        self.geometry(size)
        for row, obj in enumerate(self.objects):
            obj.grid(row=row, pady=1)

    def clear_frame(self):
        for obj in self.winfo_children():
            obj.destroy()
        self.objects = []

OSTypes = {
    'WINDOWS': 'win32',
    'LINUX': 'linux',
    'MACOS': 'darwin' # not supported but is in there
}

platform = sys.platform
detected_platform = None
root = os.path.abspath("./")

for OS in OSTypes:
    if platform == OSTypes[OS]:
        detected_platform = OS
        print(f'Detected OS: {OS}')
    
if detected_platform == None:
    # FreeBSD Cygwin Aix
    print(f'Unsupported OS: {sys.platform}')
    exit()

gui = GUI()
gui.mainloop()