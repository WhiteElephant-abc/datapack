def _process_mcfunction_impl(ctx):
    """Implementation of the process_mcfunction rule."""
    output_files = []
    
    for src in ctx.files.srcs:
        # 为每个输入文件创建对应的输出文件，添加后缀避免冲突
        if src.is_source:
            # 对于源文件，在文件名中添加 _processed 后缀
            output_name = src.basename.replace(".mcfunction", "_processed.mcfunction")
            output_file = ctx.actions.declare_file(output_name, sibling = src)
        else:
            # 对于生成的文件，处理不同的扩展名
            if ".raw.mcfunction" in src.basename:
                output_name = src.basename.replace(".raw.mcfunction", "_processed.mcfunction")
            else:
                output_name = src.basename.replace(".mcfunction", "_processed.mcfunction")
            output_file = ctx.actions.declare_file(output_name, sibling = src)
        
        output_files.append(output_file)
        
        # 运行 McfunctionProcessor 处理文件
        ctx.actions.run(
            inputs = [src],
            outputs = [output_file],
            executable = ctx.executable._mcfunction_processor,
            arguments = [src.path, output_file.path],
            mnemonic = "ProcessMcfunction",
            progress_message = "Processing mcfunction file %s" % src.short_path,
        )
    
    return [DefaultInfo(files = depset(output_files))]

process_mcfunction = rule(
    implementation = _process_mcfunction_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_files = [".mcfunction", ".raw.mcfunction"],
            mandatory = True,
            doc = "List of .mcfunction files to process",
        ),
        "_mcfunction_processor": attr.label(
            default = Label("//rule/mcfunction_processor"),
            executable = True,
            cfg = "exec",
        ),
    },
    doc = "Processes .mcfunction files by removing comments, empty lines, and handling line continuations",
)