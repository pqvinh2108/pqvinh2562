from Crypto.Hash import SHA3_256
text = input("Nhap chuoi van ban: ").encode('utf-8')
hash_obj = SHA3_256.new(text)
print("SHA-3 Hash:", hash_obj.hexdigest())