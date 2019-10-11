
# Built-In modules
import os
from os.path import isdir, isfile

# Tkinter
from tkinter import Frame, IntVar, StringVar, BooleanVar, DoubleVar, Tk, Label, Entry
from tkinter.ttk import Button, Checkbutton
from tkinter.messagebox import showerror, showinfo, showwarning, askokcancel

# Matplotlib
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
############################################################################################################

constants = {
    'width': 50,
    'height': 50,
    'font': ("Verdana", 10, "italic"),
    'bg': 'white',
    'bd': 0,
    'anchor': 'w',
    'relief': "solid",
    'relwidth': 0.3,
    'relheight': 0.04,
    'justify': 'left',
    'label': '',
}

def var_check(kw):
    for i in constants:
        if not i in list(kw.keys()):
            kw[i] = constants[i]
    return kw

__version__ = "1.0.1"

class FELion_Tk(Tk):

    def __init__(self, title="FELion GUI2", location=".", figure_widget=True, background="light grey", *args, **kwargs):

        Tk.__init__(self, *args, **kwargs)

        self.location = location
        os.chdir(self.location)

        Tk.wm_title(self, title)
        Tk.wm_geometry(self, "1000x600")

        if figure_widget:
            self.canvas_frame = Frame(self, bg='white')
            self.canvas_frame.place(relx=0, rely=0, relwidth=0.8, relheight=1)

            self.widget_frame = Frame(self, bg=background)
            self.widget_frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)
        else:
            self.widget_frame = Frame(self, bg=background)
            self.widget_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def Labels(self, txt, x, y, **kw):
        
        kw = var_check(kw)

        self.widget_frame.txt = Label(self.widget_frame, text=txt, justify=kw['justify'], font=kw['font'], bg=kw['bg'], bd=kw['bd'], relief=kw['relief'])
        self.widget_frame.txt.place(relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.txt

    def Buttons(self, btn_txt, x, y, *args, **kw):
        kw = var_check(kw)

        if len(args) == 1:
            
            func = args[0]
            self.widget_frame.btn_txt = Button(self.widget_frame, text=btn_txt, command=lambda: func())
        elif len(args)>1:
            func = args[0]
            func_parameters = args[1:]

            print(func, func_parameters)
            self.widget_frame.btn_txt = Button(self.widget_frame, text=btn_txt, command=lambda: func(*func_parameters))

        else:
            self.widget_frame.btn_txt = Button(self.widget_frame, text=btn_txt, command=lambda: print("No function set"))
        
        self.widget_frame.btn_txt.place(relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.btn_txt

    def Entries(self, method, txt, x, y, **kw):

        kw = var_check(kw)

        if method == 'Entry':

            if isinstance(txt, str): self.widget_frame.txt = StringVar()
            else: self.widget_frame.txt = DoubleVar()

            self.widget_frame.txt.set(txt)
            self.widget_frame.entry = Entry(
                self.widget_frame, bg=kw['bg'], bd=kw['bd'], textvariable=self.widget_frame.txt, font=kw['font'])
            self.widget_frame.entry.place(
                relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt

        elif method == 'Check':

            self.widget_frame.txt = BooleanVar()

            if 'default' in kw:
                self.widget_frame.txt.set(kw['default'])
            else:
                self.widget_frame.txt.set(False)

            self.widget_frame.Check = Checkbutton(self.widget_frame, text=txt, variable=self.widget_frame.txt)
            self.widget_frame.Check.place(relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt
    
    def Figure(self, connect=True, adjust_plot=True, **kw):

        self.make_figure_widgets()
        dpi = self.dpi_value.get()

        if 'figsize' in kw:
            self.fig = Figure(figsize=kw['figsize'], dpi=dpi)
        else:
            self.fig = Figure(dpi=dpi)

        if adjust_plot: self.fig.subplots_adjust(top=0.95, bottom=0.2, left=0.1, right=0.9)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        
        def on_key_press(event): key_press_handler(event, self.canvas, self.toolbar)
        if connect: self.canvas.mpl_connect("key_press_event", on_key_press)

        return self.fig, self.canvas

    def make_figure_widgets(self):

        x0 = 0.1
        x_diff = 0.4
        y_diff = 0.05

        # Row 1
        y1 = y_diff
        self.label_dpi = self.Labels("DPI", x0, y1)
        self.dpi_value = self.Entries("Entry", 100, x0+x_diff, y1, bd=5)

        # Row 2
        y2 = y1 + y_diff
        self.name = self.Entries("Entry", "Plotname", x0, y2, bd=5, relwidth=0.7)

        # Row 3
        y3 = y2 + y_diff
        self.save_btn = self.Buttons("Save", x0, y3, self.save_fig)
        
       
    def save_fig(self):
        if not isdir('./OUT'): os.mkdir('OUT')
        if isfile(f'./OUT/{self.name.get()}.png'):
            if askokcancel('Overwrite?', f'File: {self.name.get()}.png already present. \nDo you want to Overwrite the file?'):
                self.fig.savefig(f'./OUT/{self.name.get()}.png')
                showinfo('SAVED', f'File: {self.name.get()}.png saved in OUT/ directory.')
        else:
            self.fig.savefig(f'./OUT/{self.name.get()}.png')
            showinfo('SAVED', f'File: {self.name.get()}.png saved in OUT/ directory')

        print(f'Filename saved: {self.name.get()}.png\nLocation: {self.location}\n')

def print_test(arg="none"):
    print("testing:, ", arg)

class Frame1:
    def __init__(self):

        self.widget = FELion_Tk("Filename")
        
        # self.make_widgets()

        self.make_figure()

        self.widget.mainloop()
    
    def test(self): print_test(self.entry1.get())

    def make_widgets(self):
        self.button1 = self.widget.Buttons("Button1", 0.1, 0.05, self.test)
        self.button2 = self.widget.Buttons("Button2", 0.5, 0.1, self.test)

        self.label1 = self.widget.Labels("Label1", 0.1, 0.2)
        self.label2 = self.widget.Labels("Label2", 0.5, 0.2)

        self.entry1 = self.widget.Entries("Entry", "Filename", 0.1, 0.3, bd=5)
        self.entry2 = self.widget.Entries("Check", "ON/OFF", 0.5, 0.3)

    def make_figure(self):
        fig, canvas = self.widget.Figure(dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot([1, 2, 3])
        canvas.draw()

if __name__ == "__main__":
    start = Frame1()