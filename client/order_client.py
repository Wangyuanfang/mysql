#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单系统HTTP客户端
用于下载指定地区的订单文件
"""

import os
import sys
import argparse
import requests
import json
from datetime import datetime
import configparser

class OrderClient:
    """订单系统客户端"""

    def __init__(self, server_url=None):
        """初始化客户端"""
        if server_url:
            self.server_url = server_url
        else:
            self.server_url = self._get_server_url_from_config()

    def _get_server_url_from_config(self):
        """从配置文件读取服务器地址"""
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'client.ini')

        if os.path.exists(config_path):
            config.read(config_path)
            host = config.get('server', 'host', fallback='localhost')
            port = config.getint('server', 'port', fallback=5000)
            return f"http://{host}:{port}"
        else:
            return os.getenv('SERVER_URL', 'http://localhost:5000')

    def check_health(self):
        """检查服务器健康状态"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ 服务器连接正常")
                return True
            else:
                print(f"✗ 服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ 无法连接到服务器: {e}")
            return False

    def get_regions(self):
        """获取所有地区列表"""
        try:
            response = requests.get(f"{self.server_url}/api/regions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])
                else:
                    print(f"获取地区列表失败: {data.get('error', '未知错误')}")
                    return []
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            return []

    def display_regions(self):
        """显示所有地区列表"""
        regions = self.get_regions()
        if not regions:
            print("没有找到地区数据")
            return

        print("\n可用地区列表:")
        print("-" * 80)
        print(f"{'地区代码':<15} {'地区名称':<20} {'父地区':<20}")
        print("-" * 80)

        for region in regions:
            region_code = region.get('region_code', '')
            region_name = region.get('region_name', '')
            parent_name = region.get('parent_region_name', '-')
            print(f"{region_code:<15} {region_name:<20} {parent_name:<20}")

        print("-" * 80)
        print(f"总计: {len(regions)} 个地区\n")

    def get_orders(self, region_code):
        """获取指定地区的订单列表"""
        try:
            response = requests.get(
                f"{self.server_url}/api/regions/{region_code}/orders",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])
                else:
                    print(f"获取订单失败: {data.get('error', '未知错误')}")
                    return []
            elif response.status_code == 404:
                print(f"地区代码 '{region_code}' 不存在")
                return []
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            return []

    def display_orders(self, region_code):
        """显示指定地区的订单"""
        orders = self.get_orders(region_code)
        if not orders:
            print(f"地区 '{region_code}' 没有订单数据")
            return

        print(f"\n地区 '{region_code}' 的订单列表:")
        print("-" * 120)
        print(f"{'订单号':<18} {'客户姓名':<12} {'产品名称':<25} {'数量':<6} {'总金额':<12} {'状态':<12} {'下单时间':<20}")
        print("-" * 120)

        for order in orders:
            order_number = order.get('order_number', '')
            customer_name = order.get('customer_name', '')
            product_name = order.get('product_name', '')
            quantity = order.get('quantity', 0)
            total_amount = order.get('total_amount', 0)
            status = order.get('order_status', '')
            order_date = order.get('order_date', '')

            print(f"{order_number:<18} {customer_name:<12} {product_name:<25} {quantity:<6} {total_amount:<12.2f} {status:<12} {order_date:<20}")

        print("-" * 120)
        print(f"总计: {len(orders)} 个订单\n")

    def download_orders(self, region_code, output_dir=None):
        """下载指定地区的订单文件"""
        try:
            print(f"正在下载地区 '{region_code}' 的订单数据...")

            response = requests.get(
                f"{self.server_url}/api/regions/{region_code}/orders/download",
                timeout=30
            )

            if response.status_code == 200:
                # 确定保存目录
                if output_dir is None:
                    output_dir = os.path.join(os.path.dirname(__file__), '..', 'downloads')

                os.makedirs(output_dir, exist_ok=True)

                # 生成文件名
                filename = f"orders_{region_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                filepath = os.path.join(output_dir, filename)

                # 保存文件
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"✓ 下载成功!")
                print(f"  文件保存至: {os.path.abspath(filepath)}")
                print(f"  文件大小: {len(response.content)} 字节")
                return filepath

            elif response.status_code == 404:
                error_data = response.json()
                print(f"✗ 下载失败: {error_data.get('error', '未知错误')}")
                return None
            else:
                print(f"✗ 下载失败，状态码: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"✗ 下载出错: {e}")
            return None

    def get_stats(self):
        """获取订单统计信息"""
        try:
            response = requests.get(f"{self.server_url}/api/orders/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])
                else:
                    print(f"获取统计信息失败: {data.get('error', '未知错误')}")
                    return []
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            return []

    def display_stats(self):
        """显示订单统计信息"""
        stats = self.get_stats()
        if not stats:
            print("没有统计数据")
            return

        print("\n订单统计信息:")
        print("-" * 80)
        print(f"{'地区代码':<15} {'地区名称':<20} {'订单数量':<15} {'总金额':<15}")
        print("-" * 80)

        total_orders = 0
        total_amount = 0.0

        for stat in stats:
            region_code = stat.get('region_code', '')
            region_name = stat.get('region_name', '')
            order_count = stat.get('order_count', 0)
            amount = float(stat.get('total_amount', 0))

            total_orders += order_count
            total_amount += amount

            print(f"{region_code:<15} {region_name:<20} {order_count:<15} {amount:<15.2f}")

        print("-" * 80)
        print(f"{'总计':<35} {total_orders:<15} {total_amount:<15.2f}")
        print("-" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='订单系统客户端 - 下载指定地区的订单文件')
    parser.add_argument('--server', '-s', help='服务器地址 (例如: http://localhost:5000)')
    parser.add_argument('--region', '-r', help='地区代码 (例如: CN-BJ)')
    parser.add_argument('--list-regions', '-l', action='store_true', help='显示所有可用地区')
    parser.add_argument('--view-orders', '-v', help='查看指定地区的订单列表')
    parser.add_argument('--download', '-d', help='下载指定地区的订单文件')
    parser.add_argument('--output', '-o', help='输出目录 (默认: ../downloads)')
    parser.add_argument('--stats', action='store_true', help='显示订单统计信息')
    parser.add_argument('--check', action='store_true', help='检查服务器连接状态')

    args = parser.parse_args()

    # 创建客户端实例
    client = OrderClient(server_url=args.server)

    # 检查服务器连接
    if args.check:
        client.check_health()
        return

    # 显示地区列表
    if args.list_regions:
        client.display_regions()
        return

    # 查看订单列表
    if args.view_orders:
        client.display_orders(args.view_orders)
        return

    # 下载订单文件
    if args.download:
        client.download_orders(args.download, args.output)
        return

    # 显示统计信息
    if args.stats:
        client.display_stats()
        return

    # 如果指定了region参数，则下载该地区的订单
    if args.region:
        client.download_orders(args.region, args.output)
        return

    # 如果没有指定任何参数，显示帮助信息
    parser.print_help()


if __name__ == '__main__':
    main()
