import hashlib

def calculate_md5(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()

input_string = input("Nhap chuoi can bam: ")
print(f"Ma bam MD5 cua '{input_string}' la: {calculate_md5(input_string)}")