import sys
import socket
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, 
                             QLabel, QPushButton, QHBoxLayout, QListWidget)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv + ciphertext

def decrypt_message(key, encrypted_message):
    iv = encrypted_message[:AES.block_size]
    ciphertext = encrypted_message[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

class ServerThread(QThread):
    log_signal = pyqtSignal(str)
    client_connected_signal = pyqtSignal(str)
    client_disconnected_signal = pyqtSignal(str)

    def __init__(self, host='localhost', port=12345):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.server_socket = None
        self.clients = []  # List of (client_socket, aes_key, address)
        self.server_key = RSA.generate(2048)

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.log_signal.emit(f"Server started on {self.host}:{self.port}")
            self.log_signal.emit("Waiting for connections...")
        except Exception as e:
            self.log_signal.emit(f"Error starting server: {str(e)}")
            return

        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(None)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.log_signal.emit(f"Accept error: {str(e)}")
                break

    def handle_client(self, client_socket, client_address):
        addr_str = f"{client_address[0]}:{client_address[1]}"
        self.log_signal.emit(f"Connected with {addr_str}")
        self.client_connected_signal.emit(addr_str)

        try:
            # Send server's public key to client
            client_socket.send(self.server_key.publickey().export_key(format='PEM'))
            
            # Receive client's public key
            client_received_key = RSA.import_key(client_socket.recv(2048))
            
            # Generate AES key for message encryption
            aes_key = get_random_bytes(16)
            
            # Encrypt the AES key using the client's public key
            cipher_rsa = PKCS1_OAEP.new(client_received_key)
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)
            client_socket.send(encrypted_aes_key)
            
            client_info = (client_socket, aes_key, addr_str)
            self.clients.append(client_info)
            self.log_signal.emit(f"Secure AES channel established with {addr_str}")

            while self.running:
                try:
                    encrypted_message = client_socket.recv(1024)
                    if not encrypted_message:
                        break
                    
                    try:
                        decrypted_message = decrypt_message(aes_key, encrypted_message)
                        self.log_signal.emit(f"[{addr_str}]: {decrypted_message}")
                        
                        # Broadcast message to all other clients
                        for c_sock, c_key, c_addr in self.clients:
                            if c_sock != client_socket:
                                try:
                                    encrypted = encrypt_message(c_key, decrypted_message)
                                    c_sock.send(encrypted)
                                except:
                                    pass
                                    
                        if decrypted_message == "exit":
                            break
                    except Exception as e:
                        # self.log_signal.emit(f"Decryption error from {addr_str}: {e}")
                        pass
                except Exception as e:
                    break

        except Exception as e:
            self.log_signal.emit(f"Handshake error with {addr_str}: {str(e)}")

        # Client disconnected
        self.clients = [c for c in self.clients if c[0] != client_socket]
        try:
            client_socket.close()
        except:
            pass
        self.log_signal.emit(f"Connection with {addr_str} closed")
        self.client_disconnected_signal.emit(addr_str)

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        for c_sock, c_key, c_addr in self.clients:
            try:
                c_sock.close()
            except:
                pass


class ServerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SafeChat - Server Control Panel')
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #d1d1e0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 13px;
            }
            QTextEdit, QListWidget {
                background-color: #28293d;
                border: 1px solid #3d3d5c;
                border-radius: 6px;
                padding: 10px;
                font-family: Consolas, monospace;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
                color: #8c8c8c;
            }
            QLabel {
                font-weight: bold;
                margin-top: 5px;
            }
        """)

        layout = QVBoxLayout()

        # Status controls
        control_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("color: #ff4d4d; font-size: 16px;")
        
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        
        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

        # Clients and Logs split
        main_layout = QHBoxLayout()
        
        # Left side: Logs
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Server Logs:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        main_layout.addLayout(log_layout, 2)  # Log takes more space

        # Right side: Connected clients
        clients_layout = QVBoxLayout()
        clients_layout.addWidget(QLabel("Connected Clients:"))
        self.clients_list = QListWidget()
        clients_layout.addWidget(self.clients_list)
        main_layout.addLayout(clients_layout, 1)

        layout.addLayout(main_layout)

        self.setLayout(layout)

    @pyqtSlot()
    def start_server(self):
        self.server_thread = ServerThread()
        self.server_thread.log_signal.connect(self.append_log)
        self.server_thread.client_connected_signal.connect(self.add_client)
        self.server_thread.client_disconnected_signal.connect(self.remove_client)
        self.server_thread.start()
        
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("color: #00cc66; font-size: 16px;")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    @pyqtSlot()
    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None
        
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: #ff4d4d; font-size: 16px;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.append_log("Server stopped.")
        self.clients_list.clear()

    @pyqtSlot(str)
    def append_log(self, text):
        self.log_area.append(text)

    @pyqtSlot(str)
    def add_client(self, client_addr):
        self.clients_list.addItem(client_addr)

    @pyqtSlot(str)
    def remove_client(self, client_addr):
        items = self.clients_list.findItems(client_addr, pyqtSignal)
        for i in range(self.clients_list.count()):
            item = self.clients_list.item(i)
            if item.text() == client_addr:
                self.clients_list.takeItem(i)
                break

    def closeEvent(self, event):
        self.stop_server()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerWindow()
    ex.show()
    sys.exit(app.exec_())
