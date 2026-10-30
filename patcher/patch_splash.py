#!/usr/bin/env python3
"""开屏页短路：让 SplashActivity 跳过广告加载，直接进主界面。

原理：SplashActivity.e1() 里判断「是否加载开屏广告」，条件成立才 new 广告管理器。
把条件跳转改成无条件跳转（goto），即永远走「无广告」分支。

用法: python3 patch_splash.py <apktool_out_dir>
"""
import re
import sys
import pathlib

TARGET = 'smali_classes5/com/zdtc/ue/school/ui/activity/SplashActivity.smali'


def main():
    base = pathlib.Path(sys.argv[1])
    f = base / TARGET
    if not f.exists():
        print('未找到 SplashActivity.smali，检查解包路径:', f)
        return 1

    lines = f.read_text(errors='surrogateescape').split('\n')
    # 定位 e1() 方法
    start = None
    for i, l in enumerate(lines):
        if l.startswith('.method') and ' e1(' in l:
            start = i
            break
    if start is None:
        print('未找到 e1() 方法')
        return 1

    end = start
    while end < len(lines) and not lines[end].startswith('.end method'):
        end += 1

    # 在方法体里找 if-eqz 且目标标签在附近
    changed = 0
    for i in range(start, end):
        m = re.match(r'^(\s*)if-(eqz|nez)\s+(\w+),\s*(:\w+)\s*$', lines[i])
        if m:
            indent, kind, reg, label = m.groups()
            lines[i] = f'{indent}goto {label}'
            changed += 1
            print(f'  行 {i+1}: if-{kind} {reg}, {label}  ->  goto {label}')
            break

    if changed == 0:
        print('未找到可短路的条件跳转，需人工核对')
        return 1

    f.write_text('\n'.join(lines), errors='surrogateescape')
    print('开屏已短路')
    return 0


if __name__ == '__main__':
    sys.exit(main())
