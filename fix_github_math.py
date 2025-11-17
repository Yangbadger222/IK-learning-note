#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Markdown数学公式修复脚本

将 $$...$$ 格式转换为 ```math ... ``` 格式
确保数学公式在GitHub上正确显示
"""

import re
import os
import sys

def fix_math_blocks(content):
    """
    修复数学公式块
    将 $$...$$ 转换为 ```math\n...\n```
    """
    # 处理块级公式（多行）
    # 匹配 $$...$$，可能跨越多行
    pattern = r'\$\$(.*?)\$\$'
    
    def replace_block_math(match):
        formula = match.group(1).strip()
        # 如果公式为空，跳过
        if not formula:
            return match.group(0)
        return f'\n```math\n{formula}\n```\n'
    
    # 替换块级公式
    content = re.sub(pattern, replace_block_math, content, flags=re.DOTALL)
    
    return content

def should_process_file(filepath):
    """判断是否应该处理该文件"""
    # 跳过某些文件
    skip_patterns = [
        'node_modules',
        '.git',
        'build',
        'dist',
        '__pycache__',
        '.vscode',
        'GitHub数学公式修复指南.md',  # 跳过指南文件本身
        'fix_github_math.py'  # 跳过脚本本身
    ]
    
    for pattern in skip_patterns:
        if pattern in filepath:
            return False
    
    return filepath.endswith('.md')

def fix_markdown_file(filepath, dry_run=False):
    """修复单个Markdown文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 检查是否包含数学公式
        if '$$' not in original_content:
            return False
        
        fixed_content = fix_math_blocks(original_content)
        
        # 检查是否有变化
        if fixed_content == original_content:
            return False
        
        if dry_run:
            print(f'[预览] 将修复: {filepath}')
            # 显示差异示例
            original_lines = original_content.split('\n')
            fixed_lines = fixed_content.split('\n')
            
            diff_count = 0
            for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines)):
                if orig != fixed and diff_count < 3:  # 只显示前3个差异
                    print(f'  行 {i+1}:')
                    print(f'    原: {orig[:80]}...' if len(orig) > 80 else f'    原: {orig}')
                    print(f'    新: {fixed[:80]}...' if len(fixed) > 80 else f'    新: {fixed}')
                    diff_count += 1
            
            return True
        else:
            # 实际写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f'✓ 已修复: {filepath}')
            return True
    
    except Exception as e:
        print(f'✗ 错误 {filepath}: {str(e)}', file=sys.stderr)
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='修复GitHub Markdown数学公式')
    parser.add_argument('--dry-run', action='store_true', 
                       help='预览模式，不实际修改文件')
    parser.add_argument('--path', default='.', 
                       help='要处理的目录路径（默认为当前目录）')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print('=' * 60)
        print('预览模式 - 不会实际修改文件')
        print('=' * 60)
    
    processed_count = 0
    fixed_count = 0
    
    # 遍历所有.md文件
    for root, dirs, files in os.walk(args.path):
        # 过滤掉不需要处理的目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'build', 'dist']]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            if should_process_file(filepath):
                processed_count += 1
                if fix_markdown_file(filepath, args.dry_run):
                    fixed_count += 1
    
    print('\n' + '=' * 60)
    if args.dry_run:
        print(f'预览完成：检查了 {processed_count} 个文件，{fixed_count} 个需要修复')
        print('运行 python fix_github_math.py 来实际修复文件')
    else:
        print(f'修复完成：处理了 {processed_count} 个文件，修复了 {fixed_count} 个')
    print('=' * 60)

if __name__ == '__main__':
    main()
