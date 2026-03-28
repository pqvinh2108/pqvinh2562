from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization

# 1. Tạo thông số DH
parameters = dh.generate_parameters(generator=2, key_size=2048)
# 2. Tạo cặp khóa Server
private_key = parameters.generate_private_key()
public_key = private_key.public_key()

# 3. Lưu khóa công khai ra file .pem
with open("server_public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
print("Da tao xong server_public_key.pem")