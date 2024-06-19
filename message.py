import binascii

class MessageHandler:

    def calculate_crc(self, data):
        crc = binascii.crc32(data.encode())
        return crc & 0xFFFFFFFF

    def verify_crc(self, data, received_crc):
        calculated_crc = self.calculate_crc(data)
        return calculated_crc == received_crc
    
    def simple_hash(self, message, sequence_id):
        key = sequence_id
        key = (key * (len(message) // len(key) + 1))[:len(message)]
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(message, key))

    def encode_message(self, message, sequence_id):
        key = sequence_id
        return self.simple_hash(message, key)

    def decode_message(self, encoded_message, sequence_id):
        key = sequence_id 
        return self.simple_hash(encoded_message, key)

    def process_received_data(self, data):
        try:
            parts = data.split(',')
            if len(parts) != 5:
                return False, None, None, None, None

            sender_id, receiver_id, sequence_id, encoded_message, received_crc = parts
            sequence_id = f"{int(sequence_id):04d}"
            received_crc = int(received_crc)

            decoded_message = self.decode_message(encoded_message, sequence_id)
            valid_crc = self.verify_crc(decoded_message, received_crc)

            if not valid_crc:
                return False, None, None, None, None

            _, _, _, message = decoded_message.split(',', 3)
            return True, int(sender_id), int(receiver_id), sequence_id, message
        except Exception as e:
            print(f"Error processing received data: {e}")
            return False, None, None, None, None
