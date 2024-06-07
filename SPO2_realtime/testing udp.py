import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 12345

data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data.bind((UDP_IP, UDP_PORT))

while True:
    Raw_data, addr = data.recvfrom(1024)
    data_list = Raw_data.decode().split(",")
    print(Raw_data)
    data_list = []
