- 重构数据包，添加**全新**的设置界面（基于对话框）
- 添加**全新**的清除算法，在确保性能的同时保证效果
- 设置界面选项丰富，设备性能好的用户可以拥有更好的游戏体验
- 核心算法：
  - 每次执行时，以玩家为中心，螺旋遍历周围区块
  - 成功清除第一个区块后退出算法，或遍历到未加载区块，或遍历范围达到限制
  - 可自定义遍历范围，可自定义清除成功判定
  - 适配多人游戏，适配服务器

---

- Refactored the data pack and added a **brand new** settings interface (based on dialogs)
- Added a **brand new** clearing algorithm to ensure effectiveness while maintaining performance
- The settings interface has rich options, allowing users with high-performance devices to have a better gaming experience
- Core algorithm:
  - Each execution spirals through surrounding chunks centered on the player
  - The algorithm exits after successfully clearing the first chunk, or when it reaches an unloaded chunk, or the traversal range limit is reached
  - Customizable traversal range and success criteria for clearing
  - Compatible with multiplayer and servers
