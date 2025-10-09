**本数据包会在玩家脚底下不断生成 TNT**

如果遇到任何问题，请点击 [这里](https://github.com/WhiteElephant-abc/SetBlock-TNT/issues/new/choose) 反馈

如果无法访问，可点击 [这里](https://steampp.net/) 下载加速器

## 简介

- 本数据包需要前置：[数据包函数支持库](https://www.mcmod.cn/class/17244.html "数据包函数支持库")，前置未安装或未加载时数据包会提示安装（不安装会导致数据包所有功能无法使用）
- 数据包第一次加载后需要玩家的血量更新一次（如受伤）方可正常生成 TNT

## 功能

### 基本

- 在所有生存、冒险模式玩家血量大于等于 5 点（![Heart_2](https://zh.minecraft.wiki/images/Heart_%28icon%29.png)![Heart_2](https://zh.minecraft.wiki/images/Heart_%28icon%29.png)![Heart_1](https://zh.minecraft.wiki/images/Half_Heart_%28icon%29.png)）时在其脚下放置 TNT
- 在所有生存、冒险模式玩家血量小于等于 4 点（![Heart_2](https://zh.minecraft.wiki/images/Heart_%28icon%29.png)![Heart_2](https://zh.minecraft.wiki/images/Heart_%28icon%29.png)），大于等于 1 点（![Heart_1](https://zh.minecraft.wiki/images/Half_Heart_%28icon%29.png)）时在其脚下放置红石块，在红石块下方放置 TNT（我们称之为补刀）
- 将玩家背包中的每个 TNT 转化为 1 点经验
- 为所有玩家提供无限夜视、发光，移除黑暗效果，并开启死亡不掉落
- 在屏幕右侧显示死亡榜，在玩家列表栏显示血条

### 优化

- 清除玩家附近的火
- 清除距离玩家 20 格外的 TNT 实体
- 在玩家动作栏（快捷栏上方）显示实时实体数量  
- 在 TNT 附近五格内的 TNT 实体数大于 200 时清除这些 TNT 实体
