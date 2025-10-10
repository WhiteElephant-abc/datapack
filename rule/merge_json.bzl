"""JSON 文件合并规则。

此模块定义了用于合并多个JSON文件的Bazel规则。
主要功能包括：
- 深度合并多个JSON文件的键值对
- 后面的文件会覆盖前面文件的相同键
- 自动压缩输出为单行格式
- 支持批量处理多个文件组

提供 merge_json 规则，用于在构建过程中合并JSON文件，
实现键值对级别的合并而不是文件级别的覆盖。
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

def _merge_json_impl(ctx):
    """Implementation of the merge_json rule."""
    output_files = []
    dest_src_map = {}

    # 按文件名分组输入文件
    file_groups = {}
    for src in ctx.files.srcs:
        basename = src.basename
        if basename not in file_groups:
            file_groups[basename] = []
        file_groups[basename].append(src)

    # 为每个文件组创建合并后的输出文件
    for basename, files in file_groups.items():
        # 按路径排序，确保合并顺序一致
        files = sorted(files, key = lambda f: f.path)
        
        output_file = ctx.actions.declare_file(basename)
        output_files.append(output_file)

        # 使用第一个文件的相对路径作为目标路径
        src_path = _path_relative_to_package(files[0])
        dest_src_map[src_path] = output_file

        args = ctx.actions.args()
        args.add(output_file)  # 输出文件
        args.add_all([f.path for f in files])  # 输入文件列表

        args.use_param_file("@%s", use_always = True)

        ctx.actions.run(
            inputs = files,
            outputs = [output_file],
            executable = ctx.executable._json_merger,
            arguments = [args],
            mnemonic = "MergeJson",
            progress_message = "Merging JSON files into %s" % basename,
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

merge_json = rule(
    implementation = _merge_json_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_files = [".json"],
            mandatory = True,
            doc = "List of .json files to merge. Files with the same name will be merged together.",
        ),
        "_json_merger": attr.label(
            default = Label("//rule/json_merger"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Merges .json files with the same name at key-value level",
)