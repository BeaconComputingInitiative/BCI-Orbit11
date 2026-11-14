#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE | Developer Seal: CJB-DEV-2026
"""Run isolated component tests and static checks; never install or activate."""
import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    for path in ROOT.glob('components/**/*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in ROOT.glob('components/**/*.sh'):
        subprocess.run(['bash', '-n', str(path)], check=True)
    for name in ('host', 'neural', 'expansion', 'console'):
        component = ROOT / 'components' / name
        env = {**os.environ, 'PYTHONPATH': str(component/'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
        print(f'BCI-Orbit11: testing {name}', flush=True)
        subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                       cwd=component, env=env, check=True, timeout=180)
    subprocess.run([sys.executable, '-B', str(ROOT/'components/rate-aware/BCI-Orbital-Group15-v0.5.1.py'), '--self-test'],
                   check=True, timeout=60)
    print('PASS: component tests, Python parsing, and shell syntax. No installation or activation.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
