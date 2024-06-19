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
        self.ack_received = True
        self.nack_count = 0

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, message):
        if not self.ack_received:
            self.nack_count += 1
            if self.nack_count >= 3:
                self.close()
                return False

        self.nack_count = 0
        self.ack_received = False
        sequence_id_str = f"{self.sequence_id:04d}"
        self.sequence_id += 1

        final_message = f"{self.sender_id},{self.receiver_id},{sequence_id_str},{message}"
        crc = self.message_handler.calculate_crc(final_message)
        final_message += f",{crc}"

        encoded_message = self.message_handler.encode_message(final_message, sequence_id_str)
        
        print(f"Sending encoded message: {encoded_message}")
        self.serial_manager.send(encoded_message)
        return True

    def receive_messages(self):
        while self.running:
            data = self.serial_manager.receive()
            if data:
                print(f"Received encoded data: {data}")
                valid, sender_id, receiver_id, sequence_id, message = self.message_handler.process_received_data(data)
                print(f"Decoded data: valid={valid}, sender_id={sender_id}, receiver_id={receiver_id}, sequence_id={sequence_id}, message={message}")
                if valid:
                    if message == "ACK":
                        self.ack_received = True
                        self.nack_count = 0
                    elif message == "NACK":
                        self.ack_received = False
                        self.nack_count += 1
                        if self.nack_count >= 3:
                            self.close()
                    elif sender_id == self.receiver_id and receiver_id == self.sender_id:
                        self.new_messages.put(message)
                        self.send_ack()
                else:
                    self.send_nack()

    def send_ack(self):
        ack_message = f"{self.receiver_id},{self.sender_id},{self.sequence_id:04d},ACK"
        crc = self.message_handler.calculate_crc(ack_message)
        ack_message += f",{crc}"
        encoded_ack = self.message_handler.encode_message(ack_message, f"{self.sequence_id:04d}")
        print(f"Sending ACK: {encoded_ack}")
        self.serial_manager.send(encoded_ack)

    def send_nack(self):
        nack_message = f"{self.receiver_id},{self.sender_id},{self.sequence_id:04d},NACK"
        crc = self.message_handler.calculate_crc(nack_message)
        nack_message += f",{crc}"
        encoded_nack = self.message_handler.encode_message(nack_message, f"{self.sequence_id:04d}")
        print(f"Sending NACK: {encoded_nack}")
        self.serial_manager.send(encoded_nack)

    def get_new_messages(self):
        messages = []
        while not self.new_messages.empty():
            messages.append(self.new_messages.get())
        return messages

    def close(self):
        self.running = False
        self.receive_thread.join()
        self.serial_manager.close()
