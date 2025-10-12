from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import urllib.request
import sys

class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/proxy-download':
            params = parse_qs(parsed_path.query)
            url = params.get('url', [None])[0]
            filename = params.get('filename', ['download'])[0]
            
            if url:
                try:
                    url = unquote(url)
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    
                    with urllib.request.urlopen(req) as response:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(response.read())
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(f'Error: {str(e)}'.encode())
                    return
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Missing url parameter')
                return
        
        super().do_GET()

if __name__ == '__main__':
    PORT = 5000
    server = HTTPServer(('0.0.0.0', PORT), NoCacheHTTPRequestHandler)
    print(f"Server running on http://0.0.0.0:{PORT}")
    print("Press Ctrl+C to stop the server")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
