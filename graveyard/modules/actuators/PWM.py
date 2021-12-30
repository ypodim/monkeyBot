import socket

def sendPWM(pin, pulse):
    rawMsg = "%c%04d" % (48+pin, pulse)
    UDP_IP = "127.0.0.1"
    UDP_PORT = 8888
    # print(message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(rawMsg, (UDP_IP, UDP_PORT))


if __name__=="__main__":
    import sys
    pin = 21
    pulse = int(sys.argv[1])
    sendPWM(pin, pulse)