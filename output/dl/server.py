"""سيرفر التحميل: متعدّد المسارات + دعم Range كامل (سحب/تقديم الفيديو) + CORS.

python3 server.py            # يخدم المجلد الحالي على 0.0.0.0:8080
"""
import http.server
import os
import re
import socketserver

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT", "8080"))
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class H(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    _span = None

    # ---- CORS على كل رد
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range, Content-Type")
        self.send_header("Access-Control-Expose-Headers", "Content-Range, Accept-Ranges, Content-Length")
        super().end_headers()

    # ---- Range
    def send_head(self):
        self._span = None
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "Not found")
            return None
        size = os.fstat(f.fileno()).st_size
        ctype = self.guess_type(path)
        rng = self.headers.get("Range")

        if rng:
            m = RANGE_RE.match(rng.strip())
            if m:
                a, b = m.group(1), m.group(2)
                if a:
                    start = int(a)
                    end = int(b) if b else size - 1
                elif b:                      # bytes=-N  → آخر N بايت
                    start = max(size - int(b), 0)
                    end = size - 1
                else:
                    start, end = 0, size - 1
                if start >= size or start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    f.close()
                    return None
                end = min(end, size - 1)
                self._span = (start, end - start + 1)
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(self._span[1]))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                f.seek(start)
                return f

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        return f

    # ---- ما يقرأ أكتر من حدود الـ Range
    def copyfile(self, source, outputfile):
        if self._span is None:
            return super().copyfile(source, outputfile)
        left = self._span[1]
        while left > 0:
            chunk = source.read(min(64 * 1024, left))
            if not chunk:
                break
            try:
                outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return
            left -= len(chunk)

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), H) as s:
        s.serve_forever()
