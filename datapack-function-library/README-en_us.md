# Preface

*This datapack complies with the open-source license [GNU LESSER GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/lgpl-3.0.txt "Link to license page").*

**This datapack provides developers with practical functions compatible with all Minecraft versions (except those unable to install datapacks).**

**However, since the datapack involves numerous commands, older versions may not support all functions. This document will not individually specify version compatibility for each function.**

**Install the resource pack to use localized content (v3.2+). Otherwise, the datapack language defaults to zh_cn.**

**The mod version of this datapack is distributed via Modrinth and is functionally identical to the datapack version but may not be the latest release. Use the datapack version whenever possible.**

**This datapack includes a `dfl:dfl_enable` function that sets all entities' score in its objective to 1, facilitating detection by dependent datapacks or mods.**

**Example:**

```mcfunction
# Execute upon datapack load:
scoreboard objectives add dfl_enable dummy
scoreboard players set @e dfl_enable 0
# If not loaded:
function dfl:dfl_enable
execute unless score @n dfl_enable matches 1
# If loaded:
function dfl:dfl_enable
execute if score @n dfl_enable matches 1
```

**Note: Some functions specify "prerequisite functions" in their usage. These must be executed once before the main function.**

**Functions with `{xx:"xx"}` are [macro functions](https://zh.minecraft.wiki/w/Java%E7%89%88%E5%87%BD%E6%95%B0#%E5%AE%8F). Pass parameters via `{<param_name>:"<content>"}` (default parameters in usage are tested/recommended values). Parameter names (e.g., `num`) appear as `{num}` in descriptions. Format follows examples unless specified otherwise.**

Report issues [here](https://github.com/WhiteElephant-abc/datapack/issues/new/choose).

# Function Documentation

## Start

<span style="color:red;"><b>Execute functions in this category during datapack (re)load.</b></span>

### Disable Special Damage

Function: `/function dfl:start/nodamage`

- Fall damage
- Fire damage
- Freezing damage
- Drowning damage

### Set World Spawn to 0 0

Function: `/function dfl:start/setworldspawn`

- Sets world spawn to 0 0 0
- Sets spawn radius to 0
- Players respawn on the highest block at 0 0

### Enable Death Leaderboard

Function: `/function dfl:start/show/death`

- Creates `death` scoreboard
- Displays death counts on the right
- Ranks players by deaths (high to low)
- Note: Leaderboard appears only after a player dies

### Display Player Health

Function: `/function dfl:start/show/health`

- Creates `health` scoreboard
- Shows health below player names
- Hides at long distances (only IDs visible)
- Note: Initial display shows 0 HP; updates after damage/healing

### Display Player Levels

Function: `/function dfl:start/show/level`

- Creates `level` scoreboard
- Shows XP levels in Tab list
- Note: Initial display shows level 0; updates after XP gain

### Display Health Bars in Tab List

Function: `/function dfl:start/show/health_list`

- Creates `health` scoreboard
- Shows health bars in Tab list
- Effect:

![[DFL] Datapack Function Library (datapack function library)-Image 1](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/Scoreboard_Display_List_Hearts.gif?raw=true)

### Quick Team Setup

Function: `/function dfl:start/addteam {team_blue:"blue",team_red:"red",prefix_blue:"blue",prefix_red:"red"}`

- Creates teams `{team_blue}` (blue) and `{team_red}` (red)
- Disables friendly fire
- Players collide only with opposing teams
- Name prefixes: `{prefix_blue}_` and `{prefix_red}_`

## Tick

<span style="color:red;"><b>Execute functions in this category every tick.</b></span>

### Soft Ban Player

Function: `/function dfl:tick/ban`

- Note: Executor must be the **banned** player (use `/execute`)
- Teleports player to 0 0 0, sets adventure mode, applies debuffs
- Must run every tick
- Example: `/execute as @a[tag=ban] run function dfl:tick/ban`

Effect:

![[DFL] Datapack Function Library (datapack function library)-Image 2](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/tick.ban.png?raw=true)

### Beacon Elytra Launch

Function: `/function dfl:tick/beacon_fly`

- Launches players upward when beacon has iron/gold/emerald/diamond/netherite blocks below
- Heights: 20/40/60/80/100 blocks (blocks stack, max 400 blocks)
- Non-spectators only

### Apply Debuffs

Function: `/function dfl:tick/debuff`

Grants executor:

1. Slowness
2. Mining Fatigue
3. Nausea
4. Darkness
5. Hunger
6. Weakness
7. Poison
8. Bad Luck
9. Trial Omen

### Iron Block Elevator

Function: `/function dfl:tick/iron_block_elevator`

- Teleports players upward between vertical iron blocks
- Max range: 6 blocks (5-block gap)
- Affects mobs/non-player entities (not spectators)

### Clear Excess Entities

Function: `/function dfl:tick/kill {num:"1000"}`

- Kills all non-player entities when count > `{num}`
- Exempts entities with `need` tag
- Creates `dfl_scoreboard` objective
- Chat notification:

![[DFL] Datapack Function Library (datapack function library)-Image 3](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/tick.kill.png?raw=true)

### Clear High-Density Entities

Function: `/function dfl:tick/kill_better {num:"50"}`

Prerequisite: `/function dfl:lib/entity_density`

- Kills entities with >`{num}` entities within 10 blocks
- Exempts players, villagers, and `need`-tagged entities
- No chat traces

### Quality-of-Life

Function: `/function dfl:tick/relax`

- Enables keepInventory
- Grants Night Vision
- Grants Glowing
- Removes Darkness effect

### Display Entity Count

Function: `/function dfl:tick/show_entity`

Prerequisite: `/function dfl:lib/entity`

- Shows real-time entity count in action bar

Effect:

![[DFL] Datapack Function Library (datapack function library)-Image 4](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/tick.show_entity.png?raw=true)

### Disable Friendly Fire & Collisions

Function: `/function dfl:tick/team`

- Creates team `dfl`, adds all players
- Disables friendly fire and collisions
- Note: Conflicts with custom teams. Re-execute for new players if not run every tick.

### Clear High-Density TNT

Function: `/function dfl:tick/kill_tnt {num:"200"}`

- Clears TNT with >`{num}` TNT entities within 5 blocks
- Creates `dfl_tntdensity` objective

### Permissionless Suicide

Function: `/function dfl:tick/suicide`

- Creates `kill` objective
- Execute `/trigger kill` to suicide (no permissions required)

### Large-Scale Block Replacement

Function: `/function dfl:tick/change_block {new:"glass",old:"stone",num:"30"}`

- Replaces `{old}` with `{new}` in a {num}×{num}×8 area around player
- Sets `commandModificationBlockLimit` to 2147483647

### Permanent Day/Sun

Function: `/function dfl:tick/always_sunny`

- Disables day/night cycle
- Disables weather cycle
- Sets time to day
- Sets weather to clear

### Clear Item & Run Command

Function: `/function dfl:tick/clear_run_a {name:"stone",run:"tp ~ 100 ~"}`

- Clears one `{name}` per player and executes `{run}`
- Note: `{run}` must not have leading/trailing spaces or `/`

### Clear Items & Run Commands

Function: `/function dfl:tick/clear_run_b {name:"sand",run:"give @s anvil"}`

- Clears all `{name}` from executor and runs `{run}` once per item **in one tick**
- Note: `{run}` must not have leading/trailing spaces or `/`

### Maintain Item Quantity

Function: `/function dfl:tick/keep_have_things {name:"slime_block",num:"64"}`

- Ensures executor has exactly `{num}` of `{name}`

### Self-Rescue Platform

Function: `/function dfl:tick/slime`

Prerequisite: `/function dfl:lib/gametime`

- Creates `dfl_slime_marker_temp` to store spawn time
- Spawns 3×3 slime platform under players with `dfl_slime` tag (replaces air only)
- Removes slime blocks after `<slime_time>` ticks (default 200 ticks/10s)
- Clears slime block drops within 2 blocks of platform

### Item-to-XP Conversion

Function: `/function dfl:tick/things_to_xp {name:"tnt",xp:"1"}`

- Converts each `{name}` in executor's inventory to `{xp}` XP

### TPA System

Function: `/function dfl:tick/tpa`

Prerequisite: `/function dfl:lib/player_id`

- Creates `tpa` and `tpa_enable` objectives
- `/trigger tpa set <player's dfl_playerid>`: Teleport to player
- `/trigger tpa_enable`: Allow others to teleport to you (irreversible)
- Queues teleport if target is unavailable

### Auto-Smelting

Function: `/function auto_smelt:smelt {input:"raw_iron",output:"iron_ingot"}`

- Consumes `{input}`, grants `{output}`
- Costs 1 XP per item smelted
- Supports multiple fuels simultaneously
- Coal blocks smelt 9 items (costs 9 XP)

## Redstone

<span style="color:red;"><b>Execute functions in this category periodically (use [/schedule](https://zh.minecraft.wiki/w/%E5%91%BD%E4%BB%A4/schedule)).</b></span>

### Clear Dropped Items

Function: `/function dfl:redstone/kill_item`

- Creates `dfl_scoreboard`
- Clears all items (exempts `need`-tagged)
- Outputs cleared count via `/tellraw`

Effect:

![[DFL] Datapack Function Library (datapack function library)-Image 5](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/redstone.kill_item.png?raw=true)

### Display Entity Stats

Function: `/function dfl:redstone/show_entity`

Prerequisites:

`/function dfl:lib/entity`

`/function dfl:lib/item`

`/function dfl:lib/other_entity`

Effect:

![[DFL] Datapack Function Library (datapack function library)-Image 6](https://raw.githubusercontent.com/WhiteElephant-abc/datapack/refs/heads/main/datapack-function-library/README/redstone.show_entity.png?raw=true)

## Lib

<span style="color:red;"><b>Functions here have no standalone effects or don't fit other categories.</b></span>

### Force Death Drop

Function: `/function dfl:lib/clear`

1. Disables keepInventory
2. Kills executor
3. Enables keepInventory

### Get Entity Count

Function: `/function dfl:lib/entity`

- Creates `dfl_scoreboard`
- Writes entity count to `entity` score

### Get Entity Density

Function: `/function dfl:lib/entity_density`

- Creates `dfl_density`
- Writes nearby (10-block) entity count to entity's score

### Get Item Count

Function: `/function dfl:lib/item`

- Creates `dfl_scoreboard`
- Writes item count to `item` score

### Get Non-Player Entity Count

Function: `/function dfl:lib/other_entity`

- Creates `dfl_scoreboard`
- Writes non-player entity count to `other_entity` score

### Get Game Day

Function: `/function dfl:lib/day`

- Creates `dfl_scoreboard`
- Writes game day to `day` score
- Formula: `time / 24000` (integer division)

### Get Day Time

Function: `/function dfl:lib/daytime`

- Creates `dfl_scoreboard`
- Writes daytime to `daytime` score
- Formula: `time % 24000`

### Glass Cage Around Player

Function: `/function dfl:lib/fill_outline`

- Spawns 5×5 hollow glass cube at executor

### Get Game Time

Function: `/function dfl:lib/gametime`

- Creates `dfl_scoreboard`
- Writes game ticks to `gametime` score
- Also writes to players' `dfl_gametime`

### Get Player Count

Function: `/function dfl:lib/players`

- Creates `dfl_scoreboard`
- Writes player count to `players` score

### Modify Max Health

Function: `/function dfl:lib/change_max_health {num:"100"}`

- Sets all players' max health to `{num}`

### Generate UID

Function: `/function dfl:lib/player_id`

- Creates `dfl_playerid` and `dfl_scoreboard`
- Stores UID usage in `playerid_temp`
- Assigns unique immutable UIDs (dfl_playerid)
- UIDs: 1+ (earlier joiners = smaller numbers)

### Count Items

Function: `/function dfl:lib/things_count {name:"stone"}`

- Creates `dfl_{name}_num`
- Writes each player's `{name}` count to their score

### Mass-Spawn Dummies

Function: `/function dfl:lib/spawn`

- Spawns 100 Carpet mod dummies at player coordinates
