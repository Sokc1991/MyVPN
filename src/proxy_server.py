import socket
import threading
import random
import time
import select
import os
import logging

class DPIProxy:
    def __init__(self, host='127.0.0.1', port=8881):
        self.host = host
        self.port = port
        self.running = False
        self.methods = ['hybrid', 'double_fragment', 'random_delay', 'fake_padding', 'sni', 'auto', 'tls_fragment', 'delayed']
        self.current_method = 'auto'
        self.history = {}
        self.stats = {'unblocked': 0, 'speed_up': 0, 'speed_down': 0, 'errors': 0}
        
        self.blacklist = [
            "youtube.com", "googlevideo.com", "discord.com", "discordapp.com",
            "t.me", "telegram.org", "roblox.com", "brawlstars.com",
            "valorant.com", "playvalorant.com", "leagueoflegends.com", "genshin.hoyoverse.com",
            "netflix.com", "disneyplus.com", "hbo.com", "icloud.com", "viber.com",
            "apexlegends.com", "callofduty.com", "riotgames.com", "origin.com",
            "spotify.com", "soundcloud.com", "twitch.tv", "rutube.ru", "vk.com",
            "instagram.com", "facebook.com", "twitter.com", "snapchat.com", "tiktok.com"
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ProxyCore")

    def _apply_bypass(self, remote_sock, data, method):
        try:
            if method == 'double_fragment':
                p1 = len(data) // 3
                p2 = (len(data) * 2) // 3
                chunks = [data[:p1], data[p1:p2], data[p2:]]
                for c in chunks:
                    mid = len(c) // 2
                    remote_sock.send(c[:mid])
                    time.sleep(0.01)
                    remote_sock.send(c[mid:])
                    
            elif method == 'random_delay':
                for b in range(len(data)):
                    remote_sock.send(data[b:b+1])
                    if random.random() > 0.7:
                        time.sleep(random.uniform(0.005, 0.05))
                        
            elif method == 'fake_padding':
                padding = os.urandom(random.randint(32, 128))
                remote_sock.send(padding)
                time.sleep(0.05)
                remote_sock.send(data)
                
            elif method == 'sni':
                remote_sock.send(data[:10])
                time.sleep(0.1)
                remote_sock.send(data[10:])
                
            else:
                remote_sock.send(data[:2])
                time.sleep(0.12)
                remote_sock.send(data[2:])
                
            self.stats['unblocked'] += 1
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Bypass error: {e}")

    def _bridge(self, client_sock, remote_sock):
        client_sock.setblocking(0)
        remote_sock.setblocking(0)
        sockets = [client_sock, remote_sock]
        
        while self.running:
            try:
                readable, _, _ = select.select(sockets, [], [], 1.0)
                if not readable: continue
                
                for s in readable:
                    other = remote_sock if s is client_sock else client_sock
                    data = s.recv(8192)
                    if not data:
                        return
                    other.send(data)
                    
                    if s is remote_sock:
                        self.stats['speed_down'] += len(data)
                    else:
                        self.stats['speed_up'] += len(data)
            except:
                break

    def _handle_client(self, client_sock):
        try:
            initial_data = client_sock.recv(4096)
            if not initial_data: return
            
            lines = initial_data.split(b'\r\n')
            first_line = lines[0].decode(errors='ignore')
            
            if "CONNECT" in first_line:
                target = first_line.split(' ')[1]
                host = target.split(':')[0]
                port = int(target.split(':')[1]) if ":" in target else 443
                client_sock.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                data_to_bypass = client_sock.recv(4096)
            else:
                host = first_line.split(' ')[1].split('/')[2]
                port = 80
                data_to_bypass = initial_data

            method = self.current_method
            if method == 'auto':
                method = self.history.get(host, 'double_fragment')

            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(5)
            remote_sock.connect((host, port))
            
            self._apply_bypass(remote_sock, data_to_bypass, method)
            self.history[host] = method
            
            self._bridge(client_sock, remote_sock)
        except Exception as e:
            self.logger.error(f"Handler error: {e}")
        finally:
            client_sock.close()

    def start(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(128)
        self.logger.info(f"Proxy started on {self.host}:{self.port}")
        
        while self.running:
            try:
                client, _ = server.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except:
                break

    def stop(self):
        self.running = False
        self.logger.info("Proxy stopped")
