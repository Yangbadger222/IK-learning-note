#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极修复脚本 - 处理所有GitHub数学公式显示问题
特别针对练习题中的行内公式
"""

import re
import os

def fix_inline_math(content):
    """
    修复行内数学公式
    将 \vec{u} 等 LaTeX 命令转换为简单形式
    """
    # 替换 \vec{字母} 为 向量字母 或 v̅字母
    def replace_vec(match):
        var = match.group(1)
        # 使用Unicode上划线或者直接用文字"向量"
        return f'**{var}**'  # 使用粗体代替向量符号
    
    # 处理 $\vec{...}$ 
    content = re.sub(r'\$\\vec\{([a-zA-Z])\}\$', replace_vec, content)
    
    # 处理复杂行内公式中的 \vec
    content = re.sub(r'\\vec\{([a-zA-Z])\}', r'\\mathbf{\1}', content)
    
    return content

def fix_block_math(content):
    """
    确保块级公式使用正确的格式
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检查 $$...$$（单行块级公式）
        if line.strip().startswith('$$') and line.strip().endswith('$$') and line.count('$$') == 2:
            formula = line.strip()[2:-2].strip()
            if formula:
                # 确保前面有空行
                if result and result[-1].strip() != '':
                    result.append('')
                result.append('```math')
                result.append(formula)
                result.append('```')
                # 确保后面有空行（如果还有内容）
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    result.append('')
            i += 1
            continue
        
        # 检查 $$开始的多行公式
        if line.strip() == '$$':
            formula_lines = []
            i += 1
            # 收集公式内容
            while i < len(lines) and lines[i].strip() != '$$':
                formula_lines.append(lines[i])
                i += 1
            
            if i < len(lines):  # 找到了结束的$$
                formula = '\n'.join(formula_lines).strip()
                if formula:
                    # 确保前面有空行
                    if result and result[-1].strip() != '':
                        result.append('')
                    result.append('```math')
                    result.append(formula)
                    result.append('```')
                    # 确保后面有空行（如果还有内容）
                    if i + 1 < len(lines) and lines[i + 1].strip() != '':
                        result.append('')
                i += 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def remove_extra_blank_lines(content):
    """
    清理连续的空行（最多保留2个）
    """
    lines = content.split('\n')
    result = []
    blank_count = 0
    
    for line in lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    
    return '\n'.join(result)

def fix_markdown_file(filepath):
    """修复单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 应用修复（按顺序）
        content = fix_inline_math(content)  # 先修复行内公式
        content = fix_block_math(content)   # 再修复块级公式
        content = remove_extra_blank_lines(content)  # 最后清理空行
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ 修复: {filepath}')
            return True
        
        return False
    
    except Exception as e:
        print(f'✗ 错误: {filepath} - {e}')
        return False

def main():
    """主函数"""
    fixed_count = 0
    
    # 遍历所有.md文件
    for root, dirs, files in os.walk('.'):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md') and 'fix' not in file.lower() and 'clean' not in file.lower():
                filepath = os.path.join(root, file)
                if fix_markdown_file(filepath):
                    fixed_count += 1
    
    print(f'\n✅ 完成！共修复 {fixed_count} 个文件')
    print('\n现在请：')
    print('1. git add -A')
    print('2. git commit -m "最终修复：确保所有数学公式在GitHub上正确显示"')
    print('3. git push')

if __name__ == '__main__':
    main()
