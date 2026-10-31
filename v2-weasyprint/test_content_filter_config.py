"""load_config() must say so when it falls back to the defaults because the file is missing.

Run: python -m unittest discover -s v2-weasyprint -p 'test_*.py' -v
"""
import tempfile
import unittest
import warnings
from pathlib import Path

import content_filter


class LoadConfigTest(unittest.TestCase):
    def test_missing_config_warns_and_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / 'content_filter_config.yaml'
            with self.assertWarnsRegex(UserWarning, 'not found') as caught:
                config = content_filter.load_config(missing)
        self.assertIn(str(missing), str(caught.warning))
        self.assertEqual(config, content_filter.DEFAULT_CONFIG)

    def test_bundled_config_loads_without_warning(self):
        bundled = Path(content_filter.__file__).with_name('content_filter_config.yaml')
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            config = content_filter.load_config(bundled)
        self.assertIsInstance(config, dict)


if __name__ == '__main__':
    unittest.main()
