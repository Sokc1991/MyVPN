import socket
import threading
import select
import random

class DPIProxy:
    def __init__(self, host='127.0.0.1', port=8881):
        self.host = host
        self.port = port
        self.running = False
        self.method = 'hybrid'
        self.unblock_count = 0
        
        # Blacklist с поддержкой игр и соцсетей
        self.blacklist = [
            "youtube.com", "youtu.be", "googlevideo.com", "ytimg.com",
            "brawlstars.com", "supercell.com", "clashroyale.com",
            "roblox.com", "rbxcdn.com", "minecraft.net", "mojang.com",
            "roblox.com", "rbxcdn.com", "robloxcdn.com", "robloxgames.com",
            "epicgames.com", "fortnite.com", "steampowered.com",
            "discord.com", "snapchat.com", "tiktok.com", "instagram.com",
            "facebook.com", "twitter.com", "x.com", "telegram.org", "t.me",
            "soundcloud.com", "spotify.com", "music.yandex.ru", "vk.com",
            "twitch.tv", "rutube.ru", "chatgpt.com", "openai.com"
        ]

    def fragment_data(self, data):
        if self.method == 'random':
            parts = []
            offset = 0
            while offset < len(data):
                chunk_size = min(random.randint(1, 100), len(data) - offset)
                parts.append(data[offset:offset + chunk_size])
                offset += chunk_size
            return parts
        elif self.method == 'sni' or self.method == 'hybrid':
            sni_pos = -1
            for i in range(min(len(data) - 5, 500)):
                if data[i:i+2] == b'\x00\x00':
                    sni_pos = i
                    break
            if sni_pos > 0:
                parts = [data[:sni_pos], data[sni_pos:sni_pos+40], data[sni_pos+40:]]
                if self.method == 'hybrid':
                    final = []
                    for p in parts:
                        if len(p) > 100:
                            offset = 0
                            while offset < len(p):
                                chunk = random.randint(30, 100)
                                final.append(p[offset:offset+chunk])
                                offset += chunk
                        else:
                            final.append(p)
                    return final
                return parts
        return [data]

    def start(self):
        self.running = True
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(100)
            threading.Thread(target=self._listen, daemon=True).start()
            print(f"🚀 Proxy started on {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Proxy start error: {e}")

    def _listen(self):
        while self.running:
            try:
                client, _ = self.server.accept()
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
            except:
                break

    def _handle(self, client):
        try:
            data = client.recv(8192)
            if not data:
                return
            header = data.decode('utf-8', 'ignore').split('\r\n')[0]
            if "CONNECT" in header:
                host_port = header.split(' ')[1]
                target_host = host_port.split(':')[0]
                target_port = int(host_port.split(':')[1])
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((target_host, target_port))
                client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                is_blacklisted = any(domain in target_host for domain in self.blacklist)
                if is_blacklisted:
                    self.unblock_count += 1
                self._bridge(client, remote, is_blacklisted)
        except:
            pass
        finally:
            client.close()

    def _bridge(self, client, remote, fragment):
        sockets = [client, remote]
        while self.running:
            r, _, _ = select.select(sockets, [], [], 1)
            if not r:
                continue
            for s in r:
                other = remote if s is client else client
                data = s.recv(8192)
                if not data:
                    return
                if fragment and s is client and data[0] == 0x16:
                    for chunk in self.fragment_data(data):
                        other.sendall(chunk)
                else:
                    other.sendall(data)

    def stop(self):
        self.running = False
        if hasattr(self, 'server'):
            try:
                self.server.close()
            except:
                pass
        print("🛑 Proxy stopped")
