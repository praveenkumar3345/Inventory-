from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = "1234"

# ----------------- LOGIN -----------------
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    user = request.form['username']
    password = request.form['password']
    if user == "admin" and password == "3345":
        session['user'] = 'admin'
        return redirect(url_for('inventory'))
    return "Invalid credentials!"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ----------------- INVENTORY PAGE -----------------
@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', products=products)


# ----------------- ADD PRODUCT -----------------
# ----------------- ADD PRODUCT -----------------
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, quantity, price, description, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, category, quantity, price, description, image))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('inventory'))

    # for GET
    return render_template('edit_product.html', product=None)


# ----------------- EDIT PRODUCT -----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']

        cursor.execute("""
            UPDATE products
            SET name=%s, category=%s, quantity=%s, price=%s, description=%s, image=%s
            WHERE id=%s
        """, (name, category, quantity, price, description, image, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('inventory'))

    cursor.close()
    conn.close()
    return render_template('edit_product.html', product=product)


# ----------------- PRODUCT DETAIL -----------------
@app.route('/product/<int:id>')
def product_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    # Track views
    cursor.execute("UPDATE products SET views = IFNULL(views, 0) + 1 WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('product_detail.html', product=product)


# ----------------- DELETE PRODUCT -----------------
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    """Delete a product from the database."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Product deleted successfully!'})
    except Exception as e:
        print("Error deleting product:", e)
        return jsonify({'success': False, 'message': str(e)}), 500


# ----------------- FILTER PRODUCTS -----------------
@app.route('/filter')
def filter_products():
    category = request.args.get('category', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("SELECT * FROM products WHERE category=%s", (category,))
    else:
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)


# ----------------- SEARCH -----------------
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE name LIKE %s OR category LIKE %s",
                   (f"%{query}%", f"%{query}%"))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(products)


# ----------------- LOCATIONS (for branches/warehouses) -----------------
@app.route('/locations')
def locations_page():
    """Render the dedicated locations management page."""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('locations.html')

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Return a JSON list of locations with id, branch_name and city.

    Assumes a `locations` table exists with columns (id, branch_name, city).
    If the table doesn't exist or an error occurs, returns dummy data.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, branch_name, city FROM locations")
        locations = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(locations)
    except Exception as e:
        # Fail gracefully for projects without a locations table
        print("Error fetching locations:", e)
        # Return dummy data as fallback
        dummy_locations = [
            {"id": "L100", "branch_name": "Main Warehouse", "city": "Mumbai"},
            {"id": "L101", "branch_name": "South Branch", "city": "Delhi"},
            {"id": "L123", "branch_name": "Main Warehouse", "city": "Mumbai"},
            {"id": "L124", "branch_name": "South Branch", "city": "Delhi"},
            {"id": "L125", "branch_name": "East Depot", "city": "Bengaluru"},
            {"id": "L126", "branch_name": "North Branch", "city": "Coimbatore"},
            {"id": "L128", "branch_name": "Russov Main Area", "city": "Kerala"}
        ]
        return jsonify(dummy_locations)

@app.route('/api/locations/add', methods=['POST'])
def add_location():
    """Add a new location to the database."""
    try:
        branch_name = request.form.get('branch_name')
        city = request.form.get('city')
        
        if not branch_name or not city:
            return jsonify({'success': False, 'message': 'Branch name and city are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO locations (branch_name, city) VALUES (%s, %s)",
            (branch_name, city)
        )
        conn.commit()
        location_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'id': location_id})
    except Exception as e:
        print("Error adding location:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/locations/delete/<int:loc_id>', methods=['POST', 'DELETE'])
def delete_location(loc_id):
    """Delete a location from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM locations WHERE id = %s", (loc_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print("Error deleting location:", e)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/locations/update/<int:loc_id>', methods=['POST'])
def update_location(loc_id):
    """Update a location's branch_name and city.

    Expects form data: branch_name, city
    Returns JSON {success: true/false, message: ...}
    """
    branch = request.form.get('branch_name')
    city = request.form.get('city')

    if not branch or not city:
        return jsonify({'success': False, 'message': 'branch_name and city are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE locations
            SET branch_name = %s, city = %s
            WHERE id = %s
            """,
            (branch, city, loc_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print("Error updating location:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

# ----------------- ANALYZE -----------------
@app.route('/analyze')
def analyze():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT SUM(quantity) AS total_quantity FROM products")
    total_quantity = cursor.fetchone()['total_quantity'] or 0

    cursor.execute("""
        SELECT category, SUM(quantity) AS total_stock, COUNT(*) AS total_products
        FROM products
        GROUP BY category
    """)
    category_data = cursor.fetchall()

    cursor.execute("SELECT name, quantity FROM products ORDER BY quantity DESC LIMIT 1")
    top_product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('analyze.html',
                           total_quantity=total_quantity,
                           category_data=category_data,
                           top_product=top_product)


if __name__ == "__main__":
    app.run(debug=True)
