#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复脚本 - 完美清理
"""

import re
import os

def clean_math_blocks(content):
    """
    清理math代码块周围的多余空行
    规则：
    - ```math 前面最多1个空行
    - ``` 后面最多1个空行
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 如果是```math开始
        if line.strip() == '```math':
            # 往回检查，删除多余空行（保留最多1个）
            while len(result) > 0 and result[-1].strip() == '':
                result.pop()
            
            # 添加1个空行和```math
            if len(result) > 0 and result[-1].strip() != '':
                result.append('')
            
            result.append('```math')
            i += 1
            
            # 添加公式内容
            while i < len(lines) and lines[i].strip() != '```':
                result.append(lines[i])
                i += 1
            
            # 添加结束的```
            if i < len(lines):
                result.append('```')
                i += 1
                
                # 往后检查，确保只有1个空行
                empty_count = 0
                while i < len(lines) and lines[i].strip() == '':
                    empty_count += 1
                    i += 1
                
                # 添加1个空行（如果后面还有内容）
                if i < len(lines):
                    result.append('')
            continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def fix_file(filepath):
    """修复单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '```math' not in content:
            return False
        
        cleaned = clean_math_blocks(content)
        
        if cleaned != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f'✓ 清理: {filepath}')
            return True
        
        return False
    except Exception as e:
        print(f'✗ 错误: {filepath} - {e}')
        return False

def main():
    """主函数"""
    fixed = 0
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md') and 'fix_github' not in file:
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    fixed += 1
    
    print(f'\n完成！修复了 {fixed} 个文件')

if __name__ == '__main__':
    main()
