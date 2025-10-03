"""Minecraft 数据包构建规则。

此模块定义了用于构建 Minecraft 数据包的 Bazel 宏和规则，包括：
- 函数文件的扩展和处理
- JSON 文件的压缩处理
- 对话系统的处理
- 数据包的打包和部署
- 开发服务器的启动配置
- 通用的数据包配置模式
- Modrinth 上传配置的简化

主要提供 datapack 宏，用于定义完整的数据包构建流程。
"""

load("@//rule:expand_enjoy.bzl", "expand_enjoy")
load("@//rule:process_json.bzl", "process_json")
load("@//rule:process_mcfunction.bzl", "process_mcfunction")
load("@//rule:upload_modrinth.bzl", "modrinth_dependency", "upload_modrinth")
load("@rules_java//java:defs.bzl", "java_binary")
load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup", "pkg_files")
load("@rules_pkg//pkg:zip.bzl", "pkg_zip")

# 常用的游戏版本列表
MINECRAFT_VERSIONS_1_13_TO_1_21 = [
    "1.13",
    "1.13.1",
    "1.13.2",
    "1.14",
    "1.14.1",
    "1.14.2",
    "1.14.3",
    "1.14.4",
    "1.15",
    "1.15.1",
    "1.15.2",
    "1.16",
    "1.16.1",
    "1.16.2",
    "1.16.3",
    "1.16.4",
    "1.16.5",
    "1.17",
    "1.17.1",
    "1.18",
    "1.18.1",
    "1.18.2",
    "1.19",
    "1.19.1",
    "1.19.2",
    "1.19.3",
    "1.19.4",
    "1.20",
    "1.20.1",
    "1.20.2",
    "1.20.3",
    "1.20.4",
    "1.20.5",
    "1.20.6",
    "1.21",
    "1.21.1",
    "1.21.2",
    "1.21.3",
    "1.21.4",
    "1.21.5",
    "1.21.6",
    "1.21.7",
    "1.21.8",
]

MINECRAFT_VERSIONS_1_20_PLUS = [
    "1.20",
    "1.20.1",
    "1.20.2",
    "1.20.3",
    "1.20.4",
    "1.20.5",
    "1.20.6",
    "1.21",
    "1.21.1",
    "1.21.2",
    "1.21.3",
    "1.21.4",
    "1.21.5",
    "1.21.6",
    "1.21.7",
    "1.21.8",
]

def datapack_functions(pack_id):
    """生成数据包函数文件的 glob 模式。
    
    Args:
        pack_id: 数据包 ID
        
    Returns:
        包含基础函数和扩展函数的配置字典
    """
    return {
        "functions_include": ["data/%s/function/**/*.mcfunction" % pack_id],
        "functions_exclude": ["data/%s/function/**/*.enjoy.mcfunction" % pack_id],
        "functions_expand_pattern": ["data/%s/function/**/*.enjoy.mcfunction" % pack_id],
    }

def datapack_standard_files(pack_id):
    """生成数据包的标准文件 glob 模式。
    
    Args:
        pack_id: 数据包 ID
        
    Returns:
        包含各种标准文件的配置字典
    """
    return {
        "dialogs_pattern": ["data/%s/dialog/*.json" % pack_id],
        "function_tags_pattern": ["data/minecraft/tags/function/*.json"],
        "minecraft_dialog_tags_pattern": ["data/minecraft/tags/dialog/*.json"],
    }

def standard_localization_dependency():
    """获取标准的本地化资源包依赖配置。
    
    Returns:
        本地化依赖的配置字典
    """
    return {
        "name": "localization_resource_pack",
        "dependency_type": "required",
        "project_id": "3S0b1XES",
        "version_id": "80LeoUFR",
    }

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

def datapack_modrinth_upload(
        name,
        datapack_target,
        pack_version,
        project_id,
        file_name_template = None,
        version_name_template = None,
        game_versions = None,
        version_type = "release",
        changelog = "NEWS.md",
        deps = None):
    """创建 Modrinth 上传配置的简化宏。
    
    Args:
        name: 上传目标的名称
        datapack_target: 数据包目标（如 ":my-datapack"）
        pack_version: 数据包版本
        project_id: Modrinth 项目 ID
        file_name_template: 文件名模板，默认为 "{name}_v{version}_{game_range}.zip"
        version_name_template: 版本名模板，默认为 "[data pack] {name}_v{version}_{game_range}"
        game_versions: 支持的游戏版本列表，默认为 MINECRAFT_VERSIONS_1_20_PLUS
        version_type: 版本类型（alpha, beta, release），默认为 release
        changelog: 更新日志文件，默认为 "NEWS.md"
        deps: 依赖列表，默认包含本地化资源包
    """
    if game_versions == None:
        game_versions = MINECRAFT_VERSIONS_1_20_PLUS
    
    if deps == None:
        deps = [":localization_resource_pack"]
    
    # 确定游戏版本范围字符串
    if game_versions == MINECRAFT_VERSIONS_1_13_TO_1_21:
        game_range = "1.13-1.21.x"
    elif game_versions == MINECRAFT_VERSIONS_1_20_PLUS:
        game_range = "1.20+"
    else:
        # 自定义版本列表，使用首尾版本
        game_range = "%s-%s" % (game_versions[0], game_versions[-1])
    
    # 设置默认模板
    if file_name_template == None:
        file_name_template = "%s_v%s_%s.zip" % (name, pack_version, game_range)
    else:
        file_name_template = file_name_template.format(
            name = name,
            version = pack_version,
            game_range = game_range,
        )
    
    if version_name_template == None:
        version_name_template = "[data pack] %s_v%s_%s" % (name, pack_version, game_range)
    else:
        version_name_template = version_name_template.format(
            name = name,
            version = pack_version,
            game_range = game_range,
        )
    
    upload_modrinth(
        name = "upload_modrinth",
        changelog = changelog,
        file = datapack_target,
        file_name = file_name_template,
        game_versions = game_versions,
        loaders = ["datapack"],
        project_id = project_id,
        token_secret_id = "modrinth_token",
        version_id = pack_version,
        version_name = version_name_template,
        version_type = version_type,
        deps = deps,
    )

def complete_datapack_config(
    pack_id,
    pack_version,
    target_name = None,
    game_versions = MINECRAFT_VERSIONS_1_20_PLUS,
    modrinth_project_id = None,
    changelog = None,
    version_type = "release",
    include_localization_dependency = True,
    **kwargs):
    """完整的数据包配置宏，包含所有常用设置。
    
    这个宏会生成完整的数据包配置，包括：
    - 数据包规则
    - 服务器别名
    - Modrinth 上传配置（可选）
    - 本地化依赖（可选）
    
    Args:
        pack_id: 命名空间 ID
        pack_version: 数据包版本
        target_name: 主要目标名称，默认为当前包名称
        game_versions: 支持的游戏版本列表
        modrinth_project_id: Modrinth 项目 ID
        changelog: 更新日志
        version_type: 版本类型 (release, beta, alpha)
        include_localization_dependency: 是否包含本地化依赖
        **kwargs: 传递给 datapack 规则的其他参数
    """
    # 确定目标名称，默认使用当前包名称
    if target_name == None:
        target_name = native.package_name().split("/")[-1]
    
    # 获取函数文件配置
    func_config = datapack_functions(pack_id)
    
    # 获取标准文件配置
    std_files = datapack_standard_files(pack_id)
    
    # 创建本地化依赖（如果需要）
    if include_localization_dependency:
        loc_dep = standard_localization_dependency()
        modrinth_dependency(**loc_dep)
    
    # 创建数据包
    datapack(
        name = target_name,
        pack_id = pack_id,
        functions = native.glob(
            include = func_config["functions_include"],
            exclude = func_config["functions_exclude"],
        ),
        functions_expand = native.glob(func_config["functions_expand_pattern"]),
        function_tags = native.glob(std_files["function_tags_pattern"]),
        dialogs = native.glob(std_files["dialogs_pattern"], allow_empty = True),
        minecraft_dialog_tags = native.glob(std_files["minecraft_dialog_tags_pattern"], allow_empty = True),
        **kwargs
    )
    
    # 创建服务器别名
    native.alias(
        name = "server",
        actual = ":%s_server" % target_name,
    )
    
    # 创建 Modrinth 上传配置（如果提供了项目 ID）
    if modrinth_project_id:
        datapack_modrinth_upload(
            name = target_name,
            datapack_target = ":" + target_name,
            pack_version = pack_version,
            project_id = modrinth_project_id,
            game_versions = game_versions,
            version_type = version_type,
            changelog = changelog,
        )
