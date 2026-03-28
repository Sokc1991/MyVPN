"""
MyVPN - красивый интерфейс как FastCon
С карточками, анимациями и плавными эффектами
"""
import sys
import os
import random
import threading
import subprocess
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty

# Пробуем импортировать KivyMD для карточек
try:
    from kivymd.app import MDApp
    from kivymd.uix.card import MDCard
    from kivymd.uix.button import MDRaisedButton
    from kivymd.uix.label import MDLabel
    from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
    HAS_KIVYMD = True
    print("✅ KivyMD загружен")
except:
    HAS_KIVYMD = False
    print("⚠️ KivyMD не найден, используем стандартные виджеты")
    # Заглушки
    class MDCard(BoxLayout): pass
    class MDRaisedButton(Button): pass
    class MDLabel(Label): pass

try:
    from proxy_server import DPIProxy
except:
    class DPIProxy:
        def __init__(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass

LOG_FILE = '/storage/emulated/0/myvpn_error.txt'

def log(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
    except:
        pass

# Кастомная карточка сервера с анимацией
class ServerCard(BoxLayout):
    def __init__(self, server_name, server_flag, server_type, server_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '80dp'
        self.size_hint_x = 0.94
        self.pos_hint = {'center_x': 0.5}
        self.spacing = 10
        self.padding = [10, 5]
        
        # Фон карточки с закруглением
        with self.canvas.before:
            Color(0.2, 0.12, 0.3, 0.85)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Флаг (эмодзи)
        flag = Label(
            text=server_flag,
            font_size='36sp',
            size_hint=(0.15, 1),
            color=(0.9, 0.8, 1, 1)
        )
        self.add_widget(flag)
        
        # Название сервера
        name_box = BoxLayout(orientation='vertical', size_hint=(0.55, 1), spacing=2)
        name_label = Label(
            text=f"[b]{server_name}[/b]",
            markup=True,
            font_size='16sp',
            color=(1, 1, 1, 1),
            halign='left',
            size_hint_y=0.6
        )
        name_label.bind(size=name_label.setter('text_size'))
        type_label = Label(
            text=server_type,
            font_size='11sp',
            color=(0.7, 0.6, 0.9, 1),
            halign='left',
            size_hint_y=0.4
        )
        type_label.bind(size=type_label.setter('text_size'))
        name_box.add_widget(name_label)
        name_box.add_widget(type_label)
        self.add_widget(name_box)
        
        # Кнопка подключения
        self.connect_btn = Button(
            text="ПОДКЛЮЧИТЬ",
            size_hint=(0.22, 0.6),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=server_color,
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        self.connect_btn.bind(on_release=self.animate_and_connect)
        self.add_widget(self.connect_btn)
        
        self.server_name = server_name
        self.server_color = server_color
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def animate_and_connect(self, instance):
        # Анимация кнопки
        anim1 = Animation(size_hint=(0.24, 0.65), duration=0.08)
        anim2 = Animation(size_hint=(0.22, 0.6), duration=0.08)
        anim = anim1 + anim2
        anim.start(instance)
        
        # Анимация всей карточки
        card_anim = Animation(size_hint_x=0.96, duration=0.05) + Animation(size_hint_x=0.94, duration=0.05)
        card_anim.start(self)
        
        log(f"Подключение к {self.server_name}")
        # Здесь будет вызов VPN

# Главный экран
class MainScreen(RelativeLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        # Фон градиент
        with self.canvas.before:
            for i in range(100):
                Color(0.08, 0.04, 0.12 + (i/500), 1)
                Rectangle(pos=(0, i * (Window.height/100)), size=(Window.width, Window.height/100))
        
        # Статус бар сверху
        status_bar = BoxLayout(
            size_hint=(1, 0.08),
            pos_hint={'top': 1},
            padding=[15, 5],
            spacing=10
        )
        
        # Статус подключения
        self.status_indicator = Label(
            text="●",
            font_size='20sp',
            color=(0.8, 0.3, 0.3, 1),
            size_hint=(0.1, 1)
        )
        self.status_text = Label(
            text="Не подключен",
            font_size='14sp',
            color=(0.8, 0.7, 0.9, 1),
            size_hint=(0.6, 1),
            halign='left'
        )
        self.status_text.bind(size=self.status_text.setter('text_size'))
        
        # Шестеренка настроек
        settings_btn = Button(
            text="⚙️",
            font_size='22sp',
            size_hint=(0.1, 1),
            background_normal='', background_color=(0,0,0,0),
            color=(0.9, 0.8, 1, 1)
        )
        settings_btn.bind(on_release=self.app.open_settings)
        
        status_bar.add_widget(self.status_indicator)
        status_bar.add_widget(self.status_text)
        status_bar.add_widget(settings_btn)
        self.add_widget(status_bar)
        
        # Заголовок
        title = Label(
            text="[b]MyVPN[/b]",
            markup=True,
            font_size='44sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.88},
            color=get_color_from_hex('#D4AAFF')
        )
        self.add_widget(title)
        
        # Скролл с серверами
        scroll = ScrollView(
            size_hint=(1, 0.55),
            pos_hint={'center_y': 0.45},
            do_scroll_x=False
        )
        
        servers_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=12,
            padding=[10, 10]
        )
        servers_list.bind(minimum_height=servers_list.setter('height'))
        
        # Сервера как в FastCon
        servers = [
            ("🇷🇺 РФ: Все операторы", "Авто (Hybrid)", (0.4, 0.25, 0.7, 1)),
            ("🇩🇪 Германия-Авто", "Wi-Fi / Mobile", (0.35, 0.2, 0.6, 1)),
            ("🌍 Все операторы-2", "VLESS | JSON", (0.3, 0.18, 0.55, 1)),
            ("🌍 Все операторы-3", "VLESS | JSON", (0.3, 0.18, 0.55, 1)),
            ("🌍 Все операторы-4", "VLESS | JSON", (0.3, 0.18, 0.55, 1)),
            ("🌍 Все операторы-5", "VLESS | JSON", (0.3, 0.18, 0.55, 1)),
            ("🌍 Все операторы-6", "VLESS | JSON", (0.3, 0.18, 0.55, 1)),
        ]
        
        for name, stype, color in servers:
            card = ServerCard(name, name[0], stype, color)
            servers_list.add_widget(card)
        
        scroll.add_widget(servers_list)
        self.add_widget(scroll)
        
        # Карточка статистики
        stats_card = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            padding=[15, 8],
            spacing=5
        )
        with stats_card.canvas.before:
            Color(0.15, 0.1, 0.25, 0.7)
            self.stats_bg = RoundedRectangle(pos=stats_card.pos, size=stats_card.size, radius=[15])
        stats_card.bind(pos=self._update_stats_bg, size=self._update_stats_bg)
        
        self.traffic_label = Label(
            text="📊 0.0 GB / 0.0 GB",
            font_size='12sp',
            color=(0.8, 0.7, 0.9, 1),
            size_hint_y=0.5,
            halign='center'
        )
        self.traffic_label.bind(size=self.traffic_label.setter('text_size'))
        
        self.expiry_label = Label(
            text="📅 Активен до: —",
            font_size='11sp',
            color=(0.7, 0.6, 0.8, 1),
            size_hint_y=0.5,
            halign='center'
        )
        self.expiry_label.bind(size=self.expiry_label.setter('text_size'))
        
        stats_card.add_widget(self.traffic_label)
        stats_card.add_widget(self.expiry_label)
        self.add_widget(stats_card)
        
        self.stats_card = stats_card
        
        # Обновление статистики
        Clock.schedule_interval(self.update_stats, 1)
    
    def _update_stats_bg(self, *args):
        self.stats_bg.pos = self.stats_card.pos
        self.stats_bg.size = self.stats_card.size
    
    def update_stats(self, dt):
        # Обновляем статистику (заглушка, потом реальные данные)
        pass

# Экран настроек
class SettingsScreen(RelativeLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        # Фон
        with self.canvas.before:
            Color(0.08, 0.04, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)
        
        # Кнопка назад
        back_btn = Button(
            text="←",
            font_size='28sp',
            size_hint=(0.12, 0.07),
            pos_hint={'x': 0.02, 'top': 0.95},
            background_normal='', background_color=(0,0,0,0),
            color=(0.9, 0.8, 1, 1)
        )
        back_btn.bind(on_release=self.go_back)
        self.add_widget(back_btn)
        
        # Заголовок
        title = Label(
            text="⚙️ НАСТРОЙКИ",
            font_size='22sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.9},
            color=(0.9, 0.8, 1, 1),
            bold=True
        )
        self.add_widget(title)
        
        # Список настроек
        settings_list = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            spacing=12
        )
        
        # Кнопки настроек
        items = [
            ("📋 ПОКАЗАТЬ ЛОГИ", self.show_logs),
            ("📤 ОТПРАВИТЬ ЛОГИ", self.send_logs),
            ("🗑️ ОЧИСТИТЬ ЛОГИ", self.clear_logs),
            ("🔄 МЕТОД ОБХОДА: HYBRID", self.change_method),
            ("❓ О ПРИЛОЖЕНИИ", self.show_about),
        ]
        
        for text, func in items:
            btn = Button(
                text=text,
                size_hint=(1, 0.12),
                background_normal='',
                background_color=(0.2, 0.12, 0.3, 0.9),
                color=(0.9, 0.8, 1, 1),
                font_size='14sp',
                bold=True
            )
            btn.bind(on_release=func)
            settings_list.add_widget(btn)
        
        self.add_widget(settings_list)
        
        self.method_index = 0
        self.methods = ['HYBRID', 'RANDOM', 'SNI']
    
    def go_back(self, instance):
        self.app.switch_to_main()
    
    def show_logs(self, instance):
        try:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
        except:
            logs = "Логов пока нет"
        
        from kivy.uix.popup import Popup
        from kivy.uix.scrollview import ScrollView
        
        content = BoxLayout(orientation='vertical', size_hint_y=None)
        content.height = 400
        
        scroll = ScrollView()
        log_label = Label(
            text=logs,
            size_hint_y=None,
            font_size='10sp',
            color=(0.8, 0.8, 1, 1),
            halign='left',
            valign='top'
        )
        log_label.bind(size=log_label.setter('text_size'))
        log_label.text_size = (Window.width - 100, None)
        log_label.height = max(200, len(logs.split('\n')) * 20)
        scroll.add_widget(log_label)
        content.add_widget(scroll)
        
        close_btn = Button(text="ЗАКРЫТЬ", size_hint_y=0.15, background_color=(0.4, 0.2, 0.7, 1))
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
        
        from kivy.uix.popup import Popup
        from kivy.core.clipboard import Clipboard
        
        Clipboard.copy(logs)
        
        popup = Popup(
            title="📤 ЛОГИ СКОПИРОВАНЫ",
            content=Label(text="Логи скопированы в буфер.\nОтправь @gZ9zRbTt"),
            size_hint=(0.7, 0.3)
        )
        popup.open()
    
    def clear_logs(self, instance):
        try:
            with open(LOG_FILE, 'w') as f:
                f.write("=== Логи очищены ===\n")
        except:
            pass
        
        from kivy.uix.popup import Popup
        popup = Popup(
            title="✅ ГОТОВО",
            content=Label(text="Логи очищены"),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def change_method(self, instance):
        self.method_index = (self.method_index + 1) % len(self.methods)
        instance.text = f"🔄 МЕТОД ОБХОДА: {self.methods[self.method_index]}"
        
        if hasattr(self.app, 'proxy') and hasattr(self.app.proxy, 'method'):
            self.app.proxy.method = self.methods[self.method_index].lower()
        log(f"Метод изменен на {self.methods[self.method_index]}")
    
    def show_about(self, instance):
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        content.add_widget(Label(
            text="MyVPN v1.0\n\nОбход блокировок DPI\nМетоды: hybrid/random/sni\n\nАвтор: @gZ9zRbTt",
            halign='center',
            color=(0.9, 0.8, 1, 1)
        ))
        close_btn = Button(text="ЗАКРЫТЬ", size_hint_y=0.3, background_color=(0.4, 0.2, 0.7, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title="❓ О ПРИЛОЖЕНИИ", content=content, size_hint=(0.8, 0.5))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

# Основное приложение
class MyVPNApp(App):
    def build(self):
        self.proxy = DPIProxy()
        
        self.main_screen = MainScreen(self)
        self.settings_screen = SettingsScreen(self)
        
        self.root = RelativeLayout()
        self.root.add_widget(self.main_screen)
        self.root.add_widget(self.settings_screen)
        
        self.settings_screen.opacity = 0
        self.current_screen = 'main'
        
        return self.root
    
    def open_settings(self, instance):
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *args: self._show_settings())
        anim.start(self.main_screen)
    
    def _show_settings(self):
        self.main_screen.opacity = 0
        self.settings_screen.opacity = 1
        self.current_screen = 'settings'
    
    def switch_to_main(self):
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *args: self._show_main())
        anim.start(self.settings_screen)
    
    def _show_main(self):
        self.settings_screen.opacity = 0
        self.main_screen.opacity = 1
        self.current_screen = 'main'

if __name__ == '__main__':
    MyVPNApp().run()
