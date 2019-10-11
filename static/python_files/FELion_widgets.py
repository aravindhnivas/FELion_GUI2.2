
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

    def Entries(self, method, txt, x, y, bind_return=False, bind_key=False, bind_btn=False, **kw):

        kw = var_check(kw)

        if method == 'Entry':

            if isinstance(txt, str): self.widget_frame.txt = StringVar()
            else: self.widget_frame.txt = DoubleVar()

            self.widget_frame.txt.set(txt)

            self.widget_frame.entry = Entry(
                self.widget_frame, bg=kw['bg'], bd=kw['bd'], textvariable=self.widget_frame.txt, font=kw['font'])

            if bind_return: self.widget_frame.entry.bind("<Return>", kw["bind_func"])
            if bind_key: self.widget_frame.entry.bind("<Key>", kw["bind_func"])

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
            if bind_btn: self.widget_frame.Check.bind("<ButtonRelease-1>", kw["bind_func"])
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
        self.dpi_value = self.Entries("Entry", 160, x0+x_diff, y1, bind_return=True, bind_func=self.set_figureLabel, bd=5)

        # Row 2
        y2 = y1 + y_diff
        self.name = self.Entries("Entry", "Plotname", x0, y2, bind_return=True, bind_func=self.save_fig, bd=5, relwidth=0.7)

        # Row 3
        y3 = y2 + y_diff
        self.plotTitle = self.Entries("Entry", "Title", x0, y3, bind_key=True, bind_func=self.set_figureLabel, bd=5, relwidth=0.7)

        # Row 4
        y4 = y3 + y_diff
        self.plotXlabel = self.Entries("Entry", "X-axis", x0, y4, bind_key=True, bind_func=self.set_figureLabel, bd=5, relwidth=0.7)

        # Row 5
        y5 = y4 + y_diff
        self.plotYlabel = self.Entries("Entry", "Y-axis", x0, y5, bind_key=True, bind_func=self.set_figureLabel, bd=5, relwidth=0.7)

        # Row 6
        y6 = y5 + y_diff
        x_diff2 = 0.2
        self.subplot_top_label = self.Labels("TOP" , x0, y6, relwidth=0.2)
        self.subplot_bottom_label = self.Labels("Bottom" , x0+1*x_diff2, y6, relwidth=0.2)
        self.subplot_left_label = self.Labels("Left" , x0+2*x_diff2, y6, relwidth=0.2)
        self.subplot_right_label = self.Labels("Right" , x0+3*x_diff2, y6, relwidth=0.2)

        # Row 7
        y7 = y6 + y_diff
        self.subplot_top = self.Entries("Entry", 0.95 , x0, y7, bind_return=True, bind_func=self.set_subplot_position, bd=5, relwidth=0.2)
        self.subplot_bottom = self.Entries("Entry", 0.2 , x0+x_diff2, y7, bind_return=True, bind_func=self.set_subplot_position, bd=5, relwidth=0.2)
        self.subplot_left = self.Entries("Entry", 0.1 , x0+2*x_diff2, y7, bind_return=True, bind_func=self.set_subplot_position, bd=5, relwidth=0.2)
        self.subplot_right = self.Entries("Entry", 0.9 , x0+3*x_diff2, y7, bind_return=True, bind_func=self.set_subplot_position, bd=5, relwidth=0.2)
        
        # Row 8
        y8 = y7 + y_diff
        self.plotGrid = self.Entries("Check", "grid", x0, y8, default=True, bind_btn=True, bind_func=self.set_figureLabel)
        self.plotLegend = self.Entries("Check", "Legend", x0+x_diff, y8, default=True, bind_btn=True, bind_func=self.set_figureLabel)

        # # Row 9
        y9 = y8 + y_diff
        self.save_btn = self.Buttons("Save", x0, y9, self.save_fig)
    
    def set_subplot_position(self, event=None):
        self.fig.subplots_adjust(top=self.subplot_top.get(), bottom=self.subplot_bottom.get(), left=self.subplot_left.get(), right=self.subplot_right.get())
        self.canvas.draw()
        
    def set_figureLabel(self, event=None):


        if event is not None:

            widget_name = str(event.widget).split("!")[-1]

            if widget_name == "entry": # DPI

                self.fig.set_dpi(self.dpi_value.get())

                width = self.canvas_frame.winfo_width()/self.dpi_value.get()
                height = self.canvas_frame.winfo_height()/self.dpi_value.get()
                self.fig.set_size_inches(width, height)

            if widget_name == "entry3": # Title
                self.entry_value = self.plotTitle.get() + event.char
                self.ax.set(title=self.entry_value.strip())
            
            if widget_name == "entry4": # Xlabel
                self.entry_value = self.plotXlabel.get() + event.char
                self.ax.set(xlabel=self.entry_value.strip())

            if widget_name == "entry5": # Ylabel
                self.entry_value = self.plotYlabel.get() + event.char
                self.ax.set(ylabel=self.entry_value.strip())

            if widget_name == "checkbutton": # Grid
                self.ax.grid(not self.plotGrid.get())
            
            if widget_name == "checkbutton2": # Legend
                self.plot_legend.set_visible(not self.plotLegend.get())
            
        else:
            self.ax.set(title=self.plotTitle.get(), ylabel=self.plotYlabel.get(), xlabel=self.plotXlabel.get())
            self.ax.grid(self.plotGrid.get())

        self.canvas.draw()

    def make_figure_layout(self, title="Title", xaxis="X-axis", yaxis="Y-axis", xdata=None, ydata=None, label="", fmt=".-"):
        
        self.ax = self.fig.add_subplot(111)
        if xdata is not None: self.ax.plot(xdata, ydata, fmt, label=label)

        self.plotTitle.set(title)
        self.plotYlabel.set(yaxis)
        self.plotXlabel.set(xaxis)
        self.set_figureLabel()
        self.plot_legend = self.ax.legend()

        return self.ax

    def save_fig(self, event=None):
        if not isdir('./OUT'): os.mkdir('OUT')

        if isfile(f'./OUT/{self.name.get()}.png'):
            if askokcancel('Overwrite?', f'File: {self.name.get()}.png already present. \nDo you want to Overwrite the file?'):
                self.fig.savefig(f'./OUT/{self.name.get()}.png')
                showinfo('SAVED', f'File: {self.name.get()}.png saved in OUT/ directory.')

        else:
            self.fig.savefig(f'./OUT/{self.name.get()}.png')
            showinfo('SAVED', f'File: {self.name.get()}.png saved in OUT/ directory')

        print(f'Filename saved: {self.name.get()}.png\nLocation: {self.location}\n')


# class Frame1:

#     def __init__(self):

#         self.widget = FELion_Tk("Filename")
#         self.make_figure()
#         self.widget.mainloop()
    
#     def make_figure(self):
#         fig, canvas = self.widget.Figure()
#         ax = self.widget.make_figure_layout(xdata=[1, 2, 3], ydata=[1, 2, 3], label="Testing", title="CD")
#         canvas.draw()

# if __name__ == "__main__":
#     start = Frame1()