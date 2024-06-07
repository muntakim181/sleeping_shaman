import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from csv import writer
import threading
import queue
from biosppy.signals import ppg
import pandas as pd

from loggingg import logitsp, lograw
from esp32_udp import esp_udp
from oxyhr import oxyHr
from filterzx import *


class app():
    def __init__(self):
        # constants
        self.ip = '0.0.0.0'
        self.port = 12345
        self.fname = ''

        # Tkinter init
        self.root = tk.Tk()
        self.bg = tk.PhotoImage(file = "mainBGGray.png") 
        self.icon = tk.PhotoImage(file = "ghost.png")
        self.root.iconphoto(False, self.icon)
        self.root.tk.call('source', 'Azure-ttk-theme-main/azure.tcl')
        self.root.tk.call("set_theme", "dark")
        self.root.geometry("900x600")
        self.root.title('Sleeping Shaman')
        self.notebook = ttk.Notebook(self.root, padding=15)
        self.notebook.place(relx=0, rely=0, relheight=1, relwidth=1)

        # udp init
        self.udpobj = esp_udp(self.ip, self.port)
        self.obj = self.udpobj.letinit()

        # Obj init
        self.patient = oxyHr('muntakim', 23, distance=60)

        # Queue init
        self.plotirqueue = queue.Queue()
        self.reddataq = queue.Queue()
        self.irdataq = queue.Queue()
        self.exitqueue = queue.Queue()
        self.rawsaveq = queue.Queue()

        # Filter init
        self.b, self.a = hpb(cutoff=0.5, fs=100, order=5)

        # Plot init
        plt.style.use("dark_background")
        plt.tight_layout()
        

    def CollectFromUDP(self):
        irplotlist = []
        reddata = []
        irdata = []
        print("Buffer job started...")
        N = 10
        while True:
            red, ir = self.udpobj.get_data(self.obj)
            irplotlist.append(ir)
            reddata.append(red)
            irdata.append(ir)

            if not self.rawsaveq.empty():
                lograw(red, ir, f"{self.fname}_rawLog.csv")
            else:
                self.rawsaveq.queue.clear()
            if len(irplotlist) > 499:
                data = np.convolve(irplotlist, np.ones(N)/N, mode='valid')
                data = np.convolve(irplotlist, np.ones(N)/N, mode='valid')

                self.plotirqueue.put(data)
                irplotlist = irplotlist[18:-1]

            if len(reddata) > 599:
                m = np.convolve(reddata, np.ones(N)/N, mode='valid')
                n = np.convolve(irdata, np.ones(N)/N, mode='valid')
                self.reddataq.put(m)
                self.irdataq.put(n)
                reddata = []
                irdata = []

            if not self.exitqueue.empty():
                print("Thread 1 closed! ")
                break
    
    def onclose(self):
        self.exitqueue.put(True)
        plt.close()
        self.root.destroy()
        print('App Closed! ')
        exit()

    def fortab1(self):
        # Tab init
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text= "RTM")
        limg = tk.Label(self.tab1, image=self.bg)
        limg.place(relx=0,rely=0, relheight=1, relwidth=1)
        self.true_false = False
        
        def startcsv():
            self.fname = self.TextBox.get(1.0, "end-1c")
            with open(f"{self.fname}_rawLog.csv", 'a') as ll:
                writer_obj = writer(ll)
                writer_obj.writerow(['RED', 'IR'])

            with open(f'{self.fname}_spo2.csv', 'a') as ll:
                writer_obj = writer(ll)
                writer_obj.writerow(['SPO2', 'HR', 'PI'])
            self.true_false = True
            self.rawsaveq.put(True)
            print("Log started")
            

        def stopcsv():
            self.true_false = False
            self.rawsaveq.queue.clear()
            print("Log stoped")

        # Ploting
        self.fig, self.ax = plt.subplots(1,1)
        self.ax.axhline(y = 0.1, color = 'red', linestyle = '-')

        def eventloopz():
            # realtime plot
            if self.plotirqueue.empty():
                pass
            else:
                ir = self.plotirqueue.get()
                
                y = filtfilt(self.b, self.a, ir)
                self.ax.clear()
                self.ax.set_yticks([-2000, 2000])
                self.ax.plot(y, color='red')
                self.ax.set_xlabel('Time 3.5S')
                self.ax.set_ylabel('Amplitude')
                self.ax.set_title('PPG Signal')
                remcanvus.draw()

            # Real Time Data View
            if self.reddataq.empty():
                pass
            else:
                reddatas = self.reddataq.get()
                irdatas = self.irdataq.get()
                data = self.patient.hrcal(reddatas, 100)
                oxydata = self.patient.spo2(reddatas, irdatas, sampleRate=100, a = 115, b= 35)

                if self.true_false == True:
                    logitsp(oxydata, data, f'{self.fname}_spo2.csv')

                if np.mean(reddatas) > 8000:
                    self.lbl = tk.Label(self.tab1, background='#330000', text = f"bpmPR: {round(np.mean(data[1]), 2)}\n SpO2: {round((oxydata['spo2']),2)}\n PI: {round((oxydata['pi']),2)}\n Log Status: {self.true_false}") 
                else:
                    self.lbl = tk.Label(self.tab1, background='#330000', text = f"bpmPR: {0}\n SpO2: {0}\n PI: {0}\n ") 
                self.lbl.place(relx=0, rely=0.70, relheight=0.30, relwidth=0.5)
            self.root.after(10,eventloopz)


        # Label 1
        self.lbl = tk.Label(self.tab1, text = f"bpmPR: {0}\n SpO2: {0}\n PI: {0}\n Log Status: {self.true_false}", background='#330000')
        self.lbl.place(relx=0, rely=0.70, relheight=0.30, relwidth=0.5)

        # Label 2
        self.lbl2 = tk.Label(self.tab1, text = f'Enter File Name', background='#333300')
        self.lbl2.place(relx=52, rely=0.70, relheight=1, relwidth=1)

        # Text Box
        self.TextBox = tk.Text(self.tab1, background='#330000') 
        self.TextBox.place(relx=0.52, rely=0.75, relheight=0.05, relwidth=0.46)

        # Button 1
        self.StartButton = tk.Button(self.tab1, text ="Start Log",background="#330000" , command = startcsv)
        self.StartButton.place(relx=0.52, rely=0.85, relheight=0.06, relwidth=0.23)

        # Button 2
        self.StopButton = tk.Button(self.tab1, text ="Stop Log", background="#330000", command = stopcsv)
        self.StopButton.place(relx=0.75, rely=0.85, relheight=0.06, relwidth=0.23)

        # Canvus Plot Fig
        remcanvus = FigureCanvasTkAgg(self.fig, self.tab1)
        remcanvus.get_tk_widget().place(relx=0, rely=0, relheight=0.70, relwidth=1)
        eventloopz()

    def fortab2(self):
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text= "SpO2 TS")
        limg = tk.Label(self.tab2, image=self.bg)
        limg.place(x=0,y=0)

        self.fig2, self.ax2 = plt.subplots(2,1)
        self.ax2[0].set_xlabel('Time 3s/Step')
        self.ax2[0].set_ylabel('Amplitude %')
        self.ax2[0].set_title('SpO2 Time Serise')

        self.ax2[1].set_xlabel('Time 3s/Step')
        self.ax2[1].set_ylabel('BPM')
        self.ax2[1].set_title('Heart Rate Time Serise')

        def openfile():
            file_path = tk.filedialog.askopenfilename(parent=self.tab2, 
                                            title='Open file',
                                            initialdir="/home/asus/SPO2_realtime",
                                            filetypes=[("csv files", "*.csv")])
            
            df = pd.read_csv(file_path)
            self.ax2[0].clear()
            self.ax2[1].clear()

            self.ax2[0].set_xlabel('Time 3s/Step')
            self.ax2[0].set_ylabel('Amplitude %')
            self.ax2[0].set_title('SpO2 Time Serise')

            self.ax2[1].set_xlabel('Time 3s/Step')
            self.ax2[1].set_ylabel('BPM')
            self.ax2[1].set_title('Heart Rate Time Serise')
            
            self.ax2[0].plot(df['SPO2'])
            self.ax2[1].plot(df['HR'])

        loadcsv = tk.Button(self.tab2, text ="Load SpO2 CSV File", background="#330000", command = openfile)
        loadcsv.place(relx=0.0, rely=0.85, relheight=0.10, relwidth=1)
        
        spo2canvus = FigureCanvasTkAgg(self.fig2, self.tab2)
        spo2canvus.get_tk_widget().place(relx=0, rely=0, relheight=0.70, relwidth=1)
        spo2canvus.draw()

    def fortab3(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text= "Templet")
        limg = tk.Label(self.tab3, image=self.bg)
        limg.place(relx=0,rely=0)

        # Text Box
        TextBox2 = tk.Text(self.tab3, background='#330000') 
        TextBox2.place(relx=0.52, rely=0.75, relheight=0.05, relwidth=0.46)

        # Text Box
        TextBox3 = tk.Text(self.tab3, background='#330000') 
        TextBox3.place(relx=0.02, rely=0.75, relheight=0.05, relwidth=0.46)
        figu, axu = plt.subplots(1,1)
        axu.axhline(y = 0.1, color = 'red', linestyle = '-')
        canvu = FigureCanvasTkAgg(figu, self.tab3)
        canvu.get_tk_widget().place(relx=0, rely=0, relheight=0.70, relwidth=1)


        def openfile2():
            file_path2 = tk.filedialog.askopenfilename(parent=self.tab2, 
                                            title='Open file',
                                            initialdir="/home/asus/SPO2_realtime",
                                            filetypes=[("csv files", "*.csv")])
            

            t1 = int(TextBox3.get(1.0, "end-1c"))
            t2 = int(TextBox2.get(1.0, "end-1c"))
            print(t1, t2)

            df2 = pd.read_csv(file_path2)
            x = np.array(df2['RED'])
            ret = ppg.ppg(signal=x[t1:t2], sampling_rate=100)

            biocanvus = FigureCanvasTkAgg(ret['fig'], self.tab3)
            biocanvus.get_tk_widget().place(relx=0, rely=0, relheight=0.70, relwidth=1)
            biocanvus.draw()

        loadcsv = tk.Button(self.tab3, text ="Load CSV Raw File", background="#330000", command = openfile2)
        loadcsv.place(relx=0.0, rely=0.85, relheight=0.10, relwidth=1)
        
        # biocanvus = FigureCanvasTkAgg(ret['fig'], self.tab3)
        # biocanvus.get_tk_widget().place(relx=0, rely=0, relheight=0.70, relwidth=1)
        # biocanvus.draw()
        
    def mainfunc(self):
        datathread = threading.Thread(target=self.CollectFromUDP)
        datathread.start()
        self.fortab1()
        self.fortab2()
        self.fortab3()
        self.root.protocol("WM_DELETE_WINDOW", self.onclose)
        self.root.mainloop()

if __name__ == "__main__":
    appobj = app()
    appobj.mainfunc()