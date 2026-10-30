#!/usr/bin/env python3
"""把指定 smali 方法打成空炮（init 直接返回 false/void）。"""
import re, sys, pathlib

def patch(path, method_substr):
    p = pathlib.Path(path)
    lines = p.read_text(errors='surrogateescape').split('\n')
    out, i, patched = [], 0, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('.method') and method_substr in line and 'abstract' not in line and 'native' not in line:
            ret = line.rsplit(')', 1)[-1].strip()
            # 找 .locals
            j = i + 1
            locals_n = 0
            while j < len(lines) and not lines[j].strip().startswith('.locals'):
                j += 1
            if j < len(lines):
                try:
                    locals_n = int(lines[j].strip().split()[1])
                except Exception:
                    locals_n = 0
            if locals_n == 0:
                lines[j] = lines[j].replace('.locals 0', '.locals 1')
                locals_n = 1
            reg = locals_n - 1
            # 找第一条真实指令
            k = j + 1
            while k < len(lines):
                s = lines[k].strip()
                if s and not s.startswith('.') and not s.startswith(':'):
                    break
                k += 1
            ins = ['    return-void'] if ret == 'V' else [f'    const/4 v{reg}, 0x0', f'    return v{reg}']
            lines[k:k] = ins
            patched += 1
            print(f'  patched {method_substr} -> {ret} (locals={locals_n})')
        out.append(line)
        i += 1
    p.write_text('\n'.join(lines), errors='surrogateescape')
    return patched

if __name__ == '__main__':
    base = pathlib.Path(sys.argv[1])
    targets = [
        ('smali_classes4/com/kwad/sdk/api/KsAdSDK.smali', ' init('),
        ('smali_classes3/com/bytedance/sdk/openadsdk/TTAdSdk.smali', ' init('),
    ]
    total = 0
    for rel, sig in targets:
        f = base / rel
        if f.exists():
            print(f)
            total += patch(f, sig)
        else:
            print('missing:', f)
    print('total patched:', total)
