import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd
import matplotlib.pyplot as plt

def lpb(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = lpb(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def hpb(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff, fs, order=5):
    b, a = hpb(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def calculate_ac_dc(signal, fs, cutoff=0.5):
    # Apply low-pass filter to get the DC component
    dc_component = lowpass_filter(signal, cutoff, fs)
    
    # Apply high-pass filter to get the AC component
    ac_component = highpass_filter(signal, cutoff, fs)
    
    return ac_component, dc_component

def acdc(red_signal, ir_signal):
    fs = 100  # Sampling frequency in Hz
    # Calculate AC and DC components
    red_ac, red_dc = calculate_ac_dc(red_signal, fs)
    ir_ac, ir_dc = calculate_ac_dc(ir_signal, fs)
    
    red_ac_mean = np.mean(np.abs(red_ac))
    red_dc_mean = np.mean(red_dc)
    ir_ac_mean = np.mean(np.abs(ir_ac))
    ir_dc_mean = np.mean(ir_dc)

    return red_ac_mean, red_dc_mean, ir_ac_mean, ir_dc_mean

if __name__ == "__main__":
    df = pd.read_csv("test_data.csv")
    red_signal = df['RED']
    ir_signal = df['IR']
    print(acdc(red_signal, ir_signal))