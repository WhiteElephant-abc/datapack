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
        output_file = ctx.actions.declare_file(src.basename.replace(".mcfunction", ".processed.mcfunction"), sibling = src)
        output_files.append(output_file)

        src_path = _path_relative_to_package(src)
        dest_src_map[src_path] = output_file
        if function_pattern in src_path:
            dest_src_map[src_path.replace(function_pattern, function_placement)] = output_file

        ctx.actions.run(
            inputs = [src],
            outputs = [output_file],
            executable = ctx.executable._mcfunction_processor,
            arguments = [src.path, output_file.path],
            mnemonic = "ProcessMcfunction",
            progress_message = "Processing mcfunction file %s" % src.short_path,
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
        "_mcfunction_processor": attr.label(
            default = Label("//rule/mcfunction_processor"),
            executable = True,
            cfg = "exec",
        ),
        "pack_id": attr.string(
            mandatory = True,
            doc = "The ID of the pack",
        ),
    },
    doc = "Processes .mcfunction files by handling line continuations",
)
