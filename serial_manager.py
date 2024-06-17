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
            self.rxList = []
            print(f"Successfully opened serial port {port}")
            
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            self.ser = None

    def send(self, data):
        if self.ser:
            print(f"SerialManager: Sending data: {data}")
            self.ser.write(data.encode() + b'\n')

    def receive_data(self):
        while self.bAlive:
            self.ser.rts = False
            char_ch = self.ser.read(1)
            if char_ch == b'':
                if len(self.rxList) > 0:
                    complete_message = ''.join(self.rxList)
                    print(f"SerialManager: Complete message received: {complete_message}")
                    self.rxList.clear()
                continue
            if self.bAlive:
                self.rxList.append(char_ch.decode('utf-8'))

    def receive(self):
        if len(self.rxList) > 0:
            complete_message = ''.join(self.rxList)
            self.rxList.clear()
            return complete_message
        return ""

    def close(self):
        if self.ser:
            self.bAlive = False
            self.receive_thread.join()
            self.ser.close()
