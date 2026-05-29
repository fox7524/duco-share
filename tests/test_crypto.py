import unittest

from crypto import (
    derive_key,
    xor_bytes,
    sign_hmac_hex,
    verify_hmac_hex,
)


class TestCrypto(unittest.TestCase):
    def test_xor_roundtrip(self):
        key = derive_key("pass")
        pt = b"selam"
        ct = xor_bytes(pt, key)
        rt = xor_bytes(ct, key)
        self.assertEqual(rt, pt)

    def test_hmac_verify_ok(self):
        key = derive_key("pass")
        body = b"hello|world"
        sig = sign_hmac_hex(key, body)
        self.assertTrue(verify_hmac_hex(key, body, sig))

    def test_hmac_verify_fail_on_change(self):
        key = derive_key("pass")
        body = b"hello|world"
        sig = sign_hmac_hex(key, body)
        self.assertFalse(verify_hmac_hex(key, b"hello|WORLD", sig))


if __name__ == "__main__":
    unittest.main()

