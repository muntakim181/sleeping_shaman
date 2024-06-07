import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 12345

class esp_udp():
    def __init__(self, UDP_IP, UDP_PORT):
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT

    def get_data(self, data):
        Raw_data, addr = data.recvfrom(1024)
        data_list = Raw_data.decode().split(",")
        redData = int(data_list[0])
        irData  = int(data_list[1])
        return redData, irData
    
    def letinit(self):
        data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data.bind((self.UDP_IP, self.UDP_PORT))
        return data
    
if __name__ == "__main__":
    d1 = esp_udp(UDP_IP, UDP_PORT)
    obj = d1.letinit()
    while True:
        print(d1.get_data(obj))

