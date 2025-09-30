def _expand_macros(pair):
    return "-D%s=%s" % pair

def _expand_enjoy_impl(ctx):
    include_path = ctx.files.include_files[0].dirname
    for include_file in ctx.files.include_files:
        if include_file.dirname != include_path:
            fail("All include files must be in the same directory")

    output_files = []
    for src in ctx.files.srcs:
        output_file = ctx.actions.declare_file(src.basename.replace(".enjoy.", ".raw."), sibling = src)
        output_files.append(output_file)

        args = ctx.actions.args()
        args.add("-o", output_file)
        args.add("-I", include_path)
        args.add_all(ctx.attr.defines.items(), map_each = _expand_macros)
        args.add(src)

        ctx.actions.run(
            inputs = [src] + ctx.files.include_files,
            outputs = [output_file],
            executable = ctx.executable._enjoy_expander,
            arguments = [args],
        )

    return [DefaultInfo(files = depset(output_files))]

expand_enjoy = rule(
    implementation = _expand_enjoy_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_empty = True,
            allow_files = [".enjoy.mcfunction"],
        ),
        "include_files": attr.label_list(
            allow_empty = False,
            allow_files = True,
        ),
        "defines": attr.string_dict(),
        "_enjoy_expander": attr.label(
            default = Label("//rule/enjoy_expander"),
            executable = True,
            cfg = "exec",
        ),
    },
)
