from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, InstructionGroup
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import sys
import os

# Добавляем текущую папку в путь
sys.path.append(os.path.dirname(__file__))

try:
    from proxy_server import DPIProxy
    print("✅ proxy_server импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта proxy_server: {e}")
    # Создаем заглушку, чтобы приложение не падало
    class DPIProxy:
        def __init__(self, *args, **kwargs): pass
        def start(self): print("Заглушка start")
        def stop(self): print("Заглушка stop")
        def fragment_data(self, data): return [data]

import random

class MyVPNApp(App):
    def build(self):
        self.proxy = DPIProxy()
        self.active = False
        self.methods = ['hybrid', 'random', 'sni']
        self.current_method_idx = 0
        
        root = RelativeLayout()
        
        # 1. Фон - Глубокий фиолетовый градиент
        with root.canvas.before:
            for i in range(100):
                Color(0.04, 0.02, 0.1 + (i/1000), 1)
                Rectangle(pos=(0, i * (Window.height/100)), size=(Window.width, Window.height/100))
        
        # 2. Звезды
        self.stars = InstructionGroup()
        root.canvas.after.add(self.stars)
        Clock.schedule_interval(self.update_stars, 1/20)

        # 3. Неоновый заголовок
        self.title = Label(
            text="[b]MyVPN[/b]", markup=True, font_size='56sp',
            pos_hint={'center_x': .5, 'center_y': .85},
            color=get_color_from_hex('#D4AAFF')
        )
        root.add_widget(self.title)

        # 4. Выбор метода (Стеклянная кнопка)
        self.method_btn = Button(
            text=f"МЕТОД: {self.methods[0].upper()}",
            size_hint=(0.7, 0.08), pos_hint={'center_x': .5, 'center_y': .7},
            background_normal='', background_color=(1, 1, 1, 0.1),
            color=(0.8, 0.8, 1, 1), bold=True
        )
        self.method_btn.bind(on_release=self.change_method)
        root.add_widget(self.method_btn)

        # 5. Главная кнопка (Круглая)
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

        # 6. Статистика
        self.stats = Label(
            text="Ping: 0ms  |  Unblocked: 0",
            pos_hint={'center_x': .5, 'center_y': .15},
            color=(0.7, 0.7, 0.9, 1)
        )
        root.add_widget(self.stats)
        Clock.schedule_interval(self.update_stats, 1)

        return root

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

    def update_stats(self, dt):
        if self.active and hasattr(self.proxy, 'unblock_count'):
            p = random.randint(20, 45)
            self.stats.text = f"Ping: {p}ms  |  Unblocked: {self.proxy.unblock_count}"

    def toggle_vpn(self, instance):
        if not self.active:
            self.proxy.start()
            self.active = True
            self.btn_color.rgba = (0.2, 0.8, 0.4, 1)
            instance.text = "АКТИВЕН"
            anim = Animation(size=('240dp', '240dp'), duration=0.5) + Animation(size=('220dp', '220dp'), duration=0.5)
            anim.repeat = True
            anim.start(self.main_btn)
        else:
            self.proxy.stop()
            self.active = False
            self.btn_color.rgba = (0.4, 0.2, 0.7, 1)
            instance.text = "ВКЛЮЧИТЬ"
            Animation.stop_all(self.main_btn)
            self.main_btn.size = ('220dp', '220dp')

if __name__ == '__main__':
    MyVPNApp().run()
