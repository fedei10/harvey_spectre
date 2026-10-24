import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.config import BASE_DIR, Settings


class SettingsTests(unittest.TestCase):
    def test_loads_api_key_from_configured_env_file(self):
        self.assertEqual(Settings.model_config.get("env_file"), BASE_DIR / ".env")

        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                settings = Settings(_env_file=env_file)

        self.assertEqual(settings.OPENAI_API_KEY, "test-key")
