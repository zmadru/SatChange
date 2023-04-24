import customtkinter as ctk
from tkinter import filedialog
import os, sys
import lib.fishnet as fishnet
from tkinter import messagebox

class Fishnet(ctk.CTkFrame):
    """Fishnet window
    """
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.label = ctk.CTkLabel(self, text="Fishnet", font=("Helvetica", 36, "bold"))
        self.label.grid(row=0, column=0, sticky="nsew")
        
        self.selectbtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectbtn.grid(row=1, column=0, padx=5, pady=5)
        
        self.fileentry = ctk.CTkTextbox(self, width=45, height=22)
        self.fileentry.insert(0.0, "No file selected")
        self.fileentry.configure(state="disabled")
        self.fileentry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        self.shapenameentry = ctk.CTkEntry(self, justify="center", placeholder_text="Shapefile name")
        self.shapenameentry.grid(row=1, column=3, padx=5, pady=5, sticky="we")
        
        self.columslabel = ctk.CTkLabel(self, text="Columns")
        self.columslabel.grid(row=2, column=0, padx=5, pady=5)
        self.columsentry = ctk.CTkEntry(self, justify="center")
        self.columsentry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.rowslabel = ctk.CTkLabel(self, text="Rows")
        self.rowslabel.grid(row=2, column=2, padx=5, pady=5)
        self.rowsentry = ctk.CTkEntry(self, justify="center")
        self.rowsentry.grid(row=2, column=3, padx=5, pady=5, sticky="we")
        
        self.runbtn = ctk.CTkButton(self, text="Run", command=self.run)
        self.runbtn.grid(row=3, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Cancel", command=self.back)
        self.cancelbtn.grid(row=3, column=3, padx=5, pady=5)        
        
        self.pb = ctk.CTkProgressBar(self, mode="determinate")
        self.pb.set(0)
        self.pb.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
        
    def select(self):
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input file", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        if self.file:
            self.fileentry.configure(state="normal")
            self.fileentry.delete(0.0, "end")
            self.fileentry.insert(0.0, self.file)
            self.fileentry.configure(state="disabled")
        
    def run(self):
        shapename = self.shapenameentry.get()
        cols = self.columsentry.get()
        rows = self.rowsentry.get()
        file = self.fileentry.get(0.0, "end")
        if shapename and cols and rows and file:
            self.pb = ctk.CTkProgressBar(self, mode="indeterminate")
            self.pb.start()
            self.runbtn.configure(state="disabled")
            self.cancelbtn.configure(state="disabled")
            self.selectbtn.configure(state="disabled")
            self.shapenameentry.configure(state="disabled")
            self.columsentry.configure(state="disabled")
            self.rowsentry.configure(state="disabled")
            self.fileentry.configure(state="disabled")
            fishnet.fishnetfile(file,rows,cols,shapename,)
        else:
            messagebox.showerror("Error", "Please fill all the fields")
    
    def back(self):
        self.master.index()