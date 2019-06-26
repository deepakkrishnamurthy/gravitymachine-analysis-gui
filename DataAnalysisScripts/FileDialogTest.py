# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:47:29 2019

@author: Hongquan
"""

from tkinter import filedialog
import tkinter as tk

#root = tk.Tk()
filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("CSV files","*.csv"),("all files","*.*")))
print (filename)
