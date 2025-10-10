#!/usr/bin/env python3
"""
自动翻译脚本 - 使用DeepSeek API进行多语言翻译
"""

import os
import sys
import json
import requests
import time
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('translation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class KeyChange:
    """键值对变更信息"""
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    operation: str  # 'added', 'deleted', 'modified'

@dataclass
class FileChanges:
    """文件变更信息"""
    namespace: str
    file_path: str
    added_keys: List[KeyChange]
    deleted_keys: List[KeyChange]
    modified_keys: List[KeyChange]

class ChangeType(Enum):
    """变更类型枚举"""
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"

# 检测是否在GitHub Actions环境中运行
IS_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') == 'true'

def log_progress(message: str, level: str = "info"):
    """统一的进度日志函数，在GitHub Actions中使用特殊格式"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if IS_GITHUB_ACTIONS:
        # GitHub Actions 特殊格式
        if level == "error":
            print(f"::error::{message}")
        elif level == "warning":
            print(f"::warning::{message}")
        else:
            print(f"::notice::[{timestamp}] {message}")
    
    # 标准日志输出
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)
    
    # 强制刷新输出缓冲区
    sys.stdout.flush()

def log_section(title: str):
    """记录主要章节，在GitHub Actions中使用分组"""
    if IS_GITHUB_ACTIONS:
        print(f"::group::{title}")
    log_progress(f"=== {title} ===")

def log_section_end():
    """结束章节分组"""
    if IS_GITHUB_ACTIONS:
        print("::endgroup::")

class ProgressTracker:
    """进度跟踪器"""
    def __init__(self, total_languages: int, total_namespaces: int):
        self.total_languages = total_languages
        self.total_namespaces = total_namespaces
        self.current_language = 0
        self.current_namespace = 0
        self.start_time = time.time()
        
    def start_language(self, lang_code: str, lang_name: str):
        self.current_language += 1
        self.current_namespace = 0
        elapsed = time.time() - self.start_time
        log_section(f"语言 {self.current_language}/{self.total_languages}: {lang_code} ({lang_name}) - 已用时 {elapsed:.1f}s")
        
    def start_namespace(self, namespace: str):
        self.current_namespace += 1
        log_progress(f"  命名空间 {self.current_namespace}/{self.total_namespaces}: {namespace}")
        
    def log_batch_progress(self, batch_num: int, total_batches: int, batch_size: int):
        log_progress(f"    批次 {batch_num}/{total_batches} (每批 {batch_size} 个键)")
        
    def finish_language(self):
        log_section_end()
        
    def get_total_progress(self) -> str:
        total_tasks = self.total_languages * self.total_namespaces
        completed_tasks = (self.current_language - 1) * self.total_namespaces + self.current_namespace
        percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        elapsed = time.time() - self.start_time
        return f"总进度: {completed_tasks}/{total_tasks} ({percentage:.1f}%) - 已用时 {elapsed:.1f}s"

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
        
        if not texts:
            return {}

        source_text = json.dumps(texts, ensure_ascii=False, indent=2)
        log_progress(f"      开始翻译 {len(texts)} 个键到 {target_lang_name}")

        for attempt in range(max_retries):
            try:
                log_progress(f"      尝试 {attempt + 1}/{max_retries}")
                
                # 使用提示词模板或回退到默认提示词
                if self.system_prompt:
                    system_prompt = self._format_prompt(
                        self.system_prompt,
                        source_language="中文",
                        target_language=target_lang_name
                    )
                    log_progress(f"      使用自定义系统提示词 (长度: {len(system_prompt)} 字符)")
                else:
                    system_prompt = "你是一个专业的游戏本地化翻译专家，擅长Minecraft相关内容的翻译。"
                    log_progress(f"      使用默认系统提示词")

                if self.user_prompt:
                    user_prompt = self._format_prompt(
                        self.user_prompt,
                        source_language="中文",
                        target_language=target_lang_name,
                        content_to_translate=source_text
                    )
                    log_progress(f"      使用自定义用户提示词 (长度: {len(user_prompt)} 字符)")
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
                    log_progress(f"      使用默认用户提示词")

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
                log_progress(f"      发送API请求到DeepSeek...")
                start_time = time.time()
                response = requests.post(DEEPSEEK_API_URL, headers=self.headers, json=payload, timeout=60)
                api_time = time.time() - start_time
                log_progress(f"      API响应时间: {api_time:.2f}s, 状态码: {response.status_code}")
                
                response.raise_for_status()

                result = response.json()
                translated_content = result["choices"][0]["message"]["content"].strip()
                log_progress(f"      收到翻译响应 (长度: {len(translated_content)} 字符)")

                # 清理响应内容
                original_content = translated_content
                if translated_content.startswith("```json"):
                    translated_content = translated_content[7:]
                if translated_content.startswith("```"):
                    translated_content = translated_content[3:]
                if translated_content.endswith("```"):
                    translated_content = translated_content[:-3]
                translated_content = translated_content.strip()
                
                if original_content != translated_content:
                    log_progress(f"      清理代码块标记后长度: {len(translated_content)} 字符")

                # 解析JSON
                try:
                    log_progress(f"      解析JSON响应...")
                    translated_dict = json.loads(translated_content)
                    log_progress(f"      JSON解析成功，包含 {len(translated_dict)} 个键")
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON解析失败: {e}")

                # 验证翻译结果
                log_progress(f"      验证翻译结果...")
                validation_errors = self.validate_translation_result(texts, translated_dict)
                if validation_errors:
                    log_progress(f"      验证失败: {'; '.join(validation_errors)}", "warning")
                    raise ValueError(f"翻译验证失败: {'; '.join(validation_errors)}")

                # 验证成功，返回结果
                log_progress(f"      翻译成功！尝试次数: {attempt + 1}, 总耗时: {time.time() - start_time:.2f}s")
                return translated_dict

            except Exception as e:
                error_msg = f"翻译尝试 {attempt + 1} 失败: {str(e)}"
                log_progress(error_msg, "error")

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
                    log_progress(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    # 最后一次尝试失败，返回空字典
                    log_progress(f"翻译失败，已重试 {max_retries} 次: {str(e)}", "error")
                    return {}

def get_git_changes() -> List[FileChanges]:
    """获取Git变更，检测源翻译文件的变化"""
    try:
        # 获取最新提交的变更文件列表
        result = subprocess.run([
            'git', 'diff', '--name-only', 'HEAD~1', 'HEAD'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            log_progress("无法获取Git差异，使用全量翻译模式", "warning")
            return []
        
        changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        log_progress(f"检测到 {len(changed_files)} 个变更文件")
        
        file_changes = []
        
        for file_path in changed_files:
            # 只处理源翻译文件 (en_us.json)
            if not file_path.endswith('/lang/en_us.json'):
                continue
                
            # 提取命名空间
            parts = file_path.split('/')
            if len(parts) < 4 or 'assets' not in parts:
                continue
                
            assets_index = parts.index('assets')
            if assets_index + 1 >= len(parts):
                continue
                
            namespace = parts[assets_index + 1]
            
            # 获取文件的具体变更
            changes = get_file_key_changes(file_path)
            if changes:
                file_changes.append(FileChanges(
                    namespace=namespace,
                    file_path=file_path,
                    added_keys=changes['added'],
                    deleted_keys=changes['deleted'],
                    modified_keys=changes['modified']
                ))
        
        return file_changes
        
    except Exception as e:
        log_progress(f"Git差异检测失败: {e}", "error")
        return []

def get_file_key_changes(file_path: str) -> Optional[Dict[str, List[KeyChange]]]:
    """获取单个文件的键值对变更"""
    try:
        # 获取旧版本文件内容
        old_content_result = subprocess.run([
            'git', 'show', f'HEAD~1:{file_path}'
        ], capture_output=True, text=True, cwd='.')
        
        old_data = {}
        if old_content_result.returncode == 0:
            try:
                old_data = json.loads(old_content_result.stdout)
            except json.JSONDecodeError:
                pass
        
        # 获取新版本文件内容
        new_data = {}
        if os.path.exists(file_path):
            new_data = load_json_file(file_path) or {}
        
        # 比较变更
        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())
        
        added_keys = []
        deleted_keys = []
        modified_keys = []
        
        # 添加的键
        for key in new_keys - old_keys:
            added_keys.append(KeyChange(
                key=key,
                old_value=None,
                new_value=new_data[key],
                operation=ChangeType.ADDED.value
            ))
        
        # 删除的键
        for key in old_keys - new_keys:
            deleted_keys.append(KeyChange(
                key=key,
                old_value=old_data[key],
                new_value=None,
                operation=ChangeType.DELETED.value
            ))
        
        # 修改的键
        for key in old_keys & new_keys:
            if old_data[key] != new_data[key]:
                modified_keys.append(KeyChange(
                    key=key,
                    old_value=old_data[key],
                    new_value=new_data[key],
                    operation=ChangeType.MODIFIED.value
                ))
        
        return {
            'added': added_keys,
            'deleted': deleted_keys,
            'modified': modified_keys
        }
        
    except Exception as e:
        log_progress(f"获取文件变更失败 {file_path}: {e}", "error")
        return None

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

def get_context_for_keys(source_dict: Dict[str, str], target_keys: List[str], max_context: int = 10) -> Dict[str, str]:
    """为目标键获取上下文键值对"""
    if len(target_keys) >= max_context:
        # 如果目标键数量已经超过最大上下文数，直接返回目标键
        return {key: source_dict[key] for key in target_keys if key in source_dict}
    
    source_keys = list(source_dict.keys())
    target_set = set(target_keys)
    context_dict = {}
    
    # 添加目标键
    for key in target_keys:
        if key in source_dict:
            context_dict[key] = source_dict[key]
    
    # 如果目标键数量已经达到上下文限制，直接返回
    if len(context_dict) >= max_context:
        return context_dict
    
    # 计算需要添加的上下文数量
    needed_context = max_context - len(context_dict)
    
    # 为每个目标键段落添加上下文
    segments = []
    current_segment = []
    
    # 将连续的目标键分组为段落
    for i, key in enumerate(source_keys):
        if key in target_set:
            current_segment.append(i)
        else:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
    
    if current_segment:
        segments.append(current_segment)
    
    # 为每个段落添加前后上下文
    context_indices = set()
    context_per_segment = max(1, needed_context // (len(segments) * 2)) if segments else 0
    
    for segment in segments:
        start_idx = segment[0]
        end_idx = segment[-1]
        
        # 添加段落前的上下文
        for i in range(max(0, start_idx - context_per_segment), start_idx):
            context_indices.add(i)
        
        # 添加段落后的上下文
        for i in range(end_idx + 1, min(len(source_keys), end_idx + 1 + context_per_segment)):
            context_indices.add(i)
    
    # 如果还需要更多上下文，继续扩展
    remaining_needed = needed_context - len(context_indices)
    if remaining_needed > 0:
        for segment in segments:
            if remaining_needed <= 0:
                break
            start_idx = segment[0]
            end_idx = segment[-1]
            
            # 继续向前扩展
            for i in range(max(0, start_idx - context_per_segment - 1), max(0, start_idx - context_per_segment)):
                if remaining_needed <= 0:
                    break
                context_indices.add(i)
                remaining_needed -= 1
            
            # 继续向后扩展
            for i in range(min(len(source_keys), end_idx + 1 + context_per_segment), 
                          min(len(source_keys), end_idx + 1 + context_per_segment + 1)):
                if remaining_needed <= 0:
                    break
                context_indices.add(i)
                remaining_needed -= 1
    
    # 添加上下文键到结果中
    for idx in sorted(context_indices):
        key = source_keys[idx]
        if key not in context_dict and len(context_dict) < max_context:
            context_dict[key] = source_dict[key]
    
    return context_dict

def delete_keys_from_translations(namespace: str, keys_to_delete: List[str]) -> bool:
    """从所有翻译文件中删除指定的键"""
    success = True
    
    for lang_code, _ in TARGET_LANGUAGES.items():
        if lang_code == 'en_us':  # 跳过源语言
            continue
            
        translate_file = Path(TRANSLATE_DIR) / namespace / "lang" / f"{lang_code}.json"
        if not translate_file.exists():
            continue
        
        # 加载现有翻译
        translations = load_json_file(str(translate_file))
        if not translations:
            continue
        
        # 删除指定的键
        modified = False
        for key in keys_to_delete:
            if key in translations:
                del translations[key]
                modified = True
        
        # 如果有修改，保存文件
        if modified:
            if save_json_file(str(translate_file), translations):
                log_progress(f"    ✓ 从 {lang_code} 翻译中删除了 {len([k for k in keys_to_delete if k in translations])} 个键")
            else:
                log_progress(f"    ✗ 删除键失败: {translate_file}", "error")
                success = False
    
    return success

def needs_translation(namespace: str, lang_code: str, source_dict: Dict[str, str]) -> bool:
    """判断是否需要翻译"""
    force_translate = os.getenv('FORCE_TRANSLATE', 'false').lower() == 'true'

    if force_translate:
        return True

    # 检查已有翻译是否完整
    existing_translations = load_namespace_translations(namespace, lang_code)
    
    # 如果没有任何翻译，需要翻译
    if not existing_translations:
        return True

    # 检查是否有新的键需要翻译
    missing_keys = set(source_dict.keys()) - set(existing_translations.keys())
    if missing_keys:
        print(f"{lang_code}: 发现 {len(missing_keys)} 个新键需要翻译")
        return True

    return False

def main():
    """主函数"""
    log_section("翻译脚本启动")
    
    # 检查环境变量
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        log_progress("错误：未找到DEEPSEEK_API_KEY环境变量", "error")
        sys.exit(1)
    
    log_progress("✓ API密钥已配置")

    # 创建翻译器
    translator = DeepSeekTranslator(api_key)
    log_progress("✓ 翻译器初始化完成")

    # 检查是否强制翻译
    force_translate = os.getenv('FORCE_TRANSLATE', 'false').lower() == 'true'
    
    if force_translate:
        log_progress("🔄 强制翻译模式：将重新翻译所有内容")
        # 使用原有的全量翻译逻辑
        run_full_translation(translator)
    else:
        log_progress("🔍 智能翻译模式：检测Git变更")
        # 使用新的智能差异翻译逻辑
        run_smart_translation(translator)

def run_full_translation(translator):
    """运行全量翻译（原有逻辑）"""
    # 获取所有命名空间
    log_progress("扫描命名空间...")
    namespaces = get_namespace_list()
    if not namespaces:
        log_progress("错误：未找到任何命名空间", "error")
        sys.exit(1)

    log_progress(f"✓ 找到 {len(namespaces)} 个命名空间: {', '.join(namespaces)}")
    log_progress(f"✓ 目标语言: {len(TARGET_LANGUAGES)} 种")
    
    # 创建进度跟踪器
    progress_tracker = ProgressTracker(len(TARGET_LANGUAGES), len(namespaces))
    
    log_section_end()
    
    # 调用原有的翻译逻辑
    continue_full_translation(translator, progress_tracker, namespaces)

def run_smart_translation(translator):
    """运行智能差异翻译"""
    # 检测Git变更
    file_changes = get_git_changes()
    
    if not file_changes:
        log_progress("未检测到源翻译文件变更，跳过翻译")
        return
    
    log_progress(f"检测到 {len(file_changes)} 个命名空间有变更")
    
    # 处理每个有变更的命名空间
    for changes in file_changes:
        log_section(f"处理命名空间: {changes.namespace}")
        
        # 首先处理删除的键
        if changes.deleted_keys:
            deleted_key_names = [change.key for change in changes.deleted_keys]
            log_progress(f"删除 {len(deleted_key_names)} 个键: {', '.join(deleted_key_names[:5])}{'...' if len(deleted_key_names) > 5 else ''}")
            delete_keys_from_translations(changes.namespace, deleted_key_names)
        
        # 处理添加和修改的键（视为添加）
        added_and_modified = changes.added_keys + changes.modified_keys
        if not added_and_modified:
            log_progress("没有需要翻译的新增或修改内容")
            continue
        
        # 加载源文件
        source_file = Path(ASSETS_DIR) / changes.namespace / "lang" / "en_us.json"
        source_dict = load_json_file(str(source_file))
        if not source_dict:
            log_progress(f"无法加载源文件: {source_file}", "error")
            continue
        
        # 获取需要翻译的键
        keys_to_translate = [change.key for change in added_and_modified]
        log_progress(f"需要翻译 {len(keys_to_translate)} 个键")
        
        # 获取翻译上下文
        context_dict = get_context_for_keys(source_dict, keys_to_translate, max_context=10)
        log_progress(f"翻译上下文包含 {len(context_dict)} 个键值对")
        
        # 翻译到各种目标语言
        for lang_code, lang_name in TARGET_LANGUAGES.items():
            if lang_code == 'en_us':
                continue
                
            log_progress(f"  翻译到 {lang_name} ({lang_code})")
            
            # 翻译上下文
            translated_context = translator.translate_batch(context_dict, lang_code, lang_name)
            if not translated_context:
                log_progress(f"    ✗ 翻译失败", "error")
                continue
            
            # 加载现有翻译
            existing_translations = load_namespace_translations(changes.namespace, lang_code)
            
            # 只保存目标键的翻译（不包括上下文）
            target_translations = {key: translated_context[key] 
                                 for key in keys_to_translate 
                                 if key in translated_context}
            
            # 合并翻译结果
            final_translations = existing_translations.copy()
            final_translations.update(target_translations)
            
            # 保存翻译结果
            if save_namespace_translations(changes.namespace, lang_code, final_translations):
                log_progress(f"    ✓ 成功翻译 {len(target_translations)} 个键")
            else:
                log_progress(f"    ✗ 保存翻译失败", "error")
        
        log_section_end()
    
    log_section("智能翻译完成")
    log_progress("🎉 所有变更已处理完成！")
    log_section_end()

def continue_full_translation(translator, progress_tracker, namespaces):
    """继续执行全量翻译的剩余逻辑"""
    # 处理每种目标语言
    for lang_code, lang_name in TARGET_LANGUAGES.items():
        progress_tracker.start_language(lang_code, lang_name)

        # 处理每个命名空间
        for namespace in namespaces:
            progress_tracker.start_namespace(namespace)

            # 加载该命名空间的源语言文件
            source_file = Path(ASSETS_DIR) / namespace / "lang" / "zh_cn.json"
            if not source_file.exists():
                log_progress(f"    跳过：源文件不存在 {source_file}", "warning")
                continue

            source_dict = load_json_file(str(source_file))
            if not source_dict:
                log_progress(f"    跳过：无法加载源文件 {source_file}", "warning")
                continue

            log_progress(f"    ✓ 加载源文件成功，共 {len(source_dict)} 个键")

            # 检查是否需要翻译
            if not needs_translation(namespace, lang_code, source_dict):
                log_progress(f"    跳过：无需翻译")
                continue

            # 加载该命名空间已有的翻译
            log_progress(f"    加载已有翻译...")
            existing_translate = load_namespace_translations(namespace, lang_code)
            log_progress(f"    ✓ 已有翻译：{len(existing_translate)} 个键")

            # 确定需要翻译的内容
            keys_to_translate = {}
            for key, value in source_dict.items():
                if key not in existing_translate:
                    keys_to_translate[key] = value

            if not keys_to_translate:
                log_progress(f"    所有内容已翻译完成")
                continue

            log_progress(f"    需要翻译 {len(keys_to_translate)} 个新键")

            # 分批翻译（每次最多40个键，避免请求过大）
            batch_size = 40
            all_translated = existing_translate.copy()

            keys_list = list(keys_to_translate.items())
            total_batches = (len(keys_list) + batch_size - 1) // batch_size
            log_progress(f"    开始分批翻译，共 {total_batches} 批，每批最多 {batch_size} 个键")
            
            successful_translations = 0
            for i in range(0, len(keys_list), batch_size):
                batch = dict(keys_list[i:i + batch_size])
                batch_num = i//batch_size + 1
                progress_tracker.log_batch_progress(batch_num, total_batches, len(batch))

                translated_batch = translator.translate_batch(batch, lang_code, lang_name)
                if translated_batch:
                    all_translated.update(translated_batch)
                    successful_translations += len(translated_batch)
                    log_progress(f"      ✓ 批次 {batch_num} 成功翻译 {len(translated_batch)} 个键")
                else:
                    log_progress(f"      ✗ 批次 {batch_num} 翻译失败", "error")

            # 保存翻译结果到对应的命名空间目录
            log_progress(f"    保存翻译结果...")
            if save_namespace_translations(namespace, lang_code, all_translated):
                log_progress(f"    ✓ 保存成功: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json")
                log_progress(f"    ✓ 总计翻译 {successful_translations} 个新键，文件包含 {len(all_translated)} 个键")
            else:
                log_progress(f"    ✗ 保存失败: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json", "error")
                
            log_progress(progress_tracker.get_total_progress())

        progress_tracker.finish_language()

    log_section("翻译完成")
    log_progress("🎉 所有翻译任务已完成！")
    log_section_end()

if __name__ == "__main__":
    main()