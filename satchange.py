import time
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
import os
from tkinter.messagebox import showerror, showinfo
import lib.stackIntFiles as stackInt
import lib.interpolacion as interpolacion
import lib.filtro_SGV1 as filtro_SGV1
import lib.indexes as indexes
from threading import Thread

"""
This class is the main class of the program, it is the GUI of the program
    Author: Diego Madruga Ramos
    version: 0.1
"""
# Global variables
dir_out: str = ""


class App(tk.Tk):
    """
    App class
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.title("Satchange")
        self.iconphoto(True, tk.PhotoImage(file="img/satelliteicon.png"))
        self.config(bg="white")
        self.resizable(0, 0)
        self.geometry("700x350")
        self.create_widgets()
        self.indwin = indexWindow(self)
        self.indwin.grid(row=0, column=0, sticky="nsew")

    def create_widgets(self):
        """
        Create the widgets of the GUI
        """
        self.create_menu()

    def create_menu(self):
        """
        Create the menu of the GUI
        """
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)        

        # Home button in the menu
        self.menu.add_command(label="Home", command=self.index)       

        # File menu
        self.menu.add_cascade(label="Options", menu=self.file_menu)
        self.file_menu.add_command(label="Indexes", command=self.indexes)
        self.file_menu.add_command(label="Stack", command=self.viewStack)
        self.file_menu.add_command(label="Interpolation", command=self.interpolation)
        self.file_menu.add_command(label="Filter", command=self.filter)
        self.file_menu.add_command(label="Autocorrelation", command=self.autocorrelation)
        self.file_menu.add_command(label="Change detection")

        # add help entry
        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.about)
        self.help_menu.add_command(label="Exit", command=self.destroy)

    
    def about(self):
        """
        Show the about message
        """
        showinfo("About", "Satchange is a program to detect ground change using satellite images")

    def index(self):
        """
        Show the index window
        """
        self.indwin = indexWindow(self)
        self.indwin.grid(row=0, column=0, sticky="nsew")

    def viewStack(self, solo = True):
        """
        Show the stack window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        self.indwin.grid_forget()
        self.stwin = stackWindow(self)
        self.stwin.solo = solo
        self.stwin.grid(row=0, column=0, sticky="nsew")
    
    def interpolation(self, solo = True):
        """
        Show the interpolation window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        if solo:
            self.indwin.grid_forget()
        self.intwin = interpolationWindow(self, solo)
        self.intwin.grid(row=0, column=0, sticky="nsew")

    def filter(self, solo = True):
        """
        Show the filter window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        if solo:
            self.indwin.grid_forget()
        self.filtwin = filterWindow(self, solo)
        self.filtwin.grid(row=0, column=0, sticky="nsew")

    def indexes(self, solo = True):
        """
        Show the indexes window
        """
        if solo:
            self.indwin.grid_forget()
        self.indexwin = indexesWindow(self, solo)
        self.indexwin.grid(row=0, column=0, sticky="nsew")
    
    def autocorrelation(self, solo = True):
        """
        Show the autocorrelation window
        """
        if solo:
            self.indwin.grid_forget()
        self.autowin = acWindow(self, solo)
        self.autowin.grid(row=0, column=0, sticky="nsew")
    
class indexWindow(tk.Frame):
    """
    Index window class
    """

    def __init__(self, master):
        """
        Constructor
        """
        super().__init__(master, bg="white")
        self.master = master
        self.canvas = tk.Canvas(self, width=500, height=320, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=4, rowspan=7)
        self.create_widgets()

    def create_widgets(self):
        """
        Create the widgets of the index window
        """
        self.create_labels()
        self.create_buttons()

    def create_labels(self):
        """
        Create the labels of the index window
        """
        logo = tk.PhotoImage(file="img/Logo2.png")
        logo = logo.subsample(6)
        self.label1 = tk.Label(self, image=logo, bg="white")
        self.label1.image = logo
        self.label1.grid(row=0, column=0, pady=10, padx=10)
        img = tk.PhotoImage(file="img/convenio.png")
        self.labelimg = tk.Label(self, image=img)
        self.labelimg.image = img
        self.labelimg.grid(row=0, column=1, columnspan=3, rowspan=1)
        self.separator1 = ttk.Separator(self, orient=HORIZONTAL)
        self.separator1.grid(row=1, column=0, columnspan=4, sticky="ew", pady=10, padx=10)
        self.label2 = tk.Label(self, text="New single process", font=("Arial", 15), bg="white")
        self.label2.grid(row=2, column=0, pady=10, padx=10, columnspan=2)
        self.separator2 = ttk.Separator(self, orient=VERTICAL)
        self.separator2.grid(row=2, column=2, rowspan=5, sticky="ns")
        self.label3 = tk.Label(self, text="New complete process", font=("Arial", 15), bg="white")
        self.label3.grid(row=2, column=3, pady=10, padx=10)
    
    def create_buttons(self):
        """
        Create the buttons of the index window
        """
        # New complete process
        self.button1 = ttk.Button(self, text="Start", command=self.start)
        self.button1.grid(row=3, column=3, pady=10, padx=10)
        self.button2 = ttk.Button(self, text="Exit", command=self.master.destroy)
        self.button2.grid(row=5, column=3, pady=10, padx=10)

        # Individual process
        self.button3 = ttk.Button(self, text="Stack",width=20, command=self.master.viewStack)
        self.button3.grid(row=3, column=0)
        self.button4 = ttk.Button(self, text="Interpolation",width=20, command=self.master.interpolation)
        self.button4.grid(row=4, column=0)
        self.button5 = ttk.Button(self, text="Autocorrelation", width=20, command=self.master.autocorrelation)
        self.button5.grid(row=5, column=0)
        self.button6 = ttk.Button(self, text="Change detection", width=20)
        self.button6.grid(row=6, column=0)
        self.button7 = ttk.Button(self, text="Filter", command=self.master.filter)
        self.button7.grid(row=3, column=1, sticky="ew")
        self.button8 = ttk.Button(self, text="Indexes", command=self.master.indexes)
        self.button8.grid(row=4, column=1, sticky="ew")
    
    def start(self):
        """
        Start the program
        """
        self.master.viewStack(False)
        self.destroy()
  
class stackWindow(tk.Frame):
    """
    The stack window
    """
    solo: bool

    def __init__(self, master):
        """
        Constructor
        """
        super().__init__(master, bg="white")
        self.canvas = tk.Canvas(self, width=500, height=300, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=7)
        self.create_widgets()
        self.solo = True

    def create_widgets(self):
        """
        Create the widgets of the GUI
        """
        self.create_entry()
        self.create_buttons()

    def create_entry(self):
        """
        Create the entrys of the GUI
        """
        self.label1 = tk.Label(self, text="Stack", font=("Arial", 25), bg="white")
        self.label1.grid(row=0, column=0, sticky="ew")
        self.entryIn = ttk.Label(self, width=45, font=("Arial", 10))
        self.entryIn.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="w")

        self.entryOut = ttk.Label(self, width=45, font=("Arial", 10))
        self.entryOut.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="w")

        self.nameLabel = tk.Label(self, text="Stack name", font=("Arial", 10), bg="white")
        self.nameLabel.grid(row=3, column=0, padx=5, pady=5)
        self.entryName = ttk.Entry(self, width=22, font=("Arial", 10))
        self.entryName.grid(row=3, column=1, padx=5, pady=5, sticky="w", columnspan=2)
        self.label = tk.Label(self, text=".tif", bg="white", font=("Arial, 10"))
        self.label.grid(row=3, column=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the GUI
        """
        self.buttonIn = ttk.Button(self, text="Input Files", command=self.dirIn)
        self.buttonIn.grid(row=1, column=0, padx=5, pady=5)

        self.buttonOut = ttk.Button(self, text="Output directory", command=self.dirOut)
        self.buttonOut.grid(row=2, column=0, padx=5, pady=5)

      
        self.buttonStart = ttk.Button(self, text="Start", command=self.run)
        self.buttonStart.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.buttonClose = ttk.Button(self, text="Back", command=self.cancel)
        self.buttonClose.grid(row=4, column=2, padx=5, pady=5, sticky="w")

    def dirIn(self): 
        """
        Open a file dialog to select the input directory
        """
        self.in_files = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select the input files", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))  
        self.entryIn.config(text=(str(len(self.in_files))+" selected"))

    def dirOut(self):
        """
        Open a file dialog to select the output directory
        """
        global dir_out

        self.out_dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output Directory") 
        self.entryOut.config(text=self.out_dir)
        dir_out = self.out_dir

    def stack(self):
        """
        Stack the images
        """
        if not self.solo:
            global dir_out
        
        name = self.entryName.get()

        if len(self.in_files) == 0 or self.out_dir == "" or name == "":
            showerror("Error", "All fields must be filled")
            return
        else:
            self.pb = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate')
            self.pb.grid(row=6, column=1, padx=5, pady=5, columnspan=2, sticky="w")
            # disable the buttons during the process
            self.buttonStart.config(state="disabled")
            self.buttonClose.config(state="disabled")
            self.pbLabel = ttk.Label(self, justify="right", text="0/0",background="white")
            self.pbLabel.grid(row=6, column=0, padx=15, pady=5, sticky="e")
            thd = Thread(target=stackInt.stack, args=(self.in_files, self.out_dir, name))
            thd.start()

            while stackInt.start == False:
                self.master.update()

            while self.pb['value'] < 100:
                self.pb['value'] = stackInt.progress/stackInt.total*100
                self.pbLabel['text'] = str(stackInt.progress)+"/"+str(stackInt.total)+" files processed"
                self.pb.update()
                self.update()
        
            self.pbLabel['text'] = str(stackInt.progress)+"/"+str(stackInt.total)+" files processed"

            if thd.is_alive():
                thd.join()

            if self.solo:
                showinfo("Satchange", "The process has finished, "+stackInt.out_file+" has been created")
            else:
                dir_out = stackInt.out_file      
            
            # Restore the buttons
            self.buttonStart.config(state="active")
            self.buttonClose.config(state="active")
            
    def cancel(self):
        self.master.index()
        self.destroy()

    def run(self):
        """
        Run process to change between windows automatically
        """
        if self.solo:
            self.stack()
        else:
            self.stack()
            # Change to the next window
            self.master.interpolation(False)
            self.destroy()            

class interpolationWindow(tk.Frame):
    """
    Interpolation window
    """
    solo: bool
    def __init__(self, master, solo=True):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.config(bg="white")
        self.canvas = tk.Canvas(self, width=475, height=300, bg="white",border=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan= 4)
        self.solo = solo
        self.create_widgets()
        if not solo:
            self.file = dir_out
            self.selectBtn.config(state="disabled")
            self.fileLabel.config(text=self.file)
            
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()
        self.selectMode()

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = tk.Label(self, text="Interpolation", bg="white", font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2)
        self.fileLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ttk.Button(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.startBtn = ttk.Button(self, text="Interpolate", command=self.run)
        self.startBtn.grid(row=3, column=1, sticky="w")
        self.backBtn = ttk.Button(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2)

    def selectMode(self):
        """
        Select the mode of the interpolation
        """
        self.labelSelect = ttk.Label(self, text="Select the mode ->", background="white")
        self.labelSelect.grid(row=2, column=0, padx=5, pady=5)
        self.modeSelect = ttk.Combobox(self, values=["linear", 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'], state="readonly")
        self.modeSelect.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.modeSelect.current(0)
        
    def select(self):
        """
        Select the file to interpolate
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to interpolate", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.config(text=self.file)

    def interpolate(self):
        """
        Run process to interpolate
        """
        if not self.solo:
            global dir_out

        if self.file == "":
            showerror("Error", "You must select a file")
            return
        else:
            self.thd = Thread(target=interpolacion.getFiltRaster, args=(self.file, self.modeSelect.get()))
            self.thd.start()
            self.pb = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate')
            self.percentajeLabel = ttk.Label(self, justify="right", text="0%",background="white")
            self.modeSelect.grid_forget()
            self.labelSelect.grid_forget()
            self.startBtn.grid_forget()
            self.pb.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="w")
            self.percentajeLabel.grid(row=2, column=0, padx=15, pady=5, sticky="e")

            while self.pb['value'] < 100:
                self.pb['value'] = interpolacion.progress
                self.percentajeLabel['text'] = str(interpolacion.progress).split(".")[0]+"%"
                self.pb.update()
                self.update()

            self.percentajeLabel['text'] = str(interpolacion.progress)+"%"
            self.pb['value'] = 100
            self.startBtn.grid(row=3, column=1, sticky="w")

            showinfo("Satchange", "Saving the file, please wait. Dont close the window")
            while(interpolacion.saving):
                self.update()
                self.master.update()

            if(self.thd.is_alive()):
                self.thd.join()               
            
            if self.solo:
                showinfo("Satchange", "The process has finished, "+interpolacion.out_file+" has been created")
            else:
                dir_out = interpolacion.out_file

    def run(self):
        """
        Run process to change between windows automatically
        """
        if self.solo:
            self.interpolate()
        else:
            self.interpolate()
            # TODO Change to the next window
            self.destroy()
       
    def back(self):
        """
        Back to the index window
        """
        self.destroy()
        self.master.index()

class filterWindow(tk.Frame):
    """
    Filter window
    """
    solo: bool
    def __init__(self, master, solo=True):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.config(bg="white")
        self.canvas = tk.Canvas(self, width=475, height=300, bg="white",border=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan= 4)
        self.solo = solo
        self.create_widgets()
        self.file = ""
        if not solo:
            self.file = dir_out
            self.selectBtn.config(state="disabled")
            self.fileLabel.config(text=self.file)
            
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()
        self.selectMode()

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = tk.Label(self, text="Filter", bg="white", font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.fileLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ttk.Button(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.startBtn = ttk.Button(self, text="Filter", command=self.run)
        self.startBtn.grid(row=3, column=1, sticky="w")
        self.backBtn = ttk.Button(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2)

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ttk.Label(self, text="Select the mode ->", background="white")
        self.labelSelect.grid(row=2, column=0, padx=5, pady=5)
        self.modeSelect = ttk.Combobox(self, values=["SGV"], state="readonly")
        self.modeSelect.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.modeSelect.current(0)

    def select(self):
        """
        Select the file to filter
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.config(text=self.file)

    def filter(self):
        """
        Run process to filter
        """
        if not self.solo:
            global dir_out
        
        if self.file == "":
            showerror("Error", "You must select a file")
            return
        else:
            self.thd = Thread(target=filtro_SGV1.getFiltRaster, args=(self.file, 3, 2))
            self.thd.start()
            self.pb = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate')
            self.percentajeLabel = ttk.Label(self, justify="right", text="0%",background="white")
            self.modeSelect.grid_forget()
            self.labelSelect.grid_forget()
            self.startBtn.grid_forget()
            self.pb.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="w")
            self.percentajeLabel.grid(row=2, column=0, padx=15, pady=5, sticky="e")

            while self.pb['value'] < 100:
                self.pb['value'] = filtro_SGV1.progress
                self.percentajeLabel['text'] = str(filtro_SGV1.progress).split(".")[0]+"%"
                self.pb.update()
                self.update()
            
            self.percentajeLabel['text'] = str(filtro_SGV1.progress)+"%"
            self.pb['value'] = 100
            self.startBtn.grid(row=3, column=1, sticky="w")

            showinfo("Satchange", "Saving the file, please wait. Dont close the window")
            while(filtro_SGV1.saving):
                self.update()
                self.master.update()
            
            if(self.thd.is_alive()):
                self.thd.join()
            
            if self.solo:
                showinfo("Satchange", "The process has finished, "+filtro_SGV1.out_file+" has been created")
            else:
                dir_out = filtro_SGV1.out_file   


    def run(self):
        """
        Run the filter secuence calling filter
        """
        if self.solo:
            self.filter()
        else:
            self.filter()
            # TODO Change to the next window
            self.destroy()

    def back(self):
        """
        Back to the index window
        """
        self.destroy()
        self.master.index()

class indexesWindow(tk.Frame):
    """
    Indexes window
    """
    solo: bool
    def __init__(self, master, solo=True):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.config(bg="white")
        self.canvas = tk.Canvas(self, width=475, height=300, bg="white",border=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=6)
        self.solo = solo
        self.create_widgets()
        if not solo:
            self.file = dir_out
            self.selectBtn.config(state="disabled")
            self.fileLabel.config(text=self.file)
            
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()
        self.selectMode()

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = tk.Label(self, text="Indexes", bg="white", font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.fileLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")
        self.dirLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.dirLabel.grid(row=2, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ttk.Button(self, text="Select files", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.ourdirBtn = ttk.Button(self, text="Output directory", command=self.selectDir)
        self.ourdirBtn.grid(row=2, column=0, padx=0, pady=5)
        self.startBtn = ttk.Button(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=4, column=1, sticky="w")
        self.backBtn = ttk.Button(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=2)

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ttk.Label(self, text="Select the mode ->", background="white")
        self.labelSelect.grid(row=3, column=0, padx=5, pady=5)
        self.modeSelect = ttk.Combobox(self, values=["NDVI"], state="readonly")
        self.modeSelect.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.modeSelect.current(0)
        self.sensor = ttk.Combobox(self, values=["Modis", "Sentinel 2 (10m)", "Sentinel 2 (20m)", "Sentinel 2 (60m)", "AVHRR"], state="readonly")
        self.sensor.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.sensor.current(0)

    def select(self):
        """
        Select the file/files to filter
        """
        self.file = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        if len(self.file) == 1:
            self.fileLabel.config(text=self.file[0])
        elif len(self.file) >= 2:
            self.fileLabel.config(text=(str(len(self.file))+ " files selected"))
        else:
            self.fileLabel.config(text="No input file selected")

    def selectDir(self):
        """
        Select the output directory
        """
        self.dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        self.dirLabel.config(text=self.dir)
    
    def indexes(self):
        """
        Calculate the indexes selected
        """
        if not self.solo:
            global dir_out

        if len(self.file) >= 1:
            # start a thead to calculate the indexes and show the progress
            self.thread = Thread(target=indexes.calculateIndex,args=(self.modeSelect.get(), self.file, self.dir, self.sensor.get()))
            self.thread.start()
            while indexes.start == False:
                self.master.update()
            self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
            self.progress.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
            
            while self.progress["value"] < 100:
                self.progress["value"] = indexes.progress
                self.master.update()
            
            if self.thread.is_alive():
                self.thread.join()
            
            if self.solo:
                showinfo("Indexes", f"Indexes calculated and saved in {self.dir}")
            else:
                dir_out = self.dir
        else:
            showerror("Error", "No input file selected")

    def run(self):
        """
        Run the filter secuence calling filter
        """
        if self.solo:
            self.indexes()
        else:
            self.indexes()
            # TODO call the next window
            self.destroy()
    
    def back(self):
        """
        Back to the index window
        """
        self.destroy()
        self.master.index()

class acWindow(tk.Frame):
    """
    Class that contains the window to calculate the ac
    """
    def __init__(self, master, solo):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.config(bg="white")
        self.canvas = tk.Canvas(self, width=475, height=300, bg="white",border=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=6)
        self.solo = solo
        self.create_widgets()
        
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()
        self.selectMode()

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = tk.Label(self, text="AC", bg="white", font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.fileLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")
        self.dirLabel = ttk.Label(self, width=45, font=("Arial", 10))
        self.dirLabel.grid(row=2, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ttk.Button(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.ourdirBtn = ttk.Button(self, text="Output directory", command=self.selectDir)
        self.ourdirBtn.grid(row=2, column=0, padx=0, pady=5)
        self.startBtn = ttk.Button(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=4, column=1, sticky="w")
        self.backBtn = ttk.Button(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=2)

    def select(self):
        """
        Select the file to calculate the AC
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        if len(self.file) == 1:
            self.fileLabel.config(text=self.file[0])
        else:
            self.fileLabel.config(text="No input file selected")

    def selectDir(self):
        """
        Select the output directory
        """
        self.dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        self.dirLabel.config(text=self.dir)
    
    def autocorrelation(self):
        """
        Calculate the ac
        """
    
    def run(self):
        """
        Run the filter secuence calling filter
        """
        if self.solo:
            self.autocorrelation()
        else:
            self.autocorrelation()
            # TODO call the next window
            self.destroy()
    
    def back(self):
        """
        Back to the index window
        """
        self.destroy()
        self.master.index()

        
if __name__ == "__main__":
    app = App()
    app.mainloop()