# 自动翻译系统

本目录包含使用DeepSeek API进行多语言自动翻译的完整系统。

## 系统组件

### 1. 核心脚本

- **`translate.py`** - 主翻译脚本，调用DeepSeek API进行翻译
- **`merge_translations.py`** - 合并翻译文件到资源包assets目录
- **`test_translation.py`** - 系统测试脚本

### 2. 提示词模板

- **`../Localization-Resource-Pack/assets/system_prompt.md`** - 系统提示词模板
- **`../Localization-Resource-Pack/assets/user_prompt.md`** - 用户提示词模板

### 3. 工作流配置

- **`../workflows/translate.yml`** - GitHub Actions自动化工作流

## 功能特性

### 🌍 多语言支持

支持18种目标语言的自动翻译：

- 英语 (en_us)
- 葡萄牙语-巴西 (pt_br)
- 俄语 (ru_ru)
- 德语 (de_de)
- 西班牙语 (es_es, es_mx)
- 法语 (fr_fr, fr_ca)
- 土耳其语 (tr_tr)
- 日语 (ja_jp)
- 韩语 (ko_kr)
- 波兰语 (pl_pl)
- 荷兰语 (nl_nl)
- 意大利语 (it_it)
- 印尼语 (id_id)
- 越南语 (vi_vn)
- 繁体中文 (zh_tw, zh_hk)

### 🤖 智能翻译

- 使用DeepSeek Reasoner模型，支持思考模式
- 温度设置为1.3，平衡创造性和准确性
- 专业的游戏本地化提示词
- 保持JSON格式和特殊标记完整性

### 🔍 质量保证

- **占位符验证** - 自动检查翻译前后的格式化占位符（%s、%n$s等）一致性
- **JSON完整性检查** - 验证翻译结果的键完整性、值类型和非空性
- **重试机制** - API调用失败时自动重试，最多3次，支持指数退避
- **详细日志** - 记录翻译失败的详细信息，包括提示词、API响应和错误原因

### 📁 文件管理

- 输出到独立的`translate`目录
- 自动合并到资源包assets目录
- 智能增量翻译（只翻译缺失的键）
- 保留现有翻译，优先级高于新翻译

### ⚡ 自动化触发

- 监听`Localization-Resource-Pack/assets/`目录变更
- 检测目标语言文件缺失时自动翻译
- 支持手动触发（`workflow_dispatch`）
- 自动提交和推送翻译结果

## 使用方法

### 自动触发

1. 修改`Localization-Resource-Pack/assets/`目录中的源文件
2. 推送到GitHub仓库
3. GitHub Actions自动执行翻译流程

### 手动触发

1. 访问GitHub仓库的Actions页面
2. 选择"Auto Translation with DeepSeek"工作流
3. 点击"Run workflow"
4. 可选择强制重新翻译所有文件

### 本地测试

```bash
# 运行系统测试
python .github/scripts/test_translation.py

# 手动运行翻译（需要设置DEEPSEEK_API_KEY环境变量）
python .github/scripts/translate.py
```

## 配置说明

### 环境变量

- `DEEPSEEK_API_KEY` - DeepSeek API密钥（在GitHub Secrets中配置）
- `FORCE_TRANSLATE` - 强制重新翻译所有文件（可选）

### 提示词模板变量

提示词模板支持以下变量替换：

- `{{source_language}}` - 源语言名称
- `{{target_language}}` - 目标语言名称
- `{{content_to_translate}}` - 待翻译的JSON内容

### 目录结构

```
translate/                          # 翻译输出目录
├── localization_resource_pack/
│   └── lang/
│       ├── en_us.json
│       ├── pt_br.json
│       └── ...
└── white_elephant/
    └── lang/
        ├── en_us.json
        └── ...
```

## 故障排除

### 常见问题

1. **API调用失败** - 检查DEEPSEEK_API_KEY是否正确配置
2. **JSON格式错误** - 检查提示词模板是否正确
3. **文件权限问题** - 确保GitHub Actions有写入权限
4. **翻译质量问题** - 调整提示词模板或temperature参数
5. **占位符不一致** - 系统会自动检查并重试，查看日志了解具体错误
6. **重试次数耗尽** - 检查API响应和网络连接，可能需要手动重新运行

### 日志查看

- **GitHub Actions日志** - 查看工作流运行的详细过程和错误信息
- **本地日志文件** - 翻译失败时会在 `logs/` 目录生成详细的失败日志
- **测试脚本** - 运行 `test_enhanced_translation.py` 验证系统功能

## 系统架构

```
源文件 (zh_cn.json)
    ↓
DeepSeek API翻译
    ↓
translate目录输出
    ↓
合并到assets目录
    ↓
资源包编译包含
```

## 更新历史

- v1.0 - 基础翻译功能
- v1.1 - 添加提示词模板支持
- v1.2 - 优化文件合并逻辑
- v1.3 - 完善错误处理和测试
- v1.4 - 添加质量保证功能：占位符验证、JSON完整性检查、重试机制和详细日志

本项目使用DeepSeek API自动完成多语言翻译任务。

## 功能特性

- 🤖 使用DeepSeek API的思考模式进行高质量翻译
- 🌍 支持18种目标语言的自动翻译
- 📁 智能文件管理和合并
- 🔄 增量翻译，只翻译新增或修改的内容
- 🛡️ 保护现有翻译，避免覆盖已有的高质量翻译

## 支持的语言

### 第一优先级（强烈推荐）

- `en_us` - English (US)
- `pt_br` - Portuguese (Brazil)
- `ru_ru` - Russian
- `de_de` - German

### 第二优先级（推荐）

- `es_es` - Spanish (Spain)
- `es_mx` - Spanish (Mexico)
- `fr_fr` - French (France)
- `fr_ca` - French (Canada)
- `tr_tr` - Turkish
- `ja_jp` - Japanese
- `ko_kr` - Korean

### 第三优先级（可选）

- `pl_pl` - Polish
- `nl_nl` - Dutch
- `it_it` - Italian
- `id_id` - Indonesian
- `vi_vn` - Vietnamese
- `zh_tw` - Traditional Chinese (Taiwan)
- `zh_hk` - Traditional Chinese (Hong Kong)

## 工作流程

1. **触发条件**：
   - 当 `Localization-Resource-Pack/assets/` 目录中的文件发生更新时
   - 当 `translate/` 目录中缺少某种目标语言文件时
   - 手动触发工作流

2. **翻译过程**：
   - 读取 `zh_cn.json` 作为源语言文件
   - 调用DeepSeek API进行批量翻译
   - 将翻译结果保存到 `translate/` 目录

3. **文件合并**：
   - 将 `translate/` 目录中的翻译合并到 `assets/` 目录结构中
   - 现有翻译文件中的内容优先级更高，不会被覆盖

4. **提交更改**：
   - 自动提交生成的翻译文件
   - 提交信息包含 `[skip ci]` 避免触发无限循环

## API配置

### DeepSeek API参数

- **模型**: `deepseek-reasoner` (思考模式)
- **温度**: `1.3` (提高翻译的创造性和自然度)
- **批处理**: 每次最多翻译20个键值对

### 环境变量

- `DEEPSEEK_API_KEY`: DeepSeek API密钥（在GitHub Secrets中配置）
- `FORCE_TRANSLATE`: 强制重新翻译所有语言（可选，默认为false）

## 文件结构

```
.github/
├── workflows/
│   └── translate.yml          # GitHub Actions工作流
└── scripts/
    ├── translate.py           # 主翻译脚本
    ├── merge_translations.py  # 翻译合并脚本
    └── README.md             # 本文档

translate/                     # 翻译输出目录
├── en_us.json
├── pt_br.json
└── ...

Localization-Resource-Pack/
└── assets/
    ├── localization_resource_pack/
    │   └── lang/
    │       ├── zh_cn.json     # 源语言文件
    │       ├── en_us.json     # 合并后的翻译
    │       └── ...
    └── white_elephant/
        └── lang/
            ├── en_us.json
            └── ...
```

## 使用方法

### 自动触发

1. 修改 `Localization-Resource-Pack/assets/` 目录中的任何文件
2. 推送到GitHub仓库
3. 工作流将自动运行并生成翻译

### 手动触发

1. 在GitHub仓库页面，进入 "Actions" 标签
2. 选择 "Auto Translation with DeepSeek" 工作流
3. 点击 "Run workflow"
4. 可选择是否强制重新翻译所有语言

### 本地测试

```bash
# 设置API密钥
export DEEPSEEK_API_KEY="your_api_key_here"

# 运行翻译脚本
python .github/scripts/translate.py

# 合并翻译文件
python .github/scripts/merge_translations.py
```

## 翻译质量保证

1. **上下文感知**: 翻译提示包含游戏上下文信息
2. **术语一致性**: 使用游戏中的标准翻译术语
3. **格式保持**: 保持原有的格式标记和结构
4. **批量处理**: 避免单个键值对翻译的不一致性
5. **人工审核**: 支持手动覆盖自动翻译的结果

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查 `DEEPSEEK_API_KEY` 是否正确配置
   - 确认API密钥有足够的额度
   - 检查网络连接

2. **翻译质量问题**
   - 可以手动编辑 `assets/` 目录中的翻译文件
   - 手动翻译会在下次合并时保持不变

3. **文件合并问题**
   - 检查JSON格式是否正确
   - 确认文件编码为UTF-8

### 日志查看

在GitHub Actions页面可以查看详细的执行日志，包括：

- 翻译进度
- API调用状态
- 文件保存结果
- 错误信息

## 贡献指南

如需修改翻译逻辑或添加新语言支持：

1. 修改 `translate.py` 中的 `TARGET_LANGUAGES` 字典
2. 调整翻译提示以提高质量
3. 测试新的语言支持
4. 提交Pull Request

## 许可证

本翻译系统遵循项目的开源许可证。
