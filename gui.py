import tkinter as tk
from communication import CommunicationProtocol
import threading
import serial.tools.list_ports

def get_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if ports:
        return ports[0].device
    else:
        return None

class ChatGUI:
    def __init__(self, user_id, other_user_id, serial_port):
        self.user_id = user_id
        self.other_user_id = other_user_id
        self.comm_protocol = CommunicationProtocol(user_id, other_user_id, serial_port)
        self.messages = []

        self.root = tk.Tk()
        self.root.title(f"Secure Communication Protocol")

        self.message_box = tk.Text(self.root, height=10, width=50, state=tk.DISABLED)
        self.message_box.pack(pady=10)

        self.input_box = tk.Entry(self.root, width=50)
        self.input_box.pack(pady=5)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            new_messages = self.comm_protocol.get_new_messages()
            for msg in new_messages:
                self.messages.append(msg)
                self.update_message_box(f"Received message: {msg}\n")  # Display decrypted message

    def update_message_box(self, message):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message)
        self.message_box.see(tk.END)
        self.message_box.config(state=tk.DISABLED)

    def send_message(self):
        message = self.input_box.get()
        success = self.comm_protocol.send_message(message)
        if success:
            self.update_message_box(f"Message sent: {message}\n")
        else:
            self.update_message_box("Message not sent, retrying...\n")
        self.input_box.delete(0, tk.END)

    def on_closing(self):
        self.comm_protocol.close()
        self.root.destroy()

def main():
    serial_port = get_serial_port()
    if not serial_port:
        print("No COM port available. Please make sure a COM port is connected.")
        return

    user_chat = ChatGUI(1, 2, serial_port)
    user_chat.root.mainloop()

if __name__ == "__main__":
    main()
