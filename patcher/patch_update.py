#!/usr/bin/env python3
"""关闭「发现新版本」升级弹窗。

原理：App 自己的 UpdateDialog 被 R8 混淆进了 bytedance 命名空间，入口是一个静态方法
      update(Context, VersionBean, Z)V。把它打成空方法即可，不影响任何业务逻辑。

注意：只关 update() 会让 TTAdSdk.start() 在 init 返回 false 后抛
      "TTAdConfig is null"，必须同时把 TTAdSdk.start() 置空（见 patch_sdk_init.py）。

用法: python3 patch_update.py <apktool_out_dir>
"""
import pathlib
import sys

SIG = '.method public static update(Landroid/content/Context;Lcom/zdtc/ue/school/model/net/VersionBean;Z)V'


def patch_file(p):
    lines = p.read_text(errors='surrogateescape').split('\n')
    out, i, done = [], 0, False
    while i < len(lines):
        line = lines[i]
        if not done and line.startswith(SIG):
            out.append(line)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('.locals'):
                out.append(lines[i])
                i += 1
            out.append(lines[i])
            i += 1
            out.append('    return-void')
            done = True
            continue
        out.append(line)
        i += 1
    if done:
        p.write_text('\n'.join(out), errors='surrogateescape')
    return done


def main():
    base = pathlib.Path(sys.argv[1])
    hits = 0
    for f in base.glob('smali*/com/**/*.smali'):
        try:
            if SIG in f.read_text(errors='surrogateescape'):
                if patch_file(f):
                    print('  已置空:', f.relative_to(base))
                    hits += 1
        except Exception:
            continue
    print('共处理', hits, '处')
    return 0 if hits else 1


if __name__ == '__main__':
    sys.exit(main())
