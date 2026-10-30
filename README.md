# U易 去广告

把校园生活 App「U易」里的广告全部拆掉，保留扫码、下单、设备控制等全部正常功能。

> 只做去广告。不含任何设备协议、账号或计费相关内容。

## 效果

| | 原版 | 去广告版 |
|---|---|---|
| 包体积 | 91.4 MB | 89 MB |
| 广告 SDK | 穿山甲/GroMore、百度、快手、BeiZi、逗街 | 初始化已断，广告位加载失败 |
| 开屏广告 | 3–5 秒倒计时 | 直接进主界面 |
| 启动广告 SDK 日志 | 大量 | 已大幅减少（快手插件加载器仍在，见 TODO） |

## 装之前

自签名与原版不同，**必须先卸载原版**，本地登录态会丢（账号还在服务器，重新收验证码登录即可）。原包请自行备份，方便回滚。

## 使用现成包

到 [Releases](../../releases) 下载 `noad-signed.apk`，卸载原版后安装。

## 自己构建

依赖：

- JDK 17+
- `apktool.jar`（2.9+）
- Android build-tools（`zipalign` + `apksigner`）

```bash
export APKTOOL_JAR=/path/to/apktool.jar
export BUILD_TOOLS=/path/to/build-tools/34.0.0
./patcher/build.sh /path/to/UYXY.apk
# 产出 noad-signed.apk
```

首次运行会自动生成签名密钥 `ueasy.jks`（口令 `ueasypass`，可改环境变量）。

## 补丁做了什么

三处，全部在 `patcher/` 里可复现：

1. **断根**：删掉广告 SDK 的初始化 Provider（穿山甲 `TTMultiProvider`、`DJXProvider`、`DPProvider`、Pangle 主进程代理等）。Provider 是进程启动即执行的，删掉等于把广告 SDK 的自动点火拆了。
2. **短路开屏**：`SplashActivity.e1()` 里判断"要不要加载开屏广告"的条件跳转改成无条件跳转，永远走无广告分支。
3. **空炮 init**：`KsAdSDK.init()`、`TTAdSdk.init()` 直接 `return false`，让后续任何一次调用都初始化失败。

细节见 [docs/01-广告SDK清册.md](docs/01-广告SDK清册.md) 和 [docs/02-补丁说明.md](docs/02-补丁说明.md)。

## 已知问题

- 快手的动态插件加载器（`PluginUpdaterImpl`）仍会在启动时下载 `tachikoma` 等插件 dex，说明还有一条引导链没断。功能上广告位已加载失败，但会浪费流量，待继续处理。
- 版本号显示为 2.9.2（apktool 从原始清单读取），实际内容对应 2.9.3。
- 未登录状态下无法验证首页/账单页广告位，需要真实账号回归。

## 免责

仅供学习与技术研究。请自行承担使用后果，遵守学校与运营方规定。本项目不分发任何账号、不代理任何服务。
