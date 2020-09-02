import unittest
from snippet import Config, Snippet, app_name, home_config_path, app_config_path

config = Config(app_name, [home_config_path, app_config_path])
logger = config.logger


def new_snippet(format_string, arguments):
    s = Snippet(config)
    s.format_string = format_string
    s.arguments = arguments
    return s.build()


class TestSnippet(unittest.TestCase):

    def test_no_placeholders(self):
        self.assertEqual(new_snippet("abc def", []), ["abc def"])

    def test_simple_placeholders(self):
        self.assertEqual(new_snippet("abc <arg1> <arg2> def", ["arg1=test", "arg2=tset"]), ["abc test tset def"])

    def test_simple_placeholder_file_test(self):
        self.assertEqual(new_snippet("abc <arg1> <arg2> def", ["arg1=test", "arg2:test/data.txt"]), [
            "abc test 1234567 def", "abc test QWERTYU def", "abc test  a b c def"])

    def test_codec(self):
        self.assertEqual(new_snippet("abc <arg1> <arg1:b64> <arg2> <arg2:b64:b64> def", ["arg1=test", "arg2=tset"]), [
            "abc test dGVzdA== tset ZEhObGRBPT0= def"])

    def test_optional_arguments_without_start(self):
        self.assertEqual(new_snippet("[<arg2>] abc <arg1>", ["arg1=test"]), [
            " abc test"
        ])

    def test_optional_arguments_without_end(self):
        self.assertEqual(new_snippet("abc <arg1> [<arg2>]", ["arg1=test"]), [
            "abc test "
        ])

    def test_optional_arguments_without_middle(self):
        self.assertEqual(new_snippet("abc <arg1> [<arg2>] cba", ["arg1=test"]), [
            "abc test  cba"
        ])

        self.assertEqual(new_snippet("abc <arg1> [<arg2>] cba <arg3>", ["arg1=test", "arg3=tset"]), [
            "abc test  cba tset"
        ])
        self.assertEqual(new_snippet("abc <arg1> [<arg2>] cba <arg3> bsd", ["arg1=test", "arg3=tset"]), [
            "abc test  cba tset bsd"
        ])

    def test_optional_arguments_with(self):
        self.assertEqual(new_snippet("abc <arg1> [<arg2>]", ["arg1=test", "arg2=tset"]), [
            "abc test tset"
        ])

    def test_optional_arguments_no(self):
        self.assertEqual(new_snippet("abc [<arg1> <arg2>]", ["arg1=test"]), [
            "abc "
        ])

    def test_placeholder_default_text(self):
        self.assertEqual(new_snippet("abc <arg1==!test!=>", []), [
            "abc =!test!="
        ])

    def test_placeholder_default_text_with_codec(self):
        self.assertEqual(new_snippet("abc <arg1:b64=test>", []), [
            "abc dGVzdA=="
        ])

    def test_repeatable_placeholder_default_text(self):
        self.assertEqual(new_snippet("abc <arg1...=test>", []), [
            "abc test"
        ])

    def test_repeatable_placeholder_default_text_with_codec(self):
        self.assertEqual(new_snippet("abc <arg1:b64...=test>", []), [
            "abc dGVzdA=="
        ])

    def test_optional_default_text(self):
        self.assertEqual(new_snippet("<arg1> [<arg2=test> <arg3>]", ["arg1=123", "arg3=321"]), [
            "123 test 321"
        ])
        self.assertEqual(new_snippet("<arg1> [<arg2=test> <arg3>]", ["arg1=123"]), [
            "123 "
        ])


if __name__ == '__main__':
    unittest.main()
