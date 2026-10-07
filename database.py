import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freeshion.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            tagline TEXT,
            product_count TEXT,
            image_url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE,
            category_slug TEXT NOT NULL,
            price INTEGER NOT NULL,
            original_price INTEGER,
            color TEXT,
            badge TEXT,
            stock INTEGER DEFAULT 10,
            sizes TEXT DEFAULT 'S, M, L, XL',
            image_url TEXT NOT NULL,
            description TEXT,
            is_featured INTEGER DEFAULT 0,
            is_new_arrival INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            customer_phone TEXT NOT NULL,
            customer_address TEXT,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            note TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            size TEXT,
            color TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # 1. Seed Users (Default Admin & Sample User)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = generate_password_hash("admin123")
        user_pass = generate_password_hash("123456")
        cursor.executemany('''
            INSERT INTO users (email, password_hash, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('admin@freeshion.vn', admin_pass, 'Freedom Admin', '0963599999', 'admin'),
            ('ban@example.com', user_pass, 'Khách Hàng Mẫu', '0912345678', 'customer')
        ])

    # 2. Seed Categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('suit', 'Vest & Suit', 'Đẳng cấp trong từng đường chỉ', '24 SẢN PHẨM', 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80'),
            ('ao-khoac', 'Áo Khoác', 'Phong cách mọi mùa', '18 SẢN PHẨM', 'https://images.unsplash.com/photo-1520975954732-35dd22299614?auto=format&fit=crop&w=800&q=80'),
            ('casual', 'Casual', 'Tự tin mỗi ngày', '36 SẢN PHẨM', 'https://images.unsplash.com/photo-1516257984-b1b4d707412e?auto=format&fit=crop&w=800&q=80'),
            ('phu-kien', 'Phụ Kiện', 'Điểm nhấn tinh tế', '12 SẢN PHẨM', 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80')
        ]
        cursor.executemany('''
            INSERT INTO categories (slug, name, tagline, product_count, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)

    # 3. Seed Products (matching images exactly)
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            # 4 featured products from design matching Admin's initial stats (stock total: 15+18+14+12=59)
            ('Vest Đen Cổ Điển', 'vest-den-co-dien', 'suit', 2890000, 3500000, 'ĐEN', 'BÁN CHẠY', 15, 'S, M, L, XL',
             'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80',
             'Chất liệu Wool Ý cao cấp, đường may ve cổ tinh xảo tôn vinh vóc dáng quý ông.', 1, 0),
            
            ('Suit Xám Hiện Đại', 'suit-xam-hien-dai', 'suit', 3490000, None, 'XÁM', 'MỚI', 18, 'M, L, XL',
             'https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?auto=format&fit=crop&w=800&q=80',
             'Màu xám lông chuột thời thượng, kiểu dáng may đo phom Slim-fit hiện đại.', 1, 0),
            
            ('Jacket Da Đô Thị', 'jacket-da-do-thi', 'ao-khoac', 1990000, 2400000, 'ĐEN', 'SALE', 14, 'S, M, L',
             'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&w=800&q=80',
             'Da PU xử lý bề mặt nhám mờ cao cấp, khóa kéo kim loại chống gỉ ánh đồng sang trọng.', 1, 0),
            
            ('Blazer Oversized', 'blazer-oversized', 'ao-khoac', 2190000, None, 'ĐEN', 'MỚI', 12, 'M, L, XL',
             'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=800&q=80',
             'Thiết kế vai rộng phóng khoáng, thích hợp phong cách thành thị đương đại.', 1, 0),

            # New arrivals from design (section "Vừa Cập Bến")
            ('Trench Coat Camel', 'trench-coat-camel', 'ao-khoac', 3200000, None, 'CAMEL', 'MỚI', 8, 'M, L, XL',
             'https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=800&q=80',
             'Áo măng tô dáng dài tông màu Camel kinh điển, cản gió và giữ ấm thanh lịch.', 0, 1),

            ('Áo Sơ Mi Oxford', 'ao-so-mi-oxford', 'casual', 890000, None, 'TRẮNG', None, 25, 'S, M, L',
             'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80',
             'Vải dệt Oxford 100% cotton thoáng mát, cổ áo cứng cáp giữ form tuyệt đối.', 0, 1),

            ('Blazer Đen Slim', 'blazer-den-slim', 'ao-khoac', 2490000, None, 'ĐEN', None, 10, 'M, L, XL',
             'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=800&q=80',
             'Thiết kế ôm gọn dáng người, tôn bật chiều cao và thần thái đĩnh đạc.', 0, 1),

            ('Jacket Bomber Xám', 'jacket-bomber-xam', 'ao-khoac', 1650000, None, 'XÁM', None, 7, 'M, L',
             'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=800&q=80',
             'Bomber trẻ trung bo thun gấu áo, lót chần bông giữ nhiệt êm ái.', 0, 1),

            ('Quần Tây Thẳng', 'quan-tay-thang', 'casual', 1190000, None, 'ĐEN', 'CẦN BỔ SUNG', 3, 'S, M, L, XL',
             'https://images.unsplash.com/photo-1479064555552-3ef4979f8908?auto=format&fit=crop&w=800&q=80',
             'Ống đứng chỉn chu, chất vải chống nhăn co giãn nhẹ thoải mái vận động.', 0, 1)
        ]

        cursor.executemany('''
            INSERT INTO products (name, slug, category_slug, price, original_price, color, badge, stock, sizes, image_url, description, is_featured, is_new_arrival)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', products)

    # 4. Seed Orders matching exactly the sample data in Admin Dashboard (Page 1)
    # Notice: Total completed revenue in design is 4.180.000 ₫
    # FH-1026: 2.190.000 (Hoàn tất) + FH-1025: 1.990.000 (Hoàn tất) = 4.180.000 ₫ exactly!
    # FH-1028: 2.890.000 (Chờ xử lý)
    # FH-1027: 3.490.000 (Đang giao)
    # FH-1024: 1.500.000 (Đã hủy) -> Total orders = 5
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        orders = [
            ('FH-1028', 'Nguyễn Minh Anh', 'minhanh@gmail.com', '0912111222', 'Số 12 Phan Chu Trinh, Hoàn Kiếm, Hà Nội', 2890000, 'Chờ xử lý', '2026-10-01 14:30:00', 'Giao giờ hành chính'),
            ('FH-1027', 'Trần Đức Huy', 'duchuy@gmail.com', '0988222333', 'Landmark 81, P.22, Bình Thạnh, TP.HCM', 3490000, 'Đang giao', '2026-10-01 09:15:00', 'Gọi trước 15 phút'),
            ('FH-1026', 'Lê Hoàng Nam', 'hoangnam@gmail.com', '0903444555', 'Số 88 Hai Bà Trưng, Quận 1, TP.HCM', 2190000, 'Hoàn tất', '2026-09-30 18:20:00', 'Đã nhận hàng thành công'),
            ('FH-1025', 'Phạm Quang Minh', 'quangminh@gmail.com', '0977666777', 'Khu đô thị Ciputra, Tây Hồ, Hà Nội', 1990000, 'Hoàn tất', '2026-09-30 11:05:00', 'Đã thanh toán chuyển khoản'),
            ('FH-1024', 'Hoàng Tuấn Kiệt', 'tuankiet@gmail.com', '0933555999', 'Số 45 Lê Duẩn, Hải Châu, Đà Nẵng', 1650000, 'Đã hủy', '2026-09-28 16:45:00', 'Khách đổi ý đặt size khác')
        ]
        
        for ord_data in orders:
            cursor.execute('''
                INSERT INTO orders (order_code, customer_name, customer_email, customer_phone, customer_address, total_price, status, created_at, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ord_data)
            ord_id = cursor.lastrowid
            
            # Add sample item for each order
            cursor.execute('''
                INSERT INTO order_items (order_id, product_name, price, quantity, size, color)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ord_id, 'Sản phẩm thời trang Freeshion', ord_data[5], 1, 'L', 'ĐEN'))

    # 5. Seed Store Settings
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO settings (key, value) VALUES (?, ?)
        ''', [
            ('store_name', 'FREESHION'),
            ('store_address', '69 Tràng Tiền, Hoàn Kiếm, TP. Hà Nội'),
            ('store_phone', '0963599999'),
            ('store_email', 'Freedom-fashion@gmail.com'),
            ('est_year', 'EST. FREESHION'),
            ('shipping_policy', 'Miễn phí vận chuyển toàn quốc cho đơn hàng từ 1.000.000 ₫')
        ])

    conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully with seeded data!")
