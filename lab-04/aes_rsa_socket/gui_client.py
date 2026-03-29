import sys
import socket
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
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

class ReceiveThread(QThread):
    message_received = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, sock, aes_key):
        super().__init__()
        self.sock = sock
        self.aes_key = aes_key
        self.running = True

    def run(self):
        while self.running:
            try:
                encrypted_msg = self.sock.recv(2048) # Increased buffer
                if not encrypted_msg:
                    break
                decrypted_msg = decrypt_message(self.aes_key, encrypted_msg)
                self.message_received.emit(decrypted_msg)
            except Exception as e:
                break
        if self.running:
            self.connection_lost.emit()

    def stop(self):
        self.running = False


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.aes_key = None
        self.receive_thread = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SafeChat - Tự động Mã hóa AES/RSA')
        self.setGeometry(300, 300, 500, 600)
        
        # Stylesheet for a modern dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #e6e6e6;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #5c636a;
                color: #ced4da;
            }
        """)

        layout = QVBoxLayout()
        
        # Connection Controls
        top_layout = QHBoxLayout()
        self.status_label = QLabel("Trạng thái: Chưa kết nối")
        self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
        
        self.connect_btn = QPushButton("Kết nối Server")
        self.connect_btn.clicked.connect(self.connect_to_server)
        
        self.disconnect_btn = QPushButton("Ngắt kết nối")
        self.disconnect_btn.clicked.connect(self.disconnect_from_server)
        self.disconnect_btn.setEnabled(False)

        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.connect_btn)
        top_layout.addWidget(self.disconnect_btn)
        
        layout.addLayout(top_layout)

        # Chat History
        layout.addWidget(QLabel("Nội dung cuộc trò chuyện an toàn:"))
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        # Input Area
        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Nhập nội dung tin nhắn...")
        self.msg_input.returnPressed.connect(self.send_msg)
        self.msg_input.setEnabled(False)
        input_layout.addWidget(self.msg_input)

        self.send_btn = QPushButton('Gửi (Encrypted)')
        self.send_btn.clicked.connect(self.send_msg)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def connect_to_server(self):
        try:
            self.status_label.setText("Trạng thái: Đang kết nối...")
            QApplication.processEvents() # Cập nhật UI ngay lập tức

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5.0) # Đợi 5s để server trả về
            self.client_socket.connect(('localhost', 12345))
            
            # --- TRÌNH TỰ BẢO MẬT (RSA -> AES) ---
            self.chat_history.append("<span style='color:#a0a0a0;'>[Hệ thống] Bắt đầu trao đổi khóa RSA...</span>")
            QApplication.processEvents()

            # 1. Tạo RSA key cho client
            client_key = RSA.generate(2048)
            
            # 2. Nhận public key của server
            server_public_key_bytes = self.client_socket.recv(2048)
            server_public_key = RSA.import_key(server_public_key_bytes)
            
            # 3. Gửi public key của client cho server
            self.client_socket.send(client_key.publickey().export_key(format='PEM'))
            
            # 4. Nhận AES key đã được server mã hóa
            encrypted_aes_key = self.client_socket.recv(2048)
            
            # 5. Giải mã AES key bằng private key của client
            cipher_rsa = PKCS1_OAEP.new(client_key)
            self.aes_key = cipher_rsa.decrypt(encrypted_aes_key)
            # -------------------------------------

            self.client_socket.settimeout(None) # Về chế độ blocking thông thường
            
            self.status_label.setText("Trạng thái: Đã kết nối & Bảo mật")
            self.status_label.setStyleSheet("color: #198754; font-weight: bold;")
            
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.msg_input.setEnabled(True)
            
            self.chat_history.append("<span style='color:#0dcaf0;'>[Hệ thống] Đã thiết lập kênh mã hóa AES/RSA. Kết nối an toàn!</span><br>")
            
            # Khởi động luồng đọc tin nhắn
            self.receive_thread = ReceiveThread(self.client_socket, self.aes_key)
            self.receive_thread.message_received.connect(self.update_chat)
            self.receive_thread.connection_lost.connect(self.handle_disconnect)
            self.receive_thread.start()
            
            self.msg_input.setFocus()

        except ConnectionRefusedError:
            self.status_label.setText("Trạng thái: Server từ chối")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.critical(self, "Lỗi kết nối", "Server chưa mở. Vui lòng chạy server mã hóa trước!")
        except Exception as e:
            self.status_label.setText("Trạng thái: Lỗi")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra trong quá trình thiết lập bảo mật:\n{e}")

    def disconnect_from_server(self):
        if self.client_socket:
            try:
                # Gửi thông điệp thoát được mã hóa AES cho server biết
                try:
                    encrypted_exit = encrypt_message(self.aes_key, "exit")
                    self.client_socket.send(encrypted_exit)
                except:
                    pass
                self.client_socket.close()
            except:
                pass
        self.handle_disconnect()

    def send_msg(self):
        if not self.aes_key or not self.client_socket:
            return
            
        msg = self.msg_input.text().strip()
        if msg:
            try:
                # Mã hóa bằng AES trước khi gởi qua socket
                encrypted = encrypt_message(self.aes_key, msg)
                self.client_socket.send(encrypted)
                
                # Hiển thị trên UI
                self.chat_history.append(f"<span style='color:#0d6efd;'><b>Bạn:</b></span> {msg}")
                self.msg_input.clear()
            except Exception as e:
                self.handle_disconnect()
                
    def update_chat(self, msg):
        self.chat_history.append(f"<span style='color:#dc3545;'><b>Đối phương:</b></span> {msg}")
        
    def handle_disconnect(self):
        self.status_label.setText("Trạng thái: Đã ngắt kết nối")
        self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.msg_input.setEnabled(False)
        
        if self.receive_thread:
            self.receive_thread.stop()
            self.receive_thread = None
            
        self.client_socket = None
        self.aes_key = None
        self.chat_history.append("<span style='color:#6c757d;'><i>[Hệ thống] Đã ngắt kết nối với máy chủ.</i></span><br>")

    def closeEvent(self, event):
        self.disconnect_from_server()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatWindow()
    ex.show()
    sys.exit(app.exec_())