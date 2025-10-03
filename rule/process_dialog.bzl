"""对话系统处理规则。

此模块定义了用于处理 Minecraft 对话系统的 Bazel 规则。
主要功能包括：
- 配对处理 .mcfunction 和 .json 对话文件
- 从命名空间/function/dialog下寻找mcfunction文件
- 从命名空间/dialog/snbt下寻找json文件
- 生成 $dialog 命令
- 支持未配对的 mcfunction 文件直接传递
- 忽略仅有 JSON 的文件
- 在目录不存在时自动跳过处理

提供 process_dialog 规则，用于在构建过程中处理对话文件对，
将对话配置转换为可执行的 Minecraft 函数。
"""

load("@bazel_skylib//lib:paths.bzl", "paths")

def _owner(file):
    if file.owner == None:
        fail("File {} ({}) has no owner attribute; cannot continue".format(file, file.path))
    return file.owner

def _relative_workspace_root(label):
    return paths.join("..", label.workspace_name) if label.workspace_name else ""

def _path_relative_to_package(file):
    owner = _owner(file)
    return paths.relativize(
        file.short_path,
        paths.join(_relative_workspace_root(owner), owner.package),
    )

def _get_file_key(path, is_mcfunction):
    # 提取文件名（不含扩展名）作为配对键
    base = paths.basename(path)
    if is_mcfunction:
        if base.endswith(".mcfunction"):
            return base[:-11]  # 移除 .mcfunction 扩展名
    else:
        if base.endswith(".json"):
            return base[:-5]  # 移除 .json 扩展名
    return base

def _process_dialog_impl(ctx):
    # 如果文件列表为空，直接返回空结果（目录不存在时自动跳过处理）
    if not ctx.files.functions and not ctx.files.jsons:
        return [DefaultInfo(files = depset([]))]
    
    # Map 文件名到文件
    mc_map = {}
    for f in ctx.files.functions:
        # 从命名空间/function/dialog下寻找mcfunction文件
        rel_path = _path_relative_to_package(f)
        if "function/dialog/" in rel_path:
            key = _get_file_key(rel_path, True)
            mc_map[key] = f
    
    json_map = {}
    for f in ctx.files.jsons:
        # 从命名空间/dialog/snbt下寻找json文件
        rel_path = _path_relative_to_package(f)
        if "dialog/snbt/" in rel_path:
            key = _get_file_key(rel_path, False)
            json_map[key] = f

    output_files = []

    for name, mc_src in mc_map.items():
        json_src = json_map.get(name)
        if json_src:
            # Paired: generate processed mcfunction via worker
            out_file = ctx.actions.declare_file(mc_src.basename, sibling = mc_src)
            args = ctx.actions.args()
            args.add(mc_src)
            args.add(json_src)
            args.add(out_file)

            args.use_param_file("@%s", use_always = True)

            ctx.actions.run(
                inputs = [mc_src, json_src],
                outputs = [out_file],
                executable = ctx.executable._dialog_processor,
                arguments = [args],
                mnemonic = "ProcessDialog",
                progress_message = "Processing dialog pair %s" % name,
                execution_requirements = {
                    "supports-workers": "1",
                    "requires-worker-protocol": "json",
                },
            )
            output_files.append(out_file)
        else:
            # Unpaired mcfunction: pass through as-is
            output_files.append(mc_src)

    # JSON-only files are ignored (not packaged)

    return [
        DefaultInfo(files = depset(output_files)),
    ]

process_dialog = rule(
    implementation = _process_dialog_impl,
    attrs = {
        "functions": attr.label_list(
            allow_files = [".mcfunction"],
            mandatory = True,
            doc = "List of dialog .mcfunction files",
        ),
        "jsons": attr.label_list(
            allow_files = [".json"],
            mandatory = True,
            doc = "List of paired dialog .json files",
        ),
        "_dialog_processor": attr.label(
            default = Label("//rule/dialog_processor"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Pairs dialog .mcfunction/.json and generates $dialog commands; JSON excluded",
)