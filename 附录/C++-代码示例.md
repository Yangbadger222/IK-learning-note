# 附录C++：C++代码示例

## 完整IK实现示例（C++版本）

本附录包含完整的、可运行的C++代码示例，涵盖本教程中的主要IK算法。

---

## C++.1 环境设置

```cpp
// 所需头文件
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>

// 如果需要可视化，可以使用SFML或OpenGL
// #include <SFML/Graphics.hpp>
```

---

## C++.2 基础数学类

### C++.2.1 Vec2类（2D向量）

```cpp
// Vec2.h
#ifndef VEC2_H
#define VEC2_H

#include <cmath>

class Vec2 {
public:
    double x, y;
    
    // 构造函数
    Vec2() : x(0), y(0) {}
    Vec2(double x_, double y_) : x(x_), y(y_) {}
    
    // 向量加法
    Vec2 operator+(const Vec2& other) const {
        return Vec2(x + other.x, y + other.y);
    }
    
    // 向量减法
    Vec2 operator-(const Vec2& other) const {
        return Vec2(x - other.x, y - other.y);
    }
    
    // 标量乘法
    Vec2 operator*(double scalar) const {
        return Vec2(x * scalar, y * scalar);
    }
    
    // 标量除法
    Vec2 operator/(double scalar) const {
        return Vec2(x / scalar, y / scalar);
    }
    
    // 向量长度
    double length() const {
        return std::sqrt(x * x + y * y);
    }
    
    // 归一化
    Vec2 normalized() const {
        double len = length();
        if (len < 1e-10) return Vec2(0, 0);
        return Vec2(x / len, y / len);
    }
    
    // 点积
    double dot(const Vec2& other) const {
        return x * other.x + y * other.y;
    }
    
    // 距离
    double distanceTo(const Vec2& other) const {
        return (*this - other).length();
    }
    
    // 打印
    void print() const {
        std::cout << "(" << x << ", " << y << ")" << std::endl;
    }
};

#endif // VEC2_H
```

### C++.2.2 工具函数

```cpp
// Utils.h
#ifndef UTILS_H
#define UTILS_H

#include <cmath>
#include <algorithm>

const double PI = 3.14159265358979323846;

// 角度转弧度
inline double toRadians(double degrees) {
    return degrees * PI / 180.0;
}

// 弧度转角度
inline double toDegrees(double radians) {
    return radians * 180.0 / PI;
}

// 归一化角度到[-π, π]
inline double normalizeAngle(double angle) {
    while (angle > PI) angle -= 2.0 * PI;
    while (angle < -PI) angle += 2.0 * PI;
    return angle;
}

// 钳位函数
inline double clamp(double value, double min, double max) {
    return std::max(min, std::min(max, value));
}

// 角度差（考虑环绕）
inline double angleDifference(double a, double b) {
    return normalizeAngle(a - b);
}

#endif // UTILS_H
```

---

## C++.3 2D机械臂类

```cpp
// Arm2D.h
#ifndef ARM2D_H
#define ARM2D_H

#include "Vec2.h"
#include "Utils.h"
#include <vector>

class Arm2D {
private:
    std::vector<double> lengths;  // 各段长度
    std::vector<double> angles;   // 各段角度（弧度）
    int numJoints;

public:
    // 构造函数
    Arm2D(const std::vector<double>& lengths_) 
        : lengths(lengths_), numJoints(lengths_.size()) {
        angles.resize(numJoints, 0.0);
    }
    
    // 获取关节数量
    int getNumJoints() const { return numJoints; }
    
    // 设置角度
    void setAngle(int index, double angle) {
        if (index >= 0 && index < numJoints) {
            angles[index] = angle;
        }
    }
    
    // 获取角度
    double getAngle(int index) const {
        if (index >= 0 && index < numJoints) {
            return angles[index];
        }
        return 0.0;
    }
    
    // 设置所有角度
    void setAngles(const std::vector<double>& newAngles) {
        if (newAngles.size() == numJoints) {
            angles = newAngles;
        }
    }
    
    // 获取所有角度
    const std::vector<double>& getAngles() const {
        return angles;
    }
    
    // 正向运动学：计算所有关节位置
    std::vector<Vec2> forwardKinematics() const {
        std::vector<Vec2> positions;
        positions.push_back(Vec2(0, 0));  // 基座
        
        double currentAngle = 0.0;
        Vec2 currentPos(0, 0);
        
        for (int i = 0; i < numJoints; i++) {
            currentAngle += angles[i];
            currentPos.x += lengths[i] * std::cos(currentAngle);
            currentPos.y += lengths[i] * std::sin(currentAngle);
            positions.push_back(currentPos);
        }
        
        return positions;
    }
    
    // 获取末端执行器位置
    Vec2 getEndEffector() const {
        std::vector<Vec2> positions = forwardKinematics();
        return positions.back();
    }
    
    // 获取总长度
    double getTotalLength() const {
        double total = 0.0;
        for (double len : lengths) {
            total += len;
        }
        return total;
    }
    
    // 打印状态
    void printState() const {
        std::cout << "关节角度（度）: ";
        for (int i = 0; i < numJoints; i++) {
            std::cout << toDegrees(angles[i]) << " ";
        }
        std::cout << std::endl;
        
        Vec2 endPos = getEndEffector();
        std::cout << "末端位置: (" << endPos.x << ", " << endPos.y << ")" << std::endl;
    }
};

#endif // ARM2D_H
```

---

## C++.4 双关节IK（解析法）

```cpp
// TwoLinkIK.h
#ifndef TWO_LINK_IK_H
#define TWO_LINK_IK_H

#include "Vec2.h"
#include "Utils.h"
#include <cmath>

class TwoLinkIK {
public:
    // 求解双关节IK
    // 返回值：true表示成功，false表示不可达
    static bool solve(double targetX, double targetY, 
                     double L1, double L2, 
                     bool elbowUp,
                     double& theta1, double& theta2) {
        
        // 计算距离
        double d = std::sqrt(targetX * targetX + targetY * targetY);
        
        // 可达性检查
        if (d > L1 + L2 || d < std::abs(L1 - L2)) {
            return false;  // 不可达
        }
        
        // 计算theta2
        double cosTheta2 = (d * d - L1 * L1 - L2 * L2) / (2.0 * L1 * L2);
        cosTheta2 = clamp(cosTheta2, -1.0, 1.0);  // 钳位
        
        if (elbowUp) {
            theta2 = std::acos(cosTheta2);
        } else {
            theta2 = -std::acos(cosTheta2);
        }
        
        // 计算theta1
        double alpha = std::atan2(targetY, targetX);
        double beta = std::atan2(L2 * std::sin(theta2), 
                                L1 + L2 * std::cos(theta2));
        theta1 = alpha - beta;
        
        return true;
    }
    
    // 选择最优解（最小运动）
    static bool solveBest(double targetX, double targetY,
                         double L1, double L2,
                         double currentTheta1, double currentTheta2,
                         double& theta1, double& theta2) {
        
        double theta1Up, theta2Up, theta1Down, theta2Down;
        
        // 尝试两个解
        bool upValid = solve(targetX, targetY, L1, L2, true, theta1Up, theta2Up);
        bool downValid = solve(targetX, targetY, L1, L2, false, theta1Down, theta2Down);
        
        if (!upValid && !downValid) return false;
        if (!downValid) {
            theta1 = theta1Up;
            theta2 = theta2Up;
            return true;
        }
        if (!upValid) {
            theta1 = theta1Down;
            theta2 = theta2Down;
            return true;
        }
        
        // 计算运动量
        double diffUp = std::abs(angleDifference(theta1Up, currentTheta1)) + 
                       std::abs(angleDifference(theta2Up, currentTheta2));
        double diffDown = std::abs(angleDifference(theta1Down, currentTheta1)) + 
                         std::abs(angleDifference(theta2Down, currentTheta2));
        
        // 选择运动量小的
        if (diffUp < diffDown) {
            theta1 = theta1Up;
            theta2 = theta2Up;
        } else {
            theta1 = theta1Down;
            theta2 = theta2Down;
        }
        
        return true;
    }
};

#endif // TWO_LINK_IK_H
```

---

## C++.5 CCD算法

```cpp
// CCDIK.h
#ifndef CCD_IK_H
#define CCD_IK_H

#include "Arm2D.h"
#include "Vec2.h"
#include "Utils.h"

class CCDIK {
public:
    static bool solve(Arm2D& arm, const Vec2& target, 
                     int maxIterations = 100, double tolerance = 0.01) {
        
        for (int iter = 0; iter < maxIterations; iter++) {
            // 从末端到基座遍历关节
            for (int i = arm.getNumJoints() - 1; i >= 0; i--) {
                // 获取当前所有位置
                std::vector<Vec2> positions = arm.forwardKinematics();
                
                // 当前关节位置
                Vec2 jointPos = positions[i];
                
                // 末端执行器位置
                Vec2 endPos = positions.back();
                
                // 检查是否已经足够接近
                if (endPos.distanceTo(target) < tolerance) {
                    return true;
                }
                
                // 计算向量
                Vec2 toEnd = endPos - jointPos;
                Vec2 toTarget = target - jointPos;
                
                // 计算旋转角度
                double angleToEnd = std::atan2(toEnd.y, toEnd.x);
                double angleToTarget = std::atan2(toTarget.y, toTarget.x);
                double deltaAngle = normalizeAngle(angleToTarget - angleToEnd);
                
                // 更新关节角度
                double newAngle = arm.getAngle(i) + deltaAngle;
                arm.setAngle(i, newAngle);
            }
        }
        
        // 检查最终是否收敛
        Vec2 finalPos = arm.getEndEffector();
        return finalPos.distanceTo(target) < tolerance;
    }
};

#endif // CCD_IK_H
```

---

## C++.6 FABRIK算法

```cpp
// FABRIK.h
#ifndef FABRIK_H
#define FABRIK_H

#include "Arm2D.h"
#include "Vec2.h"
#include "Utils.h"
#include <vector>

class FABRIK {
private:
    // 更新机械臂角度（从位置）
    static void updateAnglesFromPositions(Arm2D& arm, 
                                         const std::vector<Vec2>& positions) {
        int numJoints = arm.getNumJoints();
        
        for (int i = 0; i < numJoints; i++) {
            Vec2 vec = positions[i + 1] - positions[i];
            double angle = std::atan2(vec.y, vec.x);
            
            if (i == 0) {
                arm.setAngle(i, angle);
            } else {
                // 相对于前一段的角度
                Vec2 prevVec = positions[i] - positions[i - 1];
                double prevAngle = std::atan2(prevVec.y, prevVec.x);
                arm.setAngle(i, normalizeAngle(angle - prevAngle));
            }
        }
    }

public:
    static bool solve(Arm2D& arm, const Vec2& target,
                     int maxIterations = 100, double tolerance = 0.01) {
        
        Vec2 base(0, 0);
        
        // 检查可达性
        double totalLength = arm.getTotalLength();
        double distToTarget = base.distanceTo(target);
        
        if (distToTarget > totalLength) {
            // 不可达，伸向目标
            std::vector<Vec2> positions;
            positions.push_back(base);
            
            Vec2 direction = (target - base).normalized();
            std::vector<double> angles = arm.getAngles();
            
            for (int i = 0; i < arm.getNumJoints(); i++) {
                // 使用原始长度
                Vec2 fk = arm.forwardKinematics();
                double len = (fk[i + 1] - fk[i]).length();
                positions.push_back(positions.back() + direction * len);
            }
            
            updateAnglesFromPositions(arm, positions);
            return false;
        }
        
        // 初始化位置
        std::vector<Vec2> positions = arm.forwardKinematics();
        std::vector<double> originalAngles = arm.getAngles();
        
        // 获取各段长度
        std::vector<double> segmentLengths;
        for (int i = 0; i < arm.getNumJoints(); i++) {
            segmentLengths.push_back((positions[i + 1] - positions[i]).length());
        }
        
        for (int iter = 0; iter < maxIterations; iter++) {
            // 检查收敛
            if (positions.back().distanceTo(target) < tolerance) {
                updateAnglesFromPositions(arm, positions);
                return true;
            }
            
            // Forward reaching：从末端到基座
            positions.back() = target;
            for (int i = positions.size() - 2; i >= 0; i--) {
                Vec2 direction = (positions[i] - positions[i + 1]).normalized();
                positions[i] = positions[i + 1] + direction * segmentLengths[i];
            }
            
            // Backward reaching：从基座到末端
            positions[0] = base;
            for (size_t i = 0; i < positions.size() - 1; i++) {
                Vec2 direction = (positions[i + 1] - positions[i]).normalized();
                positions[i + 1] = positions[i] + direction * segmentLengths[i];
            }
        }
        
        // 更新角度
        updateAnglesFromPositions(arm, positions);
        
        // 检查最终收敛
        Vec2 finalPos = arm.getEndEffector();
        return finalPos.distanceTo(target) < tolerance;
    }
};

#endif // FABRIK_H
```

---

## C++.7 雅可比转置法

```cpp
// JacobianIK.h
#ifndef JACOBIAN_IK_H
#define JACOBIAN_IK_H

#include "Arm2D.h"
#include "Vec2.h"
#include "Utils.h"
#include <vector>

class JacobianIK {
private:
    // 计算雅可比矩阵（2D，返回为向量形式）
    static void computeJacobian(const Arm2D& arm, 
                               std::vector<double>& Jx,
                               std::vector<double>& Jy) {
        std::vector<Vec2> positions = arm.forwardKinematics();
        Vec2 endPos = positions.back();
        
        int numJoints = arm.getNumJoints();
        Jx.resize(numJoints);
        Jy.resize(numJoints);
        
        for (int i = 0; i < numJoints; i++) {
            Vec2 jointPos = positions[i];
            Vec2 r = endPos - jointPos;
            
            // 在2D中，绕z轴旋转
            Jx[i] = -r.y;  // dx/dθᵢ
            Jy[i] = r.x;   // dy/dθᵢ
        }
    }

public:
    static bool solve(Arm2D& arm, const Vec2& target,
                     int maxIterations = 1000, 
                     double tolerance = 0.01,
                     double alpha = 0.1) {
        
        for (int iter = 0; iter < maxIterations; iter++) {
            // 当前末端位置
            Vec2 endPos = arm.getEndEffector();
            
            // 误差向量
            Vec2 error = target - endPos;
            
            // 检查收敛
            if (error.length() < tolerance) {
                return true;
            }
            
            // 计算雅可比矩阵
            std::vector<double> Jx, Jy;
            computeJacobian(arm, Jx, Jy);
            
            // 雅可比转置法：Δθ = α * J^T * error
            for (int i = 0; i < arm.getNumJoints(); i++) {
                double deltaTheta = alpha * (Jx[i] * error.x + Jy[i] * error.y);
                arm.setAngle(i, arm.getAngle(i) + deltaTheta);
            }
        }
        
        // 检查最终收敛
        Vec2 finalPos = arm.getEndEffector();
        return finalPos.distanceTo(target) < tolerance;
    }
};

#endif // JACOBIAN_IK_H
```

---

## C++.8 带约束的机械臂

```cpp
// ConstrainedArm2D.h
#ifndef CONSTRAINED_ARM2D_H
#define CONSTRAINED_ARM2D_H

#include "Arm2D.h"
#include "Utils.h"
#include <vector>

struct AngleLimit {
    double min;
    double max;
    
    AngleLimit() : min(-PI), max(PI) {}
    AngleLimit(double min_, double max_) : min(min_), max(max_) {}
};

class ConstrainedArm2D : public Arm2D {
private:
    std::vector<AngleLimit> angleLimits;

public:
    ConstrainedArm2D(const std::vector<double>& lengths) 
        : Arm2D(lengths) {
        // 默认限制：±180度
        angleLimits.resize(getNumJoints(), AngleLimit(-PI, PI));
    }
    
    ConstrainedArm2D(const std::vector<double>& lengths,
                    const std::vector<AngleLimit>& limits)
        : Arm2D(lengths), angleLimits(limits) {
        if (limits.size() != lengths.size()) {
            angleLimits.resize(getNumJoints(), AngleLimit(-PI, PI));
        }
    }
    
    // 设置关节限制
    void setAngleLimit(int index, double min, double max) {
        if (index >= 0 && index < getNumJoints()) {
            angleLimits[index] = AngleLimit(min, max);
        }
    }
    
    // 重写setAngle，自动应用限制
    void setAngle(int index, double angle) override {
        if (index >= 0 && index < getNumJoints()) {
            angle = clamp(angle, angleLimits[index].min, angleLimits[index].max);
            Arm2D::setAngle(index, angle);
        }
    }
    
    // 批量钳位所有角度
    void clampAngles() {
        for (int i = 0; i < getNumJoints(); i++) {
            double angle = getAngle(i);
            angle = clamp(angle, angleLimits[i].min, angleLimits[i].max);
            Arm2D::setAngle(i, angle);
        }
    }
    
    // 检查角度是否在限制内
    bool isAngleValid(int index, double angle) const {
        if (index >= 0 && index < getNumJoints()) {
            return angle >= angleLimits[index].min && 
                   angle <= angleLimits[index].max;
        }
        return false;
    }
};

#endif // CONSTRAINED_ARM2D_H
```

---

## C++.9 完整示例程序

```cpp
// main.cpp
#include "Arm2D.h"
#include "TwoLinkIK.h"
#include "CCDIK.h"
#include "FABRIK.h"
#include "JacobianIK.h"
#include "ConstrainedArm2D.h"
#include <iostream>
#include <iomanip>

void example1_TwoLinkIK() {
    std::cout << "\n=== 示例1：双关节IK ===" << std::endl;
    
    double L1 = 3.0, L2 = 2.0;
    Vec2 target(3.0, 2.0);
    
    double theta1, theta2;
    
    // 肘部向上解
    if (TwoLinkIK::solve(target.x, target.y, L1, L2, true, theta1, theta2)) {
        std::cout << "肘部向上解: " << std::endl;
        std::cout << "  θ₁ = " << toDegrees(theta1) << "°" << std::endl;
        std::cout << "  θ₂ = " << toDegrees(theta2) << "°" << std::endl;
        
        // 验证
        Arm2D arm({L1, L2});
        arm.setAngle(0, theta1);
        arm.setAngle(1, theta2);
        Vec2 result = arm.getEndEffector();
        std::cout << "  验证位置: (" << result.x << ", " << result.y << ")" << std::endl;
    }
    
    // 肘部向下解
    if (TwoLinkIK::solve(target.x, target.y, L1, L2, false, theta1, theta2)) {
        std::cout << "肘部向下解: " << std::endl;
        std::cout << "  θ₁ = " << toDegrees(theta1) << "°" << std::endl;
        std::cout << "  θ₂ = " << toDegrees(theta2) << "°" << std::endl;
    }
}

void example2_CCD() {
    std::cout << "\n=== 示例2：CCD算法 ===" << std::endl;
    
    Arm2D arm({2.0, 2.0, 1.5, 1.0});
    Vec2 target(3.0, 3.0);
    
    std::cout << "目标: (" << target.x << ", " << target.y << ")" << std::endl;
    
    if (CCDIK::solve(arm, target)) {
        std::cout << "CCD求解成功！" << std::endl;
        arm.printState();
    } else {
        std::cout << "CCD未收敛" << std::endl;
    }
}

void example3_FABRIK() {
    std::cout << "\n=== 示例3：FABRIK算法 ===" << std::endl;
    
    Arm2D arm({2.0, 2.0, 1.5, 1.0});
    Vec2 target(4.0, 3.0);
    
    std::cout << "目标: (" << target.x << ", " << target.y << ")" << std::endl;
    
    if (FABRIK::solve(arm, target)) {
        std::cout << "FABRIK求解成功！" << std::endl;
        arm.printState();
    } else {
        std::cout << "FABRIK未收敛" << std::endl;
    }
}

void example4_Jacobian() {
    std::cout << "\n=== 示例4：雅可比转置法 ===" << std::endl;
    
    Arm2D arm({2.0, 2.0, 1.5});
    Vec2 target(3.0, 2.0);
    
    std::cout << "目标: (" << target.x << ", " << target.y << ")" << std::endl;
    
    if (JacobianIK::solve(arm, target, 1000, 0.01, 0.1)) {
        std::cout << "雅可比法求解成功！" << std::endl;
        arm.printState();
    } else {
        std::cout << "雅可比法未收敛" << std::endl;
    }
}

void example5_Constrained() {
    std::cout << "\n=== 示例5：带约束的IK ===" << std::endl;
    
    // 创建带约束的机械臂
    std::vector<AngleLimit> limits = {
        AngleLimit(toRadians(-90), toRadians(90)),    // 关节1: ±90°
        AngleLimit(0, toRadians(180)),                // 关节2: 0~180°
        AngleLimit(toRadians(-45), toRadians(45))     // 关节3: ±45°
    };
    
    ConstrainedArm2D arm({2.0, 2.0, 1.5}, limits);
    Vec2 target(2.0, 2.0);
    
    std::cout << "目标: (" << target.x << ", " << target.y << ")" << std::endl;
    
    if (CCDIK::solve(arm, target)) {
        std::cout << "带约束CCD求解成功！" << std::endl;
        arm.printState();
        
        // 验证约束
        std::cout << "约束验证: " << std::endl;
        for (int i = 0; i < arm.getNumJoints(); i++) {
            double angle = toDegrees(arm.getAngle(i));
            std::cout << "  关节" << i << ": " << angle << "°";
            if (arm.isAngleValid(i, arm.getAngle(i))) {
                std::cout << " ✓" << std::endl;
            } else {
                std::cout << " ✗" << std::endl;
            }
        }
    }
}

void example6_Comparison() {
    std::cout << "\n=== 示例6：算法性能比较 ===" << std::endl;
    
    std::vector<double> lengths = {2.0, 2.0, 1.5, 1.0};
    Vec2 target(4.0, 2.5);
    
    // CCD
    {
        Arm2D arm(lengths);
        auto start = std::chrono::high_resolution_clock::now();
        bool success = CCDIK::solve(arm, target);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "CCD:      " << (success ? "成功" : "失败") 
                  << " | 时间: " << duration.count() << " μs" << std::endl;
    }
    
    // FABRIK
    {
        Arm2D arm(lengths);
        auto start = std::chrono::high_resolution_clock::now();
        bool success = FABRIK::solve(arm, target);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "FABRIK:   " << (success ? "成功" : "失败")
                  << " | 时间: " << duration.count() << " μs" << std::endl;
    }
    
    // 雅可比
    {
        Arm2D arm(lengths);
        auto start = std::chrono::high_resolution_clock::now();
        bool success = JacobianIK::solve(arm, target);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Jacobian: " << (success ? "成功" : "失败")
                  << " | 时间: " << duration.count() << " μs" << std::endl;
    }
}

int main() {
    std::cout << std::fixed << std::setprecision(3);
    
    example1_TwoLinkIK();
    example2_CCD();
    example3_FABRIK();
    example4_Jacobian();
    example5_Constrained();
    example6_Comparison();
    
    return 0;
}
```

---

## C++.10 CMake构建配置

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(IK_Tutorial)

# 设置C++标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 头文件目录
include_directories(${PROJECT_SOURCE_DIR}/include)

# 源文件
set(SOURCES
    src/main.cpp
)

# 创建可执行文件
add_executable(ik_demo ${SOURCES})

# 如果使用SFML进行可视化（可选）
# find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)
# target_link_libraries(ik_demo sfml-graphics sfml-window sfml-system)
```

---

## C++.11 目录结构建议

```
IK_Project/
├── CMakeLists.txt
├── include/
│   ├── Vec2.h
│   ├── Utils.h
│   ├── Arm2D.h
│   ├── TwoLinkIK.h
│   ├── CCDIK.h
│   ├── FABRIK.h
│   ├── JacobianIK.h
│   └── ConstrainedArm2D.h
├── src/
│   └── main.cpp
└── build/
```

---

## C++.12 编译和运行

### 使用CMake

```bash
# 创建构建目录
mkdir build
cd build

# 配置
cmake ..

# 编译
cmake --build .

# 运行
./ik_demo
```

### 使用g++直接编译

```bash
g++ -std=c++11 -I./include src/main.cpp -o ik_demo
./ik_demo
```

### 使用Visual Studio

1. 创建新的C++控制台项目
2. 将所有.h文件添加到头文件
3. 将main.cpp添加到源文件
4. 编译运行

---

## C++.13 性能优化技巧

### 1. 使用内联函数

```cpp
inline double Vec2::length() const {
    return std::sqrt(x * x + y * y);
}
```

### 2. 避免不必要的拷贝

```cpp
// 使用const引用
void processArm(const Arm2D& arm) {
    // ...
}

// 返回const引用
const std::vector<double>& getAngles() const {
    return angles;
}
```

### 3. 预分配内存

```cpp
std::vector<Vec2> positions;
positions.reserve(numJoints + 1);  // 预分配
```

### 4. 使用移动语义（C++11）

```cpp
Arm2D createArm(std::vector<double> lengths) {
    return Arm2D(std::move(lengths));  // 移动而非拷贝
}
```

---

## C++.14 调试宏

```cpp
// Debug.h
#ifndef DEBUG_H
#define DEBUG_H

#include <iostream>

#ifdef DEBUG_MODE
    #define DEBUG_PRINT(x) std::cout << "[DEBUG] " << x << std::endl
    #define DEBUG_VEC2(name, vec) \
        std::cout << "[DEBUG] " << name << ": (" \
                  << vec.x << ", " << vec.y << ")" << std::endl
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_VEC2(name, vec)
#endif

#endif // DEBUG_H

// 使用:
// #define DEBUG_MODE
// #include "Debug.h"
// 
// DEBUG_PRINT("开始IK求解");
// DEBUG_VEC2("目标", target);
```

---

## C++.15 单元测试示例

```cpp
// test_ik.cpp
#include "TwoLinkIK.h"
#include "Arm2D.h"
#include <cassert>
#include <cmath>
#include <iostream>

void test_two_link_ik() {
    std::cout << "测试双关节IK..." << std::endl;
    
    double L1 = 3.0, L2 = 2.0;
    double theta1, theta2;
    
    // 测试1：已知解
    bool success = TwoLinkIK::solve(5.0, 0.0, L1, L2, true, theta1, theta2);
    assert(success);
    assert(std::abs(theta2) < 1e-6);  // theta2应该接近0
    
    // 测试2：不可达
    success = TwoLinkIK::solve(10.0, 0.0, L1, L2, true, theta1, theta2);
    assert(!success);
    
    // 测试3：验证FK
    success = TwoLinkIK::solve(3.0, 2.0, L1, L2, true, theta1, theta2);
    if (success) {
        Arm2D arm({L1, L2});
        arm.setAngle(0, theta1);
        arm.setAngle(1, theta2);
        Vec2 result = arm.getEndEffector();
        assert(std::abs(result.x - 3.0) < 0.01);
        assert(std::abs(result.y - 2.0) < 0.01);
    }
    
    std::cout << "所有测试通过！" << std::endl;
}

int main() {
    test_two_link_ik();
    return 0;
}
```

---

## 💡 C++实现要点

1. **内存管理**：使用STL容器，避免手动内存管理
2. **性能**：C++通常比Python快10-100倍
3. **类型安全**：使用强类型，编译时检查错误
4. **头文件保护**：使用`#ifndef`防止重复包含
5. **const正确性**：合理使用const提高安全性
6. **移动语义**：C++11后优化大对象传递

## 📝 编译选项建议

```bash
# 开发阶段（调试）
g++ -std=c++11 -g -Wall -Wextra -O0 main.cpp -o ik_demo

# 发布阶段（性能）
g++ -std=c++11 -O3 -march=native main.cpp -o ik_demo
```

---

**返回**：[主目录](../README.md) | [Python版本](./C-代码示例.md)
