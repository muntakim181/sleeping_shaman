import scipy
import numpy as np
import scipy.signal
from filterzx import *

class oxyHr:
    """A class that has two methodes to calculate the value of SpO2 and Heart Rate from patient PPG signal
        Methodes:
                hrcal to calculate the Heart Rate. Type help(hrcal) for more information.
                spo2  to calculate the Oxygen Saturation. Type help(spo2) for more information.
                """
    def __init__(self,name, age, distance = 60, height = None):
        """This is a constructor of oxyHr class.
        Attributes:
                    name     (str) : name of patient
                    age      (int) : age of the patient
                    height   (int) : PPG minimum height threshold
                    distance (int) : PPG signal peak distance"""
        
        self.name     = name
        self.age      = age
        self.distance = distance
        self.height   = height

    def hrcal(self, RED : list, sampleRate : int):
        """A methode that Returns a list and a float containing the values of the PPG peaks to plot and the heart rate
            Attributes:
                        RED        (list) : Sensor Red Data.
                        sampleRate (int)  : Sampling rate of the collected Data"""

        self.sampleRate = sampleRate
        self.red = RED
        hrArr = []

        data = highpass_filter(cutoff=0.5 , fs= sampleRate, order=5, data = self.red)

        y_red = np.array(data)                                                                      # creating numpy array to calculate fast
        peaks, dummy = scipy.signal.find_peaks(y_red, height = self.height, distance= self.distance)    # finding peaks using scipy signal 
        for i in range(1,len(peaks)):                                                                   # finding heart rate
            dist = peaks[i] - peaks[i-1]
            hr = (sampleRate/dist)*60
            hrArr.append(hr)                                                              
        return peaks, hrArr
    
    def spo2(self, RED, IR, sampleRate,  a = 120, b = 9):
        """A methode that returns a dictionary that contains all informations to plot PPG in a graph also the SpO2 value.
            Note: It returns only the indexs of peak points.

            Attributes:
                        RED     (list)  : Sensor Red Data.
                        IR      (list)  : Sensor IR Data.
                        a       (float) : Constant A of calibration. Default value of a is, a = 120.
                        b       (float) : Constant B of calibration. Default value of b is, b =   9.
                        methode (str)   : Methodes to find the AC component. Example : RMS, Valley Mean, Signal Mean

            Return Demo:
                        'ts'         : ts,
                        'red_raw'    : redy,
                        'ir_raw'     : iry,
                        'spo2'       : spo2,
                        'red_peaks'  : redPeaks,
                        'ir_peaks'   : irPeaks,
                        'red_valley' : redValley,
                        'ir_valley'  : irValley,
                        'pi'         : pi}"""
        
        self.red = RED
        self.ir = IR
        self.a = a
        self.b = b

        redy = np.array(self.red)                                                                               
        iry = np.array(self.ir)                                                                           

        red_ac, red_dc, ir_ac, ir_dc = acdc(redy, iry)
        pi = ((red_ac / red_dc) * 100) *20 
        ratio = (red_ac/red_dc)/(ir_ac/ir_dc)                                                                 
        spo2 = (self.a - self.b * ratio) - pi
        ts = np.linspace(0,  len(RED), len(RED))
        return {
                'ts'         : ts,
                'red_raw'    : redy,
                'ir_raw'     : iry,
                'spo2'       : spo2,
                'pi'         : pi}
    

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import scipy 

    df = pd.read_csv("SPO2_realtime/test_data.csv")
    red = df["RED"]
    ir = df["IR"]

    person = oxyHr("Muntakim", 24)
    pv, hr = person.hrcal(red,100)
    data = person.spo2(red, ir)
    print(np.mean(hr))

    plt.plot(red)
    plt.plot(ir)
    plt.plot(data['red_peaks'], red[data["red_peaks"]], 'o')
    plt.plot(data['red_valley'], red[data["red_valley"]], 'o')
    plt.plot(data['ir_peaks'], ir[data["ir_peaks"]], 'o')
    plt.plot(data['ir_valley'], ir[data["ir_valley"]], 'o')
    plt.axhline(np.mean(red[data["red_valley"]]))
    plt.axhline(np.mean(ir[data["ir_valley"]]))
    plt.show()