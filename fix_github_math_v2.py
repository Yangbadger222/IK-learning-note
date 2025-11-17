#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Markdown数学公式修复脚本 v2.0
修复多余空行问题
"""

import re
import os
import sys

def fix_math_blocks_v2(content):
    """
    改进的数学公式修复
    1. 将 $$...$$ 转换为 ```math\n...\n```
    2. 清理多余空行
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检查是否是 $$...$$（单行）
        if line.strip().startswith('$$') and line.strip().endswith('$$') and line.count('$$') == 2:
            formula = line.strip()[2:-2].strip()
            if formula:
                result.append('')
                result.append('```math')
                result.append(formula)
                result.append('```')
                result.append('')
            i += 1
            continue
        
        # 检查是否是 $$开始（多行）
        if line.strip() == '$$':
            # 找到对应的结束$$
            formula_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '$$':
                formula_lines.append(lines[i])
                i += 1
            
            if i < len(lines) and lines[i].strip() == '$$':
                # 找到了配对的$$
                formula = '\n'.join(formula_lines).strip()
                if formula:
                    result.append('')
                    result.append('```math')
                    result.append(formula)
                    result.append('```')
                    result.append('')
                i += 1
                continue
        
        result.append(line)
        i += 1
    
    # 清理连续的多个空行（最多保留2个）
    cleaned = []
    empty_count = 0
    for line in result:
        if line.strip() == '':
            empty_count += 1
            if empty_count <= 2:
                cleaned.append(line)
        else:
            empty_count = 0
            cleaned.append(line)
    
    return '\n'.join(cleaned)

def fix_markdown_file(filepath, dry_run=False):
    """修复单个Markdown文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 检查是否包含math代码块或$$
        if '```math' not in original_content and '$$' not in original_content:
            return False
        
        fixed_content = fix_math_blocks_v2(original_content)
        
        # 检查是否有变化
        if fixed_content == original_content:
            return False
        
        if dry_run:
            print(f'[预览] 将修复: {filepath}')
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

def should_process_file(filepath):
    """判断是否应该处理该文件"""
    skip_patterns = [
        'node_modules', '.git', 'build', 'dist', '__pycache__', '.vscode',
        'GitHub数学公式修复指南.md', 'fix_github_math'
    ]
    
    for pattern in skip_patterns:
        if pattern in filepath:
            return False
    
    return filepath.endswith('.md')

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='修复GitHub Markdown数学公式 v2.0')
    parser.add_argument('--dry-run', action='store_true', help='预览模式')
    parser.add_argument('--path', default='.', help='目录路径')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print('=' * 60)
        print('预览模式 - 不会实际修改文件')
        print('=' * 60)
    
    processed_count = 0
    fixed_count = 0
    
    for root, dirs, files in os.walk(args.path):
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
        print('运行 python fix_github_math_v2.py 来实际修复')
    else:
        print(f'修复完成：处理了 {processed_count} 个文件，修复了 {fixed_count} 个')
    print('=' * 60)

if __name__ == '__main__':
    main()
