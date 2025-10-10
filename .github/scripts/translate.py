#!/usr/bin/env python3
"""
自动翻译脚本 - 使用DeepSeek API进行多语言翻译
"""

import json
import os
import requests
import sys
import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
ASSETS_DIR = "Localization-Resource-Pack/assets"
TRANSLATE_DIR = "translate"
SYSTEM_PROMPT_FILE = "Localization-Resource-Pack/assets/system_prompt.md"
USER_PROMPT_FILE = "Localization-Resource-Pack/assets/user_prompt.md"

# 目标语言列表（基于之前的推荐）
TARGET_LANGUAGES = {
    "en_us": "English (US)",
    "pt_br": "Portuguese (Brazil)",
    "ru_ru": "Russian",
    "de_de": "German",
    "es_es": "Spanish (Spain)",
    "es_mx": "Spanish (Mexico)",
    "fr_fr": "French (France)",
    "fr_ca": "French (Canada)",
    "tr_tr": "Turkish",
    "ja_jp": "Japanese",
    "ko_kr": "Korean",
    "pl_pl": "Polish",
    "nl_nl": "Dutch",
    "it_it": "Italian",
    "id_id": "Indonesian",
    "vi_vn": "Vietnamese",
    "zh_tw": "Traditional Chinese (Taiwan)",
    "zh_hk": "Traditional Chinese (Hong Kong)"
}

class DeepSeekTranslator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.system_prompt = self._load_prompt_template(SYSTEM_PROMPT_FILE)
        self.user_prompt = self._load_prompt_template(USER_PROMPT_FILE)

    def _load_prompt_template(self, file_path: str) -> str:
        """加载提示词模板文件，跳过标题行"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 跳过以 # 开头的标题行和空行
            content_lines = []
            for line in lines:
                stripped_line = line.strip()
                # 跳过标题行（以#开头）和空行，但保留内容开始后的空行
                if content_lines or (stripped_line and not stripped_line.startswith('#')):
                    content_lines.append(line)
            
            return ''.join(content_lines).strip()
        except FileNotFoundError:
            print(f"警告：提示词模板文件 {file_path} 不存在，使用默认提示词")
            return ""
        except Exception as e:
            print(f"警告：加载提示词模板 {file_path} 时出错: {e}")
            return ""

    def _format_prompt(self, template: str, **kwargs) -> str:
        """格式化提示词模板，替换变量"""
        try:
            # 使用双大括号格式进行变量替换
            formatted = template
            for key, value in kwargs.items():
                formatted = formatted.replace(f"{{{{{key}}}}}", str(value))
            return formatted
        except Exception as e:
            print(f"警告：格式化提示词时出错: {e}")
            return template

    def validate_placeholder_consistency(self, original_text: str, translated_text: str) -> bool:
        """验证翻译前后的占位符一致性

        只检查有效的本地化参数格式：%s 和 %n$s
        """
        # 匹配 %s 和 %n$s 格式的占位符
        placeholder_pattern = r'%(?:\d+\$)?s'

        original_placeholders = re.findall(placeholder_pattern, original_text)
        translated_placeholders = re.findall(placeholder_pattern, translated_text)

        # 排序后比较，确保占位符完全一致
        return sorted(original_placeholders) == sorted(translated_placeholders)

    def validate_translation_result(self, original: Dict[str, str], translated: Dict[str, str]) -> List[str]:
        """验证翻译结果的完整性和格式正确性

        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
        """
        errors = []

        # 1. 检查键完整性
        original_keys = set(original.keys())
        translated_keys = set(translated.keys())

        if original_keys != translated_keys:
            missing_keys = original_keys - translated_keys
            extra_keys = translated_keys - original_keys

            if missing_keys:
                errors.append(f"缺少键: {list(missing_keys)}")
            if extra_keys:
                errors.append(f"多余键: {list(extra_keys)}")

        # 2. 检查值类型和占位符一致性
        for key in original_keys & translated_keys:
            translated_value = translated.get(key)

            if not isinstance(translated_value, str):
                errors.append(f"键 '{key}' 的值不是字符串类型: {type(translated_value)}")
                continue

            # 检查占位符一致性（允许空值）
            original_value = original[key]
            if not self.validate_placeholder_consistency(original_value, translated_value):
                errors.append(f"键 '{key}' 的占位符不一致: '{original_value}' -> '{translated_value}'")

        return errors

    def log_translation_failure(self, attempt: int, system_prompt: str, user_prompt: str,
                              api_response: str, error: str, texts: Dict[str, str]) -> None:
        """记录翻译失败的详细信息到日志文件"""
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"translation_failure_{timestamp}_attempt_{attempt}.log")

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"翻译失败日志 - 尝试次数: {attempt}\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"错误信息:\n{error}\n")
            f.write("\n" + "=" * 80 + "\n\n")

            f.write("原始文本:\n")
            f.write(json.dumps(texts, ensure_ascii=False, indent=2))
            f.write("\n\n" + "=" * 80 + "\n\n")

            f.write("系统提示词:\n")
            f.write(system_prompt)
            f.write("\n\n" + "=" * 80 + "\n\n")

            f.write("用户提示词:\n")
            f.write(user_prompt)
            f.write("\n\n" + "=" * 80 + "\n\n")

            f.write("API响应:\n")
            f.write(api_response)
            f.write("\n\n" + "=" * 80 + "\n")

        print(f"翻译失败日志已保存: {log_file}")

    def translate_batch(self, texts: Dict[str, str], target_lang: str, target_lang_name: str) -> Dict[str, str]:
        """
        翻译一批文本，包含重试机制和完整性验证
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # 构建翻译提示
                source_text = json.dumps(texts, ensure_ascii=False, indent=2)

                # 使用提示词模板或回退到默认提示词
                if self.system_prompt:
                    system_prompt = self._format_prompt(
                        self.system_prompt,
                        source_language="中文",
                        target_language=target_lang_name
                    )
                else:
                    system_prompt = "你是一个专业的游戏本地化翻译专家，擅长Minecraft相关内容的翻译。"

                if self.user_prompt:
                    user_prompt = self._format_prompt(
                        self.user_prompt,
                        source_language="中文",
                        target_language=target_lang_name,
                        content_to_translate=source_text
                    )
                else:
                    user_prompt = f"""请将以下JSON格式的中文游戏本地化文本翻译为{target_lang_name}。

要求：
1. 保持JSON格式不变，只翻译值部分
2. 保持游戏术语的一致性和准确性
3. 考虑游戏上下文，使翻译自然流畅
4. 保持原有的格式标记（如方括号、冒号等）
5. 对于专有名词（如"数据包"、"实体"等），使用游戏中的标准翻译

源文本：
{source_text}

请直接返回翻译后的JSON，不要添加任何解释文字。"""

                payload = {
                    "model": "deepseek-reasoner",  # 使用思考模式
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "temperature": 1.3,
                    "stream": False
                }

                # 调用API
                response = requests.post(DEEPSEEK_API_URL, headers=self.headers, json=payload, timeout=60)
                response.raise_for_status()

                result = response.json()
                translated_content = result["choices"][0]["message"]["content"].strip()

                # 清理响应内容
                if translated_content.startswith("```json"):
                    translated_content = translated_content[7:]
                if translated_content.startswith("```"):
                    translated_content = translated_content[3:]
                if translated_content.endswith("```"):
                    translated_content = translated_content[:-3]
                translated_content = translated_content.strip()

                # 解析JSON
                try:
                    translated_dict = json.loads(translated_content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON解析失败: {e}")

                # 验证翻译结果
                validation_errors = self.validate_translation_result(texts, translated_dict)
                if validation_errors:
                    raise ValueError(f"翻译验证失败: {'; '.join(validation_errors)}")

                # 验证成功，返回结果
                print(f"翻译成功，尝试次数: {attempt + 1}")
                return translated_dict

            except Exception as e:
                error_msg = f"翻译尝试 {attempt + 1} 失败: {str(e)}"
                print(error_msg)

                # 记录失败详情
                self.log_translation_failure(
                    attempt=attempt + 1,
                    system_prompt=system_prompt if 'system_prompt' in locals() else "未生成",
                    user_prompt=user_prompt if 'user_prompt' in locals() else "未生成",
                    api_response=translated_content if 'translated_content' in locals() else "无响应",
                    error=str(e),
                    texts=texts
                )

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    # 最后一次尝试失败，返回空字典
                    print(f"翻译失败，已重试 {max_retries} 次: {str(e)}")
                    return {}

def load_json_file(file_path: str) -> Optional[Dict[str, str]]:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误 {file_path}: {e}")
        return None

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

def merge_translations(base_dict: Dict[str, str], override_dict: Dict[str, str]) -> Dict[str, str]:
    """合并翻译，override_dict中的内容会覆盖base_dict中的对应内容"""
    result = base_dict.copy()
    result.update(override_dict)
    return result

def get_namespace_list() -> List[str]:
    """获取所有命名空间列表"""
    namespaces = []
    assets_dir = Path(ASSETS_DIR)
    if assets_dir.exists():
        for namespace_dir in assets_dir.iterdir():
            if namespace_dir.is_dir() and namespace_dir.name not in ['system_prompt.md', 'user_prompt.md']:
                lang_dir = namespace_dir / "lang"
                if lang_dir.exists():
                    namespaces.append(namespace_dir.name)
    return namespaces

def load_namespace_translations(namespace: str, lang_code: str) -> Dict[str, str]:
    """加载指定命名空间的翻译"""
    # 先尝试从assets目录加载
    assets_file = Path(ASSETS_DIR) / namespace / "lang" / f"{lang_code}.json"
    if assets_file.exists():
        return load_json_file(str(assets_file)) or {}
    
    # 再尝试从translate目录加载
    translate_file = Path(TRANSLATE_DIR) / namespace / "lang" / f"{lang_code}.json"
    if translate_file.exists():
        return load_json_file(str(translate_file)) or {}
    
    return {}

def save_namespace_translations(namespace: str, lang_code: str, translations: Dict[str, str]) -> bool:
    """保存指定命名空间的翻译到translate目录"""
    translate_dir = Path(TRANSLATE_DIR) / namespace / "lang"
    translate_dir.mkdir(parents=True, exist_ok=True)
    
    translate_file = translate_dir / f"{lang_code}.json"
    return save_json_file(str(translate_file), translations)

def find_existing_translations(lang_code: str) -> Dict[str, str]:
    """查找现有的翻译文件"""
    existing_translations = {}

    # 动态查找assets目录中的所有命名空间
    for namespace in get_namespace_list():
        namespace_translations = load_namespace_translations(namespace, lang_code)
        existing_translations.update(namespace_translations)

    return existing_translations

def should_translate(lang_code: str, source_dict: Dict[str, str]) -> bool:
    """判断是否需要翻译"""
    force_translate = os.getenv('FORCE_TRANSLATE', 'false').lower() == 'true'

    if force_translate:
        return True

    # 检查translate目录中是否已存在该语言文件
    translate_file = f"{TRANSLATE_DIR}/{lang_code}.json"
    if not os.path.exists(translate_file):
        return True

    # 检查现有翻译是否完整
    existing = load_json_file(translate_file)
    if not existing:
        return True

    # 检查是否有新的键需要翻译
    missing_keys = set(source_dict.keys()) - set(existing.keys())
    if missing_keys:
        print(f"{lang_code}: 发现 {len(missing_keys)} 个新键需要翻译")
        return True

    return False

def main():
    """主函数"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("错误：未找到DEEPSEEK_API_KEY环境变量")
        sys.exit(1)

    # 创建翻译器
    translator = DeepSeekTranslator(api_key)

    # 获取所有命名空间
    namespaces = get_namespace_list()
    if not namespaces:
        print("错误：未找到任何命名空间")
        sys.exit(1)

    print(f"找到命名空间: {', '.join(namespaces)}")

    # 处理每种目标语言
    for lang_code, lang_name in TARGET_LANGUAGES.items():
        print(f"\n处理语言: {lang_code} ({lang_name})")

        # 处理每个命名空间
        for namespace in namespaces:
            print(f"\n  处理命名空间: {namespace}")

            # 加载该命名空间的源语言文件
            source_file = Path(ASSETS_DIR) / namespace / "lang" / "zh_cn.json"
            if not source_file.exists():
                print(f"    跳过：源文件不存在 {source_file}")
                continue

            source_dict = load_json_file(str(source_file))
            if not source_dict:
                print(f"    跳过：无法加载源文件 {source_file}")
                continue

            print(f"    加载源文件成功，共 {len(source_dict)} 个键")

            # 检查是否需要翻译
            if not should_translate(lang_code, source_dict):
                print(f"    跳过：无需翻译")
                continue

            # 加载该命名空间已有的翻译
            existing_translate = load_namespace_translations(namespace, lang_code)

            # 确定需要翻译的内容
            keys_to_translate = {}
            for key, value in source_dict.items():
                if key not in existing_translate:
                    keys_to_translate[key] = value

            if not keys_to_translate:
                print(f"    所有内容已翻译完成")
                continue

            print(f"    需要翻译 {len(keys_to_translate)} 个键")

            # 分批翻译（每次最多40个键，避免请求过大）
            batch_size = 40
            all_translated = existing_translate.copy()

            keys_list = list(keys_to_translate.items())
            for i in range(0, len(keys_list), batch_size):
                batch = dict(keys_list[i:i + batch_size])
                print(f"    翻译批次 {i//batch_size + 1}/{(len(keys_list) + batch_size - 1)//batch_size}")

                translated_batch = translator.translate_batch(batch, lang_code, lang_name)
                if translated_batch:
                    all_translated.update(translated_batch)
                    print(f"    成功翻译 {len(translated_batch)} 个键")
                else:
                    print(f"    批次翻译失败")

            # 保存翻译结果到对应的命名空间目录
            if save_namespace_translations(namespace, lang_code, all_translated):
                print(f"    保存成功: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json")
            else:
                print(f"    保存失败: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json")

if __name__ == "__main__":
    main()