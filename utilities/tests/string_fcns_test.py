import unittest
import utilities as fcn

class MyTestCase(unittest.TestCase):
    def test_multi_line_null_string(self):
        actual = fcn.encode_newlines("")
        expected = ""
        self.assertEqual(actual, expected)  # add assertion here

    def test_multi_line_encoding(self):
        actual = fcn.encode_newlines("test\nlines")
        expected = "test\\nlines"
        self.assertEqual(actual, expected)  # add assertion here

if __name__ == '__main__':
    unittest.main()
