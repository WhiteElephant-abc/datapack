def _rename_files_impl(ctx):
    """Implementation of the rename_files rule."""
    output_files = []
    
    for src in ctx.files.srcs:
        # 创建重命名后的输出文件
        if "_processed.mcfunction" in src.basename:
            output_name = src.basename.replace("_processed.mcfunction", ".mcfunction")
        elif ".raw.mcfunction" in src.basename:
            output_name = src.basename.replace(".raw.mcfunction", ".mcfunction")
        else:
            output_name = src.basename
        
        output_file = ctx.actions.declare_file(output_name, sibling = src)
        output_files.append(output_file)
        
        # 复制文件并重命名 - 使用 Bazel 内置的文件操作，完全跨平台
        ctx.actions.expand_template(
            template = src,
            output = output_file,
            substitutions = {},
        )
    
    return [DefaultInfo(files = depset(output_files))]

rename_files = rule(
    implementation = _rename_files_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_empty = True,
            allow_files = [".mcfunction", ".raw.mcfunction"],
        ),
    },
)