load("@//rule:expand_enjoy.bzl", "expand_enjoy")
load("@//rule:process_mcfunction.bzl", "process_mcfunction")
load("@rules_java//java:defs.bzl", "java_binary")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files")
load("@rules_pkg//pkg:zip.bzl", "pkg_zip")

def _datapack_impl(
        name,
        visibility,
        pack_id,
        functions_expand,
        functions,
        function_tags,
        dialogs,
        minecraft_dialog_tags,
        datapack_deps,
        deps,
        minecraft_version):
    expand_enjoy(
        name = name + "_pack_functions_expanded",
        visibility = visibility,
        srcs = functions_expand,
        include_files = ["//template:templates"],
    )

    process_mcfunction(
        name = name + "_pack_function",
        visibility = visibility,
        pack_id = pack_id,
        srcs = functions + [":%s_pack_functions_expanded" % name],
    )

    pkg_files(
        name = name + "_function_tag",
        visibility = visibility,
        srcs = function_tags,
        prefix = "data/minecraft/tags/function",
    )

    pkg_files(
        name = name + "_function_tag_legacy",
        visibility = visibility,
        srcs = function_tags,
        prefix = "data/minecraft/tags/functions",
    )

    pkg_files(
        name = name + "_pack_dialog",
        visibility = visibility,
        srcs = dialogs,
        prefix = "data/%s/dialog" % pack_id,
        strip_prefix = "data/%s/dialog" % pack_id,
    )

    pkg_files(
        name = name + "_minecraft_dialog_tag",
        visibility = visibility,
        srcs = minecraft_dialog_tags,
        prefix = "data/minecraft/tags/dialog",
    )

    native.filegroup(
        name = name + "_components",
        visibility = visibility,
        srcs = [
            ":%s_pack_function" % name,
            ":%s_function_tag" % name,
            ":%s_function_tag_legacy" % name,
            ":%s_pack_dialog" % name,
            ":%s_minecraft_dialog_tag" % name,
        ],
    )

    pkg_zip(
        name = name,
        visibility = visibility,
        srcs = [
            ":%s_components" % name,
            "//template:mcmeta",
        ] + deps + [
            dep + "_components"
            for dep in datapack_deps
        ],
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
        "function_tags": attr.label_list(default = []),
        "dialogs": attr.label_list(default = []),
        "minecraft_dialog_tags": attr.label_list(default = []),
        "datapack_deps": attr.label_list(default = []),
        "deps": attr.label_list(default = []),
        "minecraft_version": attr.string(configurable = False, default = "1.21.9"),
    },
    implementation = _datapack_impl,
)
