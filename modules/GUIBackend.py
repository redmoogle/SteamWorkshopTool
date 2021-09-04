import tkinter as tk
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self['bg'] = '#637e94'
        self.title('Steam Workshop Utility')

    def close(self):
        exit()

    def clear_frame(self):
        for obj in self.winfo_children():
            obj.destroy()


# Standard Components
def Button(*args, **kwargs):
        return tk.Button(*args, **kwargs, bg='#5a8db8', highlightbackground='#3581c1')

def Label(text, *args, **kwargs):
    return tk.Label(*args, **kwargs, bg='#637e94', text=text)

def Entry(text, *args, **kwargs):
    _ = tk.Entry(*args, **kwargs, background='#ccdae6', highlightbackground='#7598b6')
    _.insert(0, text)
    return _

def Text(text, *args, **kwargs):
    _ = tk.Text(*args, **kwargs, background='#ccdae6', highlightbackground='#7598b6')
    _.insert(tk.END, text)
    return _