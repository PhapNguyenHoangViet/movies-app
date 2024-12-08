## Website TheMovie
This is a movie recommender website which has been integrated our recommendation model
## Website có các chức năng chính sau:
1.	Đăng nhập, đăng ký
-	Hệ thống hỗ trợ đăng ký tài khoản người dùng.
-	Hệ thống cần hỗ trợ đăng nhập bằng email.
![image](https://github.com/user-attachments/assets/0d489f7d-b6e1-44b0-b727-674eb62e4d4f)
Giao diện trang đăng ký
![image](https://github.com/user-attachments/assets/0c4c18cc-bc6d-4a22-921b-0a86eb8e4fc6)
Giao diện trang đăng nhập
2.	Hiển thị phim được đề xuất, phim phổ biến, phim theo thể loại
-	Hệ thống cần hiển thị những bộ phim được đề xuất cho người dùng.
-	Ngoài ra, hệ thống còn liệt kê ra những bộ phim phổ biến, những bộ phim theo thể loại để tăng sự lựa chọn phim cho người dùng.
![image](https://github.com/user-attachments/assets/e25bbf3a-5d81-4c91-b61b-94a23c80ce76)
Giao diện trang chủ
3.	Tìm kiếm phim
-	Hệ thống hỗ trợ người dùng tìm kiếm phim theo tên phim
4.	Xem thông tin về phim và đánh giá
-	Hệ thống cần cùng cấp các thông tin chi tiết về bộ phim khi người dùng chọn bộ phim đó.
-	Cho phép người dùng đánh giá (rating) và bình luận về phim
-	Giao diện cần dễ nhìn, dễ sử dụng nhưng cũng thu hút người dùng tìm hiểu về phim
![image](https://github.com/user-attachments/assets/12503227-d7d6-4ab0-9514-4409e6661cc6)
Giao diện trang chi tiết phim
5.	Quản lý thông tin cá nhân
-	Cho phép người dùng thay đổi thông tin cá nhân cũng như thay đổi mật khẩu
-	Cần có quy trình khôi phục mật khẩu nếu người dùng quên mật khẩu
![image](https://github.com/user-attachments/assets/5327d647-c4a2-4428-b1ee-b243d0b4668f)
Giao diện trang quản lý thông tin cá nhân
6.	Cập nhật các đề xuất phim theo sự thay đổi sở thích người dùng
-	Hệ thống cần cập nhật mô hình đề xuất phim từ dữ liệu mới của người dùng
-	Hệ thống cập nhật mô hình khi có người dùng mới đăng ký 
-	Hệ thống tự động cập nhật mô hình sau một khoảng thời gian
-	Hệ thống tự động cập nhật mô hình sau một lượng rating mới nhất định
7. Chatbot hỗ trợ người dùng
-	Hệ thống hỗ trợ tính năng chatbot để người dùng dễ dàng tìm hiểu thêm thông tin liên quan đến phim
image

Giao diện chatbot


# Hướng dẫn cài đặt và chạy ứng dụng

## Yêu cầu hệ thống
- Python 3.8 trở lên
- Docker và Docker Compose
- Git

## Các bước cài đặt

1. Clone repository
```bash
git clone https://github.com/PhapNguyenHoangViet/movies-app.git
cd movies-app
```
2. Cấu hình môi trường
Copy file .env.sample thành file .env
Cập nhật các biến môi trường trong file .env theo cấu hình của bạn

3. Chạy ứng dụng với Docker
```bash
# Build và chạy các container
docker-compose -f docker-compose-deploy.yml up

# Chạy ở chế độ detached
docker-compose -f docker-compose-deploy.yml up -d

# Kiểm tra logs nếu có lỗi
docker-compose -f docker-compose-deploy.yml logs
```

Truy cập ứng dụng
Website chính: http://127.0.0.1/movie/welcome/

Liên hệ hỗ trợ
Nếu gặp vấn đề, vui lòng tạo issue trên GitHub hoặc liên hệ qua email: [vietphap090603@gmail.com]

Những thông tin này sẽ giúp người dùng:
1. Biết được yêu cầu hệ thống cần thiết
2. Các bước cài đặt chi tiết
3. Cách chạy ứng dụng với Docker
4. Liên hệ hỗ trợ

