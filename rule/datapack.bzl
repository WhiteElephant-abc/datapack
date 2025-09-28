load("@//rule:expand_enjoy.bzl", "expand_enjoy")
load("@rules_java//java:defs.bzl", "java_binary")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files")
load("@rules_pkg//pkg:zip.bzl", "pkg_zip")

def _datapack_impl(name, visibility, pack_id, functions_expand, functions, tags, dialogs, deps, minecraft_version):
    expand_enjoy(
        name = name + "_pack_functions_expanded",
        visibility = visibility,
        srcs = functions_expand,
        include_files = ["//template:templates"],
    )

    pkg_files(
        name = name + "_pack_function",
        visibility = visibility,
        srcs = functions + [name + "_pack_functions_expanded"],
        strip_prefix = "data/%s/function" % pack_id,
        prefix = "data/%s/function" % pack_id,
    )

    pkg_files(
        name = name + "_pack_function_legacy",
        visibility = visibility,
        srcs = functions + [name + "_pack_functions_expanded"],
        strip_prefix = "data/%s/function" % pack_id,
        prefix = "data/%s/functions" % pack_id,
    )

    pkg_files(
        name = name + "_vanilla_tag",
        visibility = visibility,
        srcs = tags,
        prefix = "data/minecraft/tags/function",
    )

    pkg_files(
        name = name + "_vanilla_tag_legacy",
        visibility = visibility,
        srcs = tags,
        prefix = "data/minecraft/tags/functions",
    )

    pkg_files(
        name = name + "_pack_dialog",
        visibility = visibility,
        srcs = dialogs,
        prefix = "data/%s/dialog" % pack_id,
    )

    pkg_zip(
        name = name,
        visibility = visibility,
        srcs = [
            ":%s_pack_function" % name,
            ":%s_pack_function_legacy" % name,
            ":%s_vanilla_tag" % name,
            ":%s_vanilla_tag_legacy" % name,
            "//template:mcmeta",
        ] + deps
    )

    java_binary(
        name = name + "_server",
        visibility = visibility,
        srcs = [],
        data = [
            ":" + name,
            "//game:ops_json",
        ],
        jvm_flags = [
            "-Ddev.launch.version=%s" % minecraft_version,
            "-Ddev.launch.type=server",
            "-Ddev.launch.mainClass=net.minecraft.server.Main",
            "-Xmx4G",
            "-Ddev.launch.copyFiles=" +
            "$(rlocationpath //%s:%s):world/datapacks/%s.zip," % (native.package_name(), name, name) +
            "$(rlocationpath //game:ops_json):ops.json",
        ],
        main_class = "top.fifthlight.fabazel.devlaunchwrapper.DevLaunchWrapper",
        runtime_deps = [
            "//game:server",
            "//rule/dev_launch_wrapper",
            "@minecraft//:%s_server_libraries" % minecraft_version,
        ],
    )

datapack = macro(
    attrs = {
        "pack_id": attr.string(configurable = False, mandatory = True),
        "functions_expand": attr.label_list(default = []),
        "functions": attr.label_list(default = []),
        "tags": attr.label_list(default = []),
        "dialogs": attr.label_list(default = []),
        "deps": attr.label_list(default = []),
        "minecraft_version": attr.string(configurable = False, default = "1.21.8"),
    },
    implementation = _datapack_impl,
)
