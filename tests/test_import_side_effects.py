"""Importing any script in this repository must not write anything.

Each module is imported in its own subprocess, with an empty temporary
working directory and HOME pointed at an empty temporary directory. After the
import the test checks that:

* the subprocess exited normally (no ``sys.exit`` or exception at import),
* nothing was printed to stdout,
* the working directory and HOME are still empty,
* no file or directory in the checkout was created, removed or modified.

Optional heavy dependencies that CI does not install (weasyprint, fpdf2, the
Anthropic SDK, PDF readers, jieba) are replaced by empty stub modules only when
they are missing, so every script can still be imported.

Run: python -m unittest discover -s tests -p 'test_*.py' -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', '.venv', 'venv', '__pycache__', 'tests', 'node_modules'}

# Runs inside the subprocess: argv[1] is the sys.path root, argv[2] the module name.
CHILD = r'''
import importlib, importlib.abc, importlib.machinery, importlib.util, sys, types

OPTIONAL = {'anthropic', 'fpdf', 'weasyprint', 'PyPDF2', 'pdfplumber', 'jieba'}
MISSING = {name for name in OPTIONAL if importlib.util.find_spec(name) is None}


class _Stub(types.ModuleType):
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError(attr)
        value = type(attr, (), {'__init__': lambda self, *a, **k: None})
        setattr(self, attr, value)
        return value


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in MISSING:
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = _Stub(spec.name)
        module.__path__ = []
        return module

    def exec_module(self, module):
        pass


sys.meta_path.insert(0, _StubFinder())
sys.path.insert(0, sys.argv[1])
importlib.import_module(sys.argv[2])
'''


def discover_modules():
    """Yield (sys.path root, dotted module name, path) for every non-test .py file."""
    for path in sorted(REPO.rglob('*.py')):
        rel = path.relative_to(REPO)
        if SKIP_DIRS & set(rel.parts[:-1]) or path.name.startswith('test_'):
            continue
        root = path.parent
        parts = [] if path.stem == '__init__' else [path.stem]
        while (root / '__init__.py').exists():
            parts.insert(0, root.name)
            root = root.parent
        if parts:
            yield root, '.'.join(parts), rel


def snapshot(base):
    """Map every path under base (except VCS/venv/bytecode dirs) to (size, mtime)."""
    state = {}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}]
        for name in dirnames + filenames:
            full = Path(dirpath, name)
            stat = full.lstat()
            state[str(full.relative_to(base))] = (stat.st_size, stat.st_mtime_ns) if name in filenames else 'dir'
    return state


class ImportHasNoSideEffectsTest(unittest.TestCase):
    def test_discovery_finds_the_scripts(self):
        names = {name for _, name, _ in discover_modules()}
        for expected in ('merge_hsk_levels', 'generate_hsk_content', 'enrich_hsk_content', 'generate_hsk_pdf', 'generate'):
            self.assertIn(expected, names)

    def test_import_writes_nothing(self):
        for root, name, rel in discover_modules():
            with (
                self.subTest(module=str(rel)),
                tempfile.TemporaryDirectory() as cwd,
                tempfile.TemporaryDirectory() as home,
            ):
                env = {
                    'PATH': os.environ.get('PATH', ''),
                    'HOME': home,
                    'PYTHONDONTWRITEBYTECODE': '1',
                    'PYTHONUTF8': '1',
                }
                before = snapshot(REPO)
                result = subprocess.run(
                    [sys.executable, '-B', '-c', CHILD, str(root), name],
                    cwd=cwd, env=env, capture_output=True, text=True, timeout=120,
                )
                after = snapshot(REPO)

                self.assertEqual(result.returncode, 0, f'import failed:\n{result.stdout}\n{result.stderr}')
                self.assertEqual(result.stdout, '', 'import printed output (main logic ran?)')
                self.assertEqual(sorted(os.listdir(cwd)), [], 'import wrote into the working directory')
                self.assertEqual(sorted(os.listdir(home)), [], 'import wrote into HOME')
                changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
                self.assertEqual(changed, [], 'import changed files in the checkout')


if __name__ == '__main__':
    unittest.main()
