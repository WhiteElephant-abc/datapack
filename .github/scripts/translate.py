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
import threading
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# 检测是否在GitHub Actions环境中运行
IS_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') == 'true'

# 配置详细日志
handlers = [logging.FileHandler('translation.log', encoding='utf-8')]
# 在非GitHub Actions环境中添加控制台输出
if not IS_GITHUB_ACTIONS:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers,
    force=True
)
logger = logging.getLogger(__name__)

def flush_logs():
    """强制刷新所有日志处理器"""
    for handler in logging.getLogger().handlers:
        handler.flush()

def close_logs():
    """关闭所有日志处理器"""
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'close'):
            handler.close()

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

def log_progress(message: str, level: str = "info"):
    """统一的进度日志函数，在GitHub Actions中使用特殊格式"""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # 始终写入日志文件
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)

    if IS_GITHUB_ACTIONS:
        # GitHub Actions 特殊格式输出到控制台
        if level == "error":
            print(f"::error::{message}")
        elif level == "warning":
            print(f"::warning::{message}")
        else:
            print(f"::notice::[{timestamp}] {message}")

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
    "zh_hk": "Traditional Chinese (Hong Kong)",
    "zh_cn": "Simplified Chinese (China)"
}



def get_all_target_languages() -> dict:
    """
    获取所有目标语言

    Returns:
        dict: 所有目标语言字典
    """
    return TARGET_LANGUAGES



class DeepSeekTranslator:
    def __init__(self, api_key: str, non_thinking_mode: bool = False):
        self.api_key = api_key
        self.non_thinking_mode = non_thinking_mode
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self._init_error_logging()
        self.system_prompt = self._load_prompt_template(SYSTEM_PROMPT_FILE)
        self.user_prompt = self._load_prompt_template(USER_PROMPT_FILE)

        # 多线程相关
        self._request_lock = threading.Lock()
        self._active_requests = 0
        self._streaming_requests = {}  # 跟踪流式请求状态

    def _init_error_logging(self):
        """初始化错误日志系统"""
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)

        # 创建新的错误汇总日志文件
        summary_file = os.path.join(log_dir, "error_summary.log")
        session_start = datetime.now().isoformat()

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"翻译错误汇总日志\n")
            f.write(f"会话开始时间: {session_start}\n")
            f.write(f"模式: {'非思考模式' if self.non_thinking_mode else '思考模式'}\n")
            f.write("=" * 80 + "\n\n")

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
            log_progress(f"警告：提示词模板文件 {file_path} 不存在，使用默认提示词", "warning")
            return ""
        except Exception as e:
            log_progress(f"警告：加载提示词模板 {file_path} 时出错: {e}", "warning")
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
            log_progress(f"警告：格式化提示词时出错: {e}", "warning")
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 包含毫秒
        log_file = os.path.join(log_dir, f"translation_failure_{timestamp}_attempt_{attempt}.log")

        # 详细错误日志
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"翻译失败日志 - 尝试次数: {attempt}\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            f.write(f"文本数量: {len(texts)}\n")
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

        # 错误汇总日志
        summary_file = os.path.join(log_dir, "error_summary.log")
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] 尝试 {attempt} 失败: {error[:100]}{'...' if len(error) > 100 else ''}\n")
            f.write(f"  文件: {os.path.basename(log_file)}\n")
            f.write(f"  文本数量: {len(texts)}\n\n")

        log_progress(f"翻译失败日志已保存: {log_file}", "warning")
        flush_logs()  # 确保错误日志被及时写入

    def prepare_texts_for_translation(self, texts: Dict[str, any]) -> Dict[str, str]:
        """准备合并后的文本进行翻译，处理列表值

        Args:
            texts: 可能包含列表值的文本字典

        Returns:
            Dict[str, str]: 准备好的翻译文本字典
        """
        prepared_texts = {}

        for key, value in texts.items():
            if isinstance(value, list):
                # 对于列表值，使用第一个值作为翻译源
                if value:  # 确保列表不为空
                    prepared_texts[key] = value[0]
                else:
                    prepared_texts[key] = ""
            else:
                prepared_texts[key] = str(value)

        return prepared_texts

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
                        target_language=target_lang_name
                    )
                    log_progress(f"      使用自定义系统提示词 (长度: {len(system_prompt)} 字符)")
                else:
                    system_prompt = "你是一个专业的游戏本地化翻译专家，擅长Minecraft相关内容的翻译。"
                    log_progress(f"      使用默认系统提示词")

                if self.user_prompt:
                    user_prompt = self._format_prompt(
                        self.user_prompt,
                        target_language=target_lang_name,
                        content_to_translate=source_text
                    )
                    log_progress(f"      使用自定义用户提示词 (长度: {len(user_prompt)} 字符)")
                else:
                    user_prompt = f"""请将以下JSON格式的游戏本地化文本翻译为{target_lang_name}。

要求：
1. 保持JSON格式不变，只翻译值部分
2. 保持游戏术语的一致性和准确性
3. 考虑游戏上下文，使翻译自然流畅
4. 保持原有的格式标记（如方括号、冒号等）
5. 对于专有名词（如"数据包"、"实体"等），使用游戏中的标准翻译
6. 如果遇到列表格式，则应当参考列表中的所有条目进行翻译。但确保仅输出包含{target_lang_name}语言的字符串而不是列表

源文本：
{source_text}

请直接返回翻译后的JSON，不要添加任何解释文字。"""
                    log_progress(f"      使用默认用户提示词")

                # 根据模式选择模型
                model = "deepseek-chat" if self.non_thinking_mode else "deepseek-reasoner"
                log_progress(f"      使用模型: {model} ({'非思考模式' if self.non_thinking_mode else '思考模式'})")

                payload = {
                    "model": model,
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

    def translate_batch_streaming(self, texts: Dict[str, str], target_lang: str, target_lang_name: str, request_id: int = 1) -> Dict[str, str]:
        """
        使用流式响应的翻译方法，支持早期检测响应开始
        """
        max_retries = 3

        if not texts:
            return {}

        source_text = json.dumps(texts, ensure_ascii=False, indent=2)
        log_progress(f"      [请求{request_id}] 开始流式翻译 {len(texts)} 个键到 {target_lang_name}")

        for attempt in range(max_retries):
            try:
                log_progress(f"      [请求{request_id}] 尝试 {attempt + 1}/{max_retries}")

                # 使用提示词模板或回退到默认提示词
                if self.system_prompt:
                    system_prompt = self._format_prompt(
                        self.system_prompt,
                        target_language=target_lang_name
                    )
                else:
                    system_prompt = "你是一个专业的游戏本地化翻译专家，擅长Minecraft相关内容的翻译。"

                if self.user_prompt:
                    user_prompt = self._format_prompt(
                        self.user_prompt,
                        target_language=target_lang_name,
                        content_to_translate=source_text
                    )
                else:
                    user_prompt = f"""请将以下JSON格式的游戏本地化文本翻译为{target_lang_name}。

要求：
1. 保持JSON格式不变，只翻译值部分
2. 保持游戏术语的一致性和准确性
3. 考虑游戏上下文，使翻译自然流畅
4. 保持原有的格式标记（如方括号、冒号等）
5. 对于专有名词（如"数据包"、"实体"等），使用游戏中的标准翻译

源文本：
{source_text}

请直接返回翻译后的JSON，不要添加任何解释文字。"""

                # 根据模式选择模型
                model = "deepseek-chat" if self.non_thinking_mode else "deepseek-reasoner"

                payload = {
                    "model": model,
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
                    "stream": True  # 启用流式响应
                }

                # 调用API
                log_progress(f"      [请求{request_id}] 发送流式API请求到DeepSeek...")
                start_time = time.time()

                with requests.post(DEEPSEEK_API_URL, headers=self.headers, json=payload, timeout=60, stream=True) as response:
                    response.raise_for_status()

                    # 标记请求开始输出
                    with self._request_lock:
                        self._streaming_requests[request_id] = True
                        log_progress(f"      [请求{request_id}] 开始接收流式响应")

                    # 收集流式响应
                    translated_content = ""
                    first_chunk_received = False

                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                try:
                                    chunk = json.loads(data)
                                    if 'choices' in chunk and len(chunk['choices']) > 0:
                                        delta = chunk['choices'][0].get('delta', {})
                                        if 'content' in delta and delta['content'] is not None:
                                            if not first_chunk_received:
                                                first_chunk_received = True
                                                log_progress(f"      [请求{request_id}] 收到第一个内容块")
                                            translated_content += delta['content']
                                except json.JSONDecodeError:
                                    continue

                    api_time = time.time() - start_time
                    log_progress(f"      [请求{request_id}] 流式响应完成，耗时: {api_time:.2f}s")

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
                    log_progress(f"      [请求{request_id}] JSON解析成功，包含 {len(translated_dict)} 个键")
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON解析失败: {e}")

                # 验证翻译结果
                validation_errors = self.validate_translation_result(texts, translated_dict)
                if validation_errors:
                    raise ValueError(f"翻译验证失败: {'; '.join(validation_errors)}")

                # 验证成功，返回结果
                log_progress(f"      [请求{request_id}] 翻译成功！尝试次数: {attempt + 1}, 总耗时: {time.time() - start_time:.2f}s")
                return translated_dict

            except Exception as e:
                error_msg = f"[请求{request_id}] 翻译尝试 {attempt + 1} 失败: {str(e)}"
                log_progress(error_msg, "error")

                # 记录失败详情到错误日志
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
                    wait_time = (attempt + 1) * 2
                    log_progress(f"[请求{request_id}] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    log_progress(f"[请求{request_id}] 翻译失败，已重试 {max_retries} 次: {str(e)}", "error")
                    return {}
            finally:
                # 清理流式请求状态
                with self._request_lock:
                    if request_id in self._streaming_requests:
                        del self._streaming_requests[request_id]

    def _translate_single_request(self, texts: Dict[str, str], target_lang: str, target_lang_name: str, request_id: int) -> Tuple[int, Dict[str, str]]:
        """
        单个翻译请求的实现，用于多线程调用
        返回 (request_id, 翻译结果)
        """
        with self._request_lock:
            self._active_requests += 1
            log_progress(f"      [请求{request_id}] 开始翻译 {len(texts)} 个键到 {target_lang_name} (活跃请求: {self._active_requests})")

        try:
            result = self.translate_batch(texts, target_lang, target_lang_name)
            return (request_id, result)
        finally:
            with self._request_lock:
                self._active_requests -= 1
                log_progress(f"      [请求{request_id}] 翻译完成 (活跃请求: {self._active_requests})")




    def translate_batch_concurrent_optimized(self, texts_batches: List[Dict[str, str]], target_lang: str, target_lang_name: str) -> Dict[str, str]:
        """
        优化的并发翻译方法：当上一个请求开始输出时才创建新请求
        利用DeepSeek API无并发限制的特性，移除请求数量上限
        """
        if not texts_batches:
            return {}

        # 如果只有一个批次，直接使用流式翻译
        if len(texts_batches) == 1:
            return self.translate_batch_streaming(texts_batches[0], target_lang, target_lang_name, 1)

        log_progress(f"    开始优化并发翻译 {len(texts_batches)} 个批次到 {target_lang_name}")
        log_progress(f"    使用流式响应优化策略，无并发限制")

        merged_results = {}
        completed_batches = 0
        active_futures = {}
        batch_queue = list(enumerate(texts_batches, 1))
        next_request_id = 1

        # 启动第一个请求
        if batch_queue:
            batch_id, batch = batch_queue.pop(0)
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(texts_batches))
            future = executor.submit(self.translate_batch_streaming, batch, target_lang, target_lang_name, next_request_id)
            active_futures[future] = (batch_id, next_request_id)
            next_request_id += 1
            log_progress(f"    启动第一个请求 (批次 {batch_id})")

        try:
            while active_futures or batch_queue:
                # 检查是否有新的流式请求开始输出
                if batch_queue:
                    # 检查是否有请求开始输出（可以启动新请求）
                    streaming_started = False
                    with self._request_lock:
                        if self._streaming_requests:
                            streaming_started = True

                    if streaming_started and len(active_futures) < len(texts_batches):
                        # 启动下一个请求
                        batch_id, batch = batch_queue.pop(0)
                        future = executor.submit(self.translate_batch_streaming, batch, target_lang, target_lang_name, next_request_id)
                        active_futures[future] = (batch_id, next_request_id)
                        log_progress(f"    检测到流式响应开始，启动新请求 (批次 {batch_id})")
                        next_request_id += 1

                # 检查完成的请求
                if active_futures:
                    # 使用短超时检查完成的任务
                    done_futures = []
                    for future in list(active_futures.keys()):
                        try:
                            result = future.result(timeout=0.1)
                            done_futures.append((future, result))
                        except concurrent.futures.TimeoutError:
                            continue
                        except Exception as e:
                            done_futures.append((future, {}))
                            batch_id, request_id = active_futures[future]
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译异常: {str(e)}", "error")

                    # 处理完成的请求
                    for future, result in done_futures:
                        batch_id, request_id = active_futures[future]
                        del active_futures[future]
                        completed_batches += 1

                        if result:
                            merged_results.update(result)
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译成功，获得 {len(result)} 个翻译 ({completed_batches}/{len(texts_batches)} 完成)")
                        else:
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译失败 ({completed_batches}/{len(texts_batches)} 完成)", "warning")

                # 短暂等待，避免过度占用CPU
                time.sleep(0.1)

        finally:
            executor.shutdown(wait=True)

        log_progress(f"    优化并发翻译完成，总共获得 {len(merged_results)} 个翻译")
        return merged_results

    def translate_batch_concurrent_with_context_optimized(self, texts_batches: List[Dict[str, str]], target_lang: str, target_lang_name: str) -> Dict[str, str]:
        """
        优化的上下文保证并发翻译方法：当上一个请求开始输出时才创建新请求
        """
        if not texts_batches:
            return {}

        # 如果只有一个批次，直接使用流式翻译
        if len(texts_batches) == 1:
            batch = texts_batches[0]
            core_keys = batch.pop('__core_keys__', set())
            translated = self.translate_batch_streaming(batch, target_lang, target_lang_name, 1)
            # 只返回核心内容
            return {k: v for k, v in translated.items() if k in core_keys}

        log_progress(f"    开始优化上下文保证并发翻译 {len(texts_batches)} 个批次到 {target_lang_name}")
        log_progress(f"    使用流式响应优化策略，无并发限制")

        merged_results = {}
        completed_batches = 0
        active_futures = {}
        batch_core_keys = {}
        batch_queue = []

        # 准备批次队列和核心键映射
        for i, batch in enumerate(texts_batches, 1):
            if batch:
                core_keys = batch.pop('__core_keys__', set())
                batch_core_keys[i] = core_keys
                batch_queue.append((i, batch))

        next_request_id = 1

        # 启动第一个请求
        if batch_queue:
            batch_id, batch = batch_queue.pop(0)
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(texts_batches))
            future = executor.submit(self.translate_batch_streaming, batch, target_lang, target_lang_name, next_request_id)
            active_futures[future] = (batch_id, next_request_id)
            next_request_id += 1
            log_progress(f"    启动第一个请求 (批次 {batch_id})")

        try:
            while active_futures or batch_queue:
                # 检查是否有新的流式请求开始输出
                if batch_queue:
                    streaming_started = False
                    with self._request_lock:
                        if self._streaming_requests:
                            streaming_started = True

                    if streaming_started and len(active_futures) < len(texts_batches):
                        # 启动下一个请求
                        batch_id, batch = batch_queue.pop(0)
                        future = executor.submit(self.translate_batch_streaming, batch, target_lang, target_lang_name, next_request_id)
                        active_futures[future] = (batch_id, next_request_id)
                        log_progress(f"    检测到流式响应开始，启动新请求 (批次 {batch_id})")
                        next_request_id += 1

                # 检查完成的请求
                if active_futures:
                    done_futures = []
                    for future in list(active_futures.keys()):
                        try:
                            result = future.result(timeout=0.1)
                            done_futures.append((future, result))
                        except concurrent.futures.TimeoutError:
                            continue
                        except Exception as e:
                            done_futures.append((future, {}))
                            batch_id, request_id = active_futures[future]
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译异常: {str(e)}", "error")

                    # 处理完成的请求
                    for future, result in done_futures:
                        batch_id, request_id = active_futures[future]
                        core_keys = batch_core_keys[batch_id]
                        del active_futures[future]
                        completed_batches += 1

                        if result:
                            # 只保存核心内容
                            core_result = {k: v for k, v in result.items() if k in core_keys}
                            merged_results.update(core_result)
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译成功，获得 {len(core_result)} 个核心翻译 (总共 {len(result)} 个) ({completed_batches}/{len(texts_batches)} 完成)")
                        else:
                            log_progress(f"    批次 {batch_id} (请求{request_id}) 翻译失败 ({completed_batches}/{len(texts_batches)} 完成)", "warning")

                # 短暂等待，避免过度占用CPU
                time.sleep(0.1)

        finally:
            executor.shutdown(wait=True)

        log_progress(f"    优化上下文保证并发翻译完成，总共获得 {len(merged_results)} 个核心翻译")
        return merged_results

    def split_texts_for_concurrent_translation(self, texts: Dict[str, str], batch_size: int = 40) -> List[Dict[str, str]]:
        """
        将文本字典分割为适合并发翻译的批次

        Args:
            texts: 要翻译的文本字典
            batch_size: 每个批次的大小

        Returns:
            分割后的批次列表
        """
        if not texts:
            return []

        items = list(texts.items())
        batches = []

        for i in range(0, len(items), batch_size):
            batch_items = items[i:i + batch_size]
            batch_dict = dict(batch_items)
            batches.append(batch_dict)

        log_progress(f"    将 {len(texts)} 个文本分割为 {len(batches)} 个批次 (每批次 {batch_size} 个)")
        return batches

    def split_texts_with_context_guarantee(self, texts: Dict[str, str], batch_size: int = 40, context_size: int = 4) -> List[Dict[str, str]]:
        """
        将文本字典分割为适合并发翻译的批次，并为每个批次添加上下文保证

        Args:
            texts: 要翻译的文本字典
            batch_size: 每个批次的大小
            context_size: 上下文大小（前后各添加的条数）

        Returns:
            分割后的批次列表，每个批次包含上下文
        """
        if not texts:
            return []

        items = list(texts.items())
        total_items = len(items)

        # 如果总数不超过批次大小，直接返回
        if total_items <= batch_size:
            return [dict(items)]

        batches = []

        for i in range(0, total_items, batch_size):
            batch_start = i
            batch_end = min(i + batch_size, total_items)

            # 获取当前批次的核心内容
            core_items = items[batch_start:batch_end]

            # 计算上下文范围
            context_items = []

            if i == 0:
                # 第一段：仅添加后方上下文
                context_start = batch_end
                context_end = min(batch_end + context_size, total_items)
                if context_start < total_items:
                    context_items = items[context_start:context_end]
                    log_progress(f"    批次 {len(batches)+1} (首段): 核心 {len(core_items)} 项 + 后方上下文 {len(context_items)} 项")
                else:
                    log_progress(f"    批次 {len(batches)+1} (首段): 核心 {len(core_items)} 项")
            elif batch_end >= total_items:
                # 最后一段：仅添加前方上下文
                context_start = max(0, batch_start - context_size)
                context_end = batch_start
                context_items = items[context_start:context_end]
                log_progress(f"    批次 {len(batches)+1} (末段): 前方上下文 {len(context_items)} 项 + 核心 {len(core_items)} 项")
            else:
                # 中间段落：前后各添加2条上下文
                half_context = context_size // 2
                # 前方上下文
                pre_context_start = max(0, batch_start - half_context)
                pre_context_end = batch_start
                pre_context = items[pre_context_start:pre_context_end]

                # 后方上下文
                post_context_start = batch_end
                post_context_end = min(batch_end + half_context, total_items)
                post_context = items[post_context_start:post_context_end]

                context_items = pre_context + post_context
                log_progress(f"    批次 {len(batches)+1} (中段): 前方上下文 {len(pre_context)} 项 + 核心 {len(core_items)} 项 + 后方上下文 {len(post_context)} 项")

            # 合并核心内容和上下文
            batch_items = core_items + context_items
            batch_dict = dict(batch_items)

            # 标记哪些是核心内容（需要保存），哪些是上下文（不保存）
            core_keys = set(key for key, _ in core_items)
            batch_dict['__core_keys__'] = core_keys

            batches.append(batch_dict)

        log_progress(f"    将 {len(texts)} 个文本分割为 {len(batches)} 个批次 (每批次 {batch_size} 个 + 上下文)")
        return batches

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
        log_progress(f"文件不存在: {file_path}", "warning")
        return None
    except json.JSONDecodeError as e:
        log_progress(f"JSON解析错误 {file_path}: {e}", "error")
        return None

def save_json_file(file_path: str, data: Dict[str, str]) -> bool:
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_progress(f"保存文件失败 {file_path}: {e}", "error")
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

def merge_namespace_translations(namespace: str, lang_code: str) -> Dict[str, any]:
    """合并同命名空间的所有键值对，包括重复键处理

    Args:
        namespace: 命名空间名称
        lang_code: 语言代码

    Returns:
        Dict[str, any]: 合并后的翻译字典，重复键的值为列表
    """
    merged_translations = {}

    # 收集所有可能的翻译文件路径
    file_paths = []

    # assets目录中的文件
    assets_file = Path(ASSETS_DIR) / namespace / "lang" / f"{lang_code}.json"
    if assets_file.exists():
        file_paths.append(assets_file)

    # translate目录中的文件
    translate_file = Path(TRANSLATE_DIR) / namespace / "lang" / f"{lang_code}.json"
    if translate_file.exists():
        file_paths.append(translate_file)

    # 合并所有文件的内容
    for file_path in file_paths:
        translations = load_json_file(str(file_path))
        if not translations:
            continue

        for key, value in translations.items():
            if key in merged_translations:
                # 处理重复键：转换为列表形式
                existing_value = merged_translations[key]
                if isinstance(existing_value, list):
                    # 如果已经是列表，添加新值
                    if value not in existing_value:
                        existing_value.append(value)
                else:
                    # 如果不是列表，创建新列表
                    if existing_value != value:
                        merged_translations[key] = [existing_value, value]
            else:
                merged_translations[key] = value

    return merged_translations

def get_merged_reference_translations(namespace: str) -> Dict[str, any]:
    """获取合并后的参考翻译，包含所有语言文件中的键值对

    Args:
        namespace: 命名空间名称

    Returns:
        Dict[str, any]: 合并后的参考翻译字典，包含所有已有的键值对
    """
    merged_dict = {}
    namespace_lang_dir = Path(ASSETS_DIR) / namespace / "lang"

    if not namespace_lang_dir.exists():
        return merged_dict

    # 遍历所有语言文件，合并所有键值对
    for lang_file in namespace_lang_dir.glob('*.json'):
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
                # 合并键值对，如果键已存在则保持现有值
                for key, value in lang_data.items():
                    if key not in merged_dict:
                        merged_dict[key] = value
        except (json.JSONDecodeError, IOError) as e:
            log_progress(f"警告：无法读取语言文件 {lang_file}: {e}", "warning")
            continue

    return merged_dict

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

def check_missing_translation_files() -> Dict[str, List[str]]:
    """检查缺失的翻译文件

    Returns:
        Dict[namespace, List[missing_lang_codes]]: 缺失翻译文件的命名空间和语言代码
    """
    missing_files = {}

    # 获取所有命名空间
    namespaces = get_namespace_list()
    if not namespaces:
        return missing_files

    log_progress("检查翻译文件完整性...")

    for namespace in namespaces:
        # 检查是否存在任何语言文件
        namespace_lang_dir = Path(ASSETS_DIR) / namespace / "lang"
        if not namespace_lang_dir.exists():
            continue

        # 检查是否有任何语言文件存在
        has_lang_files = any(f.suffix == '.json' for f in namespace_lang_dir.glob('*.json'))
        if not has_lang_files:
            continue

        missing_langs = []

        # 检查每种目标语言的翻译文件
        for lang_code, lang_name in get_all_target_languages().items():
            translate_file = Path(TRANSLATE_DIR) / namespace / "lang" / f"{lang_code}.json"
            if not translate_file.exists():
                missing_langs.append(lang_code)

        if missing_langs:
            missing_files[namespace] = missing_langs
            log_progress(f"  {namespace}: 缺失 {len(missing_langs)} 个语言的翻译文件")

    if missing_files:
        total_missing = sum(len(langs) for langs in missing_files.values())
        log_progress(f"发现 {len(missing_files)} 个命名空间缺失翻译文件，共 {total_missing} 个文件")
    else:
        log_progress("所有翻译文件完整")

    return missing_files

def create_virtual_changes_for_missing_files(missing_translations: Dict[str, List[str]]) -> List[FileChanges]:
    """为缺失的翻译文件创建虚拟变更

    Args:
        missing_translations: 缺失翻译文件的命名空间和语言代码

    Returns:
        List[FileChanges]: 虚拟的文件变更列表
    """
    virtual_changes = []

    for namespace, missing_langs in missing_translations.items():
        # 使用合并后的参考翻译
        source_dict = get_merged_reference_translations(namespace)
        if not source_dict:
            continue

        # 创建虚拟变更，将所有合并后的键标记为新增
        added_keys = []
        for key, value in source_dict.items():
            # 处理列表值的情况
            if isinstance(value, list):
                # 对于列表值，使用第一个值作为翻译源
                added_keys.append(KeyChange(key=key, old_value=None, new_value=value[0], operation='added'))
            else:
                added_keys.append(KeyChange(key=key, old_value=None, new_value=value, operation='added'))

        virtual_change = FileChanges(
            namespace=namespace,
            file_path=f"merged:{namespace}",  # 标记为合并源
            added_keys=added_keys,
            deleted_keys=[],
            modified_keys=[]
        )

        virtual_changes.append(virtual_change)
        log_progress(f"  为 {namespace} 创建虚拟变更，包含 {len(added_keys)} 个合并后的键")

    return virtual_changes

def check_missing_translation_files() -> List[Tuple[str, str]]:
    """检查缺失的翻译文件

    Returns:
        List[Tuple[str, str]]: 缺失文件的 (namespace, lang_code) 列表
    """
    missing_files = []

    # 获取所有命名空间
    namespaces = get_namespace_list()

    for namespace in namespaces:
        # 检查是否存在任何语言文件
        namespace_lang_dir = Path(ASSETS_DIR) / namespace / "lang"
        if not namespace_lang_dir.exists():
            continue

        # 检查是否有任何语言文件存在
        has_lang_files = any(f.suffix == '.json' for f in namespace_lang_dir.glob('*.json'))
        if not has_lang_files:
            continue

        # 检查每种目标语言的翻译文件
        for lang_code, _ in get_all_target_languages().items():
            translate_file = Path(TRANSLATE_DIR) / namespace / "lang" / f"{lang_code}.json"
            if not translate_file.exists():
                missing_files.append((namespace, lang_code))

    if missing_files:
        log_progress(f"发现 {len(missing_files)} 个缺失的翻译文件")
        for namespace, lang_code in missing_files[:5]:  # 只显示前5个
            log_progress(f"  缺失: {namespace}/{lang_code}.json")
        if len(missing_files) > 5:
            log_progress(f"  ... 还有 {len(missing_files) - 5} 个文件")

    return missing_files

def create_virtual_changes_for_missing_files(missing_files: List[Tuple[str, str]]) -> List[FileChanges]:
    """为缺失的翻译文件创建虚拟变更

    Args:
        missing_files: 缺失文件的 (namespace, lang_code) 列表

    Returns:
        List[FileChanges]: 虚拟变更列表
    """
    # 按命名空间分组
    namespace_groups = {}
    for namespace, lang_code in missing_files:
        if namespace not in namespace_groups:
            namespace_groups[namespace] = []
        namespace_groups[namespace].append(lang_code)

    virtual_changes = []

    for namespace, lang_codes in namespace_groups.items():
        # 使用合并后的参考翻译以获取所有键
        source_dict = get_merged_reference_translations(namespace)
        if not source_dict:
            continue

        # 为每个缺失的语言文件创建虚拟变更
        for lang_code in lang_codes:
            # 创建虚拟变更，将所有合并后的键标记为新增
            added_keys = []
            for key, value in source_dict.items():
                # 处理列表值的情况
                if isinstance(value, list):
                    # 对于列表值，使用第一个值作为翻译源
                    added_keys.append(KeyChange(key=key, old_value=None, new_value=value[0], operation='added'))
                else:
                    added_keys.append(KeyChange(key=key, old_value=None, new_value=value, operation='added'))

            # 构建缺失文件的路径
            missing_file_path = f"{namespace}/{lang_code}.json"

            virtual_changes.append(FileChanges(
                namespace=namespace,
                file_path=missing_file_path,
                added_keys=added_keys,
                deleted_keys=[],
                modified_keys=[]
            ))

        log_progress(f"为命名空间 {namespace} 创建虚拟变更，包含 {len(added_keys)} 个键")

    return virtual_changes

def delete_keys_from_translations(namespace: str, keys_to_delete: List[str]) -> bool:
    """从所有翻译文件中删除指定的键"""
    success = True

    # 处理所有目标语言的翻译文件
    for lang_code, _ in get_all_target_languages().items():
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
        log_progress(f"{lang_code}: 发现 {len(missing_keys)} 个新键需要翻译")
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

    # 检查是否使用非思考模式
    non_thinking_mode = os.getenv('NON_THINKING_MODE', 'false').lower() == 'true'
    if non_thinking_mode:
        log_progress("⚡ 非思考模式：使用deepseek-chat模型以提升速度")
    else:
        log_progress("🧠 思考模式：使用deepseek-reasoner模型以提升质量")

    # 创建翻译器
    translator = DeepSeekTranslator(api_key, non_thinking_mode)
    log_progress("✓ 翻译器初始化完成")

    # 检查翻译模式
    force_translate = os.getenv('FORCE_TRANSLATE', 'false').lower() == 'true'
    merge_translate = os.getenv('MERGE_TRANSLATE', 'false').lower() == 'true'

    if merge_translate:
        log_progress("🔗 合并后翻译模式：合并同命名空间键值对后翻译")
        # 使用新的合并后翻译逻辑
        run_merge_translation(translator)
    elif force_translate:
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
    # 计算需要翻译的语言数
    target_lang_count = len(get_all_target_languages())
    log_progress(f"✓ 目标语言: {target_lang_count} 种")

    # 创建进度跟踪器
    progress_tracker = ProgressTracker(target_lang_count, len(namespaces))

    log_section_end()

    # 调用原有的翻译逻辑
    continue_full_translation(translator, progress_tracker, namespaces)

def run_smart_translation(translator):
    """运行智能差异翻译"""
    # 检测Git变更
    file_changes = get_git_changes()

    # 检查输出文件缺失情况
    missing_translations = check_missing_translation_files()

    if not file_changes and not missing_translations:
        log_progress("未检测到源翻译文件变更，且所有翻译文件完整，跳过翻译")
        return

    if not file_changes and missing_translations:
        log_progress("未检测到源文件变更，但发现缺失的翻译文件，将补充翻译")
        # 为缺失的翻译文件创建虚拟变更，但只包含实际存在的键
        virtual_changes = create_virtual_changes_for_missing_files(missing_translations)
        file_changes.extend(virtual_changes)

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

        # 使用合并后的参考翻译
        source_dict = get_merged_reference_translations(changes.namespace)
        if not source_dict:
            log_progress(f"无法加载命名空间 {changes.namespace} 的合并参考翻译", "error")
            continue

        log_progress(f"✓ 加载合并后的源翻译，包含 {len(source_dict)} 个键值对")

        # 获取需要翻译的键
        keys_to_translate = [change.key for change in added_and_modified]
        log_progress(f"需要翻译 {len(keys_to_translate)} 个键")

        # 获取翻译上下文
        context_dict = get_context_for_keys(source_dict, keys_to_translate, max_context=10)
        log_progress(f"翻译上下文包含 {len(context_dict)} 个键值对")

        # 获取目标语言列表
        target_languages = get_all_target_languages().copy()

        # 如果是虚拟变更（处理缺失文件），排除当前命名空间中缺失的语言作为翻译目标
        if changes.file_path.startswith("merged:"):
            # 检查当前命名空间中缺失的语言文件
            namespace_lang_dir = Path(ASSETS_DIR) / changes.namespace / "lang"
            if namespace_lang_dir.exists():
                missing_langs = []
                for lang_code in target_languages.keys():
                    lang_file = namespace_lang_dir / f"{lang_code}.json"
                    if not lang_file.exists():
                        missing_langs.append(lang_code)

                # 排除缺失的语言作为翻译目标
                for missing_lang in missing_langs:
                    if missing_lang in target_languages:
                        del target_languages[missing_lang]
                        log_progress(f"  跳过缺失的语言: {missing_lang}")

        # 翻译到各种目标语言
        for lang_code, lang_name in target_languages.items():
            log_progress(f"  翻译到 {lang_name} ({lang_code})")

            # 准备合并后的文本进行翻译
            prepared_context = translator.prepare_texts_for_translation(context_dict)
            log_progress(f"  准备翻译文本完成，处理了 {len(prepared_context)} 个键值对")

            # 翻译上下文 - 使用上下文保证机制提升翻译质量
            if len(prepared_context) > 40:  # 如果上下文较大，使用优化的上下文保证并发翻译
                context_batches = translator.split_texts_with_context_guarantee(prepared_context, batch_size=40, context_size=4)
                translated_context = translator.translate_batch_concurrent_with_context_optimized(context_batches, lang_code, lang_name)
            else:
                translated_context = translator.translate_batch(prepared_context, lang_code, lang_name)

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
    # 翻译到所有目标语言
    for lang_code, lang_name in get_all_target_languages().items():
        progress_tracker.start_language(lang_code, lang_name)

        # 处理每个命名空间
        for namespace in namespaces:
            progress_tracker.start_namespace(namespace)

            # 使用合并后的参考翻译
            source_dict = get_merged_reference_translations(namespace)
            if not source_dict:
                log_progress(f"    跳过：无法加载命名空间 {namespace} 的合并参考翻译", "warning")
                continue

            log_progress(f"    ✓ 加载合并后的参考翻译成功，共 {len(source_dict)} 个键值对")

            # 检查是否需要翻译
            if not needs_translation(namespace, lang_code, source_dict):
                log_progress(f"    跳过：无需翻译")
                continue

            # 加载该命名空间已有的翻译
            log_progress(f"    加载已有翻译...")
            existing_translate = load_namespace_translations(namespace, lang_code)
            log_progress(f"    ✓ 已有翻译：{len(existing_translate)} 个键")

            # 确定需要翻译的内容
            force_translate = os.getenv('FORCE_TRANSLATE', 'false').lower() == 'true'
            keys_to_translate = {}

            if force_translate:
                # 强制翻译模式：翻译所有键
                keys_to_translate = source_dict.copy()
                log_progress(f"    强制翻译模式：将重新翻译所有 {len(keys_to_translate)} 个键")
            else:
                # 正常模式：只翻译缺失的键
                for key, value in source_dict.items():
                    if key not in existing_translate:
                        keys_to_translate[key] = value

            if not keys_to_translate:
                log_progress(f"    所有内容已翻译完成")
                continue

            log_progress(f"    需要翻译 {len(keys_to_translate)} 个新键")

            # 准备合并后的文本进行翻译
            prepared_texts = translator.prepare_texts_for_translation(keys_to_translate)
            log_progress(f"    准备翻译文本完成，处理了 {len(prepared_texts)} 个键值对")

            # 分批翻译（每次最多40个键，避免请求过大）
            batch_size = 40
            if force_translate:
                # 强制翻译模式：从空字典开始，完全替换
                all_translated = {}
            else:
                # 正常模式：基于现有翻译进行增量更新
                all_translated = existing_translate.copy()

            keys_list = list(prepared_texts.items())
            # 使用上下文保证机制提升翻译质量
            if len(keys_list) > batch_size:
                log_progress(f"    开始优化的上下文保证并发翻译，文本数量: {len(keys_list)}")
                text_batches = translator.split_texts_with_context_guarantee(dict(keys_list), batch_size=batch_size, context_size=4)
                all_translated = translator.translate_batch_concurrent_with_context_optimized(text_batches, lang_code, lang_name)
                successful_translations = len(all_translated)
                log_progress(f"    优化的上下文保证并发翻译完成，成功翻译 {successful_translations} 个键")
            else:
                # 文本较少时使用单线程翻译
                log_progress(f"    开始单线程翻译，文本数量: {len(keys_list)}")
                all_translated = translator.translate_batch(dict(keys_list), lang_code, lang_name)
                successful_translations = len(all_translated) if all_translated else 0
                log_progress(f"    单线程翻译完成，成功翻译 {successful_translations} 个键")

            flush_logs()  # 确保翻译进度被及时写入日志

            # 保存翻译结果到对应的命名空间目录
            log_progress(f"    保存翻译结果...")
            if save_namespace_translations(namespace, lang_code, all_translated):
                log_progress(f"    ✓ 保存成功: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json")
                if force_translate:
                    log_progress(f"    ✓ 强制翻译完成：重新翻译了 {successful_translations} 个键，文件包含 {len(all_translated)} 个键")
                else:
                    log_progress(f"    ✓ 总计翻译 {successful_translations} 个新键，文件包含 {len(all_translated)} 个键")
            else:
                log_progress(f"    ✗ 保存失败: {TRANSLATE_DIR}/{namespace}/lang/{lang_code}.json", "error")

            log_progress(progress_tracker.get_total_progress())

        progress_tracker.finish_language()

    log_section("翻译完成")
    log_progress("🎉 所有翻译任务已完成！")
    log_section_end()

    # 确保所有日志都被写入文件
    flush_logs()

if __name__ == "__main__":
    try:
        main()
    finally:
        # 确保日志文件被正确关闭
        flush_logs()
        close_logs()
