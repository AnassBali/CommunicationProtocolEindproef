import threading
import queue
from message import MessageHandler
from serial_manager import SerialManager

class CommunicationProtocol:
    def __init__(self, sender_id, receiver_id, serial_port):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.serial_manager = SerialManager(serial_port)
        self.message_handler = MessageHandler()

        self.new_messages = queue.Queue()
        self.running = True
        self.sequence_id = 0

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, message):
        sequence_id_str = f"{self.sequence_id:04d}"
        self.sequence_id += 1

        final_message = f"{self.sender_id},{self.receiver_id},{sequence_id_str},{message}"
        crc = self.message_handler.calculate_crc(final_message)
        final_message += f",{crc}"

        encoded_message = self.message_handler.encode_message(final_message, sequence_id_str)
        
        print(f"Sending message: {encoded_message}")
        self.serial_manager.send(encoded_message)
        return True

    def receive_messages(self):
        while self.running:
            data = self.serial_manager.receive()
            if data:
                print(f"Received data: {data}")
                valid, sender_id, receiver_id, sequence_id, message = self.message_handler.process_received_data(data)
                print(f"Processed data: valid={valid}, sender_id={sender_id}, receiver_id={receiver_id}, sequence_id={sequence_id}, message={message}")
                if valid and sender_id == self.other_user_id and receiver_id == self.user_id:
                    self.new_messages.put(message)

    def get_new_messages(self):
        messages = []
        while not self.new_messages.empty():
            messages.append(self.new_messages.get())
        return messages

    def close(self):
        self.running = False
        self.receive_thread.join()
        self.serial_manager.close()
