#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub数学公式终极修复
根据GitHub Flavored Markdown规范修复所有数学公式
"""

import re
import os

def process_file(filepath):
    """处理单个Markdown文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 处理单行 $$...$$ 块级公式
            if '$$' in line and line.count('$$') >= 2:
                parts = line.split('$$')
                if len(parts) == 3:  # 形如: 文本$$公式$$文本
                    formula = parts[1].strip()
                    if formula:
                        if new_lines and new_lines[-1].strip():
                            new_lines.append('')  # 前面加空行
                        new_lines.append('```math')
                        new_lines.append(formula)
                        new_lines.append('```')
                        if i + 1 < len(lines) and lines[i + 1].strip():
                            new_lines.append('')  # 后面加空行
                        i += 1
                        continue
            
            # 处理多行 $$...$$ 块级公式
            if line.strip() == '$$':
                formula_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() != '$$':
                    formula_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):  # 找到了结束的 $$
                    formula = '\n'.join(formula_lines).strip()
                    if formula:
                        if new_lines and new_lines[-1].strip():
                            new_lines.append('')
                        new_lines.append('```math')
                        new_lines.append(formula)
                        new_lines.append('```')
                        if i + 1 < len(lines) and lines[i + 1].strip():
                            new_lines.append('')
                i += 1
                continue
            
            # 处理行内公式 $...$
            # GitHub要求行内公式前后需要有空格（如果前后有字符的话）
            if '$' in line and not line.strip().startswith('```'):
                # 确保 $ 前后有适当的空格
                # 例如: "向量$\vec{u}$的" -> "向量 $\vec{u}$ 的"
                line = re.sub(r'([a-zA-Z0-9\u4e00-\u9fa5])\$', r'\1 $', line)
                line = re.sub(r'\$([a-zA-Z0-9\u4e00-\u9fa5])', r'$ \1', line)
            
            new_lines.append(line)
            i += 1
        
        # 清理连续空行（最多保留1个）
        final_lines = []
        prev_blank = False
        for line in new_lines:
            if line.strip() == '':
                if not prev_blank:
                    final_lines.append(line)
                prev_blank = True
            else:
                final_lines.append(line)
                prev_blank = False
        
        new_content = '\n'.join(final_lines)
        
        # 保存修改
        if new_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'✓ 修复: {filepath}')
            return True
        else:
            print(f'- 跳过: {filepath} (无需修改)')
            return False
            
    except Exception as e:
        print(f'✗ 错误 {filepath}: {e}')
        return False

def main():
    """主函数"""
    fixed_count = 0
    total_count = 0
    
    # 遍历所有.md文件
    for root, dirs, files in os.walk('.'):
        # 跳过.git等隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in files:
            if filename.endswith('.md'):
                # 跳过脚本说明文件
                if 'fix' in filename.lower() or 'clean' in filename.lower():
                    continue
                
                filepath = os.path.join(root, filename)
                total_count += 1
                
                if process_file(filepath):
                    fixed_count += 1
    
    print(f'\n' + '='*50)
    print(f'✅ 完成！')
    print(f'总文件数: {total_count}')
    print(f'修复文件数: {fixed_count}')
    print(f'='*50)
    print('\n下一步操作：')
    print('1. git add -A')
    print('2. git commit -m "终极修复：GitHub数学公式显示问题"')
    print('3. git push')
    print('\n提示：推送后等待1-2分钟，GitHub需要时间重新渲染Markdown')

if __name__ == '__main__':
    main()
