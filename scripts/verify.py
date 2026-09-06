#!/usr/bin/env python3
"""Verify imported assets and apply the package patch series to a temporary copy."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True,
                        help='pristine mt76 source from the commit pinned in Makefile')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = args.source.resolve()
    if not (source / 'mt792x.h').is_file():
        parser.error('--source must point to an extracted mt76 source tree')
    manifest = json.loads((root / 'docs/sources.json').read_text(encoding='utf-8'))
    for entry in manifest['imports']:
        if entry['path'] == 'Makefile':  # Deliberately extended during packaging.
            continue
        asset = root / entry['path']
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise SystemExit(f"SHA-256 mismatch: {entry['path']}")
        print(f"SHA-256 OK: {entry['path']}")
    with tempfile.TemporaryDirectory(prefix='mt76-verify-') as temp:
        work = Path(temp) / 'source'
        shutil.copytree(source, work, ignore=shutil.ignore_patterns('.git'))
        for patch in sorted((root / 'patches').glob('*.patch')):
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=work, check=True)
            subprocess.run(['git', 'apply', str(patch)], cwd=work, check=True)
            print(f'PATCH OK: {patch.name}')
        shutil.copytree(root / 'src', work, dirs_exist_ok=True)
        header = (work / 'mt792x.h').read_text(encoding='utf-8')
        for firmware in (root / 'src/firmware/mt7927').glob('*.bin'):
            path = f'mediatek/mt7927/{firmware.name}'
            if f'"{path}"' not in header:
                raise SystemExit(f'Driver firmware path mismatch: {path}')
            print(f'FIRMWARE PATH OK: {path}')
    print('Verification passed. Full OpenWrt compilation and hardware testing remain required.')


if __name__ == '__main__':
    main()
