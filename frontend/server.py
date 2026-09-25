import http.server
import socketserver
import sys

PORT = 3000

class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Permitir requisições de desenvolvimento
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    with socketserver.TCPServer(("", port), CustomHTTPHandler) as httpd:
        print(f"Frontend do YouTube Downloader iniciado com sucesso!")
        print(f"Acesse no seu navegador: http://localhost:{port}")
        print("Pressione Ctrl+C para parar o servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor finalizado.")
