from csv import writer
import numpy as np

def logitsp(oxy, hr, fname):
    log_list = [oxy['spo2'], np.mean(hr[1]), oxy['pi']]
    with open(fname, 'a') as l:
        writer_obj = writer(l)
        writer_obj.writerow(log_list)
    l.close()

def lograw(red, ir, filename):
    with open(filename, 'a') as ll:
        writer_obj = writer(ll)
        writer_obj.writerow([red, ir])
    ll.close()