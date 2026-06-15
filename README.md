# 訂餐系統 - 使用說明

## 專案結構
```
restaurant/
├── app.py              # Flask 後端（API + 路由）
├── requirements.txt    # 套件清單
├── restaurant.db       # SQLite 資料庫（自動產生）
└── templates/
    ├── index.html      # 顧客點餐頁
    └── kitchen.html    # 廚師端管理頁
```

## 資料表設計
- **menu**：id, name, price, category
- **orders**：id, customer_name, item_name, quantity, total_price, status, created_at

## 啟動方式

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器
```bash
python app.py
```

### 3. 開啟瀏覽器
- 顧客點餐頁：http://localhost:5000
- 廚師端：http://localhost:5000/kitchen

## API 端點
| 方法   | 路徑                    | 說明             |
|--------|-------------------------|------------------|
| GET    | /api/menu               | 取得菜單列表     |
| GET    | /api/orders             | 取得所有訂單     |
| POST   | /api/orders             | 新增訂單         |
| PATCH  | /api/orders/<id>        | 更新訂單狀態     |
| DELETE | /api/orders/<id>        | 刪除訂單         |
