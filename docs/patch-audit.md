# 原 hook-base.sh 补丁审计

审计日期：2026-09-06。目标 mt76 提交：`be5ce7910521492d4a2e4ce7ee3843680a46c047`。

对原 12 个补丁执行 `git apply --check` 和 `git apply --reverse --check`；对无法反向应用的补丁另行阅读当前源码，不能仅凭补丁冲突判定其已合入。

| 原补丁 | 处理 | 核对结果 |
|---|---|---|
| 003 LED ccflags | 不再外置 | 反向应用检查通过 |
| 100 unaligned 头文件 | 保留 | 正向应用检查通过 |
| 102 hrtimer_setup | 不再外置 | 反向应用检查通过 |
| 201 change_vif_links | 不再外置 | 反向应用检查通过 |
| 202 BSS 320 MHz | 不再外置 | 反向应用检查通过 |
| 203 RXV/TXS 320 MHz | 不再外置 | 反向应用检查通过 |
| 204 EHT MCS 320 MHz | 不再外置 | 反向应用检查通过 |
| 205 6 GHz EHT 能力 | 使用新版实现 | `mt7925/main.c` 已按 `is_320mhz_supported()` 设置 320 MHz 能力和 MCS；beamformee 的计算已更新 |
| 206 MT7927 芯片判断 | 使用新版实现 | `mt76_connac.h` 已有独立 `is_mt7927()`、320 MHz 判断和 TXP 分支；新版 `is_mt7925()` 仅匹配 7925，不恢复旧补丁将两种芯片混为一类的判断 |
| 207 固件路径 | 使用新版实现 | `mt792x.h` 已定义两条 MT7927 固件路径，PCI 源码已有 MODULE_FIRMWARE 声明；包层仍需补充实际固件 |
| 208 中断映射 | 使用新版实现 | PCI 驱动已有 MT7927 IRQ/DMA 布局，恢复和重置路径使用重构后的 `irq_map->rx.all_complete_mask` |
| 209 ASPM/runtime PM | 使用新版实现 | PCI probe 按 MT7927 硬件禁用 ASPM，初始化不为 MT7927 启用 runtime PM/deep sleep |

另保留 ImmortalWrt 的 MT7996 EEPROM 默认功率补丁，编号改为 110，避免与保留的 100 混淆。

原日志中的 mac80211 接口错误也已由新版源码解决：`mt7925/mac.c` 使用 `IEEE80211_MIN_ACTION_SIZE(action_code)`，公共 Connac 代码使用 `IEEE80211_MIN_ACTION_SIZE(addba_req.capab)`；action_code 与 capab 使用新结构路径，MCU 代码使用新的 EML 宏名称。

这些结果证明补丁整理与当前源码一致，不代表已经通过交叉编译或无线硬件测试。320 MHz 能力仍由芯片、频段和固件决定；旧 205 补丁本身也仅对 MT7927 开启该能力。

## 2026-10-16 更新复核

当前目标更新为 `467ae2e3f190baf737e15e318906da0dc7d0ab91`（2026-10-08），与 OpenWrt、ImmortalWrt master 的 mt76 版本一致。上面的逐项表格保留为首次审计记录。

- 两个外置补丁已在新提交的完整源码副本中依次通过检查和应用，无须修改补丁内容。
- ImmortalWrt 的 MT7996 补丁内容及 SHA-256 未变化。
- MT7927 两个固件的 SHA-256 与驱动路径验证通过，继续使用原固定版本。
- 新源码仍包含 MT7927 芯片识别、320 MHz 能力、中断映射以及省电规避逻辑；保留新版实现。
- OpenWrt 与 ImmortalWrt 当前的 mac80211/backports 均为 7.2。
- `PKG_MIRROR_HASH` 采用上游包定义的值；下载的 GitHub 源码归档仅用于源码与补丁验证，不作为 OpenWrt 镜像归档哈希的替代。

本次未执行完整交叉编译或硬件测试。
