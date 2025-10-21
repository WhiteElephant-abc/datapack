# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个使用 Bazel 构建的 Minecraft 数据包项目集合，包含多个独立的数据包。项目采用语义化版本控制（SemVer 2.0.0）进行版本管理。

## 构建系统

### 主要构建命令

- `bazelisk build //[数据包目录]` - 构建指定的数据包
- `bazelisk build //[数据包目录]:server` - 构建并启动开发服务器
- `bazelisk run //[数据包目录]:upload_modrinth` - 上传数据包到 Modrinth

### 常用构建目标

每个数据包目录都包含以下构建目标：

- `:datapack` - 构建数据包 ZIP 文件
- `:server` - 启动开发服务器别名
- `:upload_modrinth` - 上传到 Modrinth（如果配置了项目 ID）

### 示例构建命令

```bash
# 构建石头消失数据包
bazelisk build //stone-disappearance:stone-disappearance

# 启动自动幸运方块开发服务器
bazelisk run //auto-lucky-block:server

# 构建所有数据包
bazelisk build //...
```

## 项目架构

### 目录结构

- `data/` - 各数据包的 Minecraft 数据文件
  - `[pack_id]/function/` - 数据包函数文件（.mcfunction）
  - `[pack_id]/` - 其他命名空间特定文件
  - `minecraft/` - Minecraft 原生命名空间文件
- `rule/` - Bazel 构建规则定义
  - `datapack.bzl` - 主要的数据包构建宏
  - `process_mcfunction.bzl` - 函数文件处理规则
  - `process_json.bzl` - JSON 文件压缩规则
  - `upload_modrinth.bzl` - Modrinth 上传规则
- `repo/` - 外部依赖配置
- `third_party/` - 第三方库集成
- `template/` - 数据包模板文件

### 数据包组件

每个数据包通常包含：

- `load.mcfunction` - 数据包加载时执行的初始化函数
- `tick.mcfunction` - 每游戏刻执行的函数
- 其他自定义函数文件

### 依赖管理

- **内部依赖**：数据包可以依赖其他数据包（如 `//datapack-function-library:dfl`）
- **外部依赖**：通过 `@unif-logger//:unif-logger` 等引用第三方库
- **Minecraft 版本**：使用 `minecraft_versions_range()` 函数指定支持的版本范围

## 开发工作流

### 创建新数据包

1. 在根目录创建新的数据包目录
2. 创建 `BUILD.bazel` 文件，使用 `complete_datapack_config()` 宏
3. 按照标准结构组织数据文件
4. 设置正确的 `pack_id` 和版本号

### 版本管理

- 所有版本号必须符合 SemVer 2.0.0 规范
- 使用 `validate_semver()` 函数验证版本号
- 版本号格式：`主版本号.次版本号.修订号`（如 `1.2.3`）

### 函数开发

- 函数文件使用 `.mcfunction` 扩展名
- 遵循 Minecraft 数据包函数语法
- 使用 `process_mcfunction` 规则进行预处理

## 配置宏

### complete_datapack_config

主要的数据包配置宏，参数包括：

- `pack_id` - 数据包命名空间 ID
- `pack_version` - 数据包版本（必须符合 SemVer）
- `game_versions` - 支持的 Minecraft 版本范围
- `modrinth_project_id` - Modrinth 项目 ID（可选）
- `deps` - 依赖列表

### minecraft_versions_range

获取 Minecraft 版本范围的辅助函数：

- `minecraft_versions_range("1.20.3")` - 从 1.20.3 到最新版本
- `minecraft_versions_range("1.20.3", "1.21.5")` - 指定范围

## 本地化系统

### 本地化架构

项目采用自动翻译和手动维护相结合的本地化方案：

- **本地化资源包**：`Localization-Resource-Pack/` - 包含资源包和本地化源文件
  - `assets/` - 资源包资产文件
  - `languages.json` - 支持的语言配置
  - `system_prompt.md` - 翻译系统提示
  - `user_prompt.md` - 翻译用户提示

- **翻译工作目录**：`translate/` - 自动翻译输出目录
  - 由 `.github/scripts/translate.py` 和 GitHub Action 写入
  - 构建时通过 `rule/merge_json.bzl` 合并到资源包

### 翻译工作流

- **自动翻译触发**：当 `Localization-Resource-Pack/assets/**` 发生变更时，GitHub Action `/.github/workflows/translate.yml` 自动触发
- **翻译脚本**：`.github/scripts/translate.py` 驱动自动翻译
  - 源文件：`Localization-Resource-Pack/assets/` 中的所有本地化文件
  - 输出：`translate/` 目录
  - 环境变量：`DEEPSEEK_API_KEY`（必需）、`FORCE_TRANSLATE`、`NON_THINKING_MODE`、`TRANSLATION_DEBUG`

### JSON 合并策略

- **优先级规则**：`assets/` 的手工翻译优先于 `translate/` 的自动翻译
- **合并逻辑**：`rule/merge_json.bzl` 确保 `translate/` 的文件先合并，`assets/` 的键覆盖 `translate/`
- **维护原则**：手工维护的高质量翻译在 `assets/` 中优先保留

### 添加新语言支持

1. 编辑 `Localization-Resource-Pack/languages.json` 添加语言代码和名称
2. 自动翻译会在 CI 中触发生成对应语言文件
3. 构建系统自动处理合并到最终资源包

## 注意事项

- 所有数据包都使用 GPL 许可证
- 项目包含本地化资源包依赖
- 构建系统会自动处理 JSON 文件压缩和函数文件扩展
- 开发服务器配置为 4GB 内存，可在 `datapack.bzl` 中调整
- **本地化注意事项**：
  - 不必手动更新 `translate/` 的机器翻译
  - `assets/` 的条目优先于 `translate/` 的自动翻译
  - 涉及 Modrinth 上传、密钥存储或公共发布的变更必须由项目维护者审核
