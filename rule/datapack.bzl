load("@//rule:expand_enjoy.bzl", "expand_enjoy")
load("@//rule:process_json.bzl", "process_json")
load("@//rule:process_mcfunction.bzl", "process_mcfunction")
load("@rules_java//java:defs.bzl", "java_binary")
load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup", "pkg_files")
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

    process_json(
        name = name + "_function_tag_compress",
        srcs = function_tags,
    )

    pkg_files(
        name = name + "_function_tag",
        visibility = visibility,
        srcs = [":%s_function_tag_compress" % name],
        prefix = "data/minecraft/tags/function",
    )

    process_json(
        name = name + "_function_tag_legacy_compress",
        srcs = function_tags,
    )

    pkg_files(
        name = name + "_function_tag_legacy",
        visibility = visibility,
        srcs = [":%s_function_tag_legacy_compress" % name],
        prefix = "data/minecraft/tags/functions",
    )

    process_json(
        name = name + "_dialog_compress",
        srcs = dialogs,
    )

    pkg_files(
        name = name + "_pack_dialog",
        visibility = visibility,
        srcs = [":%s_dialog_compress" % name],
        prefix = "data/%s/dialog" % pack_id,
        strip_prefix = "data/%s/dialog" % pack_id,
    )

    process_json(
        name = name + "_minecraft_dialog_tag_compress",
        srcs = minecraft_dialog_tags,
    )

    pkg_files(
        name = name + "_minecraft_dialog_tag",
        visibility = visibility,
        srcs = [":%s_minecraft_dialog_tag_compress" % name],
        prefix = "data/minecraft/tags/dialog",
    )

    pkg_filegroup(
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
        ] + deps,
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
        "deps": attr.label_list(default = []),
        "minecraft_version": attr.string(configurable = False, default = "1.21.9"),
    },
    implementation = _datapack_impl,
)
