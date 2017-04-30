# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 07:02:38 2017

@author: Moses
"""

import matplotlib as plt
plt.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import array
import contextlib
import wave
import numpy as np

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename
import os

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
style.use("ggplot")

f2 = Figure(figsize=(7.5,4), dpi = 100)
b = f2.add_subplot(111)

f = Figure(figsize=(7.5,4),dpi=100)
#f = Figure(figsize=(5,2.5), dpi=100)
a = f.add_subplot(111) #1 by 1  only 1 chart
#b = f.add_subplot(111)

"""
Wave Variables
"""
numChannels   = 1                      # mono
sampleWidth   = 2                      # in bytes, a 16-bit short
SR            = 44100                  #  sample rate
MAX_AMP       = (2**(8*sampleWidth - 1) - 1)    #maximum amplitude is 2**15 - 1  = 32767
MIN_AMP       = -(2**(8*sampleWidth - 1))       #min amp is -2**15

"""
Global Variables
"""

filename = 'none'
xUnits = "Seconds"
yUnits = "Relative"
changes = False
Signal = []
changes2 = False
fr = 0
am = 0
phi = 0
dur = 0

"""
Inferface Function
"""
def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text = msg, font = NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    b1 = ttk.Button(popup, text = 'Okay', command = popup.destroy)
    b1.pack()
    popup.mainloop()
    

def changeScale(scale):
    global yUnits
    global changes
    global changes2
    yUnits = scale
    changes = not changes
    changes2 = not changes2
    
    
def changeTimeScale(scale):
    global xUnits
    global changes
    global changes2
    xUnits = scale
    changes = not changes
    changes2 = not changes2
    
def animate(i):
    left = 0
    right = -1
    minAmplitude = -(2**15 + 100)        # just to improve visibility of curve
    maxAmplitude = 2**15 + 300 
    if filename != 'none' and changes == True:
        X = readWaveFile(filename)
        if(xUnits == "Samples"):
            if(right == -1):
                right = len(X)
            T = range(left,right)
            Y = X[left:right]
        elif(xUnits == "Seconds"):
            if(right == -1):
                right = len(X)/44100
            T = np.arange(left, right, 1/44100)
            leftSampleNum = int(left*44100)
            Y = X[leftSampleNum:(leftSampleNum + len(T))]
        elif(xUnits == "Milliseconds"):
            if(right == -1):
                right = len(X)/44.1
            T = np.arange(left, right, 1/44.1)
            leftSampleNum = int(left*44.1)
            Y = X[leftSampleNum:(leftSampleNum + len(T))]
        if(yUnits == "Relative"):
            minAmplitude = -1.003            # just to improve visibility of curve
            maxAmplitude = 1.01
            Y = [x/32767 for x in Y]
    
        a.set_xlabel(xUnits)
        a.set_ylabel(yUnits + ' Amplitude')
        #a.set_ylim([minAmplitude,maxAmplitude])
        a.set_xlim([left, right])
        a.axhline(0, color='black')      # draw the 0 line in black
        a.clear()
        a.plot(T,Y)    
        title = "Display Signal, The Signal is: " + str(filename) + " ,xUnits: " + str(xUnits) + " ,yUnits:  " + str(yUnits)
        a.set_title(title)
        global changes
        changes = not changes
    else:
        pass
    
    
def createSignal_animate(i):
    left = 0
    right = -1
    minAmplitude = -(2**15 + 100)        # just to improve visibility of curve
    maxAmplitude = 2**15 + 300 
    if changes2 == True:
        X = Signal
        if(xUnits == "Samples"):
            if(right == -1):
                right = len(X)
            T = range(left,right)
            Y = X[left:right]
        elif(xUnits == "Seconds"):
            if(right == -1):
                right = len(X)/44100
            T = np.arange(left, right, 1/44100)
            leftSampleNum = int(left*44100)
            Y = X[leftSampleNum:(leftSampleNum + len(T))]
        elif(xUnits == "Milliseconds"):
            if(right == -1):
                right = len(X)/44.1
            T = np.arange(left, right, 1/44.1)
            leftSampleNum = int(left*44.1)
            Y = X[leftSampleNum:(leftSampleNum + len(T))]
        if(yUnits == "Relative"):
            minAmplitude = -1.003            # just to improve visibility of curve
            maxAmplitude = 1.01
            Y = [x/32767 for x in Y]
    
        b.set_xlabel(xUnits)
        b.set_ylabel(yUnits + ' Amplitude')
        #a.set_ylim([minAmplitude,maxAmplitude])
        b.set_xlim([left, right])
        b.axhline(0, color='black')      # draw the 0 line in black
        b.clear()
        b.plot(T,Y)    
        title = "Display Signal, The Signal is: "  
        b.set_title(title)
        global changes2
        changes2 = not changes2
    else:
        pass
            
    
def create(frequency,amplitude,phase,duration):
    global changes2
    global Signal
    X = createSineWave(frequency,amplitude,phase,duration)
    Signal = X
    changes2 = not changes2
    
    

"""
I/O Function
"""

def OpenFile():
    name = askopenfilename(initialdir="C:/Users/Moses/Desktop",
                           filetypes =(("Wave File", "*.wav"), ("All Files","*.*")),
                           title = "Choose a file."
                           )
    global filename
    global changes
    changes = not changes
    filename = name
    
    
def readWaveFile(infile,withParams=False,asNumpy=True):
    with contextlib.closing(wave.open(infile)) as f:
        params = f.getparams()
        frames = f.readframes(params[3])
        if(params[0] != 1):
            print("Warning in reading file: must be a mono file!")
        if(params[1] != 2):
            print("Warning in reading file: must be 16-bit sample type!")
        if(params[2] != 44100):
            print("Warning in reading file: must be 44100 sample rate!")
    if asNumpy:
        X = array.array('h', frames)
        X = np.array(X,dtype='int16')
    else:  
        X = array.array('h', frames)
    if withParams:
        return X,params
    else:
        return X
        
"""
Wave Functions
"""        
def createSineWave(frequency, amplitude, phase, duration):
    X = np.zeros(SR*duration)  
    for i in range(len(X)):           
            X[i] = MAX_AMP * amplitude * np.sin( 2 * np.pi * frequency * i / SR + phase)
    return X
    
    
class SeaofBTCapp(tk.Tk):
    ##args argument - any number or variables, open ended, you can pass anything
    ## kwargs are keyboard argument, passing through dictionary
    def __init__(self, *args, **kwargs):
        #container
        tk.Tk.__init__(self, *args, **kwargs)
        
        #tk.Tk.iconbitmap(self, default="favicon.ico")
        tk.Tk.wm_title(self,"CS591 Program - Display Signal")
        
        container = tk.Frame(self)
        # fill the entire space, expand: if there is any white space, expand if there is space
        container.pack(side='top', fill='both', expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0,weight=1)
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open File", 
                             command = OpenFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command = self.destroy)
        menubar.add_cascade(label="File",menu=filemenu)
        
        
        setting = tk.Menu(menubar, tearoff=1)
        setting.add_command(label = "Milliseconds",
                          command = lambda: changeTimeScale('Milliseconds'))
        setting.add_command(label = "Seconds",
                          command = lambda: changeTimeScale('Seconds'))
        setting.add_command(label = "Samples",
                  command = lambda: changeTimeScale('Samples'))
        
        setting.add_separator()
        setting.add_command(label = "Relative",
                          command = lambda: changeScale('Relative'))
        setting.add_command(label = "Absolute",
                  command = lambda: changeScale('Absolute'))       
                
        menubar.add_cascade(label="Additional Settings",menu=setting)
        
        
        
        
        
        tk.Tk.config(self, menu= menubar)
        
        
        self.frames = {}
        
        for F in (StartPage, WorkSpace, CreateSignal):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky = "nsew")
            
        #frame.grid(row=110,column=110,stickey='nsew')
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        #refering to all the frames in __init__
        frame = self.frames[cont]
        #raise it to the front
        frame.tkraise()
        
        
#def qf(param):
    #print(param)
    
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        #the parent is the seaofBTcapp
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text = 'CS591 WAVE APPLICATION - THIS PROGRAM IS ONLY FOR USE IN THE CS591 CLASS, PLEASE AGREE TO THE TERMS AND CONDITION OF THE APPLICATION', font = LARGE_FONT)
        #padding on the top and the bottom
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text ='Agree',
                           command= lambda: controller.show_frame(WorkSpace))
        button1.pack()
        
        button2 = ttk.Button(self, text ='Disagree',
                           command= controller.destroy)
        button2.pack()
        
        button3 = ttk.Button(self, text = 'CreateSignal',
                             command = lambda: controller.show_frame(CreateSignal))
        button3.pack()

        
class CreateSignal(tk.Frame):
    
    def __init__(self,parent,controller):
        
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = 'Create Signal', font = LARGE_FONT)
        label.grid(row = 0, pady=10, padx=10)
        
        label_1 = ttk.Label(self, text = "Please Type in the frequency, amplitude, phase, duration of the signal you want to create")
        label_1.grid(row=1)
        
        
        button1 = ttk.Button(self, text ='Back to Home',
                           command= lambda: controller.show_frame(StartPage))
        button1.grid(row = 2)
        
        
        type_in_frame = tk.Frame(self)
        type_in_frame.grid(row=3, pady = 10) 
        
        label_2 = ttk.Label(type_in_frame, text = "Frequency: ")
        label_2.grid(row = 0, column = 0)
        frequency_input = ttk.Entry(type_in_frame)
        frequency_input.insert(0,220)
        frequency_input.grid(row = 0, column = 1)
        frequency_input.focus_set()
        
        label_3 = ttk.Label(type_in_frame, text = "Amplitude: ")
        label_3.grid(row = 0, column = 2)
        amplitude_input = ttk.Entry(type_in_frame)
        amplitude_input.insert(0,1)
        amplitude_input.grid(row = 0, column = 3)
        amplitude_input.focus_set()
        
        label_4 = ttk.Label(type_in_frame, text = "Phase: ")
        label_4.grid(row = 0, column = 4)
        phase_input = ttk.Entry(type_in_frame)
        phase_input.insert(0,0)
        phase_input.grid(row = 0, column = 5)
        phase_input.focus_set()
        
        label_5 = ttk.Label(type_in_frame, text = "Duration: ")
        label_5.grid(row = 0, column = 6)
        duration_input = ttk.Entry(type_in_frame)
        duration_input.insert(0,0.1)
        duration_input.grid(row = 0, column = 7)
        duration_input.focus_set()
        
        
        
        toolbar_frame = tk.Frame(self) 
        toolbar_frame.grid(row=4,column=0,columnspan=10, pady = 30) 
        
        canvas = FigureCanvasTkAgg(f2, toolbar_frame)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        toolbar = NavigationToolbar2TkAgg(canvas, toolbar_frame)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        def callback():
            fr = frequency_input.get()
            am = amplitude_input.get()
            phi = phase_input.get()
            dur = duration_input.get()
            create(float(fr),float(am),float(phi),float(dur))

        button2 = ttk.Button(type_in_frame, text = 'Confirmed', 
                             command = callback)
        
        button2.grid(row =7, column = 3 )
        


        
        
class WorkSpace(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = 'WorkSpace', font = LARGE_FONT)
        label.pack(pady=10, padx=10)
        
        label_1 = ttk.Label(self, text = "Please Import the Wave File that needs to be analysis")
        label_1.pack(side = "top")
        
        button1 = ttk.Button(self, text ='Back to Home',
                           command= lambda: controller.show_frame(StartPage))
        button1.pack()
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        toolbar = NavigationToolbar2TkAgg(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
"""
class PageOne(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = 'Page 1', font = LARGE_FONT)
        label.pack(pady=10, padx=10)
        button1 = ttk.Button(self, text ='Back to Home',
                           command= lambda: controller.show_frame(StartPage))
        button1.pack()
        
        button2 = ttk.Button(self, text ='To Page 2',
                           command= lambda: controller.show_frame(PageTwo))
        button2.pack()
"""      



app = SeaofBTCapp()
app.geometry("1280x720")
ani = animation.FuncAnimation(f, animate, interval = 1000)
ani2 = animation.FuncAnimation(f2, createSignal_animate, interval = 1000)
app.mainloop()
