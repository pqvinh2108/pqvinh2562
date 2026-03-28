import hashlib
text = input("Nhap chuoi van ban: ").encode('utf-8')
blake2_hash = hashlib.blake2b(text, digest_size=64)
print("BLAKE2 Hash:", blake2_hash.hexdigest())