# 附录C：Python代码示例

## 完整IK实现示例

本附录包含完整的、可运行的Python代码示例，涵盖本教程中的主要IK算法。

---

## C.1 环境设置

```python
# 安装所需库
# pip install numpy matplotlib

import numpy as np
import matplotlib.pyplot as plt
import math
from typing import Tuple, List, Optional
```

---

## C.2 基础工具函数

### C.2.1 向量和矩阵工具

```python
def normalize(v):
    """归一化向量"""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def rotation_matrix_2d(theta):
    """2D旋转矩阵"""
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, -s],
        [s, c]
    ])

def rotation_matrix_z(theta):
    """绕z轴的3D旋转矩阵"""
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])

def transformation_matrix_2d(theta, tx, ty):
    """2D齐次变换矩阵"""
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([
        [c, -s, tx],
        [s, c, ty],
        [0, 0, 1]
    ])

def angle_difference(a, b):
    """计算两角度差（处理环绕）"""
    diff = a - b
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff
```

---

## C.3 正向运动学

### C.3.1 2D FK

```python
class Arm2D:
    """2D机械臂类"""
    
    def __init__(self, lengths):
        """
        参数:
            lengths: 各段连杆长度列表
        """
        self.lengths = np.array(lengths)
        self.num_joints = len(lengths)
        self.angles = np.zeros(self.num_joints)
    
    def forward_kinematics(self, angles=None):
        """
        计算正向运动学
        
        返回:
            positions: 所有关节位置（包括基座和末端）
        """
        if angles is None:
            angles = self.angles
        
        positions = [np.array([0.0, 0.0])]  # 基座
        current_angle = 0
        current_pos = np.array([0.0, 0.0])
        
        for i, (angle, length) in enumerate(zip(angles, self.lengths)):
            current_angle += angle
            current_pos = current_pos + length * np.array([
                math.cos(current_angle),
                math.sin(current_angle)
            ])
            positions.append(current_pos.copy())
        
        return np.array(positions)
    
    def get_end_effector(self, angles=None):
        """获取末端执行器位置"""
        positions = self.forward_kinematics(angles)
        return positions[-1]
    
    def plot(self, angles=None, target=None, ax=None):
        """绘制机械臂"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        positions = self.forward_kinematics(angles)
        
        # 绘制连杆
        ax.plot(positions[:, 0], positions[:, 1], 
                'o-', linewidth=3, markersize=10, label='Arm')
        
        # 绘制关节
        ax.plot(positions[:-1, 0], positions[:-1, 1], 
                'ro', markersize=8, label='Joints')
        
        # 绘制末端执行器
        ax.plot(positions[-1, 0], positions[-1, 1], 
                'g^', markersize=12, label='End Effector')
        
        # 绘制目标（如果有）
        if target is not None:
            ax.plot(target[0], target[1], 
                    'r*', markersize=15, label='Target')
        
        # 设置
        total_length = sum(self.lengths)
        ax.set_xlim(-total_length * 1.2, total_length * 1.2)
        ax.set_ylim(-total_length * 1.2, total_length * 1.2)
        ax.set_aspect('equal')
        ax.grid(True)
        ax.legend()
        ax.set_title('2D Robotic Arm')
        
        return ax

# 示例使用
arm = Arm2D([3, 2, 1])
arm.angles = np.array([math.radians(30), 
                       math.radians(45), 
                       math.radians(-30)])
arm.plot()
plt.show()
```

---

## C.4 双关节IK（解析法）

```python
def two_link_ik(target_x, target_y, L1, L2, elbow_up=True):
    """
    双关节2D IK（解析解）
    
    参数:
        target_x, target_y: 目标位置
        L1, L2: 连杆长度
        elbow_up: True=肘部向上，False=肘部向下
    
    返回:
        (theta1, theta2): 关节角度（弧度），或None（不可达）
    """
    # 目标距离
    d = math.sqrt(target_x**2 + target_y**2)
    
    # 可达性检查
    if d > L1 + L2 or d < abs(L1 - L2):
        return None
    
    # 计算theta2
    cos_theta2 = (d**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_theta2 = max(-1, min(1, cos_theta2))  # 钳位
    
    if elbow_up:
        theta2 = math.acos(cos_theta2)
    else:
        theta2 = -math.acos(cos_theta2)
    
    # 计算theta1
    alpha = math.atan2(target_y, target_x)
    beta = math.atan2(L2 * math.sin(theta2), 
                      L1 + L2 * math.cos(theta2))
    theta1 = alpha - beta
    
    return (theta1, theta2)

# 示例使用
L1, L2 = 3, 2
target = (3, 2)

# 肘部向上解
result = two_link_ik(target[0], target[1], L1, L2, elbow_up=True)
if result:
    theta1, theta2 = result
    print(f"肘部向上: θ₁={math.degrees(theta1):.2f}°, "
          f"θ₂={math.degrees(theta2):.2f}°")
    
    # 可视化
    arm = Arm2D([L1, L2])
    arm.angles = np.array([theta1, theta2])
    arm.plot(target=target)
    plt.title('Two-Link IK - Elbow Up')
    plt.show()

# 肘部向下解
result = two_link_ik(target[0], target[1], L1, L2, elbow_up=False)
if result:
    theta1, theta2 = result
    print(f"肘部向下: θ₁={math.degrees(theta1):.2f}°, "
          f"θ₂={math.degrees(theta2):.2f}°")
```

---

## C.5 CCD算法

```python
def ccd_ik(arm, target, max_iterations=100, tolerance=0.01):
    """
    循环坐标下降（CCD）IK算法
    
    参数:
        arm: Arm2D对象
        target: 目标位置[x, y]
        max_iterations: 最大迭代次数
        tolerance: 收敛容差
    
    返回:
        成功则返回True，否则False
    """
    target = np.array(target)
    
    for iteration in range(max_iterations):
        # 从末端到基座遍历关节
        for i in range(arm.num_joints - 1, -1, -1):
            # 获取当前所有位置
            positions = arm.forward_kinematics()
            
            # 当前关节位置
            joint_pos = positions[i]
            
            # 末端执行器位置
            end_pos = positions[-1]
            
            # 如果已经足够接近目标
            if np.linalg.norm(end_pos - target) < tolerance:
                return True
            
            # 计算向量
            to_end = end_pos - joint_pos
            to_target = target - joint_pos
            
            # 计算旋转角度
            angle = math.atan2(to_target[1], to_target[0]) - \
                    math.atan2(to_end[1], to_end[0])
            
            # 归一化角度到[-π, π]
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            
            # 更新关节角度
            arm.angles[i] += angle
    
    # 检查最终是否收敛
    final_pos = arm.get_end_effector()
    return np.linalg.norm(final_pos - target) < tolerance

# 示例使用
arm = Arm2D([2, 2, 1.5, 1])
target = np.array([3, 3])

print("CCD IK求解中...")
success = ccd_ik(arm, target)

if success:
    print("成功！")
    print(f"关节角度: {np.degrees(arm.angles)}")
    arm.plot(target=target)
    plt.title('CCD IK Solution')
    plt.show()
else:
    print("未收敛")
```

---

## C.6 FABRIK算法

```python
def fabrik_ik(arm, target, max_iterations=100, tolerance=0.01):
    """
    FABRIK（Forward And Backward Reaching IK）算法
    
    参数:
        arm: Arm2D对象
        target: 目标位置[x, y]
        max_iterations: 最大迭代次数
        tolerance: 收敛容差
    
    返回:
        成功则返回True，否则False
    """
    target = np.array(target)
    base = np.array([0.0, 0.0])
    
    # 检查可达性
    total_length = sum(arm.lengths)
    dist_to_target = np.linalg.norm(target - base)
    
    if dist_to_target > total_length:
        # 不可达，伸向目标
        direction = normalize(target - base)
        positions = [base]
        for length in arm.lengths:
            positions.append(positions[-1] + direction * length)
        _update_angles_from_positions(arm, positions)
        return False
    
    # 初始化位置
    positions = arm.forward_kinematics().tolist()
    
    for iteration in range(max_iterations):
        # 检查收敛
        if np.linalg.norm(positions[-1] - target) < tolerance:
            _update_angles_from_positions(arm, positions)
            return True
        
        # Forward reaching：从末端到基座
        positions[-1] = target.copy()
        for i in range(len(positions) - 2, -1, -1):
            direction = normalize(positions[i] - positions[i + 1])
            positions[i] = positions[i + 1] + direction * arm.lengths[i]
        
        # Backward reaching：从基座到末端
        positions[0] = base.copy()
        for i in range(len(positions) - 1):
            direction = normalize(positions[i + 1] - positions[i])
            positions[i + 1] = positions[i] + direction * arm.lengths[i]
    
    # 更新角度
    _update_angles_from_positions(arm, positions)
    
    # 检查最终收敛
    final_pos = arm.get_end_effector()
    return np.linalg.norm(final_pos - target) < tolerance

def _update_angles_from_positions(arm, positions):
    """从位置列表更新关节角度"""
    for i in range(arm.num_joints):
        vec = positions[i + 1] - positions[i]
        angle = math.atan2(vec[1], vec[0])
        
        if i == 0:
            arm.angles[i] = angle
        else:
            # 相对于前一段的角度
            prev_vec = positions[i] - positions[i - 1]
            prev_angle = math.atan2(prev_vec[1], prev_vec[0])
            arm.angles[i] = angle - prev_angle

# 示例使用
arm = Arm2D([2, 2, 1.5, 1])
target = np.array([4, 3])

print("FABRIK IK求解中...")
success = fabrik_ik(arm, target)

if success:
    print("成功！")
    print(f"关节角度: {np.degrees(arm.angles)}")
    arm.plot(target=target)
    plt.title('FABRIK IK Solution')
    plt.show()
else:
    print("未收敛或不可达")
```

---

## C.7 雅可比转置法

```python
def jacobian_transpose_ik(arm, target, max_iterations=1000, 
                         tolerance=0.01, alpha=0.1):
    """
    雅可比转置法IK
    
    参数:
        arm: Arm2D对象
        target: 目标位置[x, y]
        max_iterations: 最大迭代次数
        tolerance: 收敛容差
        alpha: 步长系数
    
    返回:
        成功则返回True，否则False
    """
    target = np.array(target)
    
    for iteration in range(max_iterations):
        # 当前末端位置
        end_pos = arm.get_end_effector()
        
        # 误差向量
        error = target - end_pos
        
        # 检查收敛
        if np.linalg.norm(error) < tolerance:
            return True
        
        # 计算雅可比矩阵
        J = compute_jacobian_2d(arm)
        
        # 雅可比转置
        delta_theta = alpha * J.T @ error
        
        # 更新角度
        arm.angles += delta_theta
    
    # 检查最终收敛
    final_pos = arm.get_end_effector()
    return np.linalg.norm(final_pos - target) < tolerance

def compute_jacobian_2d(arm):
    """计算2D机械臂的雅可比矩阵"""
    positions = arm.forward_kinematics()
    end_pos = positions[-1]
    
    J = np.zeros((2, arm.num_joints))
    
    for i in range(arm.num_joints):
        joint_pos = positions[i]
        
        # 旋转轴方向（在2D中总是z轴，即[0,0,1]）
        # 雅可比列 = axis × (end - joint)
        r = end_pos - joint_pos
        
        # 在2D中，绕z轴旋转对(x,y)的影响是(-y, x)
        J[0, i] = -r[1]  # dx/dθᵢ
        J[1, i] = r[0]   # dy/dθᵢ
    
    return J

# 示例使用
arm = Arm2D([2, 2, 1.5])
target = np.array([3, 2])

print("雅可比转置法IK求解中...")
success = jacobian_transpose_ik(arm, target)

if success:
    print("成功！")
    print(f"关节角度: {np.degrees(arm.angles)}")
    arm.plot(target=target)
    plt.title('Jacobian Transpose IK Solution')
    plt.show()
else:
    print("未收敛")
```

---

## C.8 动画演示

```python
from matplotlib.animation import FuncAnimation

def animate_ik(arm, targets, ik_method, interval=50):
    """
    动画演示IK求解过程
    
    参数:
        arm: Arm2D对象
        targets: 目标位置列表
        ik_method: IK求解函数
        interval: 动画间隔（毫秒）
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    def update(frame):
        ax.clear()
        target = targets[frame % len(targets)]
        
        # 求解IK
        ik_method(arm, target)
        
        # 绘制
        arm.plot(target=target, ax=ax)
        ax.set_title(f'IK Animation - Frame {frame}')
    
    anim = FuncAnimation(fig, update, frames=len(targets) * 3,
                        interval=interval, repeat=True)
    plt.show()
    return anim

# 示例：圆形轨迹
arm = Arm2D([2, 2, 1.5])
radius = 3
num_points = 50
targets = [
    [radius * math.cos(2 * math.pi * i / num_points),
     radius * math.sin(2 * math.pi * i / num_points)]
    for i in range(num_points)
]

# 使用CCD方法
animate_ik(arm, targets, ccd_ik)
```

---

## C.9 性能比较

```python
import time

def compare_ik_methods(lengths, target, num_trials=100):
    """比较不同IK方法的性能"""
    
    methods = {
        'CCD': ccd_ik,
        'FABRIK': fabrik_ik,
        'Jacobian Transpose': jacobian_transpose_ik
    }
    
    results = {}
    
    for name, method in methods.items():
        times = []
        successes = 0
        
        for _ in range(num_trials):
            arm = Arm2D(lengths)
            
            start = time.time()
            success = method(arm, target)
            elapsed = time.time() - start
            
            times.append(elapsed)
            if success:
                successes += 1
        
        results[name] = {
            'avg_time': np.mean(times),
            'success_rate': successes / num_trials,
            'std_time': np.std(times)
        }
    
    # 打印结果
    print("IK方法性能比较")
    print("-" * 60)
    print(f"{'方法':<20} {'平均时间(ms)':<15} {'成功率':<10}")
    print("-" * 60)
    
    for name, data in results.items():
        print(f"{name:<20} {data['avg_time']*1000:<15.3f} "
              f"{data['success_rate']:<10.2%}")
    
    return results

# 运行比较
results = compare_ik_methods([2, 2, 1.5, 1], [3, 3], num_trials=50)
```

---

## C.10 带关节限制的IK

```python
class ConstrainedArm2D(Arm2D):
    """带关节限制的2D机械臂"""
    
    def __init__(self, lengths, angle_limits=None):
        super().__init__(lengths)
        
        if angle_limits is None:
            # 默认：±180度
            self.angle_limits = [(-math.pi, math.pi)] * self.num_joints
        else:
            self.angle_limits = angle_limits
    
    def clamp_angles(self):
        """将角度限制在允许范围内"""
        for i in range(self.num_joints):
            min_angle, max_angle = self.angle_limits[i]
            self.angles[i] = max(min_angle, min(max_angle, self.angles[i]))

def ccd_ik_constrained(arm, target, max_iterations=100, tolerance=0.01):
    """带约束的CCD IK"""
    target = np.array(target)
    
    for iteration in range(max_iterations):
        for i in range(arm.num_joints - 1, -1, -1):
            positions = arm.forward_kinematics()
            joint_pos = positions[i]
            end_pos = positions[-1]
            
            if np.linalg.norm(end_pos - target) < tolerance:
                return True
            
            to_end = end_pos - joint_pos
            to_target = target - joint_pos
            
            angle = math.atan2(to_target[1], to_target[0]) - \
                    math.atan2(to_end[1], to_end[0])
            
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            
            arm.angles[i] += angle
            
            # 应用约束
            arm.clamp_angles()
    
    final_pos = arm.get_end_effector()
    return np.linalg.norm(final_pos - target) < tolerance

# 示例：有限制的机械臂
arm = ConstrainedArm2D(
    lengths=[2, 2, 1.5],
    angle_limits=[
        (-math.pi/2, math.pi/2),   # 关节1: ±90°
        (0, math.pi),               # 关节2: 0~180°
        (-math.pi/4, math.pi/4)    # 关节3: ±45°
    ]
)

target = [2, 2]
success = ccd_ik_constrained(arm, target)

if success:
    print("成功（带约束）")
    print(f"关节角度: {np.degrees(arm.angles)}")
    arm.plot(target=target)
    plt.title('Constrained CCD IK')
    plt.show()
```

---

## C.11 完整示例：交互式IK

```python
class InteractiveIK:
    """交互式IK演示"""
    
    def __init__(self, arm, ik_method=ccd_ik):
        self.arm = arm
        self.ik_method = ik_method
        self.target = [3, 3]
        
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.update_plot()
    
    def on_click(self, event):
        """鼠标点击事件"""
        if event.inaxes != self.ax:
            return
        
        self.target = [event.xdata, event.ydata]
        self.ik_method(self.arm, self.target)
        self.update_plot()
    
    def update_plot(self):
        """更新绘图"""
        self.ax.clear()
        self.arm.plot(target=self.target, ax=self.ax)
        self.ax.set_title('Interactive IK - Click to set target')
        self.fig.canvas.draw()
    
    def show(self):
        plt.show()

# 使用
arm = Arm2D([2, 2, 1.5, 1])
interactive = InteractiveIK(arm, ik_method=fabrik_ik)
interactive.show()
```

---

## 💡 使用建议

1. **选择合适的方法**：
   - 双关节：用解析法（最快最准）
   - 多关节简单场景：FABRIK（快速，效果好）
   - 需要精确控制：CCD或雅可比法
   - 有复杂约束：雅可比法

2. **参数调优**：
   - `tolerance`：精度要求
   - `max_iterations`：计算时间上限
   - `alpha`（雅可比法）：收敛速度

3. **性能优化**：
   - 缓存计算结果
   - 使用NumPy向量化
   - 限制迭代次数

4. **调试技巧**：
   - 可视化每一步
   - 检查收敛曲线
   - 验证FK结果

---

**返回**：[主目录](../README.md)
