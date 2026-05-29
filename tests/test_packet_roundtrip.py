import unittest

from crypto import pack_message, unpack_message


class TestPacketRoundtrip(unittest.TestCase):
    def test_pack_unpack_ok(self):
        passphrase = "42"
        sender = "umraniye"
        pt = b"Selam"

        payload = pack_message(sender, pt, passphrase)
        got_sender, got_pt = unpack_message(payload, passphrase)

        self.assertEqual(got_sender, sender)
        self.assertEqual(got_pt, pt)

    def test_unpack_wrong_key_fails(self):
        payload = pack_message("a", b"hi", "key1")
        with self.assertRaises(ValueError):
            unpack_message(payload, "key2")


if __name__ == "__main__":
    unittest.main()

