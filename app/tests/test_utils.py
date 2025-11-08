import unittest

from app.utils import build_response


class UtilsTestCase(unittest.TestCase):
    def test_build_response_with_dict_body_serializes_to_json(self):
        response = build_response({"foo": "bar"}, status_code=201)
        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(response["body"], '{"foo": "bar"}')

    def test_build_response_with_string_body(self):
        response = build_response("plain text")
        self.assertEqual(response["body"], "plain text")

    def test_build_response_with_non_serializable_body_falls_back_to_str(self):
        class Unserializable:
            def __str__(self):
                return "fallback"

        response = build_response(Unserializable())
        self.assertEqual(response["body"], "fallback")


if __name__ == "__main__":
    unittest.main()

