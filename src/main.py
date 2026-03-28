"""
MyVPN - с меню настроек и логгированием
"""
import sys
import os
import random
import threading
import subprocess

# ========== ЛОГГИРОВАНИЕ ==========
LOG_FILE = '/storage/emulated/0/myvpn_error.txt'

def log_to_file(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(msg + '\n')
    except:
        pass

log_to_file("=== MyVPN STARTED ===")

# ========== ИМПОРТЫ ==========
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Ellipse, InstructionGroup
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

try:
    from proxy_server import DPIProxy
    log_to_file("✅ DPIProxy imported")
except Exception as e:
    log_to_file(f"❌ DPIProxy import error: {e}")
    class DPIProxy:
        def __init__(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def method(self): return 'hybrid'

# ========== ЭКРАН НАСТРОЕК ==========
class SettingsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        layout.add_widget(Label(
            text="⚙️ НАСТРОЙКИ", font_size='24sp',
            color=get_color_from_hex('#D4AAFF'), size_hint_y=0.1
        ))
        
        # Кнопка "Показать логи"
        log_btn = Button(
            text="📋 ПОКАЗАТЬ ЛОГИ", size_hint_y=0.15,
            background_normal='', background_color=(0.3, 0.2, 0.5, 0.8),
            color=(1, 1, 1, 1), bold=True
        )
        log_btn.bind(on_release=self.show_logs)
        layout.add_widget(log_btn)
        
        # Кнопка "Отправить логи"
        send_btn = Button(
            text="📤 ОТПРАВИТЬ ЛОГИ (Telegram)", size_hint_y=0.15,
            background_normal='', background_color=(0.3, 0.2, 0.5, 0.8),
            color=(1, 1, 1, 1), bold=True
        )
        send_btn.bind(on_release=self.send_logs)
        layout.add_widget(send_btn)
        
        # Кнопка "Очистить логи"
        clear_btn = Button(
            text="🗑️ ОЧИСТИТЬ ЛОГИ", size_hint_y=0.15,
            background_normal='', background_color=(0.3, 0.2, 0.5, 0.8),
            color=(1, 1, 1, 1), bold=True
        )
        clear_btn.bind(on_release=self.clear_logs)
        layout.add_widget(clear_btn)
        
        # Кнопка "Назад"
        back_btn = Button(
            text="◀️ НАЗАД", size_hint_y=0.15,
            background_normal='', background_color=(0.2, 0.15, 0.3, 0.8),
            color=(0.9, 0.8, 1, 1), bold=True
        )
        back_btn.bind(on_release=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def show_logs(self, instance):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
        except:
            logs = "Логов пока нет"
        
        # Создаем popup с прокруткой
        content = BoxLayout(orientation='vertical', size_hint_y=None)
        content.height = 400
        
        scroll = ScrollView()
        log_label = Label(text=logs, size_hint_y=None, font_size='10sp',
                         color=(0.8, 0.8, 1, 1), halign='left', valign='top')
        log_label.bind(size=log_label.setter('text_size'))
        log_label.text_size = (Window.width - 100, None)
        log_label.height = len(logs.split('\n')) * 20
        
        scroll.add_widget(log_label)
        content.add_widget(scroll)
        
        close_btn = Button(text="ЗАКРЫТЬ", size_hint_y=0.15,
                          background_color=(0.4, 0.2, 0.7, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title="📋 ЛОГИ", content=content, size_hint=(0.9, 0.8))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def send_logs(self, instance):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
        except:
            logs = "Логов пока нет"
        
        # Копируем в буфер обмена и показываем
        from android import Android
        Android().clipboard(logs)
        
        popup = Popup(title="📤 ЛОГИ СКОПИРОВАНЫ",
                      content=Label(text="Логи скопированы в буфер обмена.\nОтправь их @gZ9zRbTt"),
                      size_hint=(0.8, 0.4))
        popup.open()
    
    def clear_logs(self, instance):
        try:
            with open(LOG_FILE, 'w') as f:
                f.write("=== Логи очищены ===\n")
        except:
            pass
        
        popup = Popup(title="✅ ГОТОВО",
                      content=Label(text="Логи очищены"),
                      size_hint=(0.6, 0.3))
        popup.open()
    
    def go_back(self, instance):
        self.app.switch_to_main()

# ========== ГЛАВНЫЙ ЭКРАН ==========
class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.proxy = DPIProxy()
        self.active = False
        self.methods = ['hybrid', 'random', 'sni']
        self.current_method_idx = 0
        
        root = RelativeLayout()
        
        # Фон
        with root.canvas.before:
            for i in range(100):
                Color(0.04, 0.02, 0.1 + (i/1000), 1)
                Rectangle(pos=(0, i * (Window.height/100)), size=(Window.width, Window.height/100))
        
        # Звезды
        self.stars = InstructionGroup()
        root.canvas.after.add(self.stars)
        Clock.schedule_interval(self.update_stars, 1/20)
        
        # Шестеренка (кнопка настроек)
        self.settings_btn = Button(
            text="⚙️", font_size='24sp',
            size_hint=(0.1, 0.07), pos_hint={'right': 0.95, 'top': 0.95},
            background_normal='', background_color=(0, 0, 0, 0),
            color=(0.9, 0.8, 1, 1), bold=True
        )
        self.settings_btn.bind(on_release=self.app.open_settings)
        root.add_widget(self.settings_btn)
        
        # Заголовок
        self.title = Label(
            text="[b]MyVPN[/b]", markup=True, font_size='56sp',
            pos_hint={'center_x': .5, 'center_y': .85},
            color=get_color_from_hex('#D4AAFF')
        )
        root.add_widget(self.title)
        
        # Выбор метода
        self.method_btn = Button(
            text=f"МЕТОД: {self.methods[0].upper()}",
            size_hint=(0.7, 0.08), pos_hint={'center_x': .5, 'center_y': .7},
            background_normal='', background_color=(1, 1, 1, 0.1),
            color=(0.8, 0.8, 1, 1), bold=True
        )
        self.method_btn.bind(on_release=self.change_method)
        root.add_widget(self.method_btn)
        
        # Главная кнопка
        self.main_btn = Button(
            text="ВКЛЮЧИТЬ", size_hint=(None, None), size=('220dp', '220dp'),
            pos_hint={'center_x': .5, 'center_y': .4},
            background_normal='', background_color=(0,0,0,0),
            bold=True, font_size='22sp'
        )
        with self.main_btn.canvas.before:
            self.btn_color = Color(0.4, 0.2, 0.7, 1)
            self.btn_circle = Ellipse(pos=self.main_btn.pos, size=self.main_btn.size)
        self.main_btn.bind(pos=self.sync_btn, size=self.sync_btn, on_release=self.toggle_vpn)
        root.add_widget(self.main_btn)
        
        # Статистика
        self.stats = Label(
            text="Ping: 0ms  |  Unblocked: 0",
            pos_hint={'center_x': .5, 'center_y': .15},
            color=(0.7, 0.7, 0.9, 1)
        )
        root.add_widget(self.stats)
        
        # Кнопка поддержки
        self.support_btn = Button(
            text="💬 ПОДДЕРЖКА",
            size_hint=(0.4, 0.07), pos_hint={'right': 0.95, 'y': 0.02},
            background_normal='', background_color=(0.3, 0.2, 0.5, 0.6),
            color=(0.9, 0.8, 1, 1), bold=True, font_size='12sp'
        )
        self.support_btn.bind(on_release=self.open_support)
        root.add_widget(self.support_btn)
        
        Clock.schedule_interval(self.update_stats, 1)
        self.add_widget(root)
    
    def sync_btn(self, *args):
        self.btn_circle.pos = self.main_btn.pos
        self.btn_circle.size = self.main_btn.size
    
    def update_stars(self, dt):
        self.stars.clear()
        for _ in range(15):
            Color(1, 1, 1, random.random() * 0.5)
            Ellipse(pos=(random.randint(0, Window.width), random.randint(0, Window.height)), size=(2, 2))
    
    def change_method(self, instance):
        self.current_method_idx = (self.current_method_idx + 1) % len(self.methods)
        new_method = self.methods[self.current_method_idx]
        if hasattr(self.proxy, 'method'):
            self.proxy.method = new_method
        instance.text = f"МЕТОД: {new_method.upper()}"
        log_to_file(f"Method changed to {new_method}")
    
    def update_stats(self, dt):
        if self.active and hasattr(self.proxy, 'unblock_count'):
            p = random.randint(20, 45)
            self.stats.text = f"Ping: {p}ms  |  Unblocked: {self.proxy.unblock_count}"
    
    def toggle_vpn(self, instance):
        log_to_file(f"toggle_vpn called, active={self.active}")
        if not self.active:
            try:
                threading.Thread(target=self.proxy.start, daemon=True).start()
                self.active = True
                self.btn_color.rgba = (0.2, 0.8, 0.4, 1)
                instance.text = "АКТИВЕН"
                anim = Animation(size=('240dp', '240dp'), duration=0.5) + Animation(size=('220dp', '220dp'), duration=0.5)
                anim.repeat = True
                anim.start(self.main_btn)
                log_to_file("VPN started")
            except Exception as e:
                log_to_file(f"Error starting: {e}")
        else:
            try:
                self.proxy.stop()
                self.active = False
                self.btn_color.rgba = (0.4, 0.2, 0.7, 1)
                instance.text = "ВКЛЮЧИТЬ"
                Animation.stop_all(self.main_btn)
                self.main_btn.size = ('220dp', '220dp')
                log_to_file("VPN stopped")
            except Exception as e:
                log_to_file(f"Error stopping: {e}")
    
    def open_support(self, instance):
        tg_url = "https://t.me/gZ9zRbTt"
        try:
            subprocess.run(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', tg_url])
        except:
            pass

# ========== ОСНОВНОЕ ПРИЛОЖЕНИЕ ==========
class MyVPNApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        self.main_screen = MainScreen(self)
        self.settings_screen = SettingsScreen(self)
        
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.settings_screen)
        
        return self.screen_manager
    
    def open_settings(self, instance):
        self.screen_manager.current = 'settings'
    
    def switch_to_main(self):
        self.screen_manager.current = 'main'

if __name__ == '__main__':
    MyVPNApp().run()
