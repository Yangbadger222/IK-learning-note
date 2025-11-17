# GitHub数学公式显示指南

## 问题说明

如果你在GitHub上看到数学公式显示为乱码（如 `\begin{bmatrix}`等），这是因为GitHub的Markdown渲染需要特定格式。

## 解决方案

### ✅ 正确的数学公式格式

#### 1. 行内公式
使用单个 `$` 包裹，例如：

这是行内公式 $ x = 5 $ 的示例。

#### 2. 块级公式（推荐格式）

**方法一：使用代码块标记（最稳定）**

```math
\vec{v} = \begin{bmatrix} x \\ y \end{bmatrix}
```

**方法二：使用双美元符号（需要空行）**

下面是一个向量：

```math
\vec{v} = \begin{bmatrix} x \\ y \end{bmatrix}
```

上面的公式应该能正确显示。

### 📝 示例对比

#### ❌ 错误格式（会显示为乱码）
```
**解答**：

```math
\vec{AB} = B - A = \begin{bmatrix} 4-1 \\ 6-2 \end{bmatrix} = \begin{bmatrix} 3 \\ 4 \end{bmatrix}
```

```

#### ✅ 正确格式1（使用math代码块）
```
**解答**：

```math
\vec{AB} = B - A = \begin{bmatrix} 4-1 \\ 6-2 \end{bmatrix} = \begin{bmatrix} 3 \\ 4 \end{bmatrix}
```

（注意：这里需要闭合反引号）

#### ✅ 正确格式2（双美元符号加空行）
```
**解答**：

```math
\vec{AB} = B - A = \begin{bmatrix} 4-1 \\ 6-2 \end{bmatrix} = \begin{bmatrix} 3 \\ 4 \end{bmatrix}
```

```

## 🔧 快速修复方法

### 方案A：全局替换为math代码块（推荐）

将所有的：
```

```math
公式
```

```

替换为：
````

```math
公式
```

````

### 方案B：确保双美元符号前后有空行

每个 `$$` 公式前后都要有空行。

## 📖 修复后的例题示例

### 例题 1.1

点A的坐标为(1, 2)，点B的坐标为(4, 6)  
求从A指向B的向量

**解答**：

```math
\vec{AB} = B - A = \begin{bmatrix} 4-1 \\ 6-2 \end{bmatrix} = \begin{bmatrix} 3 \\ 4 \end{bmatrix}
```

### 例题 1.2

已知 $\vec{u} = [2, 3]$，$\vec{v} = [1, -1]$  
求 $\vec{u} + \vec{v}$

**解答**：

```math
\vec{u} + \vec{v} = \begin{bmatrix} 2+1 \\ 3+(-1) \end{bmatrix} = \begin{bmatrix} 3 \\ 2 \end{bmatrix}
```

## 🚀 一键修复脚本

如果你想批量修复所有文件，可以使用以下Python脚本：

```python
import re
import os

def fix_math_blocks(content):

```math
...
```

    # 处理多行公式
    pattern = r'\$\$(.*?)\$\$'
    
    def replace_math(match):
        formula = match.group(1).strip()
        return f'\n```math\n{formula}\n```\n'
    
    content = re.sub(pattern, replace_math, content, flags=re.DOTALL)
    return content

def fix_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = fix_math_blocks(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f'已修复: {filepath}')

# 遍历所有.md文件
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            fix_markdown_file(filepath)
```

## 💡 验证方法

1. 在本地编辑器（VS Code）中安装Markdown预览插件
2. 推送到GitHub后检查渲染效果
3. 如果还有问题，优先使用 ````math` 代码块格式

## 📚 参考

- [GitHub数学表达式文档](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
- GitHub使用MathJax渲染LaTeX数学公式

---

**注意**：本教程中的所有数学公式都需要按照上述格式修复才能在GitHub上正确显示。
