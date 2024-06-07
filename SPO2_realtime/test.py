from oxyhr import oxyHr
from esp32_udp import esp_udp
import numpy as np
import matplotlib.pyplot as plt
import time

name = "muntakim"
age = 23
ip = '0.0.0.0'
port = 12345


def plotfunc():
    plt.ion()
    plt.style.use('Solarize_Light2')
    fig, ax = plt.subplots(2,1)
    ax[0].plot()
    plt.tight_layout()
    plt.pause(0.5)
    plt.show()
    
    return fig, ax

def RealTimePlot(buffer_size, pt):
    print("make_buffer function started....")
    patient_data = esp_udp(ip, port)
    obj = patient_data.letinit()

    redBuffer = np.array([])
    irBuffer  = np.array([])
    rtb       = np.array([])
    fig, ax = plotfunc()


    while True:
        start = time.time()
        for i in range(buffer_size+1):
            if len(redBuffer) == buffer_size:
                ax[0].clear()
                ax[1].clear()
                ax[0].set_title("RED Value", fontsize = 10)
                ax[1].set_title("IR Value", fontsize = 10)
                ax[0].plot(redBuffer - np.mean(redBuffer), color = "red")
                ax[1].plot(irBuffer - np.mean(irBuffer), color = 'purple')
                plt.tight_layout()
                fig.canvas.draw()
                plt.show()
                plt.pause(pt)
                
                redBuffer = []
                irBuffer  = []
                print("ploted ")

            else:
                redRaw, irRaw = patient_data.get_data(obj)
                redBuffer = np.append(redBuffer, redRaw)
                irBuffer  = np.append(irBuffer, irRaw)
        end = time.time()
        print(f"elapsed time: {end - start}")
        
RealTimePlot(300, 3)