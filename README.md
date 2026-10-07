# FREESHION · Luxury Menswear E-Commerce Platform

Dự án website thương mại điện tử thời trang nam cao cấp **FREESHION** được xây dựng chuẩn mực theo đúng thiết kế đồ họa nguyên bản:
- **Tông màu chủ đạo**: Dark Luxury Theme (`#0B0B0C`, than chì mờ, viền vàng ánh kim `--accent-gold`, typographic sang trọng với font serif cao cấp).
- **Kiến trúc**: Full-stack kết hợp **Python (Flask 3.x)**, CSDL **SQLite**, giao diện **HTML5, CSS3, JavaScript tương tác cao**, chuẩn Responsive cho mọi thiết bị.

---

## 🔒 Tách biệt hoàn toàn & Cơ chế bảo mật Quản trị (Admin)

### 1. Ẩn hoàn toàn liên kết Admin trên giao diện Khách hàng (`/`):
- Toàn bộ liên kết, văn bản dẫn tới trang quản trị (nút *"Quản Trị"* ở footer, header, menu điều hướng) đã được **xóa bỏ triệt để**.
- Khách truy cập thông thường vào website sẽ **không thể nhìn thấy, tìm kiếm hay bấm vào bất kỳ đường dẫn nào** tới trang Admin.

### 2. Phân quyền và Bảo vệ tuyến đường (`/admin`):
- Trang Admin được bảo vệ bởi decorator kiểm tra quyền hạn `@admin_required`.
- Bất kỳ ai cố tình gõ trực tiếp URL `/admin` hoặc các trang quản trị con mà chưa đăng nhập đều sẽ bị chặn và **tự động chuyển hướng về Cổng đăng nhập quản trị riêng biệt**: `/admin/login`.
- Nếu tài khoản khách hàng thông thường cố tình đăng nhập tại cổng `/admin/login`, hệ thống sẽ từ chối truy cập và báo lỗi: *"Tài khoản của bạn không có quyền Quản trị viên (Admin)"*.

---

## 📸 Đối chiếu tính năng theo bản thiết kế

### 1. Khu Vực Khách Hàng (`/` - Khớp Hình 3 & Hình 2)
- **Top Ticker (Marquee vô tận)**: Thông báo chính sách `✦ MIỄN PHÍ VẬN CHUYỂN ✦ ĐỔI TRẢ 30 NGÀY ✦ CHẤT LIỆU CAO CẤP ✦ THIẾT KẾ ĐỘC QUYỀN ✦ ...`
- **Menu điều hướng**: Bộ Sưu Tập, Vest & Suit, Casual, Áo Khoác, Phụ Kiện, tìm kiếm theo tên/mô tả tức thì.
- **Hero Banner**: Bộ sưu tập *"THU ĐÔNG 2026 - Phong Cách Không Thỏa Hiệp"*, nút *"KHÁM PHÁ NGAY"* và *"XEM LOOKBOOK"*, chỉ báo cuộn *"Cuộn Để Khám Phá ↓"*.
- **Danh Mục (Phong Cách Của Bạn)**: 3 card danh mục lớn (Vest & Suit - 24 sản phẩm, Áo Khoác - 18 sản phẩm, Casual - 36 sản phẩm) có hiệu ứng zoom khi hover.
- **Tuyên Ngôn (Philosophy)**: Trích dẫn ấn tượng *"Quần áo không tạo nên người đàn ông, nhưng mở ra cánh cửa"* cùng ảnh nam editorial.
- **Sản phẩm Nổi bật (Được yêu thích)**: Bộ lọc Tabs (Tất cả, Suit, Casual, Áo khoác), thẻ sản phẩm với huy hiệu (*BÁN CHẠY, MỚI, SALE*), hiển thị màu sắc, giá bán, giá gạch và tính năng **Quick View (Xem nhanh)** & **Thêm vào giỏ**.
- **Cam kết dịch vụ**: Dải 4 cột (Giao nhanh toàn quốc, Đổi trả 30 ngày, Tư vấn kích thước, Thanh toán an toàn).
- **Hàng Mới Về (Vừa Cập Bến)**: Trench Coat Camel, Áo Sơ Mi Oxford, Blazer Đen Slim, Jacket Bomber Xám, Quần Tây Thẳng.
- **Đăng ký nhận tin (Cộng Đồng)**: Khối màu vàng kem/gold luxury (`#D9C3A3`) nổi bật.
- **Chân trang (Footer)**: Thông tin showroom 69 Tràng Tiền, Hoàn Kiếm, Hà Nội, hotline, email (đã loại bỏ mọi liên kết Admin).
- **Trang Đăng Nhập / Đăng Ký Khách Hàng (`/login` & `/register`)**:
  - Giao diện chia đôi (Split layout) theo đúng Hình 2.
  - Tab chuyển đổi linh hoạt không reload giữa Đăng nhập và Đăng ký.
  - Mã hóa mật khẩu bảo mật với `werkzeug.security`.

### 2. Khu Vực Quản Trị - Freedom Admin Studio (`/admin` - Khớp Hình 1)
- **Cổng Đăng Nhập Quản Trị Riêng (`/admin/login`)**: Giao diện tối bảo mật cao cấp với lá chắn an ninh và kiểm tra thẩm quyền.
- **Layout Quản Trị Độc Lập (`admin_base.html`)**: Sidebar quản lý tách biệt hoàn toàn với trang khách hàng.
- **4 Thẻ số liệu thống kê chuẩn xác**:
  1. **Doanh thu hoàn tất**: `4.180.000 ₫` (Tính chuẩn xác từ các đơn hàng đã hoàn tất).
  2. **Tổng đơn hàng**: `05` (1 đơn cần xử lý).
  3. **Sản phẩm**: `04` (Khớp đúng số sản phẩm demo ban đầu).
  4. **Tổng tồn kho**: `59` (Có cảnh báo sản phẩm tồn kho thấp).
- **Monthly Performance (Hiệu suất tháng)**:
  - So sánh trực quan giữa Tháng trước (09/2026: 4.180.000 ₫) và Tháng này (10/2026: 0 ₫).
  - Nút chuyển đổi xem **Doanh thu** và **Số đơn hàng**.
  - Biểu đồ cột thể hiện trực quan tỷ lệ giảm 100% so với tháng trước giống ảnh thiết kế.
- **Nhịp vận hành & Cần chú ý**:
  - Thanh đo tiến độ trạng thái: Chờ xử lý (1), Đang giao (1), Hoàn tất (2), Đã hủy (1).
  - Cảnh báo nhanh: `1 đơn đang chờ xử lý`, `1 sản phẩm cần bổ sung` (tồn kho <= 5).
- **Đơn hàng gần đây**:
  - Bảng đơn hàng #FH-1028, #FH-1027, #FH-1026, #FH-1025 kèm trạng thái pill và dropdown cập nhật trực tiếp trạng thái sang SQLite.
- **Quản lý danh mục & Sản phẩm (`/admin/products`)**: Thêm mới, chỉnh sửa giá, màu sắc, tồn kho, xóa sản phẩm.
- **Quản lý đơn hàng (`/admin/orders`)**: Lọc theo trạng thái, xem thông tin giao hàng, cập nhật trạng thái đơn (tự động cập nhật doanh thu).

---

## 🔑 Tài khoản mẫu mặc định

| Mục đích | URL truy cập | Email | Mật khẩu | Quyền hạn |
| :--- | :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `/admin` hoặc `/admin/login` | `admin@freeshion.vn` | `admin123` | **Toàn quyền Quản trị** |
| **Khách hàng (Customer)** | `/login` hoặc `/register` | `ban@example.com` | `123456` | Khách hàng thông thường |

---

## 🚀 Hướng dẫn khởi chạy dự án

### Cách 1: Chạy nhanh bằng 1 click (Windows)
Nhấp đúp chuột vào file `run.bat` trong thư mục dự án.

### Cách 2: Chạy qua dòng lệnh (Terminal / PowerShell / CMD)
```bash
# 1. Cài đặt thư viện (nếu cần)
pip install -r requirements.txt

# 2. Khởi tạo cơ sở dữ liệu và dữ liệu mẫu
python database.py

# 3. Khởi động máy chủ web
python app.py
```

Sau khi máy chủ khởi động:
- Khách hàng xem cửa hàng: **http://127.0.0.1:5000**
- Khách hàng đăng nhập: **http://127.0.0.1:5000/login**
- Quản trị viên truy cập trực tiếp: **http://127.0.0.1:5000/admin** *(yêu cầu đăng nhập tài khoản admin)*
