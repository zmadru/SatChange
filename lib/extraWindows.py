import datetime
import subprocess
from typing import Optional, Tuple, Union
import customtkinter as ctk
from tkinter import filedialog, simpledialog
import os, sys
import lib.fishnetdirs as fn
import lib.split as sp
import lib.cutImage as ci
import lib.zerosViability as zv
from tkinter import messagebox
from threading import Thread
from osgeo import gdal, ogr, osr
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
        self.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=1)
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
        
        
        self.outdirbtn = ctk.CTkButton(self, text="Select output directory", command=self.selectoutdir)
        self.outdirbtn.grid(row=3, column=0, padx=5, pady=5)
        self.outdirEntry = ctk.CTkTextbox(self, width=45, height=22)
        self.outdirEntry.insert(0.0, "No output directory selected")
        self.outdirEntry.configure(state="disabled")
        self.outdirEntry.grid(row=3, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.outfilenameEntry = ctk.CTkEntry(self, placeholder_text="Output filename", justify="center")
        self.outfilenameEntry.grid(row=4, column=1, padx=5, pady=5, sticky="we")        
        
        self.runbtn = ctk.CTkButton(self, text="Run", command=self.run)
        self.runbtn.grid(row=5, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Cancel", command=self.back)
        self.cancelbtn.grid(row=5, column=2, padx=5, pady=5)
        self.pb = ctk.CTkProgressBar(self, mode="determinate")
        self.pb.set(0)
        self.pb.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
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
        
    def selectoutdir(self):
        self.pathoutdir = filedialog.askdirectory(initialdir=os.path.dirname(__file__), title="Select the output directory")
        self.outdirEntry.configure(state="normal")
        self.outdirEntry.delete(0, "end")
        self.outdirEntry.insert(0, self.pathoutdir)
        self.outdirEntry.configure(state="disabled")
        
    def run(self):
        if self.pathraster and self.pathshp:
            filename = os.path.join(self.pathoutdir, self.outfilenameEntry.get())
            self.pb.start()
            self.runbtn.configure(state="disabled")
            self.cancelbtn.configure(state="disabled")
            thd = Thread(target=ci.cut, args=(self.pathraster, self.pathshp, filename))
            thd.start()
            
            while thd.is_alive() and ci.running:
                self.update()
                
            self.pb.stop()
            messagebox.showinfo("Satchange", f"Cut raster completed, the result {filename} has been saved")
            self.runbtn.configure(state="normal")
            self.cancelbtn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Please fill all the fields")
    
    def back(self):
        self.master.index()
        
class ZerosViability(ctk.CTkFrame):
    """Window to calculate the viability of the image, analyzing the zeros
    """
    file = ''
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.label = ctk.CTkLabel(self, text="Zeros viability", font=("Helvetica", 36, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.selectBtn = ctk.CTkButton(self, text="Select raster", command=self.selectraster)
        self.selectBtn.grid(row=1, column=0, padx=5, pady=5)
        self.rasterentry = ctk.CTkTextbox(self, width=45, height=22)
        self.rasterentry.insert(0.0, "No raster selected")
        self.rasterentry.configure(state="disabled")
        self.rasterentry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="we")
        
        self.iniband = ctk.CTkEntry(self, placeholder_text="Initial Band", justify="center")
        self.iniband.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.finband = ctk.CTkEntry(self, placeholder_text="End Band", justify="center")
        self.finband.grid(row=2, column=2, padx=5, pady=5, sticky="we")
        
        self.startbtn = ctk.CTkButton(self, text="Start", command=self.start)
        self.startbtn.grid(row=3, column=1, padx=5, pady=5)
        self.cancelbtn = ctk.CTkButton(self, text="Back", command=self.back)
        self.cancelbtn.grid(row=3, column=2, padx=5, pady=5)
        
        self.pblabel = ctk.CTkLabel(self, text="Progress", font=("Helvetica", 12, "bold"))
        self.pblabel.grid(row=4, column=0, padx=5, pady=5)
        self.pb = ctk.CTkProgressBar(self, mode="determinate")
        self.pb.set(0)
        self.pb.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        
    
    def selectraster(self):
        self.file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input raster", filetypes=(("Tiff files", "*.tif"), ("All files", "*.*")))
        self.rasterentry.configure(state="normal")
        self.rasterentry.delete(0.0, "end")
        self.rasterentry.insert(0.0, self.file)
        self.rasterentry.configure(state="disabled")
        
    def start(self):
        if self.file != '' and self.iniband.get() and self.finband.get():
            self.pb = ctk.CTkProgressBar(self, mode="indeterminate")
            self.pb.start()
            self.startbtn.configure(state="disabled")
            self.cancelbtn.configure(state="disabled")
            thd = Thread(target=zv.main, args=(self.file, 1, 100000))
            thd.start()
            self.pblabel.configure(text="Loading raster")
            while not zv.start:
                self.update()
                self.master.update()
            
            while zv.progress < 100:
                self.pblabel.configure(text=f"Progress: {int(zv.progress)}%")
                self.update()
                self.master.update()
            
            while zv.saving:
                self.pblabel.configure(text="Saving raster")
                self.update()
                self.master.update()
            
            self.pb.stop()
            messagebox.showinfo("Satchange", f"Zeros viability completed, created: {zv.output}")
            self.startbtn.configure(state="normal")
            self.cancelbtn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Please fill all the fields")
    
    def back(self):
        self.master.index()
        
        
class DownLoadImages(ctk.CTkFrame):
    """Window to download images from the internet,
    it uses the Google Earth Engine API"""
    
    def __init__(self, master, **kwargs):
        ctk.CTkFrame.__init__(self, master, **kwargs)
        self.master = master
        self.poligons = []
        self.markers = []
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        self.createWidgets()
        
    def createWidgets(self):
        self.nameLabel = ctk.CTkLabel(self, text="Download images", font=("Helvetica", 36, "bold"))
        self.nameLabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.openmapbtn = ctk.CTkButton(self, text="Open map", command=self.openmap)
        self.openmapbtn.grid(row=1, column=0, padx=5, pady=5)
        
        
    def openmap(self):
        res = messagebox.askyesno("Info", "Did you already authenticate? (The token expires after a week)")
        if not res:
            res = subprocess.call('start /wait python3 authenticate.py', shell=True)
            print(res)
        self.toplevel = ctk.CTkToplevel(self.master)
        self.toplevel.title("Map")
        self.toplevel.geometry("800x600")
        self.toplevel.resizable(0,0)
        self.toplevel.focus_set()
        self.toplevel.grid_columnconfigure((0,1,2,3), weight=1)
        self.toplevel.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.mapframe = ctk.CTkFrame(self.toplevel)
        self.mapframe.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.mapframe.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.mapframe.grid(row=0, column=1, padx=5, pady=5, sticky="nswe", columnspan=3, rowspan=5)
        
        self.configframe = ctk.CTkFrame(self.toplevel)
        self.configframe.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=1)
        self.configframe.grid_columnconfigure((0), weight=1)
        self.configframe.grid(row=0, column=0, padx=5, pady=5, sticky="nswe", columnspan=1, rowspan=5)
        self.coodinatesEntry = ctk.CTkEntry(self.configframe, placeholder_text="Coordinates (35.2115, -12.65)", justify="center")
        self.coodinatesEntry.grid(row=0, column=0, padx=5, pady=5, sticky="we")
        self.coordinatesbtn = ctk.CTkButton(self.configframe, text="Set coordinates", command=self.setcoordinates)
        self.coordinatesbtn.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        
        self.loadtshpbtn = ctk.CTkButton(self.configframe, text="Load shapefile", command=self.selectshpfile)
        self.loadtshpbtn.grid(row=2, column=0, padx=5, pady=5, sticky="we")
        
        self.drawgeometrybtn = ctk.CTkButton(self.configframe, text="Draw geometry", command=self.drawgeometry)
        self.drawgeometrybtn.grid(row=3, column=0, padx=5, pady=5, sticky="we")
        
        self.sensorselect = ctk.CTkOptionMenu(self.configframe, values=["Modis", "Sentinel 2", "Landsat 8"], state="readonly")
        self.sensorselect.grid(row=4, column=0, padx=5, pady=5, sticky="we")
        self.sensorselect.set("Modis")
        
        self.labelgeometrys= ctk.CTkLabel(self.configframe, text="Geometries")
        self.labelgeometrys.grid(row=5, column=0, padx=5, pady=5, sticky="nswe")
        self.poligonsframe = ScrollableLabelButtonFrame(self.configframe, command2=self.checkboxbehavior, command1=self.downloadshp, deletecomand=self.deletegeometry)
        self.poligonsframe.grid(row=6, column=0, padx=5, pady=5, sticky="nswe")
        
        self.dowloadbtn = ctk.CTkButton(self.configframe, text="Download", command=self.download)
        self.dowloadbtn.grid(row=7, column=0, padx=5, pady=5, sticky="we")
        
        self.map =  tkmap.TkinterMapView(self.mapframe, corner_radius=10)
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=20)  # google satellite
        self.map.grid(row=0, column=0, padx=5, pady=5, columnspan=5, rowspan=5, sticky="nswe")
        # default coordinates of the map Spain
        self.map.set_position(40.463667, -3.74922)
        self.map.set_zoom(6)
        self.map.add_right_click_menu_command(label="Add Marker", command=self.add_marker_event, pass_coords=True)
        self.mapframe.mainloop()
        
    
    def checkboxbehavior(self):
        print("Checkbox behavior", self.poligonsframe.get_checked_items())
        for poligon in self.poligons:
            # print(poligon)
            if poligon.name not in self.poligonsframe.get_checked_items():
                # print("Delete poligon:", poligon.name)
                poligon.delete()
            else:
                if not poligon.displayed:
                    aux = self.map.set_polygon(poligon.getcoords(), fill_color="grey", outline_color="black", border_width=2)
                    poligon.setreference(aux)
            self.map.update()
            
    def download(self):
        if len(self.poligons) == 0:
            messagebox.showerror("Error", "You must draw a geometry")
        elif len(self.poligonsframe.get_checked_items()) != 1:
            messagebox.showerror("Error", "You must select one geometry, just mark one checkbox and unmark the others")
        else:
            # ask the user for the filter dates of the images with a emergent window
            self.initialdate = simpledialog.askstring("Initial date", "Enter the initial date (yyyy-mm-dd)")
            self.finaldate = simpledialog.askstring("Final date", "Enter the final date (yyyy-mm-dd)")     
            # check if the dates are correct
            try:
                datetime.datetime.strptime(self.initialdate, '%Y-%m-%d')
                datetime.datetime.strptime(self.finaldate, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "The dates are not correct, please enter the dates in the format yyyy-mm-dd")
                return   

            if self.initialdate > self.finaldate:
                messagebox.showerror("Error", "The initial date must be before the final date")
                return
            
            # ask the user for the output directory
            outdir = filedialog.askdirectory(title='Select a directory to save the images')
            print("Download", outdir, self.sensorselect.get(), self.initialdate, self.finaldate)
            if self.sensorselect.get() == "Modis":
                product = "MODIS/061/MOD09Q1"
            elif self.sensorselect.get() == "Sentinel 2":
                product = "COPERNICUS/S2_SR_HARMONIZED"
            elif self.sensorselect.get() == "Landsat 8":
                product = "LANDSAT/LC08/C01/T1_SR"
            if outdir:
                # authentification and initialization of the earth engine                
                ee.Initialize()
                collection = ee.ImageCollection(product).filterDate(self.initialdate, self.finaldate)
                print(len(collection.getInfo()["features"]))
                res = messagebox.askokcancel("Info", f"You are going to download {len(collection.getInfo()['features'])} images")
                if not res:
                    return
                
                
    
    def deletegeometry(self, item):
        print("Delete geometry:", item)
        self.poligonsframe.remove_item(item)
        for polygon in self.poligons:
            if polygon.name == item:
                polygon.delete()
                self.poligons.remove(polygon)
            
    def add_marker_event(self, coords):
        print("Add marker:", coords)
        new_marker = self.map.set_marker(coords[0], coords[1], text=f'{len(self.markers)+1}', text_color="white")
        new_marker.data = coords
        self.markers.append(new_marker)
      
    def setcoordinates(self):
        self.coordinates = self.coodinatesEntry.get()
        if self.coordinates:
            x = float(self.coordinates.split(",")[0])
            y = float(self.coordinates.split(",")[1])
            self.map.set_position(x, y)
            
    def selectshpfile(self):
        self.pathshp = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Select the input shapefile", filetypes=(("Shapefile files", "*.shp"), ("All files", "*.*")))
        # load the shapefile in the map, getting the list of coordinates of the polygons
        shp = ogr.Open(self.pathshp)
        name, ext = os.path.splitext(os.path.basename(self.pathshp))
        layer = shp.GetLayer()
        shpcoords = []
        for feature in layer:
            geom = feature.GetGeometryRef()
            for i in range(geom.GetGeometryCount()):
                aux = geom.GetGeometryRef(i)
                if aux.GetPoints() is not None:
                    for point in aux.GetPoints():
                        point = (point[1], point[0])
                        shpcoords.append(point)
                else:
                    if aux.GetGeometryCount() > 0:
                        for aux2 in aux:
                            for point in aux2.GetPoints():
                                point = (point[1], point[0])
                                shpcoords.append(point)
            poligon = self.map.set_polygon(shpcoords, fill_color="grey", outline_color="black", border_width=2)
            self.map.set_position(geom.Centroid().GetPoint_2D()[1], geom.Centroid().GetPoint_2D()[0])
            self.map.set_zoom(12)
            aux = Poligon(name, shpcoords, poligon)
            self.poligons.append(aux)
            self.poligonsframe.add_item(name)
            
        
    def drawgeometry(self):
        if len(self.markers) >= 3:
            coordlist = []
            for marker in self.markers:
                coordlist.append(marker.data)
                marker.delete()
            # ask the user for the name of the poligon
            name = simpledialog.askstring("Name", "Enter the name of the poligon", parent=self.mapframe)
            poligon = self.map.set_polygon(coordlist, fill_color="grey", outline_color="black", border_width=2)
            aux = Poligon(name, coordlist, poligon)
            self.poligons.append(aux)
            self.markers = []
            self.poligonsframe.add_item(name)
        else:
            messagebox.showerror("Error", "You must add at least 3 markers")
            
    def downloadshp(self, item):
        print("Download shapefile:", item)
        for poligon in self.poligons:
            if poligon.name == item:
                self.map.set_position(poligon.coords[0][0], poligon.coords[0][1])
                self.map.set_zoom(11)
                outdir = filedialog.askdirectory(title='Select a directory to save the shapefile')
                name = os.path.join(outdir, item)
                driver = gdal.GetDriverByName('ESRI Shapefile')
                ds = driver.Create(f'{name}.shp', 0, 0, 0, gdal.GDT_Unknown)
                ds.CreateLayer(f'{item}', geom_type=ogr.wkbPolygon)
                layer = ds.GetLayer()
                feature = ogr.Feature(layer.GetLayerDefn())
                wkt = "POLYGON(("
                for coord in poligon.coords:
                    wkt += f'{coord[1]} {coord[0]},'
                wkt = wkt[:-1]
                wkt += "))"
                poly = ogr.CreateGeometryFromWkt(wkt)
                feature.SetGeometry(poly)
                layer.CreateFeature(feature)           
                # tell the user that the shapefile has been created
                messagebox.showinfo("Satchange", f"Shapefile {name}.shp created")
                return
        
        
class Poligon:
    def __init__(self, name, coords, poligon):
        self.name = name
        self.coords = coords
        self.mapreference = poligon
        self.displayed = True
        
    def delete(self):
        self.mapreference.delete()
        self.displayed = False
        
    def getcoords(self):
        return self.coords  
    
    def setreference(self, poligon):
        self.mapreference = poligon  
        self.displayed = True
    
    def __str__(self) -> str:
        return f'Poligon {self.name} with {self.coords}'
           
        
class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, command1=None, command2=None, deletecomand=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command1 = command1
        self.command2 = command2
        self.commandremove = deletecomand
        self.radiobutton_variable = ctk.StringVar()
        self.button_list = []
        self.check_list = []
        self.deletebtn_list = []

    def add_item(self, item, image=None):
        button = ctk.CTkButton(self, text="Download", width=100, height=24)
        deletebtn = ctk.CTkButton(self, text="X", fg_color="red", hover_color='dark red', width=10, height=24)
        check = ctk.CTkCheckBox(self, text=item, width=100, height=24)
        if self.command1 is not None:
            button.configure(command=lambda: self.command1(item))
        if self.command2 is not None:
            check.configure(command=lambda: self.command2())
        if self.commandremove is not None:
            deletebtn.configure(command=lambda: self.commandremove(item))
        check.grid(row=len(self.check_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        deletebtn.grid(row=len(self.button_list), column=2, pady=(0, 10), padx=5)
        check.select(True)
        self.deletebtn_list.append(deletebtn)
        self.button_list.append(button)
        self.check_list.append(check)

    def remove_item(self, item):
        for button, check, delete in zip(self.button_list, self.check_list, self.deletebtn_list):
            if item == check.cget("text"):
                button.destroy()
                check.destroy()
                delete.destroy()
                self.button_list.remove(button)
                self.check_list.remove(check)
                self.deletebtn_list.remove(delete)
                return
            
    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.check_list if checkbox.get() == 1]