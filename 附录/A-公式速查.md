# 附录A：数学公式速查

快速查找IK中常用的数学公式。

---

## A.1 三角函数

### 基本定义

```math
\sin\theta = \frac{\text{对边}}{\text{斜边}} \quad \cos\theta = \frac{\text{邻边}}{\text{斜边}} \quad \tan\theta = \frac{\text{对边}}{\text{邻边}}
```


### 重要值
| θ | 0° | 30° | 45° | 60° | 90° |
|---|-----|-----|-----|-----|-----|
| sin | 0 | 1/2 | √2/2 | √3/2 | 1 |
| cos | 1 | √3/2 | √2/2 | 1/2 | 0 |

### 恒等式

```math
\sin^2\theta + \cos^2\theta = 1
```


```math
\sin(A \pm B) = \sin A \cos B \pm \cos A \sin B
```


```math
\cos(A \pm B) = \cos A \cos B \mp \sin A \sin B
```


```math
\tan(A \pm B) = \frac{\tan A \pm \tan B}{1 \mp \tan A \tan B}
```


---

## A.2 向量运算

### 向量模

```math
|\vec{v}| = \sqrt{v_x^2 + v_y^2 + v_z^2}
```


### 单位向量

```math
\hat{v} = \frac{\vec{v}}{|\vec{v}|}
```


### 点积

```math
\vec{u} \cdot \vec{v} = u_x v_x + u_y v_y + u_z v_z = |\vec{u}||\vec{v}|\cos\theta
```


### 叉积（3D）

```math
\vec{u} \times \vec{v} = \begin{bmatrix} u_y v_z - u_z v_y \\ u_z v_x - u_x v_z \\ u_x v_y - u_y v_x \end{bmatrix}
```


---

## A.3 旋转矩阵

### 2D旋转（逆时针）

```math
R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}
```


### 3D旋转

**绕x轴**：

```math
R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}
```


**绕y轴**：

```math
R_y(\theta) = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}
```


**绕z轴**：

```math
R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}
```


---

## A.4 IK核心公式

### 双关节2D IK

```math
\cos\theta_2 = \frac{x^2 + y^2 - L_1^2 - L_2^2}{2L_1 L_2}
```


```math
\theta_1 = \text{atan2}(y, x) - \text{atan2}(L_2\sin\theta_2, L_1 + L_2\cos\theta_2)
```


### 雅可比矩阵（2D）

```math
J_{i} = \begin{bmatrix} -r_y \\ r_x \end{bmatrix}
```

其中 $\vec{r} = \vec{p}_{end} - \vec{p}_{joint_i}$

### 雅可比转置法

```math
\Delta\theta = \alpha J^T \Delta x
```


### 雅可比逆法

```math
\Delta\theta = J^{-1} \Delta x
```


### 阻尼最小二乘

```math
\Delta\theta = J^T(JJ^T + \lambda^2 I)^{-1} \Delta x
```


---

## A.5 距离与几何

### 两点距离

```math
d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}
```


### 余弦定理

```math
c^2 = a^2 + b^2 - 2ab\cos C
```


### 极坐标转换

```math
r = \sqrt{x^2 + y^2}
```


```math
\theta = \text{atan2}(y, x)
```


```math
x = r\cos\theta
```


```math
y = r\sin\theta
```


---

## A.6 四元数

### 定义

```math
q = w + xi + yj + zk
```


### 归一化

```math
\hat{q} = \frac{q}{|q|} = \frac{q}{\sqrt{w^2 + x^2 + y^2 + z^2}}
```


### 旋转向量

```math
v' = qvq^{-1}
```


### 四元数乘法

```math
q_1 q_2 = \begin{bmatrix} w_1w_2 - x_1x_2 - y_1y_2 - z_1z_2 \\ w_1x_2 + x_1w_2 + y_1z_2 - z_1y_2 \\ w_1y_2 - x_1z_2 + y_1w_2 + z_1x_2 \\ w_1z_2 + x_1y_2 - y_1x_2 + z_1w_2 \end{bmatrix}
```


---

## A.7 矩阵运算

### 矩阵乘法

```math
(AB)_{ij} = \sum_k A_{ik}B_{kj}
```


### 2×2矩阵逆

```math
A^{-1} = \frac{1}{\det(A)} \begin{bmatrix} d & -b \\ -c & a \end{bmatrix}
```

其中 $A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$，$\det(A) = ad - bc$

### 伪逆

```math
J^+ = J^T(JJ^T)^{-1}
```
（左伪逆，当J行满秩）

```math
J^+ = (J^TJ)^{-1}J^T
```
（右伪逆，当J列满秩）

---

## A.8 优化与迭代

### 梯度下降

```math
\theta_{n+1} = \theta_n - \alpha \nabla f(\theta_n)
```


### 牛顿法

```math
\theta_{n+1} = \theta_n - H^{-1} \nabla f(\theta_n)
```

其中 $H$ 是Hessian矩阵

### 线搜索

```math
\alpha^* = \arg\min_\alpha f(\theta + \alpha d)
```


---

## A.9 常用数值

### π的倍数

```math
\pi \approx 3.14159
```


```math
\pi/2 \approx 1.5708
```
 (90°)

```math
\pi/3 \approx 1.0472
```
 (60°)

```math
\pi/4 \approx 0.7854
```
 (45°)

```math
\pi/6 \approx 0.5236
```
 (30°)

### 角度弧度转换

```math
\text{rad} = \text{deg} \times \frac{\pi}{180}
```


```math
\text{deg} = \text{rad} \times \frac{180}{\pi}
```


---

**返回**：[主目录](../README.md)
