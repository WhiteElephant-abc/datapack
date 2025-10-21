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

## 注意事项

- 所有数据包都使用 GPL 许可证
- 项目包含本地化资源包依赖
- 构建系统会自动处理 JSON 文件压缩和函数文件扩展
- 开发服务器配置为 4GB 内存，可在 `datapack.bzl` 中调整
