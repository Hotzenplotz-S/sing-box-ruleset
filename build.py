# -*- coding: utf-8 -*-
"""把同目录下的 *.json 规则集编译成 *.srs。

需要 sing-box 官方 CLI（带 rule-set 子命令的版本，如 1.14+）。

用法:
    python build.py                      # 自动查找 sing-box
    python build.py "D:\\path\\sing-box.exe"   # 显式指定 CLI
或设置环境变量 SINGBOX 指向 CLI。
"""
import glob, os, shutil, subprocess, sys

EXCLUDE = {"package.json"}


def find_cli():
    if len(sys.argv) > 1:
        return sys.argv[1]
    env = os.environ.get("SINGBOX")
    if env:
        return env
    return shutil.which("sing-box") or "sing-box"


def main():
    sb = find_cli()
    sources = [f for f in sorted(glob.glob("*.json")) if os.path.basename(f) not in EXCLUDE]
    if not sources:
        print("未找到任何 *.json 规则集")
        return 1
    failed = 0
    for src in sources:
        dst = src[:-5] + ".srs"
        r = subprocess.run([sb, "rule-set", "compile", "--output", dst, src],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[失败] {src}\n{(r.stdout + r.stderr).strip()}")
            failed += 1
            continue
        print(f"[完成] {src} -> {dst}  ({os.path.getsize(dst)} bytes)")
    print(f"\n共 {len(sources)} 个，失败 {failed} 个")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
