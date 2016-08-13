
import re
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
sys.path.insert(0, "..")

from handlers import API_METHODS


class Webserver(BaseHTTPRequestHandler):

    def do_GET(self):
        if "favicon.ico" in self.path:
            self.send_response(404)
            self.end_headers()
            return False

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        request_path = self.path
        if "?" in request_path:
            request_path = request_path[:request_path.index("?")]


        result = {"requested": request_path, "error": "no handler found", "errorcode": 404}

        for path, handler in API_METHODS.items():
            match = path.match(request_path)
            if match:
                result = handler(*match.groups())

        content = json.dumps(result)
        self.wfile.write(content.encode("utf-8", "ignore"))

def main():
    try:
        server = HTTPServer(("localhost", 8080), Webserver)
        print("Server started on localhost:8080 ...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shutting down server")
        server.socket.close()

if __name__ == "__main__":
    main()

