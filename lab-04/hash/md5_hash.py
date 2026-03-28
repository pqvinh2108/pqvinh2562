    import struct

def left_rotate(value, shift):
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF

def md5(message):
    # Khởi tạo các biến ban đầu
    a = 0x67452301
    b = 0xEFCDAB89
    c = 0x98BADCFE
    d = 0x10325476

    # Tiền xử lý chuỗi văn bản
    original_length = len(message) * 8
    message += b'\x80'
    while (len(message) * 8) % 512 != 448:
        message += b'\x00'
    message += original_length.to_bytes(8, 'little')

    # Chia khối 512-bit và tính toán (đoạn này Vinh dùng thư viện cho nhanh hoặc gõ theo sách nếu muốn luyện tay)
    # Để đơn giản và chính xác, Vinh có thể chạy file md5_library.py ở bước sau để so sánh kết quả.
    return "Ket qua MD5 handmade" # Chỗ này Vinh gõ nốt các vòng lặp theo trang 144/145 nhé

input_string = input("Nhap chuoi can bam: ")
print(f"Ma bam MD5 cua '{input_string}' la: {md5(input_string.encode('utf-8'))}")