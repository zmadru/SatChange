import time
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog
from tkinter import *
# import tkintermapview as tmv
import os
from tkinter.messagebox import showerror, showinfo
import lib.stackIntFiles as stackInt
import lib.interpolacion as interpolacion
import lib.filtro_SGV1 as filtro_SGV1
import lib.indexes as indexes
import lib.ACF as ACF
from threading import Thread

"""
This class is the main class of the program, it is the GUI of the program
    Author: Diego Madruga Ramos
    version: 0.1
"""
# Global variables
dir_out: str = ""

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
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
        self.resizable(0, 0)
        self.geometry("685x350")
        self.create_widgets()
        self.indwin = IndexWindow(self)
        self.indwin.pack(expand=True, padx=10, pady=10, fill="both")
        self.stackwin = None
        self.intwin = None
        self.filtwin = None
        self.indexwin = None
        self.autowin = None
        self.newwin = None

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
        if not self.indwin.winfo_exists():
            self.indwin = IndexWindow(self)
            # center the window
            self.indwin.pack(expand=True, padx=10, pady=10, fill="both")

    def viewStack(self, solo = True):
        """
        Show the stack window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        try:
            self.indwin.destroy()
            self.stackwin.destroy()
            self.stackwin = StackWindow(self)
            self.stackwin.pack(expand=True, fill="both", padx=10, pady=10)
        except:
            self.stackwin = StackWindow(self)
            self.stackwin.pack(expand=True, fill="both", padx=10, pady=10)
        
        
    
    def interpolation(self, solo = True):
        """
        Show the interpolation window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        if solo:
            self.indwin.destroy()
        self.intwin = InterpolationWindow(self, solo)
        self.intwin.pack(expand=True, fill="both", padx=10, pady=10)

    def filter(self, solo = True):
        """
        Show the filter window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        if solo:
            self.indwin.destroy()
        self.filtwin = FilterWindow(self, solo)
        self.filtwin.pack(expand=True, fill="both", padx=10, pady=10)

    def indexes(self, solo = True):
        """
        Show the indexes window
        """
        if solo:
            self.indwin.destroy()
        self.indexwin = IndexesWindow(self, solo)
        self.indexwin.pack(expand=True, fill="both", padx=10, pady=10)
    
    def autocorrelation(self, solo = True):
        """
        Show the autocorrelation window
        """
        if solo:
            self.indwin.destroy()
        self.autowin = AcWindow(self, solo)
        self.autowin.pack(expand=True, fill="both", padx=10, pady=10)

    def newProcess(self):
        """
        Show the new process window
        """
        self.indwin.destroy()
        self.newwin = NewProcessWin(self)
        self.newwin.pack(expand=True, fill="both", padx=10, pady=10)
    
class IndexWindow(ctk.CTkFrame):
    """
    Index window class
    """

    def __init__(self, master):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.grid_rowconfigure(0, weight=7)
        self.grid_columnconfigure((0,1), weight=3)
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
        logo = logo.subsample(5)
        self.label1 = ctk.CTkLabel(self, image=logo)
        self.label1.image = logo
        self.label1.grid(row=0, column=0)
        img = tk.PhotoImage(file="img/convenio.png")
        self.labelimg = ctk.CTkLabel(self, image=img)
        self.labelimg.image = img
        self.labelimg.grid(row=0, column=1, columnspan=3, rowspan=1)
        self.label2 = ctk.CTkLabel(self, text="New single process", text_font=("Arial", 15))
        self.label2.grid(row=2, column=0, pady=10, padx=10, columnspan=2)
        self.separator2 = ttk.Separator(self, orient=VERTICAL)
        self.separator2.grid(row=2, column=2, rowspan=5, sticky="ns", pady=10, padx=10)
        self.label3 = ctk.CTkLabel(self, text="New complete process", text_font=("Arial", 15))
        self.label3.grid(row=2, column=3, pady=10, padx=10)
    
    def create_buttons(self):
        """
        Create the buttons of the index window
        """
        # New complete process
        self.button1 = ctk.CTkButton(self, text="Start", command=self.master.newProcess)
        self.button1.grid(row=3, column=3, pady=10, padx=10)
        self.button2 = ctk.CTkButton(self, text="Exit", command=self.master.destroy)
        self.button2.grid(row=5, column=3, pady=10, padx=10)

        # Individual process
        self.button3 = ctk.CTkButton(self, text="Stack", command=self.master.viewStack)
        self.button3.grid(row=3, column=0)
        self.button4 = ctk.CTkButton(self, text="Interpolation", command=self.master.interpolation)
        self.button4.grid(row=4, column=0)
        self.button5 = ctk.CTkButton(self, text="Autocorrelation", command=self.master.autocorrelation)
        self.button5.grid(row=5, column=0)
        self.button6 = ctk.CTkButton(self, text="Change detection")
        self.button6.grid(row=5, column=1)
        self.button7 = ctk.CTkButton(self, text="Filter", command=self.master.filter)
        self.button7.grid(row=3, column=1)
        self.button8 = ctk.CTkButton(self, text="Indexes", command=self.master.indexes)
        self.button8.grid(row=4, column=1)
    
  
class StackWindow(ctk.CTkFrame):
    """
    The stack window
    """
    solo: bool

    def __init__(self, master):
        """
        Constructor
        """
        super().__init__(master)
        # self.label1 = ctk.CTkLabel(self, text="Stack", text_font=("Arial", 25))
        # self.canvas = tk.Canvas(self,bg=self.label1['bg'], highlightthickness=0)
        # self.canvas.grid(row=0, column=0, columnspan=3, rowspan=7)
        self.grid_rowconfigure(0, weight=7)
        self.grid_columnconfigure((0,1), weight=3)
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
        self.label1 = ctk.CTkLabel(self, text="Stack", text_font=("Arial", 25))
        self.label1.grid(row=0, column=0)
        self.entryIn = ctk.CTkLabel(self, width=45, text="0 images selected" ,text_font=("Arial", 10))
        self.entryIn.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="w")

        self.entryOut = ctk.CTkTextbox(self, width=45, height=22, text_font=("Arial", 10))
        self.entryOut.insert("0.0", "Output directory not selected")
        self.entryOut.configure(state="disabled")
        self.entryOut.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="we") 

        self.nameLabel = ctk.CTkLabel(self, text="Stack name", text_font=("Arial", 10))
        self.nameLabel.grid(row=3, column=0, padx=5, pady=5)
        self.entryName = ctk.CTkEntry(self, width=22, text_font=("Arial", 10))
        self.entryName.grid(row=3, column=1, padx=5, pady=5, sticky="we", columnspan=1)
        self.label = ctk.CTkLabel(self, text=".tif", text_font=("Arial, 10"))
        self.label.grid(row=3, column=2, sticky="w")
        self.void = ctk.CTkLabel(self, text=" ")
        self.void.grid(row=7, column=0, sticky="w")
        


    def create_buttons(self):
        """
        Create the buttons of the GUI
        """
        self.buttonIn = ctk.CTkButton(self, text="Input Files", command=self.dirIn)
        self.buttonIn.grid(row=1, column=0, padx=5, pady=5)

        self.buttonOut = ctk.CTkButton(self, text="Output directory", command=self.dirOut)
        self.buttonOut.grid(row=2, column=0, padx=5, pady=5)

      
        self.buttonStart = ctk.CTkButton(self, text="Start", command=self.run)
        self.buttonStart.grid(row=4, column=1, padx=10, pady=10)
        self.buttonClose = ctk.CTkButton(self, text="Back", command=self.cancel)
        self.buttonClose.grid(row=4, column=2, padx=10, pady=10)

    def dirIn(self): 
        """
        Open a file dialog to select the input directory
        """
        self.in_files = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select the input files", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))  
        self.entryIn.configure(text=(str(len(self.in_files))+" selected"))

    def dirOut(self):
        """
        Open a file dialog to select the output directory
        """
        global dir_out

        self.out_dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output Directory") 
        self.entryOut.configure(state="normal")
        self.entryOut.insert("0.0", self.out_dir)
        self.entryOut.configure(state="disabled")
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
        else:
            self.pb = ctk.CTkProgressBar(self, orient=HORIZONTAL, mode='indeterminate', width=300)
            self.pb.grid(row=6, column=1, padx=5, pady=5, columnspan=2, sticky="we")
            # disable the buttons during the process
            self.buttonStart.configure(state="disabled")
            self.buttonClose.configure(state="disabled")
            self.pbLabel = ctk.CTkLabel(self, justify="right", text="0/0")
            self.pbLabel.grid(row=6, column=0, padx=15, pady=5)
            thd = Thread(target=stackInt.stack, args=(self.in_files, self.out_dir, name))
            thd.start()
            self.pb.start()

            while stackInt.start == False:
                self.master.update()

            
            while stackInt.progress/stackInt.total*100 < 100:
                self.pbLabel.configure(text=str(stackInt.progress)+"/"+str(stackInt.total)+" files processed")
                self.pbLabel.update()
                self.pb.update()
                self.update()

            self.pbLabel.configure(text=str("Saving..."))

            if thd.is_alive():
                thd.join()

            self.pb.grid_forget()
            self.pbLabel.grid_forget()
            
            if self.solo:
                showinfo("Satchange", "The process has finished, "+stackInt.out_file+" has been created")
            else:
                dir_out = stackInt.out_file      
            
            # Restore the buttons
            self.buttonStart.configure(state="active")
            self.buttonClose.configure(state="active")
            
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

class InterpolationWindow(ctk.CTkFrame):
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
        self.grid_rowconfigure((0,1), weight=4)
        self.grid_columnconfigure((0,1), weight=3)
        self.solo = solo
        self.create_widgets()
        if not solo:
            self.file = dir_out
            self.selectBtn.configure(state="disabled")
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
        self.label = ctk.CTkLabel(self, text="Interpolation", text_font=("Arial", 25))
        self.label.grid(row=0, column=0)
        self.fileLabel = ctk.CTkLabel(self, width=45, text_font=("Arial", 10), text="No file selected")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=10, pady=10)
        self.startBtn = ctk.CTkButton(self, text="Interpolate", command=self.run)
        self.startBtn.grid(row=3, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2, padx=10, pady=10)

    def selectMode(self):
        """
        Select the mode of the interpolation
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
        self.labelSelect.grid(row=2, column=0, padx=5, pady=5)
        self.modeSelect = ttk.Combobox(self, values=["linear", 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'], state="readonly")
        self.modeSelect.grid(row=2, column=1, padx=5, pady=5, sticky="we")
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
        else:
            self.thd = Thread(target=interpolacion.getFiltRaster, args=(self.file, self.modeSelect.get()))
            self.thd.start()
            self.pb = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate')
            self.percentajeLabel = ctk.CTkLabel(self, justify="right", text="0%")
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

class FilterWindow(ctk.CTkFrame):
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
        self.grid_rowconfigure(0, weight=4)
        self.grid_columnconfigure((0,1), weight=2)
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
        self.label = ctk.CTkLabel(self, text="Filter", text_font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.fileLabel = ctk.CTkLabel(self, width=45, text_font=("Arial", 10), text="No file selected")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.startBtn = ctk.CTkButton(self, text="Filter", command=self.run)
        self.startBtn.grid(row=3, column=1, sticky="w")
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2)

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
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
        else:
            self.thd = Thread(target=filtro_SGV1.getFiltRaster, args=(self.file, 3, 2))
            self.thd.start()
            self.pb = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate')
            self.percentajeLabel = ctk.CTkLabel(self, justify="right", text="0%")
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

class IndexesWindow(ctk.CTkFrame):
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
        self.grid_rowconfigure(0, weight=5)
        self.grid_columnconfigure((0,1), weight=2)
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
        self.label = ctk.CTkLabel(self, text="Indexes", text_font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.fileLabel = ctk.CTkLabel(self, width=45, text_font=("Arial", 10), text="No file selected")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")
        self.dirLabel = ctk.CTkLabel(self, width=45, text_font=("Arial", 10), text="No directory selected")
        self.dirLabel.grid(row=2, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select files", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.ourdirBtn = ctk.CTkButton(self, text="Output directory", command=self.selectDir)
        self.ourdirBtn.grid(row=2, column=0, padx=0, pady=5)
        self.startBtn = ctk.CTkButton(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=4, column=1, sticky="w")
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=2)

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
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
                self.update()
                self.pb.update()
            
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

class AcWindow(ctk.CTkFrame):
    """
    Class that contains the window to calculate the ac
    """
    def __init__(self, master, solo):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.grid_rowconfigure(0, weight=5)
        self.grid_columnconfigure((0,1), weight=2)
        self.solo = solo
        self.file = ""
        self.create_widgets()
        
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = ctk.CTkLabel(self, text="Autocorrelation", bg="white", text_font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        self.fileLabel = ctk.CTkLabel(self, width=45, text_font=("Arial", 10), text="No input file selected")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.startBtn = ctk.CTkButton(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=3, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2, padx=10, pady=10)

    def select(self):
        """
        Select the file to calculate the AC
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        if self.file != "":
            self.fileLabel.config(text=self.file)
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
        if self.file == "":
            showerror("Error", "No input file selected")
        else:
            self.thd = Thread(target=ACF.ACFtif, args=(self.file))
            self.thd.start()
            self.pb = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
            self.pb.grid(row=5, column=1, columnspan=3, padx=5, pady=5)
            self.percentajeLabel = ctk.CTkLabel(self, justify="right", text="0%")
            self.percentajeLabel.grid(row=5, column=0, padx=5, pady=5)
            self.startBtn.config(state="disabled")
            self.backBtn.config(state="disabled")

            while self.pb["value"] < 100:
                self.pb["value"] = ACF.progress
                self.percentajeLabel["text"] = f"{ACF.progress}%"
                self.update()
                self.pb.update()
            
            self.percentajeLabel["text"] = "100%"
            self.pb["value"] = 100
            
            showinfo("Satchange", "Saving the file, please wait. Dont close the window")
            while ACF.saving:
                self.update()
                self.master.update()
            
            self.startBtn.config(state="normal")
            self.backBtn.config(state="normal")
            showinfo("Satchange", f"File saved in {ACF.dir_out}")            


    
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


class NewProcessWin(ctk.CTkFrame):
    """
    Class that contains the window to start a new entire process
    """

    def __init__(self, master):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.grid_rowconfigure(0, weight=3)
        self.grid_columnconfigure((0,1), weight=3)
        self.create_widgets()
    
    def create_widgets(self):
        """
        Create the widgets of the window
        """
        self.create_label()
        self.create_buttons()
        # self.map = tmv.TkinterMapView(self)
        # self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
        # self.map.grid(row=0, column=0, columnspan=3, rowspan=4, sticky="nsew")

    def create_label(self):
        """
        Create the label of the window
        """
        self.label = ctk.CTkLabel(self, text="New Satchange process", text_font=("Arial", 25))
        self.label.grid(row=0, column=0, columnspan=2, sticky="w")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.startBtn = ctk.CTkButton(self, text="Start", command=self.run)
        self.startBtn.grid(row=4, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=2, padx=10, pady=10)

    def run(self):
        """
        Run the logic of the entire process
        """

    def back(self):
        """
        Back to the index window
        """
        self.destroy()
        self.master.index()

        
if __name__ == "__main__":
    app = App()
    app.mainloop()