# 订单管理系统

基于 MySQL 的订单数据库系统，提供 HTTP API 服务端和客户端工具，用于查询和下载指定地区的订单数据。

## 项目结构

```
mysql/
├── database/           # 数据库相关
│   └── schema.sql     # 数据库初始化脚本
├── server/            # 服务端程序
│   └── order_server.py
├── client/            # 客户端程序
│   └── order_client.py
├── web/               # Web前端页面
│   └── index.html     # 订单下载界面
├── config/            # 配置文件
│   ├── database.ini.example    # 数据库配置示例
│   └── client.ini.example      # 客户端配置示例
├── downloads/         # 下载的订单文件（自动创建）
├── requirements.txt   # Python 依赖
└── README.md         # 项目文档
```

## 功能特性

### 数据库设计
- **地区表 (regions)**: 管理地区信息，支持层级结构（省-市）
- **订单表 (orders)**: 存储订单详细信息，包括客户信息、产品、金额、状态等
- 自带示例数据：11个地区，10条订单

### HTTP 服务端
提供 RESTful API 接口：
- `GET /api/health` - 健康检查
- `GET /api/regions` - 获取所有地区列表
- `GET /api/regions/<region_code>/orders` - 获取指定地区订单
- `GET /api/regions/<region_code>/orders/download` - 下载订单文件（CSV格式）
- `GET /api/orders/stats` - 获取订单统计信息

### Web 前端界面
提供美观的可视化操作界面：
- 🎨 现代化的渐变色设计，响应式布局
- 📋 下拉框选择地区，操作简单直观
- 📊 实时预览订单列表和统计信息
- ⬇️ 一键下载订单CSV文件
- 📈 下载进度条显示，实时反馈下载状态
- 🟢 服务器在线状态指示
- ✨ 流畅的交互动画和消息提示

### HTTP 客户端
命令行工具，支持：
- 查看所有可用地区
- 查看指定地区的订单列表
- 下载指定地区的订单文件为 CSV
- 查看订单统计信息
- 检查服务器连接状态

## 快速开始

### 1. 环境要求

- Python 3.7+
- MySQL 5.7+ 或 MariaDB 10.2+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库设置

#### 3.1 创建数据库和导入数据

```bash
# 登录 MySQL
mysql -u root -p

# 导入数据库结构和示例数据
source database/schema.sql

# 或者使用命令行直接导入
mysql -u root -p < database/schema.sql
```

#### 3.2 配置数据库连接

复制配置文件模板：
```bash
cp config/database.ini.example config/database.ini
```

编辑 `config/database.ini`，填入你的数据库信息：
```ini
[mysql]
host = localhost
port = 3306
user = root
password = your_password
database = order_system
```

### 4. 启动服务端

```bash
cd server
python order_server.py
```

服务端默认运行在 `http://localhost:5000`

你也可以通过环境变量配置：
```bash
SERVER_PORT=8080 DEBUG=true python order_server.py
```

或者使用启动脚本：
```bash
./start_server.sh
```

### 5. 使用 Web 界面（推荐）

启动服务端后，在浏览器中访问：

```
http://localhost:5000
```

**Web 界面使用步骤：**

1. **查看服务器状态**
   - 页面顶部会显示服务器在线状态
   - 🟢 绿色表示在线，🔴 红色表示离线

2. **选择地区**
   - 从下拉框中选择要查询的地区
   - 地区列表会自动从服务器加载

3. **预览订单**
   - 点击"👁️ 预览订单"按钮
   - 查看该地区的订单列表和统计信息
   - 包括订单数量、总金额等统计数据

4. **下载订单**
   - 点击"⬇️ 下载订单"按钮
   - 系统会显示下载进度条
   - 下载完成后自动保存CSV文件到浏览器默认下载位置

**界面特点：**
- 📱 响应式设计，支持手机、平板、电脑访问
- 🎨 美观的渐变色界面
- ⚡ 实时进度反馈
- 💡 智能错误提示

### 6. 使用命令行客户端

#### 6.1 配置客户端

复制配置文件模板：
```bash
cp config/client.ini.example config/client.ini
```

编辑 `config/client.ini`：
```ini
[server]
host = localhost
port = 5000
```

#### 6.2 客户端使用示例

**检查服务器连接：**
```bash
python client/order_client.py --check
```

**查看所有可用地区：**
```bash
python client/order_client.py --list-regions
```

**查看指定地区的订单：**
```bash
python client/order_client.py --view-orders CN-BJ
```

**下载指定地区的订单文件：**
```bash
# 下载北京地区的订单
python client/order_client.py --download CN-BJ

# 下载到指定目录
python client/order_client.py --download CN-BJ --output /path/to/output

# 简写形式
python client/order_client.py -d CN-GD-GZ -o ./my_downloads
```

**查看订单统计信息：**
```bash
python client/order_client.py --stats
```

**指定服务器地址：**
```bash
python client/order_client.py --server http://192.168.1.100:5000 --download CN-SH
```

## API 使用示例

### 使用 curl 测试 API

**获取所有地区：**
```bash
curl http://localhost:5000/api/regions
```

**获取指定地区订单：**
```bash
curl http://localhost:5000/api/regions/CN-BJ/orders
```

**下载订单文件：**
```bash
curl -O http://localhost:5000/api/regions/CN-BJ/orders/download
```

**获取统计信息：**
```bash
curl http://localhost:5000/api/orders/stats
```

### API 响应示例

**成功响应：**
```json
{
  "success": true,
  "region_code": "CN-BJ",
  "data": [
    {
      "order_id": 1,
      "order_number": "ORD20250101001",
      "customer_name": "张三",
      "product_name": "iPhone 15 Pro",
      "total_amount": 7999.00,
      "order_status": "delivered",
      "order_date": "2025-01-01T10:30:00"
    }
  ],
  "count": 1
}
```

**错误响应：**
```json
{
  "error": "地区代码 INVALID 不存在"
}
```

## 数据库表结构

### regions 表
| 字段 | 类型 | 说明 |
|------|------|------|
| region_id | INT | 主键 |
| region_code | VARCHAR(50) | 地区代码（唯一） |
| region_name | VARCHAR(100) | 地区名称 |
| parent_region_id | INT | 父地区ID |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### orders 表
| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | BIGINT | 主键 |
| order_number | VARCHAR(100) | 订单号（唯一） |
| region_id | INT | 地区ID（外键） |
| customer_name | VARCHAR(100) | 客户姓名 |
| customer_phone | VARCHAR(20) | 客户电话 |
| customer_email | VARCHAR(100) | 客户邮箱 |
| product_name | VARCHAR(200) | 产品名称 |
| quantity | INT | 数量 |
| unit_price | DECIMAL(10,2) | 单价 |
| total_amount | DECIMAL(10,2) | 总金额 |
| order_status | ENUM | 订单状态 |
| order_date | DATETIME | 下单时间 |
| shipping_address | TEXT | 收货地址 |
| remarks | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 示例数据说明

系统预置了以下地区和订单数据：

**地区：**
- 中国（CN）
  - 北京（CN-BJ）- 2个订单
  - 上海（CN-SH）- 1个订单
  - 广东（CN-GD）
    - 广州（CN-GD-GZ）- 2个订单
    - 深圳（CN-GD-SZ）- 2个订单
  - 浙江（CN-ZJ）
    - 杭州（CN-ZJ-HZ）- 1个订单
- 美国（US）
  - 加利福尼亚（US-CA）- 1个订单
  - 纽约（US-NY）- 1个订单

**订单状态：**
- `pending` - 待处理
- `confirmed` - 已确认
- `shipped` - 已发货
- `delivered` - 已送达
- `cancelled` - 已取消

## 常见问题

### 1. 数据库连接失败

确保：
- MySQL 服务正在运行
- `config/database.ini` 中的配置正确
- 数据库用户有足够的权限

### 2. 客户端无法连接服务器

确保：
- 服务端已启动
- 防火墙允许访问对应端口
- `config/client.ini` 中的服务器地址正确

### 3. 下载的 CSV 文件中文乱码

CSV 文件使用 UTF-8 BOM 编码，用 Excel 打开应该能正确显示中文。如果仍然乱码，可以：
- 使用记事本打开文件，另存为时选择 UTF-8 编码
- 使用 WPS Office 或 LibreOffice 打开

### 4. 如何添加新的地区或订单

可以直接在数据库中添加：

```sql
-- 添加新地区
INSERT INTO regions (region_code, region_name, parent_region_id)
VALUES ('CN-JS', '江苏', 1);

-- 添加新订单
INSERT INTO orders (order_number, region_id, customer_name, product_name,
                    quantity, unit_price, total_amount, order_status, order_date, shipping_address)
VALUES ('ORD20250106001', 3, '测试用户', '测试产品', 1, 100.00, 100.00, 'pending', NOW(), '测试地址');
```

## 扩展开发

### 添加新的 API 端点

在 `server/order_server.py` 中添加新的路由：

```python
@app.route('/api/custom-endpoint', methods=['GET'])
def custom_endpoint():
    # 你的逻辑
    return jsonify({'data': 'your_data'})
```

### 客户端添加新功能

在 `client/order_client.py` 的 `OrderClient` 类中添加新方法。

## 安全建议

1. **不要将配置文件提交到版本控制**
   - `config/database.ini` 和 `config/client.ini` 已在 `.gitignore` 中

2. **生产环境建议**
   - 使用环境变量存储敏感信息
   - 启用 HTTPS
   - 添加 API 认证机制（如 JWT）
   - 限制 API 访问频率
   - 使用数据库连接池

3. **数据库安全**
   - 使用强密码
   - 限制数据库用户权限
   - 定期备份数据

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 Issue 联系。
