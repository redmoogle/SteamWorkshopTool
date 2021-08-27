"""
File that runs all the things
"""

import os
import sys
from threading import Timer

import tkinter as tk
from tkinter.filedialog import askdirectory

from pysteamcmdwrapper import SteamCMD, SteamCMDException
import vdf

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('1500x1000')
        self.objects = []
        self.gui_MainMenu()
        self.vdfloc = ''

    def win_update(self):
        pass

    def gui_MainMenu(self):
        self.clear_frame()
        self.title = 'Steam Worshop Utility'
        self.objects.append(tk.Button(self, text="New Mod", command=self.gui_NewStage1))
        self.objects.append(tk.Button(self, text="Load Mod", command=self.gui_LoadStage1))
        self.objects.append(tk.Button(self, text="Exit", command=self.close))
        self.render()

    def gui_LoadStage1(self):
        self.clear_frame()
        self.title = 'Load Workshop Mod'
        self.objects.append(tk.Button(self, text="Open Mod Folder", command=self.load))
        self.objects.append(tk.Button(self, text="Back", command=self.gui_MainMenu))
        self.render()

    def gui_LoadStage2(self):
        self.clear_frame()
        self.title = 'Modify Mod'
        with open(self.vdfloc) as vdffile:
            parsed = vdf.parse(vdffile)['workshopitem']
        
        print(parsed)
        tk.Label(text='Workshop Description').grid(row=0,column=0)
        txt = tk.Text(width=50, height=55)
        txt.insert('end', parsed['description'])
        txt.grid(row=2,column=0)
        tk.Label(text='App-ID').grid(row=0,column=2)
        tk.Entry(textvariable=parsed['appid']).grid(row=2,column=2)

        self.render()

    def gui_NewStage1(self):
        return

    def gui_NewStage2(self):
        pass

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
            self.gui_LoadStage2()

    def render(self):
        for obj in self.objects:
            obj.pack()

    def clear_frame(self):
        for obj in self.objects:
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


"""
if detected_platform == 'LINUX':
    scmd = SteamCMD("./")
    try:
        scmd.install()
    except SteamCMDException:
        print("Already installed, try to use the --force option to force installation")
    scmd.login()
"""
