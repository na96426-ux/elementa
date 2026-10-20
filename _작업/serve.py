# 검수용 로컬 서버. 브라우저 미리보기(launch.json "elementa")가 이 스크립트를 띄운다.
# 게임 자체는 index.html 을 그냥 열어도 되지만, 자동 검수는 localStorage 가 필요해 http 로 띄운다.
import os, sys, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):  # 요청 로그는 조용히
        pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

handler = functools.partial(Quiet, directory=ROOT)
ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
