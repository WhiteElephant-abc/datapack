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
        
        # 复制文件并重命名
        ctx.actions.run(
            inputs = [src],
            outputs = [output_file],
            executable = "cmd",
            arguments = ["/c", "copy", src.path.replace("/", "\\"), output_file.path.replace("/", "\\")],
            mnemonic = "RenameFile",
            progress_message = "Renaming %s to %s" % (src.basename, output_name),
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