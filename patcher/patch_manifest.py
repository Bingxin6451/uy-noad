#!/usr/bin/env python3
"""从 AndroidManifest.xml 中移除广告 SDK 的初始化 Provider 与专属组件。

用法: python3 patch_manifest.py <apktool_out_dir>
"""
import re
import sys
import pathlib

# 广告 SDK 的包前缀
AD_PREFIXES = (
    'com.bytedance.sdk.openadsdk',
    'com.bytedance.sdk.djx',
    'com.bytedance.sdk.dp',
    'com.bytedance.pangle',
    'com.baidu.mobads',
    'com.kwad.',
    'com.beizi.',
    'com.qq.e.',
)

# 必须保留的（FileProvider 被业务下载/分享功能依赖）
KEEP = (
    'TTFileProvider',
    'BdFileProvider',
    'AdSdkFileProvider',
    'GDTFileProvider',
)


def is_ad(name, keep_file_providers=True):
    if not any(p in name for p in AD_PREFIXES):
        return False
    if keep_file_providers and any(k in name for k in KEEP):
        return False
    return True


def strip_providers(xml):
    """删除广告 provider 整段（含 meta-data 子节点）。"""
    pattern = re.compile(r'<provider\b[^>]*?android:name="([^"]+)"[^>]*?>.*?</provider>',
                         re.S)
    removed = []

    def repl(m):
        block, name = m.group(0), m.group(1)
        if is_ad(name):
            removed.append(name)
            return ''
        return block

    xml = pattern.sub(repl, xml)
    # 自闭合形式
    pattern2 = re.compile(r'<provider\b[^>]*?android:name="([^"]+)"[^>]*?/>')

    def repl2(m):
        block, name = m.group(0), m.group(1)
        if is_ad(name):
            removed.append(name)
            return ''
        return block

    xml = pattern2.sub(repl2, xml)
    return xml, removed


def main():
    base = pathlib.Path(sys.argv[1])
    mf = base / 'AndroidManifest.xml'
    xml = mf.read_text(errors='surrogateescape')
    xml, removed = strip_providers(xml)
    mf.write_text(xml, errors='surrogateescape')
    print(f'removed {len(removed)} providers:')
    for r in removed:
        print('  -', r)


if __name__ == '__main__':
    main()
