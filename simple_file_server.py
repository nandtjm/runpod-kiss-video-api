#!/usr/bin/env python3
"""
Simple file server for serving generated videos
Run this in background to serve video files over HTTP
"""

import os
import http.server
import socketserver
from pathlib import Path
import threading

class VideoHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/tmp", **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def start_file_server(port=8080):
    """Start simple HTTP file server for videos"""
    try:
        with socketserver.TCPServer(("", port), VideoHandler) as httpd:
            print(f"🌐 Video file server running on http://localhost:{port}/")
            print("📹 Videos will be accessible at: http://localhost:{port}/filename.mp4")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Failed to start file server: {e}")

if __name__ == "__main__":
    start_file_server()