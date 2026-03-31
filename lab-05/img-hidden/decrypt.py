import sys
from PIL import Image

def decode_image(encoded_image_path):
    # 1. Mở ảnh đã được mã hóa
    img = Image.open(encoded_image_path)
    width, height = img.size
    binary_message = ""

    # 2. Duyệt qua từng pixel để trích xuất bit cuối cùng (LSB)
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))
            
            # Lấy bit cuối từ cả 3 kênh màu R, G, B
            for color_channel in range(3):
                # Chuyển giá trị màu sang nhị phân 8 bit và lấy bit cuối cùng [-1]
                binary_message += format(pixel[color_channel], '08b')[-1]

    # 3. Chuyển chuỗi nhị phân thành văn bản
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        
        # Nếu đoạn nhị phân không đủ 8 bit (ở cuối ảnh) thì bỏ qua
        if len(byte) < 8:
            break
            
        # Chuyển 8 bit thành một ký tự văn bản
        char = chr(int(byte, 2))
        
        # ĐIỂM DỪNG: Nếu gặp ký tự Null (\0), dừng giải mã ngay lập tức
        if char == '\0':
            break
            
        message += char
        
    return message

def main():
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) != 2:
        print("Usage: python decrypt.py <encoded_image_path>")
        return

    encoded_image_path = sys.argv[1]
    
    # Thực hiện giải mã
    try:
        decoded_message = decode_image(encoded_image_path)
        print("Decoded message:", decoded_message)
    except Exception as e:
        print("Lỗi khi giải mã:", e)

if __name__ == "__main__":
    main()