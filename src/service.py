import asyncio
import json
import logging
import os
import random
import threading
from lib.android.notification import create_notify_channel, notify
from lib.android.storage import app_storage_path

BLOCKED = []
RESERVED_BLOCKED = [
    b'youtube.com',
    b'youtu.be',
    b'yt.be',
    b'googlevideo.com',
    b'ytimg.com',
    b'ggpht.com',
    b'gvt1.com',
    b'youtube-nocookie.com',
    b'youtube-ui.l.google.com',
    b'youtubeembeddedplayer.googleapis.com',
    b'youtube.googleapis.com',
    b'youtubei.googleapis.com',
    b'yt-video-upload.l.google.com',
    b'wide-youtube.l.google.com',
]

if os.path.exists(os.path.join(app_storage_path(), "blacklist.txt")):
    try:
        with open(os.path.join(app_storage_path(), "blacklist.txt"), 'r', encoding='utf-8') as f:
            count = 0
            for line in f.readlines():
                BLOCKED.append(line.strip().encode())
                if not line.isspace():
                    count += 1
            if count <= 0:
                raise ValueError('Empty blacklist')
        logging.info('Read blacklist from file')
    except Exception as e:
        logging.info(
            f'Error reading blacklist: {e}')
        BLOCKED = RESERVED_BLOCKED
else:
    logging.info(
        "No blacklist file found, using default")
    BLOCKED = RESERVED_BLOCKED

TASKS = []


async def pipe(reader, writer):
    try:
        while not reader.at_eof() and not writer.is_closing():
            data = await reader.read(1500)
            writer.write(data)
            await writer.drain()
    except:
        pass
    finally:
        writer.close()


async def new_conn(reader, writer):
    try:
        http_data = await reader.read(1500)
        if not http_data:
            writer.close()
            return
        headers = http_data.split(b"\r\n")
        first_line = headers[0].split(b" ")
        method = first_line[0]
        url = first_line[1]

        if method == b"CONNECT":
            host_port = url.split(b":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 443
        else:
            host_header = next(
                (h for h in headers if h.startswith(b"Host: ")), None
            )
            if not host_header:
                raise ValueError("Missing Host header")

            host_port = host_header[6:].split(b":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 80

        if method == b"CONNECT":
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()

            remote_reader, remote_writer = await asyncio.open_connection(
                host.decode(), port
            )

            await fragment_data(reader, remote_writer)
        else:
            remote_reader, remote_writer = await asyncio.open_connection(
                host.decode(), port
            )
            remote_writer.write(http_data)
            await remote_writer.drain()

        TASKS.extend(
            [
                asyncio.create_task(
                    pipe(reader, remote_writer,)
                ),
                asyncio.create_task(
                    pipe(remote_reader, writer)
                ),
            ]
        )
    except Exception as e:
        try:
            writer.write(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
            await writer.drain()
        except Exception:
            pass
        writer.close()


async def fragment_data(reader, writer):
    try:
        head = await reader.read(5)
        data = await reader.read(2048)
    except Exception as e:
        return

    if all(site not in data for site in BLOCKED):
        writer.write(head + data)
        await writer.drain()
        return

    parts = []
    host_end = data.find(b"\x00")
    if host_end != -1:
        parts.append(
            bytes.fromhex("160304")
            + (host_end + 1).to_bytes(2, "big")
            + data[: host_end + 1]
        )
        data = data[host_end + 1:]

    while data:
        chunk_len = random.randint(1, len(data))
        parts.append(
            bytes.fromhex("160304")
            + chunk_len.to_bytes(2, "big")
            + data[:chunk_len]
        )
        data = data[chunk_len:]

    writer.write(b"".join(parts))
    await writer.drain()


class ProxyServer:
    def __init__(self):
        if os.path.exists(os.path.join(app_storage_path(), "proxy_config.json")):
            try:
                with open(os.path.join(app_storage_path(), "proxy_config.json"), "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.host = config.get("host", "0.0.0.0")
                    self.port = str(config.get("port", "8881"))
            except Exception as e:
                self.host = "0.0.0.0"
                self.port = "8881"
        else:
            self.host = "0.0.0.0"
            self.port = "8881"
        self.server = None
        self.loop = None
        self.running = False

    def start(self):

        if self.running:
            return

        notify(0, "0", "NoDPI",
               f"Proxy server is starting on {self.host}:{self.port} Enjoy watching!")

        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def _run_server(self):

        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            async def server_main():
                self.server = await asyncio.start_server(
                    new_conn, self.host, self.port
                )

                async with self.server:
                    await self.server.serve_forever()

            self.loop.run_until_complete(server_main())
        except Exception as e:
            pass
        finally:
            if self.loop and self.loop.is_running():
                self.loop.stop()
            if self.loop:
                self.loop.close()
            self.running = False

    def stop(self):

        if not self.running:
            return

        self.running = False

        if self.server:
            self.server.close()
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)


if __name__ == '__main__':

    from kivy import platform

    if platform != 'android':
        raise Exception('This module only for Android devices!')

    logging.info("Starting Proxy Service")

    try:
        logging.info("Creating notification channel")
        create_notify_channel('0', 'Proxy Service', '')
        logging.info("Notification channel created")
    except Exception as e:
        logging.error(
            f"Error creating notification channel: {e}")

    try:
        logging.info("Initializing proxy server")
        proxy = ProxyServer()
        logging.info("Starting proxy server")
        proxy.start()
        logging.info("Proxy server started")

        logging.info("Entering main loop")
        while proxy.running:
            threading.Event().wait(1)

    except Exception as e:
        logging.error(f"Main error: {e}")
    finally:
        logging.info("Shutting down")
        if 'proxy' in locals():
            proxy.stop()
        logging.info("Service stopped")
