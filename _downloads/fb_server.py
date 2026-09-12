# -*- coding: utf-8 -*-
"""本地接收服务器：接收 Chrome 控制台 POST 的粉笔数据"""
import http.server, json, os, socketserver

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fb")


class Handler(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        name = "fb_data.json"
        if "name=" in self.path:
            name = self.path.split("name=")[1].split("&")[0] + ".json"
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(body)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"saved " + name.encode())

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8765), Handler) as httpd:
    print("listening 8765")
    httpd.serve_forever()
