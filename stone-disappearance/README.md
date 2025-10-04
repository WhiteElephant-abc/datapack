# [SD]石头消失（Stone Disappearance）

## 简介

此数据包将世界中的石头替换为其他方块，最低兼容 Minecraft 1.20.3，但只有 Minecraft 1.21.6 及以上版本才能体验完整功能。

## 功能

默认情况下，数据包将世界中三个维度的四种石头替换为玻璃，每次替换以区块为单位，从玩家所在区块向远处遍历，直到成功清除一个区块，或者遍历完加载范围内所有区块。默认遍历距离为 1，即以玩家为中心的 9 个区块。

## 配置

此数据包拥有丰富的配置项，在游戏菜单中可以进入数据包的配置界面，但低于 1.21.6 的版本只能通过命令来配置。在此不作说明，如有需要可以修改 `new/reset_settings` 函数文件内的默认配置，并输入 `/function stone_disappearance:new/reset_settings` 初始化配置。

### 用于替换的方块

- `overworld_block`：用于替换主世界石头的方块
- `nether_block`：用于替换下界石头的方块
- `end_block`：用于替换末地石头的方块

### 世界高度限制

- `overworld_min`：主世界最低建筑高度
- `overworld_max`：主世界最高建筑高度
- `nether_min`：下界最低建筑高度
- `nether_max`：下界最高建筑高度
- `end_min`：末地最低建筑高度
- `end_max`：末地最高建筑高度

### 遍历参数

- `n`：遍历距离
- `tick`：每次清除后等待的 tick 数
- `success_num`：一次区块清除被视为成功需要替换的方块数量

### 优化设置

- `fill_falling_block`：是否替换沙子、红沙、沙砾
- `fill_falling_block_with`：用于替换三种沙子的方块
- `tick_fill`：是否实时清除玩家附近3*3*3区域内的石头
