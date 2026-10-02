"""
Smoke tests for CrisisGuard workspace layout and integrity.
Ensures zero third-party dependencies are required to verify structure.
"""

import unittest
from pathlib import Path

class TestWorkspaceLayout(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent

    def test_required_directories(self):
        dirs = [
            "data/raw", "data/interim", "data/processed", "data/features",
            "models", "results", "logs", "docs/datasets", "config",
            "tests/smoke", "scripts/validation", "src"
        ]
        for d in dirs:
            target = self.root / d
            self.assertTrue(target.is_dir(), f"Missing directory: {d}")

    def test_required_root_files(self):
        files = [
            "PROJECT_STATUS.md", "README.md", "config/paths.yaml",
            ".gitignore", ".env.example",
            "docs/datasets/DATASET_MANIFEST_TEMPLATE.yaml"
        ]
        for f in files:
            target = self.root / f
            self.assertTrue(target.is_file(), f"Missing file: {f}")

    def test_raw_directory_isolated(self):
        raw_dir = self.root / "data" / "raw"
        raw_files = list(raw_dir.glob("*"))
        # Phase 0 constraint: raw directory must not contain raw datasets
        for f in raw_files:
            self.assertFalse(f.name.endswith(('.csv', '.parquet', '.mp4', '.json')),
                            f"Illegal file in data/raw during Phase 0: {f.name}")

if __name__ == "__main__":
    unittest.main()
