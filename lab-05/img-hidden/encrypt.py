import sys
from PIL import Image

def encode_image(image_path, message):
    # 1. Mở ảnh và lấy thông tin kích thước
    img = Image.open(image_path)
    width, height = img.size
    
    # THÊM BƯỚC NÀY: Cộng thêm ký tự kết thúc \0 vào sau message
    message += '\0'
    
    # 2. Chuyển đổi thông điệp sang chuỗi nhị phân
    # Mỗi ký tự được chuyển thành 8 bit (08b)
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    # Thêm dấu mốc kết thúc bằng chuỗi bit (tùy chọn để bảo mật hơn)
    binary_message += '1111111111111110' 
    
    data_index = 0
    
    # 3. Duyệt qua từng pixel của ảnh để giấu tin
    for row in range(height):
        for col in range(width):
            # Lấy giá trị màu (R, G, B) của pixel tại vị trí (col, row)
            pixel = list(img.getpixel((col, row)))
            
            # Duyệt qua 3 kênh màu: Đỏ, Xanh lá, Xanh dương
            for color_channel in range(3):
                if data_index < len(binary_message):
                    # Thay thế bit cuối cùng (LSB) của kênh màu bằng 1 bit dữ liệu
                    channel_value = format(pixel[color_channel], '08b')
                    new_channel_value = channel_value[:-1] + binary_message[data_index]
                    pixel[color_channel] = int(new_channel_value, 2)
                    data_index += 1
            
            # Cập nhật lại pixel đã được sửa vào ảnh
            img.putpixel((col, row), tuple(pixel))
            
            # Nếu đã giấu hết thông điệp thì dừng lại
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break

    # 4. Lưu ảnh mới đã được giấu tin (Dùng .png để không mất dữ liệu)
    encoded_image_path = 'encoded_image.png'
    img.save(encoded_image_path)
    print("Steganography complete. Encoded image saved as", encoded_image_path)

def main():
    # Kiểm tra xem người dùng có nhập đủ tham số không
    if len(sys.argv) != 3:
        print("Usage: python encrypt.py <image_path> <message>")
        return

    image_path = sys.argv[1]
    message = sys.argv[2]
    
    encode_image(image_path, message)

if __name__ == "__main__":
    main()