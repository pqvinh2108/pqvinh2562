import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel)
from PyQt5.QtCore import QThread, pyqtSignal
# Import các hàm bảo mật từ file client.py cũ của Vinh
from client import encrypt_message, decrypt_message, client_socket, aes_key

class ReceiveThread(QThread):
    signal = pyqtSignal(str)
    def run(self):
        while True:
            try:
                encrypted_msg = client_socket.recv(1024)
                decrypted_msg = decrypt_message(aes_key, encrypted_msg)
                self.signal.emit(decrypted_msg)
            except:
                break

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SafeChat - AES/RSA Encryption')
        self.setGeometry(300, 300, 400, 500)
        layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(QLabel("Nội dung tin nhắn:"))
        layout.addWidget(self.chat_history)

        self.msg_input = QLineEdit()
        layout.addWidget(self.msg_input)

        self.send_btn = QPushButton('Gửi tin nhắn (Encrypted)')
        self.send_btn.clicked.connect(self.send_msg)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

        # Chạy luồng nhận tin nhắn ngầm
        self.thread = ReceiveThread()
        self.thread.signal.connect(self.update_chat)
        self.thread.start()

    def send_msg(self):
        msg = self.msg_input.text()
        if msg:
            encrypted = encrypt_message(aes_key, msg)
            client_socket.send(encrypted)
            self.chat_history.append(f"Bạn: {msg}")
            self.msg_input.clear()

    def update_chat(self, msg):
        self.chat_history.append(f"Đối phương: {msg}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatWindow()
    ex.show()
    sys.exit(app.exec_())