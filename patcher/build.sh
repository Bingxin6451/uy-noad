#!/bin/bash
# 一键去广告：解包 → 打补丁 → 重建 → 对齐 → 签名
# 用法: ./patcher/build.sh <原始.apk> [工作目录]
set -e
cd "$(dirname "$0")/.."

APK=${1:?用法: build.sh <原始.apk> [工作目录]}
WORK=${2:-work}
APKTOOL_JAR=${APKTOOL_JAR:-/tmp/apktool.jar}
BT=${BUILD_TOOLS:-/tmp/btools/android-14}
KS=${KEYSTORE:-./ueasy.jks}
KS_PASS=${KS_PASS:-ueasypass}
OUT=noad-unsigned.apk
FINAL=noad-signed.apk

echo "==> 解包"
java -jar "$APKTOOL_JAR" d -f "$APK" -o "$WORK" > /dev/null

echo "==> 移除广告 Provider"
python3 patcher/patch_manifest.py "$WORK"

echo "==> 开屏短路"
python3 patcher/patch_splash.py "$WORK"

echo "==> 关闭升级弹窗"
python3 patcher/patch_update.py "$WORK"

echo "==> SDK init 空炮"
python3 patcher/patch_sdk_init.py "$WORK"

echo "==> 重建"
java -jar "$APKTOOL_JAR" b "$WORK" -o "$OUT" > /dev/null

echo "==> 对齐 + 签名"
"$BT/zipalign" -p -f 4 "$OUT" aligned.apk
if [ ! -f "$KS" ]; then
  keytool -genkeypair -keystore "$KS" -alias noad -keyalg RSA -keysize 2048 \
    -validity 3650 -storepass "$KS_PASS" -keypass "$KS_PASS" -dname "CN=UEasy-NoAd"
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$KS_PASS" --key-pass "pass:$KS_PASS" \
  --v1-signing-enabled true --v2-signing-enabled true --out "$FINAL" aligned.apk

"$BT/apksigner" verify --print-certs "$FINAL" | head -3
ls -lh "$FINAL"
echo "完成: $FINAL"
