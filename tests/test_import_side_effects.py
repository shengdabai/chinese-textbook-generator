"""Importing any script in this repository must not write anything.

Each module is imported in its own subprocess, with an empty temporary
working directory and HOME pointed at an empty temporary directory. After the
import the test checks that:

* the subprocess exited normally (no ``sys.exit`` or exception at import),
* nothing was printed to stdout,
* the working directory and HOME are still empty,
* no file or directory in the checkout was created, removed or modified,
* no write happened anywhere else either: an audit hook in the subprocess
  blocks and reports open() for writing, mkdir, rmdir, remove, rename, symlink,
  link and truncate outside the temporary cwd/HOME (and /dev/null), so writes
  to absolute or ``..``-relative paths fail the import even if the module
  catches the error.

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


import os

# Block every filesystem write outside the temp cwd and HOME (the snapshot check
# in the parent still requires those to stay empty). Reads are allowed.
SANDBOX = [os.path.realpath(os.getcwd()), os.path.realpath(os.environ['HOME'])]
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
# event -> indexes of the path arguments it writes to
PATH_EVENTS = {
    'os.mkdir': (0,), 'os.rmdir': (0,), 'os.remove': (0,), 'os.rename': (0, 1),
    'os.symlink': (1,), 'os.link': (1,), 'os.truncate': (0,),
}
BLOCKED = []
_in_hook = False


def _allowed(path):
    if isinstance(path, int):  # an already-open file descriptor
        return True
    full = os.path.realpath(os.fsdecode(path))
    return full == os.devnull or any(full == d or full.startswith(d + os.sep) for d in SANDBOX)


def _audit(event, args):
    global _in_hook
    if _in_hook:
        return
    if event == 'open':
        path, mode, flags = args
        writes = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool((flags or 0) & WRITE_FLAGS)
        paths = [path] if writes and path is not None else []
    else:
        paths = [args[i] for i in PATH_EVENTS.get(event, ())]
    _in_hook = True
    try:
        bad = [p for p in paths if not _allowed(p)]
    finally:
        _in_hook = False
    if bad:
        BLOCKED.extend((event, os.fsdecode(p)) for p in bad)
        raise PermissionError(f'blocked {event} outside the sandbox: {bad}')


sys.meta_path.insert(0, _StubFinder())
sys.path.insert(0, sys.argv[1])
sys.addaudithook(_audit)
try:
    importlib.import_module(sys.argv[2])
finally:
    # Also report writes the module caught and ignored.
    if BLOCKED:
        sys.stderr.write(''.join(f'blocked {event}: {path}\n' for event, path in BLOCKED))
        sys.exit(3)
'''


def import_in_child(root, name, cwd, home):
    """Import ``name`` from ``root`` in a fresh interpreter with the given cwd and HOME."""
    env = {
        'PATH': os.environ.get('PATH', ''),
        'HOME': str(home),
        'PYTHONDONTWRITEBYTECODE': '1',
        'PYTHONUTF8': '1',
    }
    return subprocess.run(
        [sys.executable, '-B', '-c', CHILD, str(root), name],
        cwd=cwd, env=env, capture_output=True, text=True, timeout=120,
    )


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
                before = snapshot(REPO)
                result = import_in_child(root, name, cwd, home)
                after = snapshot(REPO)

                self.assertEqual(result.returncode, 0, f'import failed:\n{result.stdout}\n{result.stderr}')
                self.assertEqual(result.stdout, '', 'import printed output (main logic ran?)')
                self.assertEqual(sorted(os.listdir(cwd)), [], 'import wrote into the working directory')
                self.assertEqual(sorted(os.listdir(home)), [], 'import wrote into HOME')
                changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
                self.assertEqual(changed, [], 'import changed files in the checkout')



class SandboxCatchesEscapingWritesTest(unittest.TestCase):
    """Mutation checks: a module that writes outside cwd/HOME/the repo must fail the import.

    The child runs in ``outer/a/b/cwd`` so a ``../..`` escape lands in ``outer/a``,
    which is still inside this test's temporary directory.
    """

    def import_module_source(self, source):
        outer = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        pkg = outer / 'src'
        cwd = outer / 'a' / 'b' / 'cwd'
        home = outer / 'home'
        for directory in (pkg, cwd, home):
            directory.mkdir(parents=True)
        (pkg / 'mutant.py').write_text(source, encoding='utf-8')
        return outer, import_in_child(pkg, 'mutant', cwd, home)

    def assert_blocked(self, result, leaked):
        self.assertNotEqual(result.returncode, 0, f'escaping write was not caught:\n{result.stderr}')
        self.assertIn('blocked', result.stderr)
        self.assertFalse(leaked.exists(), f'{leaked} was created')

    def test_relative_escape_mkdir_is_caught(self):
        outer, result = self.import_module_source('from pathlib import Path\nPath("../../LEAK").mkdir()\n')
        self.assert_blocked(result, outer / 'a' / 'LEAK')

    def test_absolute_path_write_is_caught(self):
        outer = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        target = outer / 'LEAK.txt'
        _, result = self.import_module_source(f'open({str(target)!r}, "w").write("x")\n')
        self.assert_blocked(result, target)

    def test_caught_even_if_the_module_swallows_the_error(self):
        outer, result = self.import_module_source(
            'import os\ntry:\n    os.makedirs("../../LEAK/x")\nexcept OSError:\n    pass\n'
        )
        self.assert_blocked(result, outer / 'a' / 'LEAK')

    def test_reads_and_dev_null_writes_are_allowed(self):
        _, result = self.import_module_source(
            'import os, sys\nopen(sys.executable, "rb").read(16)\n'
            'with open(os.devnull, "w") as f:\n    f.write("x")\n'
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
