import os
import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = 'freeshion_luxury_secret_key_2026'

# Custom filter for currency formatting
@app.template_filter('currency')
def currency_filter(value):
    if value is None:
        return '0 ₫'
    try:
        return f"{int(value):,} ₫".replace(',', '.')
    except (ValueError, TypeError):
        return f"{value} ₫"

@app.template_filter('format_date')
def format_date_filter(val_str):
    if not val_str:
        return ''
    try:
        dt = datetime.datetime.strptime(val_str[:10], '%Y-%m-%d')
        return dt.strftime('%d/%m/%Y')
    except Exception:
        return val_str

@app.context_processor
def inject_global_data():
    cart = session.get('cart', [])
    cart_count = sum(item.get('quantity', 1) for item in cart)
    cart_total = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)
    current_user = session.get('user', None)
    current_admin = current_user if (current_user and current_user.get('role') == 'admin') else None
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart_items': cart,
        'current_user': current_user,
        'current_admin': current_admin,
        'now_year': 2026
    }

# ================= AUTH DECORATORS & GUARDS =================

def admin_required(f):
    """
    Bảo vệ nghiêm ngặt các route Quản trị:
    Chỉ cho phép người dùng đã đăng nhập VÀ có quyền 'admin'.
    Nếu không thỏa mãn -> Lập tức chuyển hướng về trang /admin/login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = session.get('user')
        if not current_user or current_user.get('role') != 'admin':
            flash("Khu vực Quản trị yêu cầu quyền Admin. Vui lòng đăng nhập bằng tài khoản Quản trị viên.", "error")
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ================= STOREFRONT ROUTES (KHU VỰC KHÁCH HÀNG) =================

@app.route('/')
def index():
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('q', '').strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Get categories
    cursor.execute("SELECT * FROM categories")
    categories = [dict(row) for row in cursor.fetchall()]

    # Get featured products (Sản phẩm được yêu thích)
    featured_query = "SELECT * FROM products WHERE is_featured = 1"
    params = []
    if category_filter and category_filter != 'all':
        featured_query += " AND category_slug = ?"
        params.append(category_filter)
    if search_query:
        featured_query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    featured_query += " ORDER BY id ASC"
    cursor.execute(featured_query, params)
    featured_products = [dict(row) for row in cursor.fetchall()]

    # Get new arrivals (Hàng mới về - Vừa cập bến)
    cursor.execute("SELECT * FROM products WHERE is_new_arrival = 1 ORDER BY id ASC")
    new_arrivals = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template('index.html', 
                           categories=categories, 
                           featured_products=featured_products, 
                           new_arrivals=new_arrivals,
                           active_category=category_filter,
                           search_query=search_query)

@app.route('/category/<slug>')
def category_view(slug):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE slug = ?", (slug,))
    category = cursor.fetchone()
    if not category:
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM products WHERE category_slug = ? ORDER BY id DESC", (slug,))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', 
                           categories=[], 
                           featured_products=products, 
                           new_arrivals=[],
                           active_category=slug,
                           category_detail=dict(category))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(dict(product))

# ================= CUSTOMER AUTHENTICATION =================

@app.route('/login', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
@app.route('/auth', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        action = request.form.get('action') # 'login' or 'register'
        
        if action == 'login':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user'] = {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'phone': user['phone'],
                    'role': user['role']
                }
                flash(f"Chào mừng trở lại, {user['full_name']}!", 'success')
                redirect_target = request.args.get('next')
                if redirect_target:
                    return redirect(redirect_target)
                return redirect(url_for('index'))
            else:
                flash("Email hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại.", "error")
                return render_template('auth.html', active_tab='login', email=email)

        elif action == 'register':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not full_name or not email or not password:
                flash("Vui lòng điền đầy đủ các thông tin bắt buộc.", "error")
                return render_template('auth.html', active_tab='register', full_name=full_name, email=email, phone=phone)

            if password != confirm_password:
                flash("Mật khẩu xác nhận không khớp.", "error")
                return render_template('auth.html', active_tab='register', full_name=full_name, email=email, phone=phone)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                flash("Email này đã được sử dụng. Hãy đăng nhập hoặc chọn email khác.", "error")
                return render_template('auth.html', active_tab='register', full_name=full_name, phone=phone)

            pwd_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, role)
                VALUES (?, ?, ?, ?, 'customer')
            ''', (email, pwd_hash, full_name, phone))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()

            session['user'] = {
                'id': new_id,
                'email': email,
                'full_name': full_name,
                'phone': phone,
                'role': 'customer'
            }
            flash("Đăng ký tài khoản thành công! Chào mừng bạn đến với Freeshion Circle.", "success")
            return redirect(url_for('index'))

    # If requested via /register, default tab to register
    default_tab = 'register' if request.path == '/register' else request.args.get('tab', 'login')
    return render_template('auth.html', active_tab=default_tab)

@app.route('/logout')
def customer_logout():
    session.pop('user', None)
    flash("Bạn đã đăng xuất tài khoản thành công.", "info")
    return redirect(url_for('index'))

# ================= CART & CHECKOUT APIS =================

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json() or request.form
    product_id = data.get('product_id')
    size = data.get('size', 'L')
    color = data.get('color', 'ĐEN')
    quantity = int(data.get('quantity', 1))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'}), 404

    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item['id'] == product['id'] and item.get('size') == size and item.get('color') == color:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'image_url': product['image_url'],
            'size': size,
            'color': color or product['color'],
            'quantity': quantity
        })

    session['cart'] = cart
    session.modified = True

    total_count = sum(item['quantity'] for item in cart)
    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    return jsonify({
        'success': True, 
        'message': f"Đã thêm '{product['name']}' vào giỏ hàng!",
        'cart_count': total_count,
        'cart_total': total_amount,
        'cart': cart
    })

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.get_json()
    index = data.get('index')
    quantity = int(data.get('quantity', 1))
    cart = session.get('cart', [])

    if 0 <= index < len(cart):
        if quantity <= 0:
            cart.pop(index)
        else:
            cart[index]['quantity'] = quantity
        session['cart'] = cart
        session.modified = True

    total_count = sum(item['quantity'] for item in cart)
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    return jsonify({'success': True, 'cart_count': total_count, 'cart_total': total_amount, 'cart': cart})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    return jsonify({'success': True, 'cart_count': 0, 'cart_total': 0})

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Giỏ hàng của bạn đang trống.", "error")
        return redirect(url_for('index'))

    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    customer_address = request.form.get('customer_address', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    note = request.form.get('note', '').strip()

    if not customer_name or not customer_phone or not customer_address:
        flash("Vui lòng nhập đầy đủ họ tên, số điện thoại và địa chỉ giao hàng.", "error")
        return redirect(url_for('index'))

    total_price = sum(item['price'] * item['quantity'] for item in cart)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1")
    last_order = cursor.fetchone()
    next_num = 1029
    if last_order:
        next_num = 1000 + last_order['id'] + 1
    order_code = f"FH-{next_num}"

    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO orders (order_code, customer_name, customer_email, customer_phone, customer_address, total_price, status, created_at, note)
        VALUES (?, ?, ?, ?, ?, ?, 'Chờ xử lý', ?, ?)
    ''', (order_code, customer_name, customer_email, customer_phone, customer_address, total_price, created_at, note))
    
    order_id = cursor.lastrowid

    for item in cart:
        cursor.execute('''
            INSERT INTO order_items (order_id, product_name, price, quantity, size, color)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (order_id, item['name'], item['price'], item['quantity'], item.get('size', 'L'), item.get('color', 'ĐEN')))
        
        # Deduct stock
        cursor.execute("UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?", (item['quantity'], item['id']))

    conn.commit()
    conn.close()

    session['cart'] = []
    session.modified = True

    flash(f"Đặt hàng thành công! Mã đơn của bạn là #{order_code}. Chuyên viên tư vấn sẽ liên hệ sớm nhất.", "success")
    return redirect(url_for('index'))

# ================= DEDICATED ADMIN AUTHENTICATION =================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Cổng đăng nhập riêng biệt dành riêng cho Quản trị viên (/admin/login)"""
    # Nếu admin đã đăng nhập từ trước, chuyển thẳng vào dashboard
    if session.get('user') and session['user'].get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    next_url = request.args.get('next') or request.form.get('next') or url_for('admin_dashboard')

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            if user['role'] != 'admin':
                flash("Tài khoản của bạn không có quyền Quản trị viên (Admin).", "error")
                return render_template('admin_login.html', email=email, next_url=next_url)

            # Lưu session Admin
            session['user'] = {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'phone': user['phone'],
                'role': user['role']
            }
            flash(f"Chào mừng Quản trị viên {user['full_name']} đến với Freedom Admin Studio!", "success")
            return redirect(next_url)
        else:
            flash("Email hoặc mật khẩu Quản trị không chính xác.", "error")
            return render_template('admin_login.html', email=email, next_url=next_url)

    return render_template('admin_login.html', next_url=next_url)

@app.route('/admin/logout')
def admin_logout():
    """Đăng xuất khỏi khu vực Quản trị"""
    session.pop('user', None)
    flash("Bạn đã đăng xuất an toàn khỏi hệ thống Quản trị Freedom Admin.", "info")
    return redirect(url_for('admin_login'))

# ================= FREEDOM ADMIN MANAGEMENT (BẮT BUỘC QUYỀN ADMIN) =================

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Total completed revenue (Chỉ tính đơn 'Hoàn tất')
    cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'Hoàn tất'")
    completed_revenue = cursor.fetchone()[0]

    # 2. Total orders count & pending orders count
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Chờ xử lý'")
    pending_orders_count = cursor.fetchone()[0]

    # 3. Total products count (distinct count in demo)
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # 4. Total stock and low stock count (stock <= 5)
    cursor.execute("SELECT COALESCE(SUM(stock), 0) FROM products")
    total_stock = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 5")
    low_stock_count = cursor.fetchone()[0]

    # 5. Order status breakdown (Nhịp vận hành)
    cursor.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status")
    status_rows = cursor.fetchall()
    status_counts = {'Chờ xử lý': 0, 'Đang giao': 0, 'Hoàn tất': 0, 'Đã hủy': 0}
    for row in status_rows:
        if row['status'] in status_counts:
            status_counts[row['status']] = row['cnt']

    # 6. Monthly comparison (Tháng trước: 09/2026 vs Tháng này: 10/2026)
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0) FROM orders 
        WHERE status = 'Hoàn tất' AND (created_at LIKE '2026-09%' OR created_at LIKE '%/09/2026%')
    ''')
    revenue_last_month = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0) FROM orders 
        WHERE status = 'Hoàn tất' AND (created_at LIKE '2026-10%' OR created_at LIKE '%/10/2026%')
    ''')
    revenue_this_month = cursor.fetchone()[0]

    # Count of orders per month
    cursor.execute('''
        SELECT COUNT(*) FROM orders 
        WHERE (created_at LIKE '2026-09%' OR created_at LIKE '%/09/2026%')
    ''')
    orders_last_month = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM orders 
        WHERE (created_at LIKE '2026-10%' OR created_at LIKE '%/10/2026%')
    ''')
    orders_this_month = cursor.fetchone()[0]

    # 7. Recent orders (Top 6 orders)
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 6")
    recent_orders = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('admin_dashboard.html',
                           completed_revenue=completed_revenue,
                           total_orders=total_orders,
                           pending_orders_count=pending_orders_count,
                           total_products=total_products,
                           total_stock=total_stock,
                           low_stock_count=low_stock_count,
                           status_counts=status_counts,
                           revenue_last_month=revenue_last_month,
                           revenue_this_month=revenue_this_month,
                           orders_last_month=orders_last_month,
                           orders_this_month=orders_this_month,
                           recent_orders=recent_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM categories")
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('admin_products.html', products=products, categories=categories)

@app.route('/admin/products/add', methods=['POST'])
@admin_required
def admin_product_add():
    name = request.form.get('name', '').strip()
    category_slug = request.form.get('category_slug', 'suit')
    price = int(request.form.get('price', 0))
    orig_price = request.form.get('original_price')
    orig_price = int(orig_price) if orig_price else None
    color = request.form.get('color', 'ĐEN')
    badge = request.form.get('badge', '')
    stock = int(request.form.get('stock', 10))
    sizes = request.form.get('sizes', 'S, M, L, XL')
    image_url = request.form.get('image_url') or 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80'
    description = request.form.get('description', '')
    is_featured = 1 if request.form.get('is_featured') else 0
    is_new = 1 if request.form.get('is_new_arrival') else 0

    import re
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-') + f"-{int(datetime.datetime.now().timestamp())}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, slug, category_slug, price, original_price, color, badge, stock, sizes, image_url, description, is_featured, is_new_arrival)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, slug, category_slug, price, orig_price, color, badge, stock, sizes, image_url, description, is_featured, is_new))
    conn.commit()
    conn.close()

    flash(f"Đã thêm sản phẩm '{name}' thành công!", 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash("Đã xóa sản phẩm khỏi hệ thống.", 'info')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    conn = get_connection()
    cursor = conn.cursor()
    status_filter = request.args.get('status', 'all')
    
    if status_filter != 'all':
        cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = [dict(row) for row in cursor.fetchall()]

    for ord_dict in orders:
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (ord_dict['id'],))
        ord_dict['items'] = [dict(item) for item in cursor.fetchall()]

    conn.close()
    return render_template('admin_orders.html', orders=orders, active_status=status_filter)

@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def admin_order_update_status(order_id):
    new_status = request.form.get('status')
    if new_status in ['Chờ xử lý', 'Đang giao', 'Hoàn tất', 'Đã hủy']:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()
        flash(f"Đã cập nhật trạng thái đơn hàng #{order_id} sang: {new_status}", 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        for key in ['store_name', 'store_address', 'store_phone', 'store_email', 'shipping_policy']:
            if key in request.form:
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, request.form[key]))
        conn.commit()
        flash("Đã lưu cài đặt cửa hàng thành công!", "success")
    
    cursor.execute("SELECT key, value FROM settings")
    settings = dict(cursor.fetchall())
    conn.close()
    return render_template('admin_settings.html', settings=settings)

if __name__ == '__main__':
    init_db()
    print("🚀 FREESHION Luxury Fashion E-Commerce Server starting at http://127.0.0.1:5000")
    print("👉 Khách hàng truy cập: http://127.0.0.1:5000")
    print("👉 Cổng Quản trị Admin: http://127.0.0.1:5000/admin (yêu cầu tài khoản admin@freeshion.vn / admin123)")
    app.run(debug=True, port=5000, host='0.0.0.0')
