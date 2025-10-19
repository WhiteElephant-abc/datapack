"""Minecraft 函数文件处理规则。

此模块定义了用于处理 .mcfunction 文件的 Bazel 规则。
主要功能包括：
- 处理 .mcfunction 文件的行连续符
- 支持数据包 ID 配置
- 自动处理函数文件路径映射
- 使用 Worker 协议提高构建性能

提供 process_mcfunction 规则，用于在构建过程中预处理 Minecraft 函数文件，
确保函数文件格式正确并优化构建性能。
"""

load("@bazel_skylib//lib:paths.bzl", "paths")
load("@rules_pkg//pkg:providers.bzl", "PackageFilesInfo")

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

def _process_mcfunction_impl(ctx):
    """Implementation of the process_mcfunction rule."""
    output_files = []
    dest_src_map = {}
    function_pattern = "data/%s/function" % ctx.attr.pack_id
    function_placement = "data/%s/functions" % ctx.attr.pack_id

    for src in ctx.files.srcs:
        if ctx.attr.keep_original_name:
            output_file = ctx.actions.declare_file(src.basename, sibling = src)
        else:
            output_file = ctx.actions.declare_file(src.basename.replace(".mcfunction", ".processed.mcfunction"), sibling = src)
        output_files.append(output_file)

        src_path = _path_relative_to_package(src)
        dest_src_map[src_path] = output_file
        if function_pattern in src_path:
            dest_src_map[src_path.replace(function_pattern, function_placement)] = output_file

        args = ctx.actions.args()
        args.add(src)
        args.add(output_file)

        args.add_all(ctx.files.deps)

        args.use_param_file("@%s", use_always = True)

        ctx.actions.run(
            inputs = [src] + ctx.files.deps,
            outputs = [output_file],
            executable = ctx.executable._mcfunction_processor,
            arguments = [args],
            mnemonic = "ProcessMcfunction",
            progress_message = "Processing mcfunction file %s" % src.short_path,
            execution_requirements = {
                "supports-workers": "1",
                "requires-worker-protocol": "json",
            },
        )

    return [
        PackageFilesInfo(
            attributes = {},
            dest_src_map = dest_src_map,
        ),
        DefaultInfo(files = depset(output_files)),
    ]

process_mcfunction = rule(
    implementation = _process_mcfunction_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_files = [".mcfunction"],
            mandatory = True,
            doc = "List of .mcfunction files to process",
        ),
        "deps": attr.label_list(
            allow_files = True,
            doc = "Dependencies that provide additional data pack files for cross-pack function calls",
        ),
        "_mcfunction_processor": attr.label(
            default = Label("//rule/mcfunction_processor"),
            executable = True,
            cfg = "exec",
        ),
        "pack_id": attr.string(
            mandatory = True,
            doc = "The ID of the pack",
        ),
        "keep_original_name": attr.bool(
            default = False,
            doc = "Whether to keep the original file name without adding .processed suffix",
        ),
    },
    doc = "Processes .mcfunction files by handling line continuations",
)
