import json
import pyautogui
import threading
import pydirectinput
import os  # Commands your system hardware directly to bypass web browsers

# Standard Python server libraries
from http.server import BaseHTTPRequestHandler, HTTPServer
from pycloudflared import try_cloudflare

print("\n" + "="*60)
print("⚙️ [STARTING] Python Server Direct-ID Loop Running...")
print("🎯 Status: Initializing local port binding listener...")
print("="*60 + "\n")

HOST = "0.0.0.0"
PORT = 8124
GRID_WIDTH = 100
GRID_HEIGHT = 100

class HTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            screenshot = pyautogui.screenshot()
            img = screenshot.convert('RGB')
            new_img = img.resize((GRID_WIDTH, GRID_HEIGHT))
            raw_pixels = list(new_img.getdata())
            
            clean_pixel_list = [list(pixel) for pixel in raw_pixels]
            img_data = {
                "data": clean_pixel_list,
                "size": [GRID_WIDTH, GRID_HEIGHT]
            }
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(img_data), encoding='utf8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"error": str(e)}), encoding='utf8'))

    def do_POST(self):
        if self.path == "/keyboard":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                if payload and 'key' in payload:
                    key_to_press = payload['key']
                    print(f"📡 Received command string packet: {key_to_press}")
                    
                    if key_to_press.startswith("teleport:"):
                        # FIXED: Grabbed the second part of the split array [1] first, then applied .strip()
                        target_id = key_to_press.split("teleport:")[1].strip()
                        print(f"🎯 Extracted Target ID sequence: '{target_id}'")
                        
                        if target_id.isdigit():
                            print(f"🌀 RUNNING LAUNCHER COMMAND: Forcing game boot for ID -> {target_id}")
                            os.system(f"start roblox://placeId={target_id}")
                        else:
                            print(f"⚠️ REJECTED: '{target_id}' contains letters instead of numbers.")
                            
                    elif key_to_press.lower() == "i":
                        pyautogui.scroll(150) 
                    elif key_to_press.lower() == "o":
                        pyautogui.scroll(-150)
                    elif key_to_press.lower() == "space":
                        pydirectinput.press("space")
                    elif key_to_press.lower() == "backspace":
                        pydirectinput.press("backspace")
                    elif key_to_press.lower() == "enter":
                        pydirectinput.press("enter")
                    else:
                        pydirectinput.press(key_to_press.lower())
                        
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(bytes(json.dumps({"status": "pressed"}), encoding='utf8'))
            except Exception as e:
                print(f"❌ Input payload processing crashed: {e}")
                self.send_response(400)
                self.end_headers()

    def log_message(self, format, *args):
        return

def start_cloudflare_tunnel():
    """Automatically starts a free public tunnel and fixes the attribute object bug"""
    print("[SYSTEM] Booting secure public connection thread...")
    try:
        tunnel = try_cloudflare(port=PORT)
        try:
            tunnel_url = tunnel.url
        except AttributeError:
            raw_string = str(tunnel)
            if "Url:" in raw_string:
                tunnel_url = raw_string.split("Url:")[1].strip().split()[0]
            else:
                tunnel_url = raw_string.strip().split()[0]
        
        if not tunnel_url.startswith("https://"):
            tunnel_url = "https://" + tunnel_url
            
        print("\n" + "="*60)
        print("🚀 CLOUDFLARE PUBLIC TUNNEL IS ALIVE!")
        print(f"👉 COPY THIS LINK FOR ROBLOX: {tunnel_url}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"[ERROR] Could not track tunnel output automatically: {e}")

server = HTTPServer((HOST, PORT), HTTP)
threading.Thread(target=start_cloudflare_tunnel, daemon=True).start()

print("✅ [ONLINE] Python Server listening locally on port " + str(PORT) + "!")
print("🎯 Status: Waiting for Cloudflare connection tunnel to finish building...")

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass

server.server_close()
print("Server stopped")