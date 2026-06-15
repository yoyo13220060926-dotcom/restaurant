from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "restaurant.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 餐點資料表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # 訂單資料表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT '待處理',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 預設菜單資料（如果是空的才插入）
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        sample_menu = [
            ("牛肉麵", 120, "主食"),
            ("炒飯", 90, "主食"),
            ("水餃（10顆）", 70, "主食"),
            ("紅茶", 30, "飲料"),
            ("珍珠奶茶", 55, "飲料"),
            ("味噌湯", 40, "湯品"),
        ]
        cursor.executemany("INSERT INTO menu (name, price, category) VALUES (?, ?, ?)", sample_menu)

    conn.commit()
    conn.close()

# ── 頁面路由 ──────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/kitchen")
def kitchen():
    return render_template("kitchen.html")

# ── 菜單 API ──────────────────────────────────────
@app.route("/api/menu", methods=["GET"])
def get_menu():
    conn = get_db()
    items = conn.execute("SELECT * FROM menu ORDER BY category, id").fetchall()
    conn.close()
    return jsonify([dict(i) for i in items])

# ── 訂單 API ──────────────────────────────────────
@app.route("/api/orders", methods=["GET"])
def get_orders():
    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    customer_name = data.get("customer_name", "").strip()
    item_name = data.get("item_name", "").strip()
    quantity = data.get("quantity", 1)
    total_price = data.get("total_price", 0)

    if not customer_name or not item_name or quantity < 1:
        return jsonify({"error": "資料不完整"}), 400

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO orders (customer_name, item_name, quantity, total_price) VALUES (?, ?, ?, ?)",
        (customer_name, item_name, quantity, total_price)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "訂單建立成功", "order_id": order_id}), 201

@app.route("/api/orders/<int:order_id>", methods=["PATCH"])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")
    valid_statuses = ["待處理", "製作中", "已完成", "已取消"]

    if new_status not in valid_statuses:
        return jsonify({"error": "無效的狀態"}), 400

    conn = get_db()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "狀態已更新"})

@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    conn = get_db()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "訂單已刪除"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
