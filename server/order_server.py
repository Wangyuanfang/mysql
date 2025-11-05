#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单系统HTTP服务端
提供订单查询和下载API
"""

import os
import json
import csv
from io import StringIO
from datetime import datetime
from flask import Flask, jsonify, request, send_file, Response
import mysql.connector
from mysql.connector import Error
import configparser

app = Flask(__name__)

# 数据库配置
def get_db_config():
    """从配置文件读取数据库配置"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'database.ini')

    if os.path.exists(config_path):
        config.read(config_path)
        return {
            'host': config.get('mysql', 'host', fallback='localhost'),
            'port': config.getint('mysql', 'port', fallback=3306),
            'user': config.get('mysql', 'user', fallback='root'),
            'password': config.get('mysql', 'password', fallback=''),
            'database': config.get('mysql', 'database', fallback='order_system')
        }
    else:
        # 默认配置
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'order_system')
        }

def get_db_connection():
    """获取数据库连接"""
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """获取所有地区列表"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT r.region_id, r.region_code, r.region_name, r.parent_region_id,
                   p.region_name as parent_region_name
            FROM regions r
            LEFT JOIN regions p ON r.parent_region_id = p.region_id
            ORDER BY r.region_id
        """
        cursor.execute(query)
        regions = cursor.fetchall()

        return jsonify({
            'success': True,
            'data': regions,
            'count': len(regions)
        })
    except Error as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/regions/<region_code>/orders', methods=['GET'])
def get_orders_by_region(region_code):
    """获取指定地区的订单列表"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # 先查询地区ID
        cursor.execute("SELECT region_id FROM regions WHERE region_code = %s", (region_code,))
        region = cursor.fetchone()

        if not region:
            return jsonify({'error': f'地区代码 {region_code} 不存在'}), 404

        region_id = region['region_id']

        # 查询该地区的订单
        query = """
            SELECT o.order_id, o.order_number, o.customer_name, o.customer_phone,
                   o.customer_email, o.product_name, o.quantity, o.unit_price,
                   o.total_amount, o.order_status, o.order_date, o.shipping_address,
                   o.remarks, r.region_code, r.region_name
            FROM orders o
            JOIN regions r ON o.region_id = r.region_id
            WHERE o.region_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (region_id,))
        orders = cursor.fetchall()

        # 转换日期时间为字符串
        for order in orders:
            if order['order_date']:
                order['order_date'] = order['order_date'].isoformat()

        return jsonify({
            'success': True,
            'region_code': region_code,
            'data': orders,
            'count': len(orders)
        })
    except Error as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/regions/<region_code>/orders/download', methods=['GET'])
def download_orders_by_region(region_code):
    """下载指定地区的订单文件（CSV格式）"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # 先查询地区ID
        cursor.execute("SELECT region_id, region_name FROM regions WHERE region_code = %s", (region_code,))
        region = cursor.fetchone()

        if not region:
            return jsonify({'error': f'地区代码 {region_code} 不存在'}), 404

        region_id = region['region_id']
        region_name = region['region_name']

        # 查询该地区的订单
        query = """
            SELECT o.order_number as '订单号', o.customer_name as '客户姓名',
                   o.customer_phone as '客户电话', o.customer_email as '客户邮箱',
                   o.product_name as '产品名称', o.quantity as '数量',
                   o.unit_price as '单价', o.total_amount as '总金额',
                   o.order_status as '订单状态', o.order_date as '下单时间',
                   o.shipping_address as '收货地址', o.remarks as '备注',
                   r.region_name as '地区'
            FROM orders o
            JOIN regions r ON o.region_id = r.region_id
            WHERE o.region_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (region_id,))
        orders = cursor.fetchall()

        if not orders:
            return jsonify({'error': f'地区 {region_code} 没有订单数据'}), 404

        # 创建CSV内容
        output = StringIO()

        # 获取字段名
        fieldnames = list(orders[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 写入数据
        for order in orders:
            # 转换日期时间为字符串
            if order['下单时间']:
                order['下单时间'] = order['下单时间'].strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(order)

        # 准备下载
        output.seek(0)
        filename = f"orders_{region_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            output.getvalue().encode('utf-8-sig'),  # 添加BOM以支持Excel正确打开
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    except Error as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/orders/stats', methods=['GET'])
def get_order_stats():
    """获取订单统计信息"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # 按地区统计订单数量和金额
        query = """
            SELECT r.region_code, r.region_name,
                   COUNT(o.order_id) as order_count,
                   COALESCE(SUM(o.total_amount), 0) as total_amount
            FROM regions r
            LEFT JOIN orders o ON r.region_id = o.region_id
            GROUP BY r.region_id, r.region_code, r.region_name
            HAVING order_count > 0
            ORDER BY total_amount DESC
        """
        cursor.execute(query)
        stats = cursor.fetchall()

        return jsonify({
            'success': True,
            'data': stats,
            'count': len(stats)
        })
    except Error as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500
    finally:
        cursor.close()
        connection.close()

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    port = int(os.getenv('SERVER_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"订单系统服务端启动在端口 {port}")
    print(f"API文档:")
    print(f"  - GET  /api/health - 健康检查")
    print(f"  - GET  /api/regions - 获取所有地区")
    print(f"  - GET  /api/regions/<region_code>/orders - 获取指定地区订单")
    print(f"  - GET  /api/regions/<region_code>/orders/download - 下载指定地区订单")
    print(f"  - GET  /api/orders/stats - 获取订单统计信息")

    app.run(host='0.0.0.0', port=port, debug=debug)
