import serial
import threading

class SerialManager:
    def __init__(self, port):
        try:
            self.ser = serial.Serial(
                port, 
                9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.bAlive = True
            self.rxBuffer = ""
            self.rxList = []
            print(f"Successfully opened serial port {port}, let the communication begin!")
            
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            self.ser = None

    def send(self, data):
        if self.ser:
            print(f"Sending data: {data}")
            self.ser.write(data.encode() + b'\n')

    def receive_data(self):
        while self.bAlive:
            if self.ser.in_waiting:
                char_ch = self.ser.read().decode('utf-8')
                if char_ch == '\n':
                    complete_message = self.rxBuffer.strip()
                    self.rxBuffer = ""
                    self.rxList.append(complete_message)
                    print(f"Received complete message: {complete_message}")
                else:
                    self.rxBuffer += char_ch

    def receive(self):
        if self.rxList:
            return self.rxList.pop(0)
        return ""

    def close(self):
        if self.ser:
            self.bAlive = False
            self.receive_thread.join()
            self.ser.close()
