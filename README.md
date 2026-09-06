# package_kernel_mt76

独立的 ImmortalWrt mt76 包：新版驱动源码、仍需要的外置补丁，以及 MT7927 固件打包。

## 当前版本

- mt76：`2026-09-01`，提交 `be5ce7910521492d4a2e4ce7ee3843680a46c047`。
- 包定义基于 ImmortalWrt `7089af38d165a2105e0736fb7e8823bf17f12e82`。
- 保留 ImmortalWrt 的 MT7922 固件依赖、MediaTek 平台 WED 默认设置和平台限制。
- 新增 `kmod-mt7927-firmware`，驱动仍使用 `kmod-mt7925e`。
- 源码与固件固定版本；构建时不会从浮动 master 下载自定义补丁。

目标是与该 ImmortalWrt master 的 mac80211/backports 7.2 配套使用。Linux 内核版本相同并不代表无线接口兼容，不能直接保证适用于旧版 OpenWrt/mac80211。

## 补丁

`patches/` 下的补丁由 OpenWrt 构建系统按文件名顺序应用：

1. `100-fix-build-with-linux-6.12rc2.patch`：根据内核版本选择 unaligned 头文件，来自原 sbwml 补丁集。
2. `110-mt7996-use-default-tx-power-for-zero-eeprom.patch`：保留 ImmortalWrt 的 MT7996 EEPROM 零功率修复。

原来的 LED、hrtimer、320 MHz 和 MT7927 补丁大多已有上游实现，不重复应用。逐项说明见 [补丁审计](docs/patch-audit.md)。后续自定义补丁可从 `200-` 开始编号，每次更新源码都应重新检查。

## 接入构建

将本项目完整放在 OpenWrt 源码的 `package/kernel/mt76`，替换原来的同名包。只保留一份 mt76 包定义。

在 OpenWrt 源码根目录，或 `hook-base.sh` 的 `# mt76` 段中使用：

```sh
rm -rf package/kernel/mt76
git clone https://github.com/xuanranran/package_kernel_mt76.git package/kernel/mt76 || exit 1
```

旧的 mt76 下载和打补丁段必须整体替换，避免再次覆盖为旧版。仓库中的补丁与固件会随克隆获取。

在 OpenWrt 源码根目录运行：

```sh
make defconfig
make package/kernel/mt76/clean
make package/kernel/mt76/compile -j1 V=s
```

使用 MT7927 时，在 `.config` 选择：

```text
CONFIG_PACKAGE_kmod-mt7925e=y
CONFIG_PACKAGE_kmod-mt7927-firmware=y
```

只选择 `kmod-mt7925e` 不会自动带上可选的 MT7927 固件包。两个固件已放在 `src/firmware/mt7927/`；OpenWrt 的默认 Prepare 会将 `src/` 内容覆盖到驱动构建目录。

## 本地验证与更新

先准备与 Makefile 提交一致的、未应用补丁的 mt76 源码目录，然后运行：

```sh
python3 scripts/verify.py --source /path/to/pristine/mt76
```

脚本检查导入补丁和固件的 SHA-256，在临时副本中顺序应用补丁，并核对 MT7927 固件路径。不会修改传入的源码。`--source` 目录必须来自 Makefile 固定的提交；脚本不验证任意目录的完整源码身份。

更新时同步核对 mac80211 版本，更新 `PKG_SOURCE_DATE`、`PKG_SOURCE_VERSION`、`PKG_MIRROR_HASH`，重新审计补丁并递增 `PKG_RELEASE`。不要只把源码提交改成最新值后继续套用旧补丁。

验证范围：补丁应用与固件完整性；完整交叉编译和硬件运行仍需在 Linux 构建机验证。

## 来源

原始文件的固定提交 URL 和 SHA-256 记录在 [sources.json](docs/sources.json)。其中 Makefile 的哈希对应修改前的导入文件；本地增加了 MT7927 固件包并调整包修订号。驱动、补丁、固件保留各自上游的许可及作者归属。
