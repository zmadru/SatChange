import customtkinter as ctk
from tkinter import filedialog
import os, sys
import lib.fishnetdirs as fn
import lib.split as sp
from tkinter import messagebox
from threading import Thread
from osgeo import gdal
import numpy as np
import geemap, ee
import tkintermapview as tkmap

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
        
        self.outdirbtn = ctk.CTkButton(self, text="Output directory", command=self.outdir)
        self.outdirbtn.grid(row=2, column=0, padx=5, pady=5)
        self.outentry = ctk.CTkTextbox(self, width=45, height=22)
        self.outentry.insert(0.0, "No directory selected")
        self.outentry.configure(state="disabled")
        self.outentry.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.columslabel = ctk.CTkLabel(self, text="Columns")
        self.columslabel.grid(row=3, column=0, padx=5, pady=5)
        self.columsentry = ctk.CTkEntry(self, justify="center")
        self.columsentry.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        self.rowslabel = ctk.CTkLabel(self, text="Rows")
        self.rowslabel.grid(row=3, column=2, padx=5, pady=5)
        self.rowsentry = ctk.CTkEntry(self, justify="center")
        self.rowsentry.grid(row=3, column=3, padx=5, pady=5, sticky="we")
        
        self.runbtn = ctk.CTkButton(self, text="Run", command=self.run)
        self.runbtn.grid(row=4, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Cancel", command=self.back)
        self.cancelbtn.grid(row=4, column=3, padx=5, pady=5)        
        
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
            
    def outdir(self):
        self.dirout = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        if self.dirout:
            self.outentry.configure(state="normal")
            self.outentry.delete(0.0, "end")
            self.outentry.insert(0.0, self.dirout)
            self.outentry.configure(state="disabled")
            
        
    def run(self):
        shapename = self.shapenameentry.get()
        if shapename.split(".")[-1] != "shp":
            shapename = shapename+".shp"
        try:
            int(self.columsentry.get())
            int(self.rowsentry.get())
        except ValueError:
            messagebox.showerror("Error", "Columns and rows must be integers")
            return
        cols = int(self.columsentry.get())
        rows = int(self.rowsentry.get())
        if shapename and cols and rows and self.file:
            self.pb = ctk.CTkProgressBar(self, mode="indeterminate")
            self.pb.start()
            self.runbtn.configure(state="disabled")
            self.cancelbtn.configure(state="disabled")
            self.selectbtn.configure(state="disabled")
            self.shapenameentry.configure(state="disabled")
            self.columsentry.configure(state="disabled")
            self.rowsentry.configure(state="disabled")
            self.fileentry.configure(state="disabled")
            thd = Thread(target=fn.fishnetfile, args=(self.file, cols, rows, shapename, self.dirout))
            thd.start()
            
            while thd.is_alive():
                self.update()
                
            self.pb.stop()
            messagebox.showinfo("Satchange", "Fishnet completed, the result is next to the input file in the same folder")
            self.runbtn.configure(state="normal")
            self.cancelbtn.configure(state="normal")
            self.selectbtn.configure(state="normal")
            self.shapenameentry.configure(state="normal")
            self.columsentry.configure(state="normal")
            self.rowsentry.configure(state="normal")
        else:
            messagebox.showerror("Error", "Please fill all the fields")
    
    def back(self):
        self.master.index()
        
class CutTimeSerie(ctk.CTkFrame):
    """
    Class for the cut time serie window
    """
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.titlelabel = ctk.CTkLabel(self, text="Cut time serie", font=("Helvetica", 36, "bold"))
        self.titlelabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.selectbtn = ctk.CTkButton(self, text="Select file", command=self.select)
        self.selectbtn.grid(row=1, column=0, padx=5, pady=5)
        self.fileentry = ctk.CTkTextbox(self, width=45, height=22)
        self.fileentry.insert(0.0, "No file selected")
        self.fileentry.configure(state="disabled")
        self.fileentry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.nbanslabel = ctk.CTkLabel(self, text="Number of bands")
        self.nbanslabel.grid(row=2, column=0, padx=5, pady=5)
        self.nbansentry = ctk.CTkEntry(self, justify="center")
        self.nbansentry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.nbansentry.configure(state="disabled")
        
        self.bandcutentry = ctk.CTkEntry(self, justify="center", placeholder_text="Band to cut")
        self.bandcutentry.grid(row=2, column=2, padx=5, pady=5, sticky="we")
        self.bandcutentry.configure(state="disabled")
        
        self.runbtn = ctk.CTkButton(self, text="Run", command=self.run)
        self.runbtn.grid(row=3, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Cancel", command=self.back)
        self.cancelbtn.grid(row=3, column=2, padx=5, pady=5)
        
        self.pb = ctk.CTkProgressBar(self, mode="determinate")
        self.pb.set(0)
        self.pb.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
    
    def select(self):
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input file", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        raster = gdal.Open(self.file)
        if raster:
            nbands = raster.RasterCount
            self.bandcutentry.configure(state="normal")
            
        self.nbansentry.configure(state="normal")
        self.nbansentry.delete(0, "end")
        self.nbansentry.insert(0, nbands)
        self.nbansentry.configure(state="disabled")
        
        self.fileentry.configure(state="normal")
        self.fileentry.delete(0.0, "end")
        self.fileentry.insert(0.0, self.file)
        self.fileentry.configure(state="disabled")
        
    def run(self):
        if self.file and self.bandcutentry.get():
            try:
                int(self.bandcutentry.get())
            except ValueError:
                messagebox.showerror("Error", "Band to cut must be an integer")
                return
            self.pb = ctk.CTkProgressBar(self, mode="indeterminate")
            self.pb.start()
            self.runbtn.configure(state="disabled")
            self.cancelbtn.configure(state="disabled")
            self.selectbtn.configure(state="disabled")
            self.bandcutentry.configure(state="disabled")
            thd = Thread(target=sp.splitfile, args=(self.file, int(self.bandcutentry.get())))
            thd.start()
            
            while thd.is_alive():
                self.update()
                
            self.pb.stop()
            messagebox.showinfo("Satchange", "Cut time serie completed, the result is next to the input file in the same folder")
            self.runbtn.configure(state="normal")
            self.cancelbtn.configure(state="normal")
            self.selectbtn.configure(state="normal")
            self.bandcutentry.configure(state="normal")
        else:
            messagebox.showerror("Error", "Please fill all the fields")
            
    def back(self):
        self.master.index()
        
class CutRaster(ctk.CTkFrame):
    """
    Cut raster window
    """
    
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.titlelabel = ctk.CTkLabel(self, text="Cut raster", font=("Helvetica", 36, "bold"))
        self.titlelabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.selectrasterbtn = ctk.CTkButton(self, text="Select raster", command=self.selectraster)
        self.selectrasterbtn.grid(row=1, column=0, padx=5, pady=5)
        self.rasterentry = ctk.CTkTextbox(self, width=45, height=22)
        self.rasterentry.insert(0.0, "No raster selected")
        self.rasterentry.configure(state="disabled")
        self.rasterentry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.selectshpfilebtn = ctk.CTkButton(self, text="Select shapefile", command=self.selectshpfile)
        self.selectshpfilebtn.grid(row=2, column=0, padx=5, pady=5)
        self.shpfileentry = ctk.CTkTextbox(self, width=45, height=22)
        self.shpfileentry.insert(0.0, "No shapefile selected")
        self.shpfileentry.configure(state="disabled")
        self.shpfileentry.grid(row=2, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.runbtn = ctk.CTkButton(self, text="Run", command=self.run)
        self.runbtn.grid(row=3, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Cancel", command=self.back)
        self.cancelbtn.grid(row=3, column=2, padx=5, pady=5)
        self.pb = ctk.CTkProgressBar(self, mode="determinate")
        self.pb.set(0)
        self.pb.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
    def selectraster(self):
        self.pathraster = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input raster", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.rasterentry.configure(state="normal")
        self.rasterentry.delete(0.0, "end")
        self.rasterentry.insert(0.0, self.pathraster)
        self.rasterentry.configure(state="disabled")
        
    def selectshpfile(self):
        self.pathshp = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input shapefile", filetypes=(("Shapefile files", "*.shp"), ("All files", "*.*")))
        self.shpfileentry.configure(state="normal")
        self.shpfileentry.delete(0.0, "end")
        self.shpfileentry.insert(0.0, self.pathshp)
        self.shpfileentry.configure(state="disabled")
        
    def run(self):
        pass
    
    def back(self):
        self.master.index()
        
        
class DownLoadImages(ctk.CTkFrame):
    """Window to download images from the internet,
    it uses the Google Earth Engine API"""
    
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.nameLabel = ctk.CTkLabel(self, text="Download images", font=("Helvetica", 36, "bold"))
        self.nameLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.openmapbtn = ctk.CTkButton(self, text="Open map", command=self.openmap)
        self.openmapbtn.grid(row=1, column=0, padx=5, pady=5)
        
        
    def openmap(self):
        self.toplevel = ctk.CTkToplevel(self.master)
        self.toplevel.title("Map")
        self.toplevel.geometry("800x600")
        self.toplevel.resizable(0,0)
        self.toplevel.focus_set()
        self.mapframe = ctk.CTkFrame(self.toplevel)
        self.mapframe.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.mapframe.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        self.mapframe.pack(fill="both", expand=True)
        
        
        self.map =  tkmap.TkinterMapView(self.mapframe, corner_radius=15)
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
        self.map.grid(row=1, column=1, padx=5, pady=5, columnspan=4, rowspan=4, sticky="nswe")
        self.mapframe.mainloop()
       
        
        
        
        
        
        
    