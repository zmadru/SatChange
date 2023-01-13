import sys
import time
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog
from tkinter import *
import os
from tkinter.messagebox import askyesno, showerror, showinfo
import lib.stackIntFiles as stackInt
import lib.interpolacion as interpolacion
import lib.filtro_SGV1 as filtro
import lib.indexes as indexes
import lib.ACF as ACF
import lib.changeDetector as changeDetector
from threading import Thread
import multiprocessing

"""
This class is the main class of the program, it is the GUI of the program
    Author: Diego Madruga Ramos
    version: 0.1
"""
# Global variables
dir_out: str = ""

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

error = open("error.log", "w")

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
        self.geometry("720x350")
        self.create_widgets()
        self.indwin = IndexWindow(self)
        self.indwin.pack(expand=True, padx=10, pady=10, fill="both")
        self.stackwin = StackWindow(self)
        self.intwin = InterpolationWindow(self)
        self.filtwin = FilterWindow(self)
        self.indexwin = IndexesWindow(self)
        self.autowin = AcWindow(self)
        self.changewin = ChangedetectorWin(self)
        self.newwin = NewProcessWin(self)
        # when the window end delete the error log file
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.file_menu.add_command(label="Change detection", command=self.changedetector)

        # add help entry
        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.about)
        self.help_menu.add_command(label="Log", command=self.log)
        self.help_menu.add_command(label="Exit", command=self.destroy)

    def on_closing(self):
        """
        When the window is closed, delete the error log file
        """
        error.close()
        os.remove("error.log")
        self.destroy()

    
    def about(self):
        """
        Show the about message
        """
        showinfo("About", "Satchange is a program to detect ground change using satellite images")


    def log(self):
        """
        Show the log console window
        """
        global error

        error.close()
        error = open("error.log", "r")
        self.logwin = ctk.CTkToplevel(self)
        self.logwin.title("Log")
        self.logwin.geometry("700x300")
        self.logwin.iconphoto(False, tk.PhotoImage(file="img\Windows_Terminal_Logo.png"))
        
        textbox = ctk.CTkTextbox(self.logwin)
        textbox.pack(expand=True, fill="both", padx=10, pady=10)
        textbox.insert("end", error.readlines())
        textbox.configure(state="disabled")
        sys.stderr = error


    def unpackAll(self):
        self.indwin.pack_forget()
        self.stackwin.pack_forget()
        self.intwin.pack_forget()
        self.filtwin.pack_forget()
        self.indexwin.pack_forget()
        self.autowin.pack_forget()
        self.changewin.pack_forget()
        self.newwin.pack_forget()
        

    def index(self):
        """
        Show the index window
        """
        self.unpackAll()
        self.indwin.pack(expand=True, fill="both", padx=10, pady=10)

    def viewStack(self, solo = True):
        """
        Show the stack window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        self.unpackAll()
        self.stackwin.pack(expand=True, fill="both", padx=10, pady=10)
        
        
    
    def interpolation(self, solo = True):
        """
        Show the interpolation window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        self.unpackAll()
        self.intwin.pack(expand=True, fill="both", padx=10, pady=10)

    def filter(self, solo = True):
        """
        Show the filter window

        Args:
            solo (bool, optional): Single ejecution flag. Defaults to True.
        """
        self.unpackAll()
        self.filtwin.pack(expand=True, fill="both", padx=10, pady=10)

    def indexes(self, solo = True):
        """
        Show the indexes window
        """
        self.unpackAll()
        self.indexwin.pack(expand=True, fill="both", padx=10, pady=10)
    
    def autocorrelation(self, solo = True):
        """
        Show the autocorrelation window
        """
        self.unpackAll()    
        self.autowin.pack(expand=True, fill="both", padx=10, pady=10)
    
    def changedetector(self):
        """
        Show the change detector window
        """
        self.unpackAll()
        self.changewin.pack(expand=True, fill="both", padx=10, pady=10)

    def newProcess(self):
        """
        Show the new process window
        """
        self.unpackAll()
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
        self.grid_rowconfigure((0,4), weight=7)
        self.grid_columnconfigure((0,1,2,3), weight=3)
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
        self.label1 = ctk.CTkLabel(self, image=logo, text="")
        self.label1['image'] = logo
        self.label1.grid(row=0, column=0, padx=10, pady=10)
        img = tk.PhotoImage(file="img/convenio.png")
        self.labelimg = ctk.CTkLabel(self, image=img, text="")
        self.labelimg.grid(row=0, column=1, columnspan=3, rowspan=1, padx=10, pady=10)
        self.label2 = ctk.CTkLabel(self, text="New single process",font=("Helvetica", 16, "bold"))
        self.label2.grid(row=2, column=0, pady=10, padx=10, columnspan=2)
        self.separator2 = ttk.Separator(self, orient=VERTICAL)
        self.separator2.grid(row=2, column=2, rowspan=5, sticky="ns", pady=10, padx=10)
        self.label3 = ctk.CTkLabel(self, text="New complete process",font=("Helvetica", 16, "bold"))
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
        self.button6 = ctk.CTkButton(self, text="Change detection", command=self.master.changedetector)
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
        self.grid_rowconfigure((0,3), weight=7)
        self.grid_columnconfigure((0,3), weight=3)
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
        self.label1 = ctk.CTkLabel(self, text="Stack",font=("Helvetica", 36, "bold"))
        self.label1.grid(row=0, column=0)
        self.entryIn = ctk.CTkTextbox(self, width=45, height=22)
        self.entryIn.insert("0.0", "0 files selected")
        self.entryIn.configure(state="disabled")
        self.entryIn.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="we")

        self.entryOut = ctk.CTkTextbox(self, width=45, height=22,)
        self.entryOut.insert("0.0", "Output directory not selected")
        self.entryOut.configure(state="disabled")
        self.entryOut.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="we") 

        self.nameLabel = ctk.CTkLabel(self, text="Stack name")
        self.nameLabel.grid(row=3, column=0, padx=5, pady=5)
        self.entryName = ctk.CTkEntry(self, width=22)
        self.entryName.grid(row=3, column=1, padx=5, pady=5, sticky="we", columnspan=1)
        self.label = ctk.CTkLabel(self, text=".tif")
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

        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=6, column=1, padx=5, pady=5, columnspan=2, sticky="ew")

    def dirIn(self): 
        """
        Open a file dialog to select the input directory
        """
        self.in_files = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select the input files", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))  
        self.entryIn.configure(state="normal")
        self.entryIn.delete("0.0", "end")
        self.entryIn.insert("0.0",(str(len(self.in_files))+" selected"))
        self.entryIn.configure(state="disabled")

    def dirOut(self):
        """
        Open a file dialog to select the output directory
        """
        global dir_out

        self.out_dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output Directory") 
        self.entryOut.configure(state="normal")
        self.entryOut.delete("0.0", "end")
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
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.pb.grid(row=6, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
            # disable the buttons during the process
            self.buttonStart.configure(state="disabled")
            self.buttonClose.configure(state="disabled")
            self.pbLabel = ctk.CTkLabel(self, text="0/0")
            self.pbLabel.grid(row=6, column=0, padx=15, pady=5)
            thd = Thread(target=stackInt.stack, args=(self.in_files, self.out_dir, name))
            thd.start()
            self.pb.start()

            while stackInt.start == False:
                self.master.update()

            
            while stackInt.progress/stackInt.total*100 < 100:
                self.pbLabel.configure(text=str(stackInt.progress)+"/"+str(stackInt.total)+" files processed")
                self.update()
                if not thd.is_alive():
                    self.error()
                    self.cancel()
                    break

            self.pbLabel.configure(text=str("Saving..."))
            self.pbLabel.update()

            while stackInt.saving:
                self.update()
                self.master.update()

            if thd.is_alive():
                thd.join()

            
            if self.solo:
                showinfo("Satchange", "The process has finished, "+stackInt.out_file+" has been created")
            else:
                dir_out = stackInt.out_file      
            
            # Restore the buttons
            self.buttonStart.configure(state="normal")
            self.buttonClose.configure(state="normal")
            self.pbLabel.destroy()
            self.pb.stop()

    def error(self):
        """
        Display an error message
        """
        showerror("Error", "The process has failed, please check the input files and the log")
        self.master.log()
            
    def cancel(self):
        self.master.index()

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
        self.grid_rowconfigure((0,1,2,3,4), weight=5)
        self.grid_columnconfigure((0,3), weight=3)
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
        self.label = ctk.CTkLabel(self, text="Interpolation", font=("Helvetica", 36, "bold"))
        self.label.grid(row=0, column=0, rowspan=1)
        self.fileLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.fileLabel.insert("0.0", "No file selected")
        self.fileLabel.configure(state="disabled")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="we", padx=10, pady=10)

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
        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky="ew")


    def selectMode(self):
        """
        Select the mode of the interpolation
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
        self.labelSelect.grid(row=2, column=0, padx=10, pady=10)
        self.modeSelect = ctk.CTkOptionMenu(self, values=["linear", 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'])
        self.modeSelect.grid(row=2, column=1, sticky="we", padx=10, pady=10)
        self.modeSelect.set("linear")
        
    def select(self):
        """
        Select the file to interpolate
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to interpolate", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.configure(state="normal")
        self.fileLabel.delete("0.0", "end")
        self.fileLabel.insert("0.0",self.file)
        self.fileLabel.configure(state="disabled")

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
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.percentajeLabel = ctk.CTkLabel(self, justify="right", text="0%")
            self.startBtn.configure(state='disabled')
            self.backBtn.configure(state='disabled')
            self.pb.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
            self.percentajeLabel.grid(row=4, column=0, padx=15, pady=5)
            self.pb.start()

            while interpolacion.progress < 100:
                self.percentajeLabel.configure(text=(str(interpolacion.progress).split(".")[0]+"%"))
                self.update()
                if not self.thd.is_alive():
                    self.error()
                    self.master.log()
                    break

            self.percentajeLabel.configure(text="Saving...")
            self.percentajeLabel.update()
            
            while(interpolacion.saving):
                self.update()
                self.master.update()

            if(self.thd.is_alive()):
                self.thd.join()  

            self.pb.stop()
            self.percentajeLabel.destroy()
            self.startBtn.configure(state='normal')
            self.backBtn.configure(state='normal')

            if self.solo:
                showinfo("Satchange", "The process has finished, "+interpolacion.out_file+" has been created")
            else:
                dir_out = interpolacion.out_file

    def error(self):
        """
        Show error message
        """
        showerror("Error", "The process has failed, check the log file")
        self.back()

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
        self.grid_rowconfigure((0,1,2,3,4), weight=4)
        self.grid_columnconfigure((0,3), weight=2)
        self.solo = solo
        self.create_widgets()
        self.file = ""
        
            
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
        self.label = ctk.CTkLabel(self, text="Filter", font=("Helvetica",36, "bold"))
        self.label.grid(row=0, column=0, columnspan=1)
        self.fileLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.fileLabel.insert("0.0", "No file selected")
        self.fileLabel.configure(state="disabled")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="we", padx=10, pady=10)

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=10, pady=10)
        self.startBtn = ctk.CTkButton(self, text="Filter", command=self.run)
        self.startBtn.grid(row=3, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2, padx=10, pady=10)
        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky="ew")

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
        self.labelSelect.grid(row=2, column=0, padx=5, pady=5)
        self.modeSelect = ctk.CTkOptionMenu(self, values=["SGV"], state="readonly")
        self.modeSelect.grid(row=2, column=1, padx=10, pady=10 )
        self.modeSelect.set("SGV")

    def select(self):
        """
        Select the file to filter
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.configure(state="normal")
        self.fileLabel.delete("0.0", "end")
        self.fileLabel.insert("0.0",self.file)
        self.fileLabel.configure(state="disabled")

    def filter(self):
        """
        Run process to filter
        """
        if not self.solo:
            global dir_out
        
        if self.file == "":
            showerror("Error", "You must select a file")
        else:
            self.thd = Thread(target=filtro.getFiltRaster, args=(self.file, 3, 2))
            self.thd.start()
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.percentajeLabel = ctk.CTkLabel(self, justify="right", text="0%")
            self.startBtn.configure(state='disabled')
            self.backBtn.configure(state='disabled')
            self.pb.grid(row=4, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
            self.percentajeLabel.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
            self.pb.start()

            while not filtro.start:
                self.update()
                self.master.update()

            while filtro.progress < 100:
                self.percentajeLabel.configure(text=str(filtro.progress).split(".")[0]+"%")
                self.update()
                if not self.thd.is_alive():
                    self.error()
                    self.master.log()
                    break
            
            self.percentajeLabel.configure(text="Saving...")
            self.percentajeLabel.update()            

            while(filtro.saving):
                self.update()
                self.master.update()
            
            if(self.thd.is_alive()):
                self.thd.join()

            self.pb.stop()
            self.percentajeLabel.destroy()
            self.startBtn.configure(state='normal')
            self.backBtn.configure(state='normal')
            
            if self.solo:
                showinfo("Satchange", "The process has finished, "+filtro.out_file+" has been created")
            else:
                dir_out = filtro.out_file   
            
    def error(self):
        """
        Show error message
        """
        showerror("Error", "The process has failed, check the log file")
        self.back()


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
        self.grid_rowconfigure((0,5), weight=5)
        self.grid_columnconfigure((0,3), weight=3)
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
        self.label = ctk.CTkLabel(self, text="Indexes", font=("Helvetica",36, "bold"))
        self.label.grid(row=0, column=0, columnspan=1)
        self.fileLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.fileLabel.insert("0.0", "No file selected")
        self.fileLabel.configure(state="disabled")
        self.fileLabel.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="we")
        self.dirLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.dirLabel.insert("0.0", "No directory selected")
        self.dirLabel.configure(state="disabled")
        self.dirLabel.grid(row=2, column=1, columnspan=2, sticky="ew", padx=10, pady=10)

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select files", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.ourdirBtn = ctk.CTkButton(self, text="Output directory", command=self.selectDir)
        self.ourdirBtn.grid(row=2, column=0, padx=0, pady=5)
        self.startBtn = ctk.CTkButton(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=2,padx=10, pady=10, sticky="ew")
        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=5, column=1, padx=5, pady=5, columnspan=2, sticky="ew")

    def selectMode(self):
        """
        Select the mode of the filter
        """
        self.labelSelect = ctk.CTkLabel(self, text="Select the mode ->")
        self.labelSelect.grid(row=3, column=0, padx=5, pady=5)
        self.modeSelect = ctk.CTkOptionMenu(self, values=indexes.indexes)
        self.modeSelect.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        self.modeSelect.set("NDVI")
        self.sensor = ctk.CTkOptionMenu(self, values=indexes.sensors)
        self.sensor.grid(row=3, column=2, padx=10, pady=10, sticky="ew")
        self.sensor.set("Modis")

    def select(self):
        """
        Select the file/files to filter
        """
        self.file = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.configure(state="normal")
        self.fileLabel.delete("0.0", "end")
        if len(self.file) == 1:
            self.fileLabel.insert("0.0",self.file[0])
        elif len(self.file) >= 2:
            self.fileLabel.insert("0.0",(str(len(self.file))+ " files selected"))
        else:
            self.fileLabel.insert("0.0","No input file selected")
        self.fileLabel.configure(state="disabled")

    def selectDir(self):
        """
        Select the output directory
        """
        self.dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        self.dirLabel.configure(state="normal")
        self.dirLabel.delete("0.0", "end")
        self.dirLabel.insert("0", self.dir)
        self.dirLabel.configure(state="disabled")
    
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
            
            self.pblabel = ctk.CTkLabel(self, text="0%")
            self.pblabel.grid(row=5, column=0, padx=5, pady=5)
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.pb.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
            self.startBtn.configure(state="disabled")
            self.backBtn.configure(state="disabled")
            self.pb.start()
            
            while indexes.progress < 100:
                self.pblabel.configure(text=str(indexes.progress).split(".")[0]+"%")
                self.update()
                if not self.thread.is_alive():
                    self.error()
                    self.master.log()
                    break
            
            
            if self.thread.is_alive():
                self.thread.join()
            
            self.pb.stop()
            self.pblabel.destroy()
            self.startBtn.configure(state="normal")
            self.backBtn.configure(state="normal")

            if self.solo:
                showinfo("Indexes", f"Indexes calculated and saved in {self.dir}")
            else:
                dir_out = self.dir
        else:
            showerror("Error", "No input file selected")

    def error(self):
        """
        Show error message
        """
        showerror("Error", "The process has failed, check the log file")
        self.back()
        

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
        self.master.index()

class AcWindow(ctk.CTkFrame):
    """
    Class that contains the window to calculate the ac
    """
    def __init__(self, master, solo=True):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.grid_rowconfigure((0,5), weight=5)
        self.grid_columnconfigure((0,3), weight=2)
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
        self.label = ctk.CTkLabel(self, text="Autocorrelation", font=("Helvetica", 36, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.fileLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.fileLabel.insert("0.0", "No input file selected")
        self.fileLabel.configure(state="disabled")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="we",padx=10, pady=10)

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.entry = ctk.CTkEntry(self, placeholder_text="Number of lags")
        self.entry.grid(row=3, column=0, padx=10, pady=10)
        self.startBtn = ctk.CTkButton(self, text="Calculate", command=self.run)
        self.startBtn.grid(row=3, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2, padx=10, pady=10)
        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    def select(self):
        """
        Select the file to calculate the AC
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to filter", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.configure(state="normal")
        self.fileLabel.delete("0.0", "end")
        if self.file != "":
            self.fileLabel.insert("0.0",self.file)
        else:
            self.fileLabel.insert("0.0","No input file selected")
        self.fileLabel.configure(state="disabled")

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
        elif self.entry.get() == "":
            showerror("Error", "No number of lags selected")
        elif not self.entry.get().isdigit():
            showerror("Error", "The number of lags must be a number")
        else:
            self.thd = Thread(target=ACF.ACFtif, args=(self.file, int(self.entry.get())))
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.pb.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
            self.percentajeLabel = ctk.CTkLabel(self, text="Loading...")
            self.percentajeLabel.grid(row=5, column=0, padx=5, pady=5)
            self.startBtn.configure(state="disabled")
            self.backBtn.configure(state="disabled")
            self.thd.start()
            self.pb.start()

            while not ACF.start:
                self.update()
                self.master.update()

            while ACF.progress < 100:
                self.percentajeLabel.configure(text=f"{ACF.progress}%")
                self.percentajeLabel.update()
                self.update()

            self.percentajeLabel.configure(text="Saving...")
            self.percentajeLabel.update()
            
            while ACF.saving:
                self.update()
                self.master.update()
            
            self.startBtn.configure(state="normal")
            self.backBtn.configure(state="normal")
            self.pb.stop()
            self.percentajeLabel.destroy()
            showinfo("Satchange", f"File saved in {ACF.dir_out}")            

    def error(self):
        """
        Show error message
        """
        showerror("Error", "The process has failed, check the log file")
        self.back()
    
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
        self.master.index()

class ChangedetectorWin(ctk.CTkFrame):
    """Class which contains the change detector given a autocorrelation file
    """
    def __init__(self, master, solo=True):
        """
        Constructor
        """
        super().__init__(master)
        self.master = master
        self.grid_rowconfigure((0,5), weight=5)
        self.grid_columnconfigure((0,3), weight=2)
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
        self.label = ctk.CTkLabel(self, text="Change Detector", font=("Helvetica", 36, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.fileLabel = ctk.CTkTextbox(self, width=45, height=22)
        self.fileLabel.insert("0.0", "No input file selected")
        self.fileLabel.configure(state="disabled")
        self.fileLabel.grid(row=1, column=1, columnspan=2, sticky="we",padx=10, pady=10)

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.selectBtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectBtn.grid(row=1, column=0, padx=0, pady=5)
        self.senEntry = ctk.CTkEntry(self, placeholder_text="Enter the sensitivity, 0.2 by default")
        self.senEntry.grid(row=2, column=1, padx=10, pady=10, columnspan=2, sticky="ew")
        self.startBtn = ctk.CTkButton(self, text="Calculate", command=self.changedetection)
        self.startBtn.grid(row=3, column=1, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=3, column=2, padx=10, pady=10)
        self.pb = ctk.CTkProgressBar(self, mode='determinate')
        self.pb.set(0)
        self.pb.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    def select(self):
        """
        Select the file to calculate the AC
        """
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the file to analize", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.fileLabel.configure(state="normal")
        self.fileLabel.delete("0.0", "end")
        if self.file != "":
            self.fileLabel.insert("0.0",self.file)
        else:
            self.fileLabel.insert("0.0","No input file selected")
        self.fileLabel.configure(state="disabled")

    def selectDir(self):
        """
        Select the output directory
        """
        self.dir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        self.dirLabel.config(text=self.dir)
    
    def changedetection(self):
        """
        Calculate the ac
        """
        if self.file == "":
            showerror("Error", "No input file selected")
        else:
            if self.senEntry.get() == "":
                sensitivity = 0.2
            else:
                try:
                    sensitivity = float(self.senEntry.get())
                except ValueError:
                    showerror("Error", "The sensitivity must be a number")
                    return
            self.thd = Thread(target=changeDetector.changeDetectorFile, args=(self.file, sensitivity))
            self.thd.start()
            self.pb = ctk.CTkProgressBar(self, mode='indeterminate')
            self.pb.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
            self.percentajeLabel = ctk.CTkLabel(self, text="Loading...")
            self.percentajeLabel.grid(row=5, column=0, padx=5, pady=5)
            self.startBtn.configure(state="disabled")
            self.backBtn.configure(state="disabled")
            self.pb.start()

            while not changeDetector.start:
                self.update()
                self.master.update()

            while changeDetector.progress < changeDetector.total:
                self.percentajeLabel.configure(text=f"{changeDetector.progress}/{changeDetector.total}")
                self.percentajeLabel.update()
                self.update()
                # if not self.thd.is_alive():
                #     self.error()
                #     self.master.log()
                #     break

            self.percentajeLabel.configure(text="Saving...")
            self.percentajeLabel.update()
            
            while changeDetector.saving:
                self.update()
                self.master.update()
            # if self.thd.is_alive():
            #     self.join()
            
            self.startBtn.configure(state="normal")
            self.backBtn.configure(state="normal")
            self.pb.stop()
            self.percentajeLabel.destroy()
            showinfo("Satchange", f"File saved in {changeDetector.out_file}")            

    def error(self):
        """
        Show error message
        """
        showerror("Error", "The process has failed, check the log file")
        self.back()
    
    
    def back(self):
        """
        Back to the index window
        """
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
        self.grid_rowconfigure((0,1,2,3), weight=3)
        self.grid_columnconfigure((0,1,2,3,4), weight=5)
        self.create_widgets()
        self.infiles = list()
        self.outdir = ""

    def createtoplevel(self):
        """
        Create the toplevel window
        """
        self.toplevel = ctk.CTkToplevel(self.master)
        self.toplevel.title("New Satchange process")
        self.toplevel.geometry("700x500")
        self.toplevel.resizable(False, False)
        self.toplevel.grid_rowconfigure((0,1), weight=1)
        self.toplevel.grid_columnconfigure((0,1,2,3), weight=3)

        # two frames, one for the input images and other for the configuration options
        self.inputFrame = ctk.CTkFrame(self.toplevel)
        self.inputFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", rowspan=2)
        self.inputFrame.grid_rowconfigure((0,1,2,3,4,5,6), weight=1)
        self.inputFrame.grid_columnconfigure((0), weight=1)
        self.create_inputwidgets()

        self.configFrame = ctk.CTkFrame(self.toplevel)
        self.configFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew", columnspan=3, rowspan=2)
        self.configFrame.grid_rowconfigure((0,1,2,3,4,5), weight=3)
        self.configFrame.grid_columnconfigure((0,1,2,3), weight=1)
        self.create_configwidgets()
        
    def create_inputwidgets(self):
        """
        Create the widgets of the input frame
        """
        self.inputLabel = ctk.CTkLabel(self.inputFrame, text="Input images", font=("Helvetica",16,"bold"))
        self.inputLabel.grid(row=0, column=0)

        self.infilesButton = ctk.CTkButton(self.inputFrame, text="Select input files", state="disabled", command=self.selectFiles)
        self.infilesButton.grid(row=1, column=0, padx=5, pady=5)
        self.outdirButton = ctk.CTkButton(self.inputFrame, text="Select output directory", command=self.selectDir)
        self.outdirButton.grid(row=2, column=0, padx=5, pady=5)
        self.rawSwitch = ctk.CTkSwitch(self.inputFrame, text="Raw images", command=self.switch_behaviour, onvalue=True, offvalue=False)
        self.rawSwitch.grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.procesedSwitch = ctk.CTkSwitch(self.inputFrame, text="Processed images", command=self.switch_behaviour, onvalue=True, offvalue=False)
        self.procesedSwitch.grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.stackSwitch = ctk.CTkSwitch(self.inputFrame, text="Stack image", command=self.switch_behaviour, onvalue=True, offvalue=False)
        self.stackSwitch.grid(row=5, column=0, padx=15, pady=5, sticky="w")
        self.nfilesLabel = ctk.CTkEntry(self.inputFrame)
        self.nfilesLabel.insert(0, "0 files selected")
        self.nfilesLabel.configure(state="disabled")
        self.nfilesLabel.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

        
    def create_configwidgets(self):
        """
        Create the widgets of the configuration frame
        """
        self.configLabel = ctk.CTkLabel(self.configFrame, text="Configuration", font=("Helvetica",16,"bold"))
        self.configLabel.grid(row=0, column=0)
        self.nextbutton = ctk.CTkButton(self.configFrame, text="Next", command=self.checkparams, state="disabled")
        self.nextbutton.grid(row=7, column=3, padx=5, pady=5)
        self.backbutton = ctk.CTkButton(self.configFrame, text="Cancel", command=self.cancel)
        self.backbutton.grid(row=7, column=0, padx=5, pady=5)

        # select the index and the sensor 
        self.indexLabel = ctk.CTkLabel(self.configFrame, text="Index configuration")
        self.indexLabel.grid(row=1, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.indexSelect = ctk.CTkOptionMenu(self.configFrame, values=indexes.indexes)
        self.indexSelect.configure(state="disabled")
        self.indexSelect.grid(row=1, column=2, padx=5, pady=5)
        self.indexSensor = ctk.CTkOptionMenu(self.configFrame, values=indexes.sensors)
        self.indexSensor.configure(state="disabled")
        self.indexSensor.grid(row=1, column=3, padx=5, pady=5)

        # stack configuration
        self.stackLabel = ctk.CTkLabel(self.configFrame, text="Stack configuration")
        self.stackLabel.grid(row=2, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.stackEntry = ctk.CTkEntry(self.configFrame, state="disabled")
        self.stackEntry.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        self.stackLabel2 = ctk.CTkLabel(self.configFrame, text=".tif")
        self.stackLabel2.grid(row=2, column=3, padx=5, pady=5, sticky="w") 

        # interpolation configuration
        self.interpLabel = ctk.CTkLabel(self.configFrame, text="Interpolation configuration")
        self.interpLabel.grid(row=3, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.modeInter = ctk.CTkOptionMenu(self.configFrame, values=["linear", 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous'])
        self.modeInter.grid(row=3, column=2, padx=5, pady=5)

        # filter configuration
        self.filterLabel = ctk.CTkLabel(self.configFrame, text="Filter configuration")
        self.filterLabel.grid(row=4, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.modeSelect = ctk.CTkOptionMenu(self.configFrame, values=["SGV"], state="readonly")
        self.modeSelect.grid(row=4, column=2, padx=5, pady=5)

        # autocorrelation configuration
        self.autolabel = ctk.CTkLabel(self.configFrame, text="Autocorrelation configuration")
        self.autolabel.grid(row=5, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.autoEntry = ctk.CTkEntry(self.configFrame, placeholder_text="Number of lags")
        self.autoEntry.grid(row=5, column=2, padx=5, pady=5, sticky="ew")

        # changedetection configuration sensivility
        self.senslabel = ctk.CTkLabel(self.configFrame, text="Sensibility")
        self.senslabel.grid(row=6, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        self.sensEntry = ctk.CTkEntry(self.configFrame, placeholder_text="Sensibility, default 0.2")
        self.sensEntry.grid(row=6, column=2, padx=5, pady=5, sticky="ew")



    def checkparams(self):
        """
        Check the parameters of the configuration before starting the process
        """
        if (self.rawSwitch.get() or self.procesedSwitch.get() or self.stackSwitch.get()) and len(self.infiles) == 0:
            showerror("Error", "No input selected")
        elif (self.rawSwitch.get() or self.procesedSwitch.get()) and self.stackEntry.get() == "":
            showerror("Error", "No stack name selected")
        elif self.outdir == "":
            showerror("Error", "No output directory selected")
        elif self.autoEntry.get() == "":
            showerror("Error", "No number of lags selected")
        elif self.autoEntry.get().isdecimal() == False:
            showerror("Error", "The number of lags must be a number")
        else:
            if self.sensEntry.get() == "":
                self.sens = 0.2
            else:
                try:
                   self.sens = float(self.sensEntry.get())
                except ValueError:
                    showerror("Error", "The sensibility must be a number")
            # ask for confirmation before starting the process
            if askyesno("Confirmation", "Are you sure you want to start the process?\nAll the files will be saved at:\n" + self.outdir):
                self.startprocess()
        

    def switch_behaviour(self):
        """
        Switch the behaviour of the buttons depending on the switch, and enable the button and disable the rest of the switches.
        Just one switch can be active at the same time
        """        
        if self.rawSwitch.get() == True:
            self.infilesButton.configure(state="normal")
            self.indexSelect.configure(state="normal")
            self.indexSensor.configure(state="normal")
            self.procesedSwitch.configure(state="disabled")
            self.stackSwitch.configure(state="disabled")
            self.stackEntry.configure(state="normal")
            self.stackEntry.configure(placeholder_text="Stack name")
            self.indexSelect.set("NDVI")
            self.indexSensor.set("Modis")
            self.nextbutton.configure(state="normal")
        elif self.procesedSwitch.get() == True:
            self.infilesButton.configure(state="normal")
            self.rawSwitch.configure(state="disabled")
            self.stackSwitch.configure(state="disabled")
            self.stackEntry.configure(state="normal")
            self.stackEntry.configure(placeholder_text="Stack name")
            self.nextbutton.configure(state="normal")

        elif self.stackSwitch.get() == True:
            self.infilesButton.configure(state="normal")
            self.infilesButton.configure(text="Select stack")
            self.rawSwitch.configure(state="disabled")
            self.procesedSwitch.configure(state="disabled")
            self.nextbutton.configure(state="normal")
            
        else:
            self.rawSwitch.configure(state="normal")
            self.procesedSwitch.configure(state="normal")
            self.stackSwitch.configure(state="normal")
            self.infilesButton.configure(state="disabled")
            self.indexSelect.set("")
            self.indexSensor.set("")
            self.indexSelect.configure(state="disabled")
            self.indexSensor.configure(state="disabled")
            self.stackEntry.configure(placeholder_text="")
            self.stackEntry.configure(state="disabled")
            self.nextbutton.configure(state="disabled")
            self.infilesButton.configure(text="Select input files")
            
    
    def selectFiles(self):
        """
        Select the input files depending of the option selected
        """
        text = ""
        if self.rawSwitch.get() == True:
            self.infiles = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select files the multiband images", filetypes=(("GeoTiff", "*.tif"), ("All files", "*.*")))
            text = str(len(self.infiles)) + " multiband images selected"
        elif self.procesedSwitch.get() == True:
            self.infiles = filedialog.askopenfilenames(initialdir=os.path.dirname(__file__), title="Select files the index calculated images", filetypes=(("GeoTiff", "*.tif"), ("All files", "*.*")))
            text = str(len(self.infiles)) + " index calculated images selected"
        elif self.stackSwitch.get() == True:
            self.infiles = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the stack", filetypes=(("GeoTiff", "*.tif"), ("All files", "*.*")))
            text = "1 stack image selected"

        self.nfilesLabel.configure(state="normal")
        self.nfilesLabel.delete(0, "end")
        self.nfilesLabel.insert(0, text)
        self.nfilesLabel.configure(state="disabled")

    def selectDir(self):
        """
        Select the output directory
        """
        self.outdir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        
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
        self.label = ctk.CTkLabel(self, text="New Satchange process", font=("Helvetica",32,"bold"))
        self.label.grid(row=0, column=0, columnspan=3, sticky="w")
        self.infolabel = ctk.CTkTextbox(self, font=("Helvetica",16))
        self.infolabel.insert("0.0", '''This is a new satchange process. 
        -To start, press the "Start" button, and a options window will appear. 
        -Then, you can select the configuration you want to use, and press "Next" to continue.''')
        self.infolabel.configure(state="disabled")
        self.infolabel.grid(row=1, column=0, columnspan=5, sticky="ew")

    def create_buttons(self):
        """
        Create the buttons of the window
        """
        self.startBtn = ctk.CTkButton(self, text="Start", command=self.run)
        self.startBtn.grid(row=4, column=0, padx=10, pady=10)
        self.backBtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.backBtn.grid(row=4, column=3, padx=10, pady=10)

    def startprocess(self):
        """
        Start the complete process
        """
        self.toplevel.withdraw()
        self.infolabel.grid_forget()
        self.startBtn.grid_forget()
        self.backBtn.grid_forget()

        self.infolabel = ctk.CTkTextbox(self, font=("Helvetica",16))
        self.infolabel.insert("0.0","Completed processes:")
        self.infolabel.configure(state="disabled")
        self.infolabel.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="ew")
        self.processlabel = ctk.CTkEntry(self, font=("Helvetica",16), state="disabled", justify=CENTER)
        self.processlabel.grid(row=1, column=2, columnspan=2, sticky="ew", padx=10, pady=10)
        self.abortBtn = ctk.CTkButton(self, text="Abort", command=self.abort)
        self.abortBtn.grid(row=2, column=2, padx=10, pady=10, columnspan=2)
        self.pb = ctk.CTkProgressBar(self, mode="indeterminate")
        self.pb.grid(row=3, column=1, columnspan=3, sticky="ew", padx=10, pady=10)
        self.percentagelabel = ctk.CTkLabel(self, text="0%")
        self.percentagelabel.grid(row=3, column=0, padx=10, pady=10)
        
        self.pb.start()
        if self.rawSwitch.get() == True:
            # 1 - Calculate indexes
            self.indexes()
            # 2 - Calculate the stack
            self.stack()
            # 3 - Interpolate the stack
            self.interpolate()
            # 4 - Filter the stack interpolated
            self.filter()
            # 5 - Calculate the autocorrelation
            self.autocorrelation()
            # 6 - Calculate the change
            self.changeDetection()
        elif self.procesedSwitch.get() == True:
            # 1 - Calculate the stack
            self.stack()
            # 2 - Interpolate the stack
            self.interpolate()
            # 3 - Filter the stack interpolated
            self.filter()
            # 4 - Calculate the autocorrelation
            self.autocorrelation()
            # 5 - Calculate the change
            self.changeDetection()
        elif self.stackSwitch.get() == True:
            # 1 - Interpolate the stack
            self.interpolate()
            # 2 - Filter the stack interpolated
            self.filter()
            # 3 - Calculate the autocorrelation
            self.autocorrelation()
            # 4 - Calculate the change
            self.changeDetection()
        
        

        self.pb.stop()

            

    def indexes(self):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Calculating indexes")
        self.processlabel.configure(state="disabled")

        thread = Thread(target=indexes.calculateIndex, args=(self.indexSelect.get(), self.infiles, self.outdir, self.indexSensor.get()))
        thread.start()
        while indexes.progress < 100:
            self.percentagelabel.configure(text=str((indexes.progress/len(self.infiles))*100).split('.')[0] + "%")
            self.update()
            if not thread.is_alive():
                self.error()
                self.back()
                break
            
        if thread.is_alive():
            thread.join()
            
        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nIndexes calculated")
        self.infolabel.configure(state="disabled")


    def stack(self, index="2.0"):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Stacking")
        self.processlabel.configure(state="disabled")

        name = self.stackEntry.get()
        thread = Thread(target=stackInt.stack, args=(self.infiles, self.outdir, name))
        thread.start()
        while stackInt.start == False:
            self.update()
            
        while stackInt.progress/len(self.infiles)*100 < 100:
            self.percentagelabel.configure(text=str((stackInt.progress/len(self.infiles))*100).split('.')[0] + "%")
            self.update()
            if not thread.is_alive():
                self.error()
                self.back()
                break
            
        self.percentagelabel.configure(text="Saving...")
        self.percentagelabel.update()
        while stackInt.saving == True:
            self.update()
            
        if thread.is_alive():
            thread.join()

        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nStack calculated")
        self.infolabel.configure(state="disabled")


    def interpolate(self, index="3.0"):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Interpolating")
        self.processlabel.configure(state="disabled")

        if self.stackSwitch.get() == True:
            thread = Thread(target=interpolacion.getFiltRaster, args=(self.infiles, self.modeInter.get()))
        else:
            thread = Thread(target=interpolacion.getFiltRaster, args=(stackInt.out_file, self.modeInter.get()))
        thread.start()

        while interpolacion.progress < 100:
            self.percentagelabel.configure(text=str(interpolacion.progress).split('.')[0] + "%")
            self.update()
            
        self.percentagelabel.configure(text="Saving...")
        self.percentagelabel.update()
        while interpolacion.saving == True:
            self.update()
            if not thread.is_alive():
                self.error()
                self.back()
                break

        if thread.is_alive():
            thread.join()
            
        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nStack interpolated")
        self.infolabel.configure(state="disabled")
    
    def filter(self, index="4.0"):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Filtering")
        self.processlabel.configure(state="disabled")

        thread = Thread(target=filtro.getFilter, args=(interpolacion.array, 3, 2, interpolacion.out_file, interpolacion.rt))
        # thread = Thread(target=filtro.getFiltRaster, args=(self.infiles, 3, 2))
        thread.start()

        while not filtro.start:
            self.update()
            self.master.update()
            
        while filtro.progress < 100:
            self.percentagelabel.configure(text=str(filtro.progress).split('.')[0] + "%")
            self.update()
            # if not thread.is_alive():
            #     self.error()
            #     self.back()
            #     break

        self.percentagelabel.configure(text="Saving...")
        self.percentagelabel.update()
        while filtro.saving == True:
            self.update()
            
        if thread.is_alive():
           thread.join()
            
        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nStack filtered")
        self.infolabel.configure(state="disabled")


    def autocorrelation(self, index="5.0"):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Calculating autocorrelation")
        self.processlabel.configure(state="disabled")

        print(filtro.out_file)
        # thread = Thread(target=ACF.ACFtif(filtro.out_file))
        lags = int(self.autoEntry.get())
        thread = Thread(target=ACF.ac, args=(filtro.out_array, filtro.out_file, filtro.rt, lags))
        thread.start()

        while not ACF.start:
            self.update()
            self.master.update()

        while ACF.progress < 100:
            self.percentagelabel.configure(text=str(ACF.progress).split('.')[0] + "%")
            self.update()
            
        self.percentagelabel.configure(text="Saving...")
        self.percentagelabel.update()
        while ACF.saving == True:
            self.update()
            self.master.update()
            # if not thread.is_alive():
            #     break        
            
        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nAutocorrelation calculated")
        self.infolabel.configure(state="disabled")

    def changeDetection(self):
        self.processlabel.configure(state="normal")
        self.processlabel.delete(0, "end")
        self.processlabel.insert(0, "Calculating change detection")
        self.processlabel.configure(state="disabled")

        thread = Thread(target=changeDetector.changeDetector, args=(ACF.out_array, ACF.out_file, ACF.rt, self.sens))
        thread.start()

        while not changeDetector.start:
            self.update()
            self.master.update()

        while changeDetector.progress < changeDetector.total:
            percentage = (changeDetector.progress/changeDetector.total)*100
            self.percentagelabel.configure(text=str(percentage).split(".")[0] + "%")
            self.update()
            
        self.percentagelabel.configure(text="Saving...")
        self.percentagelabel.update()
        while changeDetector.saving:
            self.update()
            self.master.update() 
        #     if not thread.is_alive():
        #         break          
            
        self.infolabel.configure(state="normal")
        self.infolabel.insert("end", "\nChange detection calculated")
        self.infolabel.configure(state="disabled")
        showinfo("Done", f"Process finished, check the output folder,{changeDetector.out_file} has been created")

    def error(self):
        showerror("Error", "An error has occurred. Please check the error log file")
        self.master.log()

    def run(self):
        """
        Run the logic of the entire process
        """
        self.createtoplevel()

    def cancel(self):
        """
        Cancel the process
        """
        self.toplevel.destroy()
    
    def abort(self):
        """
        Abort the process
        """
        if askyesno("Abort", "Are you sure you want to abort the process?"):
            self.master.destroy()

    def back(self):
        """
        Back to the index window
        """
        self.master.index()

        
if __name__ == "__main__":
    # redirect stderr to a file
    sys.stderr = error
    # Initialize the main window
    app = App()
    app.mainloop()