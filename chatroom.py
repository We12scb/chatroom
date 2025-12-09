import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog, messagebox
import os
import time

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.clients = {}  
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self.server.bind((host, port))  
        self.server.listen(5) 
        print(f"Server started on {host}:{port}")

    def broadcast(self, message, client_socket):
        for client in self.clients.values():
            if client != client_socket:  
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def send_private_message(self, message, recipient_alias):
        recipient_socket = self.clients.get(recipient_alias)  
        if recipient_socket:
            try:
                recipient_socket.send(message)
            except:
                self.remove_client(recipient_socket)

    def broadcast_file(self, file_data, filename, client_socket, file_type):
        file_size = len(file_data)
        for client in self.clients.values():
            if client != client_socket:  
                try:
                    # Send header with size
                    header = f"FILE:{filename}:{file_type}:{file_size}"
                    client.send(header.encode('utf-8'))
                    time.sleep(0.1) # Small buffer to ensure header is processed
                    client.sendall(file_data)
                    
                    # Notify about the file
                    notification = f"{client_socket.getpeername()[0]} sent {file_type}: {filename}"
                    client.send(notification.encode('utf-8'))
                except:
                    self.remove_client(client)

    def handle_client(self, client_socket):
        try:
            alias = client_socket.recv(1024).decode('utf-8')
            self.clients[alias] = client_socket
            print(f"User {alias} connected.")
            
            while True:
                try:
                    message = client_socket.recv(1024)
                    if not message:
                        break
                        
                    if message.startswith(b"FILE:"):
                        try:
                            header_parts = message.decode('utf-8').split(':', 3)
                            filename = header_parts[1]
                            file_type = header_parts[2]
                            file_size = int(header_parts[3])
                            
                            file_data = b""
                            remaining = file_size
                            while remaining > 0:
                                chunk_size = 4096 if remaining >= 4096 else remaining
                                part = client_socket.recv(chunk_size)
                                if not part:
                                    break
                                file_data += part
                                remaining -= len(part)
                                
                            self.broadcast_file(file_data, filename, client_socket, file_type)
                        except ValueError:
                            print("Error parsing file header")
                            
                    elif message.startswith(b"PRIVATE:"):
                        try:
                            parts = message[8:].decode('utf-8').split(":", 1)
                            if len(parts) == 2:
                                recipient_alias, private_message = parts
                                self.send_private_message(f"PRIVATE from {alias}: {private_message}".encode('utf-8'), recipient_alias)
                        except:
                            print("Error processing private message")
                    else:
                        print(f"Received message from {alias}: {message.decode('utf-8')}")
                        self.broadcast(f"{alias}: {message.decode('utf-8')}".encode('utf-8'), client_socket)
                except Exception as e:
                    print(f"Error handling message: {e}")
                    break
        except:
            pass
        finally:
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        for alias, socket_obj in list(self.clients.items()):
            if socket_obj == client_socket:
                del self.clients[alias]
                print(f"User {alias} disconnected.")
                break
        client_socket.close()

    def run(self):
        while True:
            try:
                client_socket, client_address = self.server.accept()  
                print(f"Connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except KeyboardInterrupt:
                print("Server stopping...")
                break


class ChatClient:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_done = False
        self.running = True
        self.alias = None

        try:
            self.client.connect((self.host, self.port))
            self.init_alias()
        except ConnectionRefusedError:
            print("Could not connect to server.")
            exit(1)

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive_messages)
        
        gui_thread.start()
        receive_thread.start()

    def init_alias(self):
        root = tk.Tk()
        root.withdraw()
        # Modern styling for dialog not easily possible with simpledialog, but we'll stick to it for simplicity of init
        self.alias = simpledialog.askstring("Alias", "Choose your alias", parent=root)
        if not self.alias:
            self.alias = "Guest"
        self.client.send(self.alias.encode('utf-8'))
        root.destroy()

    def gui_loop(self):
        self.root = tk.Tk()
        self.root.title(f"ProChat - {self.alias}")
        self.root.geometry("600x700")
        
        # Modern Color Palette
        self.bg_color = "#1e1e2e"       # Dark background
        self.text_color = "#cdd6f4"     # Light text
        self.accent_color = "#89b4fa"   # Blue accent
        self.input_bg = "#313244"       # Slightly lighter input
        self.button_bg = "#45475a"      # Button background
        self.button_fg = "#ffffff"      # Button text
        
        self.root.config(bg=self.bg_color)

        # Header
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(padx=20, pady=10, fill='x')
        
        title_label = tk.Label(header_frame, text="Chat Room", bg=self.bg_color, fg=self.accent_color, font=("Helvetica", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        status_label = tk.Label(header_frame, text="● Online", bg=self.bg_color, fg="#a6e3a1", font=("Helvetica", 10))
        status_label.pack(side=tk.RIGHT, pady=5)

        # Chat Area
        self.text_area = scrolledtext.ScrolledText(self.root, bg=self.input_bg, fg=self.text_color, 
                                                 font=("Segoe UI", 11), borderwidth=0, padx=10, pady=10)
        self.text_area.pack(padx=20, pady=10, expand=True, fill='both')
        self.text_area.config(state='disabled')

        # Input Area Frame
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(padx=20, pady=(0, 20), fill='x')

        self.input_area = tk.Text(input_frame, height=3, bg=self.input_bg, fg=self.text_color, 
                                font=("Segoe UI", 11), borderwidth=0, padx=10, pady=10)
        self.input_area.pack(fill='x', pady=(0, 10))
        self.input_area.bind("<Return>", self.write_event)

        # Buttons Frame
        button_frame = tk.Frame(input_frame, bg=self.bg_color)
        button_frame.pack(fill='x')

        # Style for buttons
        btn_font = ("Segoe UI", 10, "bold")
        
        self.send_button = tk.Button(button_frame, text="Send", command=self.write, 
                                   bg=self.accent_color, fg="#1e1e2e", font=btn_font, borderwidth=0, padx=20, pady=5)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        self.file_button = tk.Button(button_frame, text="📎 Media", command=self.send_file, 
                                   bg=self.button_bg, fg=self.button_fg, font=btn_font, borderwidth=0, padx=15, pady=5)
        self.file_button.pack(side=tk.LEFT, padx=5)

        self.private_button = tk.Button(button_frame, text="🔒 Private", command=self.send_private_message, 
                                      bg=self.button_bg, fg=self.button_fg, font=btn_font, borderwidth=0, padx=15, pady=5)
        self.private_button.pack(side=tk.LEFT, padx=5)

        self.gui_done = True
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def write_event(self, event):
        if not event.state & 0x0001: # Shift not pressed
            self.write()
            return 'break'

    def write(self):
        message = self.input_area.get('1.0', 'end').strip()
        if message:
            timestamp = time.strftime("%H:%M")
            display_text = f"[{timestamp}] You: {message}"
            self.display_message(display_text, align='right', color=self.accent_color)
            self.send_message(message) # Send raw message, server adds alias
            self.input_area.delete('1.0', 'end')

    def send_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Images", "*.jpg *.jpeg *.png"), ("Video", "*.mp4 *.avi")])
        if file_path:
            try:
                file_size = os.path.getsize(file_path)
                filename = os.path.basename(file_path)
                file_type = self.get_file_type(filename)
                
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                
                # Header: FILE:filename:type:size
                header = f"FILE:{filename}:{file_type}:{file_size}"
                self.client.send(header.encode('utf-8'))
                time.sleep(0.1) # Wait for header to be processed
                self.client.sendall(file_data)
                
                self.display_message(f"You sent {file_type}: {filename}", align='right', color="#f9e2af")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send file: {e}")

    def get_file_type(self, filename):
        ext = filename.lower().split('.')[-1]
        if ext in ['mp4', 'avi', 'mov', 'mkv']:
            return 'video'
        elif ext in ['mp3', 'wav', 'aac']:
            return 'audio'
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'photo'
        else:
            return 'file'

    def send_private_message(self):
        recipient_alias = simpledialog.askstring("Private Message", "Enter recipient's alias:", parent=self.root)
        if recipient_alias:
            private_message = simpledialog.askstring("Private Message", f"Message to {recipient_alias}:", parent=self.root)
            if private_message:
                self.client.send(f"PRIVATE:{recipient_alias}:{private_message}".encode('utf-8'))
                self.display_message(f"Private to {recipient_alias}: {private_message}", align='right', color="#f38ba8")

    def display_message(self, message, align='left', color=None):
        if not self.gui_done: return
        
        self.text_area.config(state='normal')
        
        # Create a unique tag for this message to apply styles
        tag_name = f"msg_{time.time()}_{align}"
        
        self.text_area.insert('end', message + '\n', tag_name)
        
        # Configure tag
        justify = 'right' if align == 'right' else 'left'
        msg_color = color if color else self.text_color
        
        self.text_area.tag_configure(tag_name, justify=justify, foreground=msg_color, 
                                   lmargin1=10, lmargin2=10, rmargin=10, spacing3=5)
        
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def stop(self):
        self.running = False
        self.root.quit()
        self.client.close()
        exit(0)

    def receive_messages(self):
        while self.running:
            try:
                message = self.client.recv(1024)
                if message:
                    if message.startswith(b"FILE:"):
                        try:
                            header_parts = message.decode('utf-8').split(':', 3)
                            filename = header_parts[1]
                            file_type = header_parts[2]
                            file_size = int(header_parts[3])
                            
                            file_data = b""
                            remaining = file_size
                            while remaining > 0:
                                chunk_size = 4096 if remaining >= 4096 else remaining
                                part = self.client.recv(chunk_size)
                                if not part:
                                    break
                                file_data += part
                                remaining -= len(part)
                                
                            save_name = f"received_{filename}"
                            with open(save_name, 'wb') as file:
                                file.write(file_data)
                            self.display_message(f"Received {file_type}: {filename}", align='left', color="#f9e2af")
                        except Exception as e:
                            print(f"Error receiving file: {e}")
                            
                    else:
                        if self.gui_done:
                            msg_text = message.decode('utf-8')
                            self.display_message(msg_text, align='left')
                else:
                    break
            except (ConnectionResetError, ConnectionAbortedError):
                if self.gui_done:
                    self.display_message("Disconnected from server.", align='center', color="#f38ba8")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_message(self, message):
        try:
            self.client.send(message.encode('utf-8'))
        except:
            self.display_message("Failed to send message.", align='right', color="#f38ba8")

if __name__ == "__main__":
    choice = input("Start as (server/client): ").strip().lower()
    if choice == 'server':
        server = ChatServer()
        server.run()
    elif choice == 'client':
        client = ChatClient()
