#!/usr/bin/env python3
"""
合并翻译文件脚本 - 将translate目录中的翻译文件合并到assets目录结构中
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict

TRANSLATE_DIR = "translate"
ASSETS_DIR = "Localization-Resource-Pack/assets"
TARGET_DIRS = [
    "localization_resource_pack/lang",
    "white_elephant/lang"
]

def load_json_file(file_path: str) -> Dict[str, str]:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json_file(file_path: str, data: Dict[str, str]) -> bool:
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存文件失败 {file_path}: {e}")
        return False

def merge_translations_for_lang(lang_code: str):
    """为特定语言合并翻译"""
    translate_file = f"{TRANSLATE_DIR}/{lang_code}.json"
    
    if not os.path.exists(translate_file):
        return
    
    translate_data = load_json_file(translate_file)
    if not translate_data:
        return
    
    print(f"处理语言: {lang_code}")
    
    # 为每个目标目录创建翻译文件
    for target_dir in TARGET_DIRS:
        target_path = f"{ASSETS_DIR}/{target_dir}/{lang_code}.json"
        
        # 加载现有翻译（如果存在）
        existing_data = load_json_file(target_path)
        
        # 合并翻译（现有翻译优先级更高）
        merged_data = translate_data.copy()
        merged_data.update(existing_data)
        
        # 保存合并后的翻译
        if save_json_file(target_path, merged_data):
            print(f"  保存到: {target_path}")

def main():
    """主函数"""
    if not os.path.exists(TRANSLATE_DIR):
        print(f"translate目录不存在: {TRANSLATE_DIR}")
        return
    
    # 获取所有翻译文件
    translate_files = [f for f in os.listdir(TRANSLATE_DIR) if f.endswith('.json')]
    
    if not translate_files:
        print("translate目录中没有找到翻译文件")
        return
    
    print(f"找到 {len(translate_files)} 个翻译文件")
    
    # 处理每个翻译文件
    for translate_file in translate_files:
        lang_code = translate_file[:-5]  # 移除.json后缀
        merge_translations_for_lang(lang_code)
    
    print("翻译合并完成")

if __name__ == "__main__":
    main()