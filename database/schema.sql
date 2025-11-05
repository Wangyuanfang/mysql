-- 订单数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS order_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE order_system;

-- 地区表
CREATE TABLE IF NOT EXISTS regions (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_code VARCHAR(50) NOT NULL UNIQUE COMMENT '地区代码',
    region_name VARCHAR(100) NOT NULL COMMENT '地区名称',
    parent_region_id INT DEFAULT NULL COMMENT '父地区ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_region_code (region_code),
    FOREIGN KEY (parent_region_id) REFERENCES regions(region_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地区信息表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(100) NOT NULL UNIQUE COMMENT '订单号',
    region_id INT NOT NULL COMMENT '地区ID',
    customer_name VARCHAR(100) NOT NULL COMMENT '客户姓名',
    customer_phone VARCHAR(20) COMMENT '客户电话',
    customer_email VARCHAR(100) COMMENT '客户邮箱',
    product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
    quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '总金额',
    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending' COMMENT '订单状态',
    order_date DATETIME NOT NULL COMMENT '下单时间',
    shipping_address TEXT COMMENT '收货地址',
    remarks TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_number (order_number),
    INDEX idx_region_id (region_id),
    INDEX idx_order_date (order_date),
    INDEX idx_order_status (order_status),
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单信息表';

-- 插入示例地区数据
INSERT INTO regions (region_code, region_name, parent_region_id) VALUES
('CN', '中国', NULL),
('CN-BJ', '北京', 1),
('CN-SH', '上海', 1),
('CN-GD', '广东', 1),
('CN-GD-GZ', '广州', 4),
('CN-GD-SZ', '深圳', 4),
('CN-ZJ', '浙江', 1),
('CN-ZJ-HZ', '杭州', 7),
('US', '美国', NULL),
('US-CA', '加利福尼亚', 9),
('US-NY', '纽约', 9);

-- 插入示例订单数据
INSERT INTO orders (order_number, region_id, customer_name, customer_phone, customer_email, product_name, quantity, unit_price, total_amount, order_status, order_date, shipping_address, remarks) VALUES
('ORD20250101001', 2, '张三', '13800138000', 'zhangsan@example.com', 'iPhone 15 Pro', 1, 7999.00, 7999.00, 'delivered', '2025-01-01 10:30:00', '北京市朝阳区xxx街道xxx号', '请尽快发货'),
('ORD20250101002', 3, '李四', '13900139000', 'lisi@example.com', 'MacBook Pro', 1, 12999.00, 12999.00, 'shipped', '2025-01-01 11:00:00', '上海市浦东新区xxx路xxx号', NULL),
('ORD20250102001', 5, '王五', '13700137000', 'wangwu@example.com', 'iPad Air', 2, 4399.00, 8798.00, 'confirmed', '2025-01-02 09:15:00', '广州市天河区xxx大道xxx号', '需要开发票'),
('ORD20250102002', 6, '赵六', '13600136000', 'zhaoliu@example.com', 'AirPods Pro', 3, 1899.00, 5697.00, 'pending', '2025-01-02 14:20:00', '深圳市南山区xxx路xxx号', NULL),
('ORD20250103001', 8, '钱七', '13500135000', 'qianqi@example.com', 'Apple Watch', 1, 2999.00, 2999.00, 'delivered', '2025-01-03 16:45:00', '杭州市西湖区xxx街xxx号', '顺丰快递'),
('ORD20250103002', 2, '孙八', '13400134000', 'sunba@example.com', 'Mac Mini', 1, 4299.00, 4299.00, 'shipped', '2025-01-03 17:30:00', '北京市海淀区xxx路xxx号', NULL),
('ORD20250104001', 10, 'John Smith', '+1-555-0100', 'john@example.com', 'iPhone 15', 2, 799.00, 1598.00, 'confirmed', '2025-01-04 08:00:00', '123 Main St, Los Angeles, CA', 'Express shipping'),
('ORD20250104002', 11, 'Jane Doe', '+1-555-0200', 'jane@example.com', 'MacBook Air', 1, 1099.00, 1099.00, 'pending', '2025-01-04 10:30:00', '456 Park Ave, New York, NY', NULL),
('ORD20250105001', 5, '周九', '13300133000', 'zhoujiu@example.com', 'HomePod', 2, 2299.00, 4598.00, 'pending', '2025-01-05 11:00:00', '广州市越秀区xxx路xxx号', NULL),
('ORD20250105002', 6, '吴十', '13200132000', 'wushi@example.com', 'Magic Keyboard', 1, 2399.00, 2399.00, 'confirmed', '2025-01-05 15:20:00', '深圳市福田区xxx大道xxx号', '白色款');
