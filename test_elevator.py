#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电梯派梯算法测试用例
Test cases for elevator dispatch algorithm
"""

import unittest
from elevator_dispatch import Elevator, Direction, ElevatorDispatchSystem


class TestElevator(unittest.TestCase):
    """测试电梯类"""

    def test_elevator_initialization(self):
        """测试电梯初始化"""
        elevator = Elevator(1, max_floor=20, max_capacity=10)
        self.assertEqual(elevator.id, 1)
        self.assertEqual(elevator.current_floor, 1)
        self.assertEqual(elevator.direction, Direction.IDLE)
        self.assertEqual(elevator.passengers, 0)
        self.assertEqual(len(elevator.target_floors), 0)

    def test_add_target(self):
        """测试添加目标楼层"""
        elevator = Elevator(1)
        elevator.add_target(5)
        elevator.add_target(10)
        elevator.add_target(3)
        self.assertEqual(elevator.target_floors, [3, 5, 10])

    def test_is_full(self):
        """测试满载检测"""
        elevator = Elevator(1, max_capacity=10)
        self.assertFalse(elevator.is_full())
        elevator.passengers = 10
        self.assertTrue(elevator.is_full())

    def test_move_up(self):
        """测试向上移动"""
        elevator = Elevator(1)
        elevator.current_floor = 1
        elevator.add_target(5)
        elevator.move()
        self.assertEqual(elevator.current_floor, 2)
        self.assertEqual(elevator.direction, Direction.UP)

    def test_move_down(self):
        """测试向下移动"""
        elevator = Elevator(1)
        elevator.current_floor = 10
        elevator.add_target(5)
        elevator.move()
        self.assertEqual(elevator.current_floor, 9)
        self.assertEqual(elevator.direction, Direction.DOWN)

    def test_calculate_distance_idle(self):
        """测试空闲电梯的代价计算"""
        elevator = Elevator(1)
        elevator.current_floor = 5
        elevator.direction = Direction.IDLE
        cost = elevator.calculate_distance(10, Direction.UP)
        self.assertEqual(cost, 5)  # 距离为5层

    def test_calculate_distance_full(self):
        """测试满载电梯的代价"""
        elevator = Elevator(1, max_capacity=10)
        elevator.passengers = 10
        cost = elevator.calculate_distance(10, Direction.UP)
        self.assertEqual(cost, float('inf'))


class TestElevatorDispatchSystem(unittest.TestCase):
    """测试电梯调度系统"""

    def test_system_initialization(self):
        """测试系统初始化"""
        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)
        self.assertEqual(len(system.elevators), 2)
        self.assertEqual(system.max_floor, 20)

    def test_dispatch_basic(self):
        """测试基本派梯"""
        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)
        elevator = system.dispatch(10, Direction.UP)
        self.assertIsNotNone(elevator)
        self.assertIn(10, elevator.target_floors)

    def test_dispatch_invalid_floor(self):
        """测试无效楼层"""
        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)
        elevator = system.dispatch(25, Direction.UP)
        self.assertIsNone(elevator)

    def test_dispatch_load_balancing(self):
        """测试负载均衡"""
        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)

        # 电梯1在10楼向上
        system.elevators[0].current_floor = 10
        system.elevators[0].direction = Direction.UP
        system.elevators[0].add_target(15)

        # 电梯2在1楼空闲
        system.elevators[1].current_floor = 1
        system.elevators[1].direction = Direction.IDLE

        # 在5楼请求下行,应该选择更近的电梯2
        elevator = system.dispatch(5, Direction.DOWN)
        self.assertEqual(elevator.id, 2)


class TestComplexScenarios(unittest.TestCase):
    """测试复杂场景"""

    def test_scenario_rush_hour(self):
        """测试高峰期场景"""
        print("\n" + "=" * 60)
        print("测试场景: 高峰期多个请求")
        print("=" * 60)

        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)

        # 模拟早高峰,多人在底层等待上楼
        requests = [
            (1, Direction.UP),
            (2, Direction.UP),
            (3, Direction.UP),
            (1, Direction.UP),
        ]

        for floor, direction in requests:
            print(f"\n请求: {floor}楼 {'上行' if direction == Direction.UP else '下行'}")
            system.dispatch(floor, direction)
            system.print_status()

    def test_scenario_opposite_directions(self):
        """测试相反方向的请求"""
        print("\n" + "=" * 60)
        print("测试场景: 相反方向的请求")
        print("=" * 60)

        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)

        # 设置初始状态
        system.elevators[0].current_floor = 5
        system.elevators[0].direction = Direction.UP
        system.elevators[0].add_target(10)

        system.elevators[1].current_floor = 15
        system.elevators[1].direction = Direction.DOWN
        system.elevators[1].add_target(5)

        system.print_status()

        # 在8楼请求上行
        print("请求: 8楼上行")
        elevator = system.dispatch(8, Direction.UP)
        print(f"选中电梯: {elevator.id}")
        self.assertEqual(elevator.id, 1)  # 应该选择电梯1,因为它在上行且在下方

        # 在12楼请求下行
        print("\n请求: 12楼下行")
        elevator = system.dispatch(12, Direction.DOWN)
        print(f"选中电梯: {elevator.id}")
        self.assertEqual(elevator.id, 2)  # 应该选择电梯2,因为它在下行且在上方

    def test_scenario_capacity(self):
        """测试容量限制场景"""
        print("\n" + "=" * 60)
        print("测试场景: 容量限制")
        print("=" * 60)

        system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)

        # 电梯1满载
        system.elevators[0].passengers = 10
        system.elevators[0].current_floor = 5

        # 电梯2较远但有空间
        system.elevators[1].current_floor = 15

        system.print_status()

        # 在6楼请求,应该选择远但有空间的电梯2
        print("请求: 6楼上行 (电梯1满载)")
        elevator = system.dispatch(6, Direction.UP)
        print(f"选中电梯: {elevator.id}")
        self.assertEqual(elevator.id, 2)  # 应该选择电梯2,因为电梯1满载


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行电梯派梯算法测试")
    print("=" * 60)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestElevator))
    suite.addTests(loader.loadTestsFromTestCase(TestElevatorDispatchSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexScenarios))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"测试完成: 运行 {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
