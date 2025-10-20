## 快速入门 — 给 AI 代码代理的操作要点

下面是让你能立即在本仓库中高效工作的精简指引。保持简短、具体，并以可执行的文件/命令引用为主。

1) 项目概览（高层）
- 这个仓库包含若干 Minecraft datapack 子项目（例如 `auto-lucky-block/`、`stone-disappearance/`、`Localization-Resource-Pack/`）。根目录使用 Bazel 管理所有子包，构建入口以 `BUILD.bazel` 和 `MODULE.bazel` 为准。
- 主要关注点：数据（`*/data/<namespace>/...`）、资源（`Localization-Resource-Pack/assets/...`）与构建规则（`rule/` 目录）。

2) 重要目录与示例文件
- `Localization-Resource-Pack/` — 资源包与本地化源（`assets/`、`languages.json`、`system_prompt.md`、`user_prompt.md`）。
- `translate/` — 自动翻译的输出目录（由 `.github/scripts/translate.py` 与 GitHub Action 写入）。
- `rule/` — 自定义 Bazel 规则与工具（例如 `merge_json.bzl`, `mcfunction_processor/McfunctionProcessor.java`, `json_merger/`）。
- `datapack-function-library/data/dfl/function/` — 可参考的 mcfunction 编写范例。

3) 构建 / 运行 快速命令（项目特有）
- 本地主要使用 bazelisk；常见命令（Windows Powershell）示例：
  - 构建 Localization 资源包并构建某子项目：
    bazelisk build //Localization-Resource-Pack ; bazelisk build //highly-toxic-water
  - 运行某子项目的 server 目标：
    bazelisk run //highly-toxic-water:server
- VSCode 任务已配置在 `.vscode/tasks.json`（查看 `Bazel Build` / `Bazel Run Server` / `Bazel Upload Modrinth`）。使用相同命名的任务可以简化交互。

4) 翻译工作流（具体且重要）
- 自动翻译由 `.github/scripts/translate.py` 驱动，GitHub Action `/.github/workflows/translate.yml` 在 `Localization-Resource-Pack/assets/**` 变更时触发。
- 脚本关键点：
  - 源文件：`Localization-Resource-Pack/assets/<namespace>/lang/zh_cn.json`（和其他命名空间）
  - 输出：`translate/`（随后 `rule/merge_json.bzl` 在构建时将 `translate/` 的内容按策略合并到 `assets/`）
  - 环境变量：`DEEPSEEK_API_KEY`（需要在 CI/本地设定），`FORCE_TRANSLATE`, `NON_THINKING_MODE`, `TRANSLATION_DEBUG`。

5) 项目约定和注意事项（AI 必须遵守的规则）
- JSON 合并策略：`rule/merge_json.bzl` 保证 `translate/` 的文件会先合并，`assets/` 的键将覆盖 `translate/`（所以手工维护的高质量翻译在 assets 中优先）。引用示例：合并逻辑在 `rule/merge_json.bzl`。
- mcfunction 处理：`rule/mcfunction_processor/McfunctionProcessor.java` 提供函数内联、宏展开与返回检测逻辑。对于任何对 `.mcfunction` 的修改，注意：
  - 支持 #function namespace:path 强制替换，支持 $(key) 宏参数，最多内联深度 5 层
  - 命名空间 ID 格式受 NAMESPACE_ID_PATTERN 约束（小写字母、数字、下划线或点等）
- 构建工具和 worker：自定义 Java worker（例如 McfunctionProcessor）在规则中作为可执行工具被调用，修改时请维护对应的 `rule/*` BUILD 规则。

6) 典型改动示例（写给 AI 的可执行指令）
- 添加新语言支持到自动翻译：
  - 编辑 `Localization-Resource-Pack/languages.json` 增加语言代码/名称，自动翻译会在 CI 触发。禁止 AI 直接推送。
- 修改 mcfunction 内联逻辑或模板：编辑 `rule/mcfunction_processor/McfunctionProcessor.java` 并运行相关 Bazel rule 测试构建（保持 worker 可执行性）。

7) 排错与调试提示（快速定位问题）
  - 构建失败时：
    - 在 GitHub Actions 环境下查看 `build.log`（自动生成在 CI 任务中）。
    - 本地构建时请关注 Bazel 的终端输出（可加 `--verbose_failures` 参数）。
- 翻译失败或占位符错误：`translation.log` 与 `.github/scripts/logs/error_summary.log` 包含详细失败记录。

8) 不要做的事情（避免浪费时间）
- 不要直接覆盖 `Localization-Resource-Pack/assets/*` 的手工翻译，除非你确实想替换已有人维护的翻译——assets 的条目优先于 translate 的自动翻译。

9) 如果不确定，优先向人类开发者请求：
- 涉及 Modrinth 上传（`upload_modrinth` 目标）、密钥/凭证存储或公共发布的变更必须由项目维护者审核。
