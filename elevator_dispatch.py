#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两座电梯派梯算法实现
Elevator Dispatch Algorithm for Two Elevators
"""

from enum import Enum
from typing import List, Optional


class Direction(Enum):
    """电梯运行方向"""
    UP = 1      # 向上
    DOWN = -1   # 向下
    IDLE = 0    # 空闲


class Elevator:
    """电梯类"""

    def __init__(self, elevator_id: int, max_floor: int = 20, max_capacity: int = 10):
        """
        初始化电梯

        Args:
            elevator_id: 电梯ID
            max_floor: 最大楼层数
            max_capacity: 最大载客量
        """
        self.id = elevator_id
        self.current_floor = 1  # 当前楼层
        self.direction = Direction.IDLE  # 当前方向
        self.target_floors = []  # 目标楼层列表
        self.passengers = 0  # 当前乘客数
        self.max_floor = max_floor
        self.max_capacity = max_capacity

    def add_target(self, floor: int):
        """添加目标楼层"""
        if floor not in self.target_floors and 1 <= floor <= self.max_floor:
            self.target_floors.append(floor)
            self.target_floors.sort()

    def is_full(self) -> bool:
        """检查电梯是否满载"""
        return self.passengers >= self.max_capacity

    def move(self):
        """移动电梯一层"""
        if not self.target_floors:
            self.direction = Direction.IDLE
            return

        # 确定运行方向
        if self.direction == Direction.IDLE:
            if self.target_floors[0] > self.current_floor:
                self.direction = Direction.UP
            elif self.target_floors[0] < self.current_floor:
                self.direction = Direction.DOWN

        # 移动电梯
        if self.direction == Direction.UP:
            self.current_floor += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1

        # 检查是否到达目标楼层
        if self.current_floor in self.target_floors:
            self.target_floors.remove(self.current_floor)

            # 如果没有更多目标楼层,设置为空闲
            if not self.target_floors:
                self.direction = Direction.IDLE

    def calculate_distance(self, request_floor: int, request_direction: Direction) -> float:
        """
        计算电梯到达请求楼层的代价

        Args:
            request_floor: 请求楼层
            request_direction: 请求方向

        Returns:
            代价值(越小越好)
        """
        # 如果电梯满载,返回较大的代价
        if self.is_full():
            return float('inf')

        distance = abs(self.current_floor - request_floor)

        # 如果电梯空闲,代价就是距离
        if self.direction == Direction.IDLE:
            return distance

        # 如果电梯方向与请求方向相同
        if self.direction == request_direction:
            # 如果请求楼层在电梯前进方向上
            if (self.direction == Direction.UP and request_floor >= self.current_floor) or \
               (self.direction == Direction.DOWN and request_floor <= self.current_floor):
                return distance  # 顺路,代价较小
            else:
                # 需要先完成当前方向的任务再返回
                if self.target_floors:
                    if self.direction == Direction.UP:
                        max_target = max(self.target_floors)
                        return (max_target - self.current_floor) + (max_target - request_floor)
                    else:
                        min_target = min(self.target_floors)
                        return (self.current_floor - min_target) + (request_floor - min_target)
                return distance * 2

        # 如果方向相反,需要等电梯完成当前方向的任务
        if self.target_floors:
            if self.direction == Direction.UP:
                max_target = max(self.target_floors)
                return (max_target - self.current_floor) + (max_target - request_floor)
            else:
                min_target = min(self.target_floors)
                return (self.current_floor - min_target) + (request_floor - min_target)

        return distance * 1.5

    def __str__(self) -> str:
        """返回电梯状态的字符串表示"""
        direction_str = {
            Direction.UP: "↑",
            Direction.DOWN: "↓",
            Direction.IDLE: "○"
        }
        return f"电梯{self.id}: 楼层{self.current_floor} {direction_str[self.direction]} " \
               f"乘客{self.passengers}/{self.max_capacity} 目标{self.target_floors}"


class ElevatorDispatchSystem:
    """电梯调度系统"""

    def __init__(self, num_elevators: int = 2, max_floor: int = 20):
        """
        初始化调度系统

        Args:
            num_elevators: 电梯数量
            max_floor: 最大楼层数
        """
        self.elevators = [Elevator(i + 1, max_floor) for i in range(num_elevators)]
        self.max_floor = max_floor

    def dispatch(self, request_floor: int, direction: Direction) -> Optional[Elevator]:
        """
        派梯算法 - 选择最合适的电梯响应请求

        Args:
            request_floor: 请求楼层
            direction: 请求方向 (UP或DOWN)

        Returns:
            被选中的电梯
        """
        if not 1 <= request_floor <= self.max_floor:
            print(f"错误: 楼层 {request_floor} 超出范围 [1, {self.max_floor}]")
            return None

        # 计算每部电梯的代价
        best_elevator = None
        min_cost = float('inf')
        best_priority = -1  # 优先级分数

        for elevator in self.elevators:
            cost = elevator.calculate_distance(request_floor, direction)
            print(f"  电梯{elevator.id} 代价: {cost:.1f} (当前: {elevator.current_floor}层 {elevator.direction.name})")

            # 计算优先级(当代价相同时使用)
            priority = 0
            # 1. 方向相同且顺路的优先级更高
            if elevator.direction == direction:
                if (direction == Direction.UP and request_floor >= elevator.current_floor) or \
                   (direction == Direction.DOWN and request_floor <= elevator.current_floor):
                    priority += 10  # 顺路
            # 2. 空闲电梯优先级较高
            if elevator.direction == Direction.IDLE:
                priority += 5
            # 3. 乘客少的优先级较高
            priority += (elevator.max_capacity - elevator.passengers)

            # 选择代价最小的,代价相同时选择优先级高的
            if cost < min_cost or (cost == min_cost and priority > best_priority):
                min_cost = cost
                best_elevator = elevator
                best_priority = priority

        if best_elevator:
            best_elevator.add_target(request_floor)
            print(f"→ 选择电梯{best_elevator.id} (代价: {min_cost:.1f})")

        return best_elevator

    def print_status(self):
        """打印所有电梯状态"""
        print("\n当前电梯状态:")
        for elevator in self.elevators:
            print(f"  {elevator}")
        print()


def demo():
    """演示电梯调度算法"""
    print("=" * 60)
    print("两座电梯派梯算法演示")
    print("=" * 60)

    # 创建调度系统(2部电梯,20层楼)
    system = ElevatorDispatchSystem(num_elevators=2, max_floor=20)

    # 初始状态
    system.print_status()

    # 场景1: 1楼有人要上楼
    print("场景1: 1楼有人按上行按钮")
    system.dispatch(1, Direction.UP)
    system.print_status()

    # 场景2: 10楼有人要上楼
    print("场景2: 10楼有人按上行按钮")
    system.dispatch(10, Direction.UP)
    system.print_status()

    # 场景3: 5楼有人要下楼
    print("场景3: 5楼有人按下行按钮")
    system.dispatch(5, Direction.DOWN)
    system.print_status()

    # 模拟电梯1移动到目标
    print("模拟: 电梯1移动到1楼")
    elevator1 = system.elevators[0]
    while elevator1.current_floor != 1:
        elevator1.move()
    print(f"  {elevator1}")

    # 场景4: 15楼有人要下楼
    print("\n场景4: 15楼有人按下行按钮")
    system.dispatch(15, Direction.DOWN)
    system.print_status()

    # 场景5: 8楼有人要上楼
    print("场景5: 8楼有人按上行按钮")
    system.dispatch(8, Direction.UP)
    system.print_status()

    print("=" * 60)
    print("演示结束")
    print("=" * 60)


if __name__ == "__main__":
    demo()
