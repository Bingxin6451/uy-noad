# 广告 SDK 清册

V2.9.3 静态确认，5 家。全部与业务代码同体打包，没有独立进程或插件化隔离（快手部分组件走动态插件）。

| SDK | 包名 | Manifest 证据 | 初始化机制 |
|---|---|---|---|
| 穿山甲 + GroMore 聚合 | `com.bytedance.sdk.openadsdk` / `msdk` / `nov` | `TTMultiProvider`、`TTFileProvider`、`MainProcessProviderProxy`、`LiveServerManager` | ContentProvider 自动初始化 |
| 百度联盟 | `com.baidu.mobads` | `AppActivity`、`MobRewardVideoActivity`、`BdShellActivity`、`BdFileProvider` | 首调初始化 |
| 快手联盟 | `com.kwad.sdk` | `AdSdkFileProvider`、`KsAdSDK` | 首调 + 动态插件加载 |
| BeiZi | `com.beizi.ad` | `AdActivity`、`BeiZiNewInterstitialActivity`、`BeiZiNewRewardVideoActivity` | 首调初始化 |
| 逗街 / 抖音推 | `com.bytedance.sdk.djx` / `dp` | `DJXProvider`、`DPProvider` | Provider 自动初始化 |

## 广告位与 App 侧调用点

| 文件 | 广告形式 |
|---|---|
| `ui/activity/SplashActivity` | 开屏 |
| `ui/adapter/BannerWithAdsAdapter` | 首页信息流 / 横幅 |
| `ui/activity/device/StopuseDeviceActivity` | 设备结束页 |
| `ui/activity/user/UserBillDetailActivity` | 账单明细 |
| `ui/activity/WebViewActivity` / `ui/fragment/WebViewFragment` | 内嵌网页广告 |
| `ui/activity/device/common/BaseUsingDeviceAct` | 快手激励视频入口 |

## 广告位 ID 的来源

服务端下发，`AppInitBean.sysAdSettingV2` 里共 19 个位置：

```
welcomePageId          开屏
homeShufflingId        首页轮播
homePlaqueId           首页贴片
billPageBannerId       账单页 banner
billPageNativeId       账单页原生
settlementPageBannerId 结算页 banner
settlementPageNativeId 结算页原生
settlementPagePlaqueId 结算页贴片
signPageId             签到页
webInterId             网页插屏
webBannerId            网页 banner
useDeviceBannerId      设备页 banner
useDeviceBigBannerId   设备页大图
informationStream      信息流
storyAdv_video         短剧
dramaAdv_informationStream 小说信息流
...
```

**这意味着**：单纯屏蔽本地广告位 ID 没用，云端会重新下发。必须让 SDK 本身起不来，广告位自然空容器——这也是本项目选择"断初始化"而不是"删广告位"的原因。

## 为什么不能直接删 SDK 类

- 业务代码里有 `catch` 不到的静态引用，删类 → `NoClassDefFoundError`
- 聚合 SDK 互相引用（GroMore ↔ 穿山甲 ↔ Pangle），删一个必炸另一个
- 部分 SDK 的 `FileProvider` 被子类化后用于业务下载

结论：**断初始化 > 删类**。体积优化留到功能验证稳定之后单独做。
