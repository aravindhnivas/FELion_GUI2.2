
# Built-In modules
import os
from os.path import isdir, isfile

# # Custom module
# from line_profiler import profile

# Tkinter
from tkinter import Frame, IntVar, StringVar, BooleanVar, DoubleVar, Tk, filedialog
from tkinter.ttk import Button, Checkbutton, Label, Entry, Scale
from tkinter.messagebox import showerror, showinfo, showwarning, askokcancel

# Matplotlib
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
############################################################################################################

constants = {
    'relwidth': 0.3,
    'relheight': 0.04,
    "anchor": "w",
    "slider_orient": "horizontal"
}

def var_check(kw):
    for i in constants:
        if not i in kw:
            kw[i] = constants[i]
    return kw

class FELion_Tk(Tk):

    def __init__(self, title="FELion GUI2", location=".", background="light grey", *args, **kwargs):

        Tk.__init__(self, *args, **kwargs)

        self.location = location
        os.chdir(self.location)

        Tk.wm_title(self, title)
        Tk.wm_geometry(self, "1000x600")

        self.canvas_frame = Frame(self, bg='white')
        self.canvas_frame.place(relx=0, rely=0, relwidth=0.8, relheight=1)

        self.widget_frame = Frame(self, bg=background)
        self.widget_frame.bind("<Button-1>", lambda event:print(self.focus()))
        self.widget_frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)

    def Labels(self, txt, x, y, **kw):

        kw = var_check(kw)
        self.widget_frame.txt = Label(self.widget_frame, text=txt)
        self.widget_frame.txt.place(
            relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])
        return self.widget_frame.txt

    def Sliders(self, txt, value, x, y, bind_func, **kw):
        kw = var_check(kw)

        self.Labels(txt, x, y, relwidth=0.2)
        self.widget_frame.value = DoubleVar()
        self.widget_frame.value.set(value)

        self.widget_frame.scale = Scale(
            self.widget_frame, variable=self.widget_frame.value, from_=0, to=1, orient=kw["slider_orient"])

        self.widget_frame.scale.bind("<ButtonRelease-1>", bind_func)
        self.widget_frame.scale.place(
            relx=x+0.2, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.value

    def Buttons(self, btn_txt, x, y, *args, **kw):
        kw = var_check(kw)

        if len(args) == 1:

            func = args[0]
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: func())
        elif len(args) > 1:
            func = args[0]
            func_parameters = args[1:]

            print(func, func_parameters)
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: func(*func_parameters))

        else:
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: print("No function set"))

        self.widget_frame.btn_txt.place(
            relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.btn_txt

    def Entries(self, method, txt, x, y, bind_return=False, bind_key=False, bind_btn=False, **kw):

        kw = var_check(kw)

        if method == 'Entry':

            if isinstance(txt, str):
                self.widget_frame.txt = StringVar()
            else:
                self.widget_frame.txt = DoubleVar()

            self.widget_frame.txt.set(txt)

            self.widget_frame.entry = Entry(
                self.widget_frame, textvariable=self.widget_frame.txt)

            if bind_return:
                self.widget_frame.entry.bind("<Return>", kw["bind_func"])
            if bind_key:
                self.widget_frame.entry.bind("<Key>", kw["bind_func"])

            self.widget_frame.entry.place(
                relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt

        elif method == 'Check':

            self.widget_frame.txt = BooleanVar()

            if 'default' in kw:
                self.widget_frame.txt.set(kw['default'])
            else:
                self.widget_frame.txt.set(False)

            self.widget_frame.Check = Checkbutton(
                self.widget_frame, text=txt, variable=self.widget_frame.txt)
            if bind_btn:
                self.widget_frame.Check.bind(
                    "<ButtonRelease-1>", kw["bind_func"])
            self.widget_frame.Check.place(
                relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt

    def Figure(self, connect=True, dpi=None, **kw):

        self.make_figure_widgets()

        if dpi is not None: self.dpi_value.set(dpi)

        self.fig = Figure(dpi=self.dpi_value.get())

        self.fig.subplots_adjust(top=0.95, bottom=0.2, left=0.1, right=0.9)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        def on_key_press(event): key_press_handler(
            event, self.canvas, self.toolbar)

        if connect:
            self.canvas.mpl_connect("key_press_event", on_key_press)

        return self.fig, self.canvas

    def make_figure_widgets(self):

        # Position
        x0, x_diff = 0.1, 0.4
        y, y_diff = 0, 0.05

        # Row 1
        y += y_diff
        self.label_dpi = self.Labels("DPI", x0, y)
        self.dpi_value = self.Entries("Entry", 120, x0+x_diff, y, bind_return=True, bind_func=self.set_figureLabel)

        # Row 2
        y += y_diff
        self.name = self.Entries("Entry", "Plotname", x0, y, bind_return=True, bind_func=self.save_fig, relwidth=0.7)

        # Row 3
        y += y_diff
        self.plotTitle = self.Entries("Entry", "Title", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
        self.titleSz = self.Entries("Entry", 12, x0+0.5, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

        # Row 4
        y += y_diff
        self.plotXlabel = self.Entries("Entry", "X-axis", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
        self.xlabelSz = self.Entries("Entry", 10, x0+0.5, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

        # Row 5
        y += y_diff
        self.plotYlabel = self.Entries("Entry", "Y-axis", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
        self.ylabelSz = self.Entries("Entry", 10, x0+0.5, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

        # Row 6
        y += y_diff
        self.plotFigText = self.Entries("Entry", "Figure 1", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
        self.figtextFont = self.Entries("Entry", 12, x0+0.5, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

        # Row 7
        y += y_diff
        self.subplot_top = self.Sliders("TOP", 0.95, x0, y, self.set_subplot_position, relwidth=0.5)
        self.subplot_bottom = self.Sliders("Bottom", 0.2, x0, y+y_diff, self.set_subplot_position, relwidth=0.5)
        self.subplot_left = self.Sliders("Left", 0.1, x0, y+2*y_diff, self.set_subplot_position, relwidth=0.5)
        self.subplot_right = self.Sliders("Right", 0.9, x0, y+3*y_diff, self.set_subplot_position, relwidth=0.5)
        y += 3*y_diff

        # Row 8
        y += y_diff
        self.plotGrid = self.Entries("Check", "grid", x0, y, default=True, bind_btn=True, bind_func=self.set_figureLabel)
        self.plotLegend = self.Entries("Check", "Legend", x0+x_diff, y, default=True, bind_btn=True, bind_func=self.set_figureLabel)

        # Row 9
        y += y_diff
        self.plotYscale = self.Entries("Check", "Yscale (log)", x0, y, default=False, bind_btn=True, bind_func=self.set_figureLabel)

        #  Row 9
        y += y_diff
        self.browseDir = self.Buttons("Browse", x0, y, self.changeLocation)
        self.save_btn = self.Buttons("Save", x0+x_diff, y, self.save_fig)

    def changeLocation(self): 
        newLocation = filedialog.askdirectory(initialdir = "./")
        
        if newLocation is not "": self.location=newLocation
        else: print(f"No location changed\nCurrent Location: {self.location}")

    def set_subplot_position(self, event=None):
        self.fig.subplots_adjust(
            top=self.subplot_top.get(), 
            bottom=self.subplot_bottom.get(), 
            left=self.subplot_left.get(), 
            right=self.subplot_right.get())

        self.canvas.draw()

    def set_figureLabel(self, event=None):

        if event is not None:

            widget_name = str(event.widget).split("!")[-1]

            print(widget_name)

            if widget_name == "entry":  # DPI

                self.fig.set_dpi(self.dpi_value.get())

                width = self.canvas_frame.winfo_width()/self.dpi_value.get()
                height = self.canvas_frame.winfo_height()/self.dpi_value.get()
                self.fig.set_size_inches(width, height)

            if widget_name == "entry3":  # Title
                self.entry_value = self.plotTitle.get() + event.char
                self.ax.set(title=self.entry_value.strip())
            
            if widget_name == "entry4":  # Title size
                self.ax.set_title(self.plotTitle.get(), fontsize=self.titleSz.get())

            if widget_name == "entry5":  # Xlabel
                self.entry_value = self.plotXlabel.get() + event.char
                self.ax.set(xlabel=self.entry_value.strip())

            if widget_name == "entry6":  # Xalbel fontsize
                self.ax.xaxis.label.set_size(self.xlabelSz.get())

            if widget_name == "entry7":  # Ylabel
                self.entry_value = self.plotYlabel.get() + event.char
                self.ax.set(ylabel=self.entry_value.strip())
            
            if widget_name == "entry8":  # Ylabel fontsize
                self.ax.yaxis.label.set_size(self.ylabelSz.get())

            if widget_name == "entry9":  # Figtext label
                self.entry_value = self.plotFigText.get() + event.char
                self.figtext.set_text(self.entry_value.strip())
            
            if widget_name == "entry10":  # Figtext fontsize
                self.figtext.set_fontsize(self.figtextFont.get())

            if widget_name == "checkbutton":  # Grid
                self.ax.grid(not self.plotGrid.get())

            if widget_name == "checkbutton2":  # Legend
                self.plot_legend.set_visible(not self.plotLegend.get())
            
            if widget_name == "checkbutton3":  # Yscale
                if self.plotYscale.get(): scale = "linear"
                else: scale = "log"
                self.ax.set(yscale=scale)

        # self.focus_set()
        self.canvas.draw()

    def make_figure_layout(self, 
        ax=None, savename=None,
        title="Title", xaxis="X-axis", yaxis="Y-axis", fig_caption="Figure 1", 
        xdata=None, ydata=None, label="", fmt=".-", yscale="linear", **kw):

        if savename is not None: self.name.set(savename)

        # Making subplot
        self.ax = ax
        if ax is None: self.ax = self.fig.add_subplot(111)

        # Plotting data if any:
        if xdata is not None: plot, = self.ax.plot(xdata, ydata, fmt, label=label, **kw)

        # Setting default title, xlabel and ylabel entries
        self.plotTitle.set(title)
        self.plotYlabel.set(yaxis)
        self.plotXlabel.set(xaxis)
        self.plotFigText.set(fig_caption)

        # Yscale
        self.ax.set(yscale=yscale)
        if yscale == "log": self.plotYscale.set(True)

        # Setting title
        self.ax.set_title(title, fontsize=self.titleSz.get())

        # Setting X and Y label
        self.ax.set(
            ylabel=yaxis, 
            xlabel=xaxis
        )

        # Xlabel and Ylabel fontsize
        self.ax.xaxis.label.set_size(self.xlabelSz.get())
        self.ax.yaxis.label.set_size(self.ylabelSz.get())

        # Grid
        self.ax.grid(self.plotGrid.get())

        # Figure caption
        self.figtext = self.fig.text(0.5, 0.07, self.plotFigText.get(), ha="center", wrap=True, fontsize=self.figtextFont.get())

        # Setting legend (later for toggling its visibility)
        if ax is not None: self.plot_legend = self.ax.legend()

        # Returning plot

        if ax is not None: 
            print("Data available, returning", plot)
            return plot

        else: 
            print("Data not available, returning", self.ax)
            return self.ax 

    def save_fig(self, event=None):

        print(self.location)

        if isfile(f'{self.location}/{self.name.get()}.png'):
            if askokcancel('Overwrite?', f'File: {self.name.get()}.png already present. \nDo you want to Overwrite the file?'):
                self.fig.savefig(f'{self.location}/{self.name.get()}.png')
                showinfo('SAVED', f'File: {self.name.get()}.png saved in directory: {self.location}')

        else:
            self.fig.savefig(f'{self.location}/{self.name.get()}.png')
            showinfo('SAVED', f'File: {self.name.get()}.png saved in directory: {self.location}')

        print(f'Filename saved: {self.name.get()}.png\nLocation: {self.location}\n')

# @profile
def main():

    widget = FELion_Tk("Filename")
    fig, canvas = widget.Figure()
    ax = widget.make_figure_layout(xdata=[1, 2, 3], ydata=[1, 2, 3], title="CD")
    widget.mainloop()

if __name__ == "__main__":
    main()