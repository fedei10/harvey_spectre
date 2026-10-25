import unittest
from unittest.mock import patch

import redis

from app.config import settings
from app.services.Redis.connection import check_redis_connection, get_redis_connection


class RedisConnectionTests(unittest.TestCase):
    def test_both_public_names_are_available(self):
        from app.services.Redis.connection import test_redis_connection
        self.assertIs(test_redis_connection, check_redis_connection)

    def test_client_uses_loaded_settings(self):
        with patch.object(settings, 'REDIS_HOST', 'redis.example'), patch.object(settings, 'REDIS_PORT', 6380):
            with patch('app.services.Redis.connection.redis.StrictRedis') as constructor:
                get_redis_connection()
        self.assertEqual(constructor.call_args.kwargs['host'], 'redis.example')
        self.assertEqual(constructor.call_args.kwargs['port'], 6380)

    def test_check_pings_without_writing_and_closes_client(self):
        with patch('app.services.Redis.connection.get_redis_connection') as factory:
            client = factory.return_value.__enter__.return_value
            client.ping.return_value = True
            self.assertIn('Successfully', check_redis_connection())
            client.ping.assert_called_once_with()
            client.set.assert_not_called()
            factory.return_value.__exit__.assert_called_once()

    def test_connection_error_does_not_expose_details(self):
        with patch('app.services.Redis.connection.get_redis_connection') as factory:
            factory.return_value.__enter__.return_value.ping.side_effect = redis.ConnectionError('private details')
            result = check_redis_connection()
        self.assertIn('ConnectionError', result)
        self.assertNotIn('private details', result)

    def test_main_import_and_connection_check(self):
        from app.main import test_connections
        with patch('app.main.health.check_groq_connection', return_value={'status': 'OK'}):
            with patch('app.services.Redis.connection.get_redis_connection') as factory:
                factory.return_value.__enter__.return_value.ping.return_value = True
                self.assertIn('Successfully', test_connections()['redis'])
