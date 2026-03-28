import socket
import threading
import select
import random
import time
import struct

class DPIProxy:
    def __init__(self, host='127.0.0.1', port=8881):
        self.host = host
        self.port = port
        self.running = False
        self.method = 'auto'  # auto выбирает лучший метод автоматически
        self.unblock_count = 0
        self.last_method_used = 'hybrid'
        
        # Расширенный blacklist
        self.blacklist = [
            # YouTube
            "youtube.com", "youtu.be", "googlevideo.com", "ytimg.com", "ggpht.com",
            # Игры
            "brawlstars.com", "supercell.com", "clashroyale.com", "clashofclans.com",
            "roblox.com", "rbxcdn.com", "robloxcdn.com", "minecraft.net", "mojang.com",
            "epicgames.com", "fortnite.com", "steampowered.com", "steamcommunity.com",
            # Соцсети
            "discord.com", "discordapp.com", "snapchat.com", "tiktok.com",
            "instagram.com", "facebook.com", "twitter.com", "x.com",
            "telegram.org", "t.me", "whatsapp.com",
            # Музыка
            "soundcloud.com", "spotify.com", "music.yandex.ru", "vk.com",
            # Видео
            "twitch.tv", "rutube.ru", "netflix.com",
            # AI
            "chatgpt.com", "openai.com", "claude.ai"
        ]

    # ==================== МЕТОД 1: СЛУЧАЙНАЯ ФРАГМЕНТАЦИЯ ====================
    def fragment_random(self, data):
        """Режет на случайные куски от 1 до 100 байт"""
        if len(data) < 200:
            return [data]
        parts = []
        offset = 0
        while offset < len(data):
            chunk = min(random.randint(1, 100), len(data) - offset)
            parts.append(data[offset:offset + chunk])
            offset += chunk
        return parts

    # ==================== МЕТОД 2: SNI ФРАГМЕНТАЦИЯ ====================
    def fragment_sni(self, data):
        """Режет по позиции SNI"""
        if len(data) < 200:
            return [data]
        
        sni_pos = -1
        for i in range(min(len(data) - 5, 500)):
            if data[i:i+2] == b'\x00\x00':
                sni_pos = i
                break
        
        if sni_pos > 0:
            # Режем на 3 части
            parts = [
                data[:sni_pos],
                data[sni_pos:sni_pos + 40],
                data[sni_pos + 40:]
            ]
            return [p for p in parts if len(p) > 0]
        
        # Fallback
        chunk = len(data) // 3
        return [data[:chunk], data[chunk:2*chunk], data[2*chunk:]]

    # ==================== МЕТОД 3: HYBRID (SNI + RANDOM) ====================
    def fragment_hybrid(self, data):
        """Сначала SNI, потом большие куски режет случайно"""
        if len(data) < 200:
            return [data]
        
        sni_parts = self.fragment_sni(data)
        final = []
        
        for part in sni_parts:
            if len(part) > 100:
                # Дополнительная случайная резка
                offset = 0
                while offset < len(part):
                    chunk = random.randint(30, 100)
                    final.append(part[offset:offset + chunk])
                    offset += chunk
            else:
                final.append(part)
        
        return final

    # ==================== МЕТОД 4: РАЗРЫВ (TLS FRAGMENT) ====================
    def fragment_tls_fragment(self, data):
        """Специальный метод для обхода DPI через разрыв TLS записи"""
        if len(data) < 100:
            return [data]
        
        # Создаем фейковую TLS запись
        fake_header = b'\x16\x03\x03\x00\x01\x00'
        
        parts = []
        # Сначала отправляем фейк
        parts.append(fake_header)
        # Потом оригинал по частям
        offset = 0
        while offset < len(data):
            chunk = random.randint(20, 80)
            parts.append(data[offset:offset + chunk])
            offset += chunk
        
        return parts

    # ==================== МЕТОД 5: ЗАДЕРЖКА МЕЖДУ ЧАСТЯМИ ====================
    def fragment_delayed(self, data):
        """Режет на части и добавляет задержку между отправкой"""
        if len(data) < 200:
            return [data]
        
        parts = []
        offset = 0
        while offset < len(data):
            chunk = random.randint(1, 50)
            parts.append(data[offset:offset + chunk])
            offset += chunk
        
        self.last_delayed_parts = parts
        return parts

    # ==================== МЕТОД 6: AUTO (ВЫБИРАЕТ ЛУЧШИЙ) ====================
    def fragment_auto(self, data, host=None):
        """Автоматически выбирает метод в зависимости от сайта"""
        # Для YouTube лучше работает hybrid
        if host and ('youtube' in host or 'googlevideo' in host):
            return self.fragment_hybrid(data)
        # Для игр лучше работает tls_fragment
        if host and ('brawlstars' in host or 'roblox' in host or 'minecraft' in host):
            return self.fragment_tls_fragment(data)
        # Для соцсетей лучше работает random
        if host and ('instagram' in host or 'facebook' in host or 'tiktok' in host):
            return self.fragment_random(data)
        # По умолчанию hybrid
        return self.fragment_hybrid(data)

    # ==================== ОСНОВНАЯ ЛОГИКА ====================
    def fragment_data(self, data, host=None):
        """Выбор метода фрагментации"""
        if self.method == 'random':
            return self.fragment_random(data)
        elif self.method == 'sni':
            return self.fragment_sni(data)
        elif self.method == 'hybrid':
            return self.fragment_hybrid(data)
        elif self.method == 'tls_fragment':
            return self.fragment_tls_fragment(data)
        elif self.method == 'delayed':
            return self.fragment_delayed(data)
        else:  # auto
            return self.fragment_auto(data, host)

    def start(self):
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(100)
        threading.Thread(target=self._listen, daemon=True).start()
        print(f"✅ Прокси запущен на {self.host}:{self.port}")
        print(f"✅ Метод: {self.method.upper()}")

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
                    print(f"🔓 Разблокирован: {target_host}")
                    fragment = True
                else:
                    fragment = False
                
                self._bridge(client, remote, fragment, target_host)
        except Exception as e:
            pass
        finally:
            client.close()

    def _bridge(self, client, remote, fragment, host):
        sockets = [client, remote]
        delayed_parts = None
        
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
                    parts = self.fragment_data(data, host)
                    
                    # Для метода delayed отправляем с задержкой
                    if self.method == 'delayed':
                        for part in parts:
                            other.sendall(part)
                            time.sleep(0.02)  # 20ms задержка
                    else:
                        for part in parts:
                            other.sendall(part)
                else:
                    other.sendall(data)

    def stop(self):
        self.running = False
        if hasattr(self, 'server'):
            self.server.close()
        print("🛑 Прокси остановлен")
