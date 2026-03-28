from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization

# 1. Đọc khóa công khai của Server từ file đã tạo
with open("server_public_key.pem", "rb") as f:
    server_public_key = serialization.load_pem_public_key(f.read())

# 2. Client tự tạo khóa dựa trên thông số của Server
parameters = server_public_key.parameters()
private_key = parameters.generate_private_key()

# 3. Trao đổi khóa để tạo ra bí mật chung (Shared Secret)
shared_secret = private_key.exchange(server_public_key)

# In kết quả ra màn hình
print("-" * 30)
print("KET QUA TRAO DOI KHOA DH:")
print("Shared Secret (Hex):", shared_secret.hex())
print("-" * 30)