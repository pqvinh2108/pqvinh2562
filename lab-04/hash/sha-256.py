import hashlib
data = input("Nhap du lieu de hash SHA-256: ")
hash_value = hashlib.sha256(data.encode()).hexdigest()
print("Gia tri hash SHA-256:", hash_value)