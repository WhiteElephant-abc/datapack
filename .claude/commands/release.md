比对 $ARGUMENTS 的上一个release（检索git标签）和最新commit的差异，总结然后执行以下步骤：

- 询问用户此次更新的级别，更新 `/$ARGUMENTS/BUILD.bazel` 的pack_version，确保符合SemVer规范：请阅读 `/SemVer.md` 以了解命名规范。注意：如果当前pack_version从来没有发布过，则不修改版本号
- 完全覆盖 `/$ARGUMENTS/NEWS.md` 先添加中文更新日志（格式为无序列表），然后空一行添加分割线，再空一行添加英文翻译
- 检查 `/$ARGUMENTS/README.md` ，如果有陈旧描述，更新它
- 提供一个总结报告
- 询问用户是否满意，获得意见后进行改进
- 如果用户表示满意，添加一个包含此次更改的commit，等待用户最终发布新版本。请阅读 `/.claude/commands/commit.md` 以了解commit规范
