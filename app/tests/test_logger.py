import io
import json
import os
import unittest
from unittest.mock import patch

from app.logger import Logger


class LoggerTestCase(unittest.TestCase):
    def test_plaintext_format_in_local_mode(self):
        logger = Logger("main.py")
        with patch.dict(os.environ, {"LOG_JSON": "", "AWS_LAMBDA_FUNCTION_NAME": ""}, clear=False):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                logger.info("Hello world")

        output = fake_out.getvalue().strip()
        self.assertRegex(
            output,
            r"^\[\d{6}\.\d{2}\]\[main\.py\]\[INFO\]: Hello world$",
        )

    def test_json_format_when_env_flag_set(self):
        logger = Logger("handlers.py")
        with patch.dict(os.environ, {"LOG_JSON": "true"}, clear=False):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                logger.error("uh oh")

        payload = json.loads(fake_out.getvalue())
        self.assertEqual(
            payload,
            {
                "file_name": "handlers.py",
                "log_level": "ERROR",
                "message": "uh oh",
            },
        )

    def test_lambda_environment_enforces_json(self):
        logger = Logger("service.py")
        with patch.dict(os.environ, {"LOG_JSON": "", "AWS_LAMBDA_FUNCTION_NAME": "dm-hours"}, clear=False):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                logger.warning("running in lambda")

        payload = json.loads(fake_out.getvalue())
        self.assertEqual(payload["log_level"], "WARNING")
        self.assertEqual(payload["file_name"], "service.py")
        self.assertEqual(payload["message"], "running in lambda")


if __name__ == "__main__":
    unittest.main()

