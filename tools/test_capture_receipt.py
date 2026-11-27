import importlib.util
import struct
import tempfile
import threading
import time
import unittest
import zlib
from pathlib import Path

spec = importlib.util.spec_from_file_location("capture_receipt", Path(__file__).with_name("capture-receipt.py"))
receipt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt)


def png():
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\0" * 5)) + chunk(b"IEND", b""))


class CaptureReceipt(unittest.TestCase):
    def test_command_acknowledges_before_readbacks_finish(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            stale = folder / "frame-42-1x1-rgba-p4.raw"
            stale.write_bytes(b"old!")
            def respond():
                for _ in range(200):
                    if (folder / "cmd").exists():
                        break
                    time.sleep(.01)
                (folder / "reply.txt").write_text("cap: presents 41..42 are saved\n")
                (folder / "done").touch()
                image = png()
                first = folder / "frame-41.png"
                first.write_bytes(image[:-12])
                time.sleep(.6)
                first.write_bytes(image)
                stale.write_bytes(b"new!")
            worker = threading.Thread(target=respond)
            worker.start()
            try:
                result = receipt.capture(folder, folder, 2, 3)
            finally:
                worker.join()
            self.assertEqual([frame["present"] for frame in result["frames"]], [41, 42])
            self.assertEqual(result["frames"][0]["bytes"], len(png()))
            self.assertEqual(result["frames"][1]["sha256"], receipt.hashlib.sha256(b"new!").hexdigest())

    def test_stale_incomplete_and_padded_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame-7-4x2-bgra-p32.raw"
            path.write_bytes(bytes(47))
            self.assertIsNone(receipt.read_frame(path, 7, {}))
            path.write_bytes(bytes(48))
            self.assertIsNone(receipt.read_frame(path, 7, {path: receipt.stamp(path.stat())}))
            self.assertEqual(receipt.read_frame(path, 7, {})["height"], 2)
            path.write_bytes(bytes(64))
            self.assertEqual(receipt.read_frame(path, 7, {})["width"], 4)


if __name__ == "__main__":
    unittest.main()
