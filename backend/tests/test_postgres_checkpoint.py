import unittest
from unittest.mock import patch

from pydantic import SecretStr

from app.ai_engineering.agent.checkpoint import get_checkpoint_dsn
from app.config import settings


class CheckpointDsnTests(unittest.TestCase):
    def test_cloud_postgres_url_is_accepted(self):
        with patch.object(settings, "LANGGRAPH_DATABASE_URL", SecretStr(
            "postgresql://agent:p%40ss@db.example.com:5432/harvey?sslmode=require"
        )):
            dsn = get_checkpoint_dsn()
        self.assertIn("postgresql://agent:", dsn)
        self.assertIn("db.example.com:5432/harvey", dsn)
        self.assertIn("sslmode=require", dsn)

    def test_sqlalchemy_driver_scheme_is_normalized(self):
        with patch.object(settings, "LANGGRAPH_DATABASE_URL", SecretStr(
            "postgresql+psycopg2://agent:secret@db.example.com/harvey"
        )):
            dsn = get_checkpoint_dsn()
        self.assertTrue(dsn.startswith("postgresql://"))

    def test_settings_fallback_encodes_password(self):
        with patch.object(settings, "LANGGRAPH_DATABASE_URL", None), \
             patch.object(settings, "DATABASE_URL", None), \
             patch.object(settings, "POSTGRES_PASSWORD", "p@ss:word"), \
             patch.object(settings, "POSTGRES_HOST", "db.example.com"), \
             patch.object(settings, "POSTGRES_PORT", 5432), \
             patch.object(settings, "POSTGRES_DB", "harvey"), \
             patch.object(settings, "POSTGRES_USER", "agent"), \
             patch.object(settings, "POSTGRES_SSLMODE", "require"):
            dsn = get_checkpoint_dsn()
        self.assertIn("p%40ss%3Aword", dsn)
        self.assertIn("sslmode=require", dsn)

    def test_unsupported_database_url_rejected(self):
        with patch.object(settings, "LANGGRAPH_DATABASE_URL", SecretStr(
            "sqlite:///app.db"
        )):
            with self.assertRaises(ValueError):
                get_checkpoint_dsn()
