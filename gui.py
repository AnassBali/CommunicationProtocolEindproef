import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk
from communication import CommunicationProtocol
import threading
import serial.tools.list_ports
import time
from datetime import datetime

def get_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if ports:
        for port in ports:
            print(f"Available port: {port.device}")
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

        self.root.configure(bg='#2E2E2E')
        
        self.message_box = scrolledtext.ScrolledText(self.root, height=20, width=60, state=tk.DISABLED, bg='#1C1C1C', fg='#F2F2F2', font=("Helvetica", 12))
        self.message_box.pack(pady=10, padx=10)

        self.input_frame = tk.Frame(self.root, bg='#2E2E2E')
        self.input_frame.pack(pady=5, padx=10, fill=tk.X)

        self.input_box = tk.Entry(self.input_frame, width=40, font=("Helvetica", 12))
        self.input_box.grid(row=0, column=0, padx=5)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg='#4CAF50', fg='#FFFFFF', font=("Helvetica", 12))
        self.send_button.grid(row=0, column=1)

        self.stats_button = tk.Button(self.input_frame, text="Stats", command=self.show_stats, bg='#2196F3', fg='#FFFFFF', font=("Helvetica", 12))
        self.stats_button.grid(row=0, column=2)

        self.time_label = tk.Label(self.root, text="", bg='#2E2E2E', fg='#F2F2F2', font=("Helvetica", 12))
        self.time_label.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_time)

    def receive_messages(self):
        while True:
            new_messages = self.comm_protocol.get_new_messages()
            for msg in new_messages:
                self.messages.append(f"Received from User {self.other_user_id}: {msg}")
                self.update_message_box(f"Received from User {self.other_user_id}: {msg}\n")  # Display decrypted message
                self.update_stats()

    def update_message_box(self, message):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message)
        self.message_box.see(tk.END)
        self.message_box.config(state=tk.DISABLED)

    def send_message(self):
        message = self.input_box.get()
        start_time = time.time()
        success = self.comm_protocol.send_message(message)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if success:
            self.messages.append(f"User {self.user_id}: {message}")
            self.update_message_box(f"User {self.user_id}: {message}\n")
            print(f"Message sent in {elapsed_time:.2f} seconds")
        else:
            self.update_message_box("Message not sent, retrying...\n")
        self.input_box.delete(0, tk.END)
        self.update_stats()

    def show_stats(self):
        sent_messages = [msg for msg in self.messages if msg.startswith(f"User {self.user_id}:")]
        received_messages = [msg for msg in self.messages if msg.startswith(f"Received from User {self.other_user_id}:")]

        stats_message = (f"Statistics:\n\n"
                         f"Messages Sent: {len(sent_messages)}\n"
                         f"Messages Received: {len(received_messages)}\n"
                         f"Total Messages: {len(self.messages)}")

        messagebox.showinfo("Communication Stats", stats_message)

    def update_stats(self):
        sent_messages = [msg for msg in self.messages if msg.startswith(f"User {self.user_id}:")]
        received_messages = [msg for msg in self.messages if msg.startswith(f"Received from User {self.other_user_id}:")]
        print(f"Messages Sent: {len(sent_messages)}, Messages Received: {len(received_messages)}, Total Messages: {len(self.messages)}")

    def on_closing(self):
        self.comm_protocol.close()
        self.root.destroy()

def prompt_user_id():
    attempts = 3
    while attempts > 0:
        user_id = simpledialog.askstring("User ID", "Enter your User ID (1, 2, or 3):")
        if user_id in {'1', '2', '3'}:
            print(f"User ID chosen: {user_id}")
            return int(user_id)
        else:
            attempts -= 1
            messagebox.showerror("Invalid ID", f"Invalid ID entered. You have {attempts} attempt(s) left.")
    return None

def main():
    user_id = prompt_user_id()
    if user_id is None:
        print("Failed to enter a valid User ID. Exiting the program.")
        return

    other_user_id = 2 if user_id == 1 else 1  # For demonstration purposes, we'll set the other user ID

    serial_port = get_serial_port()
    if not serial_port:
        print("No COM port available. Please make sure a COM port is connected.")
        return

    user_chat = ChatGUI(user_id, other_user_id, serial_port)
    user_chat.root.mainloop()

if __name__ == "__main__":
    main()
