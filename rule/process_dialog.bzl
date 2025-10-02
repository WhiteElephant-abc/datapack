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

def _basename_without_ext(path):
    # Return file name without extension
    base = paths.basename(path)
    for ext in [".mcfunction", ".json"]:
        if base.endswith(ext):
            return base[:-len(ext)]
    return base

def _process_dialog_impl(ctx):
    # Map basenames to files
    mc_map = {}
    for f in ctx.files.functions:
        mc_map[_basename_without_ext(_path_relative_to_package(f))] = f
    json_map = {}
    for f in ctx.files.jsons:
        json_map[_basename_without_ext(_path_relative_to_package(f))] = f

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