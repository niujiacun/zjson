import unittest
import zjson


class ZjsonTest(unittest.TestCase):

    def test_parse_null(self):
        self.assertIsNone(zjson.parse("null"))

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("null0")

    def test_parse_false(self):
        self.assertFalse(zjson.parse("false"))

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("flase")

    def test_parse_true(self):
        self.assertTrue(zjson.parse("true"))

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("ture")

    def test_parse_number(self):
        self.assertEqual(zjson.parse("-1"), -1.0)
        self.assertEqual(zjson.parse("1"), 1.0)
        self.assertEqual(zjson.parse("0"), 0.0)
        self.assertEqual(zjson.parse("-0"), 0.0)
        self.assertEqual(zjson.parse("1.1"), 1.1)
        self.assertEqual(zjson.parse("1.10"), 1.1)
        self.assertEqual(zjson.parse("1E1"), 10.0)
        self.assertEqual(zjson.parse("1E-1"), 0.1)
        self.assertEqual(zjson.parse("1E0"), 1.0)
        self.assertEqual(zjson.parse("1E-0"), 1.0)
        self.assertEqual(zjson.parse("1.1E0"), 1.1)
        self.assertEqual(zjson.parse("-1.1E1"), -11.0)

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("00")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("0..0")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("0.E0")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("0.")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("-")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("+0")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("+1")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse(".23")

    def test_parse_string(self):
        self.assertEqual(zjson.parse('"hello"'), "hello")
        self.assertEqual(zjson.parse('"1111"'), "1111")
        self.assertEqual(zjson.parse('"1111\\""'), "1111\"")
        self.assertEqual(zjson.parse('"1111\\n"'), "1111\n")
        self.assertEqual(zjson.parse('"1111\\r"'), "1111\r")
        self.assertEqual(zjson.parse('"1111   "'), "1111   ")
        self.assertEqual(zjson.parse('"  1111   "'), "  1111   ")
        self.assertEqual(zjson.parse('"\\\\"'), "\\")
        self.assertEqual(zjson.parse('"\\/"'), "/")
        self.assertEqual(zjson.parse('""'), "")
        self.assertEqual(zjson.parse('"\\u6c49"'), "汉")
        self.assertEqual(zjson.parse('"\\uD834\\uDD1E"'), "𝄞")

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("\"")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("\"111")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("111\"")
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse('"\\uxxxx"')
        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse('"\\uD801\\ux"')

    def test_parse_array(self):
        self.assertEqual(zjson.parse('["hello"]'), ["hello"])
        self.assertEqual(zjson.parse('[1]'), [1])
        self.assertEqual(zjson.parse('[null]'), [None])
        self.assertEqual(zjson.parse('[1,2,3]'), [1,2,3])
        self.assertEqual(zjson.parse('[1,2,"hello"]'), [1,2,"hello"])
        self.assertEqual(zjson.parse('[true, false]'), [True, False])
        self.assertEqual(zjson.parse('[[1,2], [3,4]]'), [[1,2], [3,4]])
        self.assertEqual(zjson.parse('[{"hello": "world"}]'), [{"hello": "world"}])

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse('[1')
            zjson.parse('[1, 2')
            zjson.parse('[1, 2}')

    def test_parse_object(self):
        self.assertEqual(zjson.parse(' {"hello": 1} '), {"hello": 1})
        self.assertEqual(zjson.parse('\t{"hello": "world"}\n'), {"hello": "world"})
        self.assertEqual(zjson.parse('{"hello": "world", "k2": "v2"}'), {"hello": "world", "k2": "v2"})
        self.assertEqual(zjson.parse('{"hello": [1,2]}'), {"hello": [1,2]})
        self.assertEqual(zjson.parse('{"hello": {"k1":"v1", "k2": "v2"}}'), {"hello": {"k1":"v1", "k2": "v2"}})

        with self.assertRaises(zjson.UnexpectedCharacterError):
            zjson.parse("{1:2}")
            zjson.parse('{"1":2')
            zjson.parse('{"1":2')

