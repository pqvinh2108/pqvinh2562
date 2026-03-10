from flask import Flask, request, jsonify
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher 

app = Flask(__name__)

# --- KHỞI TẠO ALGORITHM ---
caesar_cipher = CaesarCipher()
# 2. Thêm khởi tạo đối tượng Vigenere
vigenere_cipher = VigenereCipher()

# ==========================================
# CÁC ROUTE CHO CAESAR CIPHER
# ==========================================
@app.route("/api/caesar/encrypt", methods=["POST"])
def caesar_encrypt():
    data = request.json
    plain_text = data['plain_text']
    key = int(data['key'])
    encrypted_text = caesar_cipher.encrypt_text(plain_text, key)
    return jsonify({'encrypted_message': encrypted_text})

@app.route("/api/caesar/decrypt", methods=["POST"])
def caesar_decrypt():
    data = request.json
    cipher_text = data['cipher_text']
    key = int(data['key'])
    decrypted_text = caesar_cipher.decrypt_text(cipher_text, key)
    return jsonify({'decrypted_message': decrypted_text})


# ==========================================
# 3. CẬP NHẬT CÁC ROUTE CHO VIGENERE CIPHER
# ==========================================
@app.route('/api/vigenere/encrypt', methods=['POST'])
def vigenere_encrypt():
    data = request.json
    plain_text = data['plain_text']
    key = data['key'] # Key của Vigenere thường là một chuỗi (string)
    encrypted_text = vigenere_cipher.vigenere_encrypt(plain_text, key)
    return jsonify({'encrypted_text': encrypted_text})

@app.route('/api/vigenere/decrypt', methods=['POST'])
def vigenere_decrypt():
    data = request.json
    cipher_text = data['cipher_text']
    key = data['key']
    decrypted_text = vigenere_cipher.vigenere_decrypt(cipher_text, key)
    return jsonify({'decrypted_text': decrypted_text})


# --- MAIN FUNCTION ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)