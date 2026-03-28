import os
import sys
import threading
import time
import random
from datetime import datetime

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from proxy_server import DPIProxy

# Иконки (эмодзи как запасной вариант)
ICO_SHIELD = "🛡"
ICO_GEAR = "⚙"
ICO_WORLD = "🌍"
ICO_CHART = "📊"
ICO_SPEED = "⚡"
ICO_LOCK = "🔒"

# Ripple Button
class RippleButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0)
        self.ripple_pos = (0, 0)
        self.ripple_rad = 0
        self.ripple_alpha = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ripple_pos = touch.pos
            self.ripple_rad = 0
            self.ripple_alpha = 0.5
            with self.canvas.after:
                self.r_color = Color(1, 1, 1, self.ripple_alpha)
                self.r_ellipse = Ellipse(pos=(touch.x, touch.y), size=(0, 0))
            
            anim = Animation(ripple_rad=self.width * 2, ripple_alpha=0, duration=0.5)
            anim.bind(on_progress=self._upd_ripple)
            anim.start(self)
            return super().on_touch_down(touch)

    def _upd_ripple(self, anim, gen, prog):
        self.r_ellipse.size = (self.ripple_rad, self.ripple_rad)
        self.r_ellipse.pos = (self.ripple_pos[0] - self.ripple_rad/2, self.ripple_pos[1] - self.ripple_rad/2)
        self.r_color.a = self.ripple_alpha

# Glass Card
class GlassCard(BoxLayout):
    def __init__(self, name, flag, method, ping, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '85dp'
        self.padding = [15, 10]
        self.spacing = 15
        self.opacity = 0

        with self.canvas.before:
            Color(1, 1, 1, 0.05)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            Color(1, 1, 1, 0.1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 20), width=1.1)

        self.bind(pos=self._update, size=self._update)
        
        self.add_widget(Label(text=flag, font_size='32sp', size_hint_x=0.2))
        
        info = BoxLayout(orientation='vertical', spacing=2)
        info.add_widget(Label(text=f"[b]{name}[/b]", markup=True, halign='left', font_size='17sp'))
        info.add_widget(Label(text=f"{method} • [color=44ff44]{ping}[/color]", markup=True, font_size='12sp', color=(0.7,0.7,0.8,1)))
        self.add_widget(info)
        
        self.add_widget(Label(text="❯", size_hint_x=0.1, color=(0.4,0.4,0.5,1)))

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

# Main Screen
class MainDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.layout = RelativeLayout()
        
        # Градиент
        with self.canvas.before:
            for i in range(120):
                Color(0.04 + (i/2000), 0.02, 0.1 + (i/800), 1)
                Rectangle(pos=(0, i * (Window.height/120)), size=(Window.width, Window.height/120))
        
        # Header
        header = BoxLayout(size_hint=(1, 0.08), pos_hint={'top': 1}, padding=[20, 0])
        settings_btn = RippleButton(size_hint_x=0.15)
        settings_btn.bind(on_release=lambda x: setattr(self.app.sm, 'current', 'settings'))
        settings_btn.add_widget(Label(text=ICO_GEAR, font_size='26sp', center=settings_btn.center))
        
        header.add_widget(settings_btn)
        header.add_widget(Label(text="[b]MyVPN[/b]", markup=True, font_size='22sp'))
        header.add_widget(Label(text=ICO_WORLD, font_size='26sp', size_hint_x=0.15))
        self.layout.add_widget(header)

        # Power Button
        self.power_group = RelativeLayout(size_hint=(None, None), size=('260dp', '260dp'), 
                                          pos_hint={'center_x': 0.5, 'center_y': 0.72})
        
        with self.power_group.canvas:
            self.glow_color = Color(0.4, 0.3, 1, 0.1)
            self.glow = Ellipse(size=('260dp', '260dp'), pos=(0,0))
            Color(0.1, 0.07, 0.22, 1)
            Ellipse(size=('210dp', '210dp'), pos=('25dp', '25dp'))
            self.border_color = Color(0.5, 0.4, 1, 0.4)
            self.border = Line(ellipse=(25, 25, 210, 210), width=2)
            
        self.power_icon = Label(text=ICO_SHIELD, font_size='90sp', color=(0.5, 0.4, 1, 1))
        self.power_group.add_widget(self.power_icon)
        
        self.trigger = Button(size_hint=(None, None), size=('210dp', '210dp'), 
                              pos_hint={'center_x': 0.5, 'center_y': 0.5}, background_color=(0,0,0,0))
        self.trigger.bind(on_release=self.toggle_vpn)
        self.power_group.add_widget(self.trigger)
        self.layout.add_widget(self.power_group)

        # Stats Box
        self.stats_box = BoxLayout(orientation='vertical', size_hint=(0.92, 0.16), 
                                   pos_hint={'center_x': 0.5, 'y': 0.44}, padding=18, spacing=8)
        with self.stats_box.canvas.before:
            Color(1, 1, 1, 0.04)
            self.stats_bg = RoundedRectangle(radius=[22])
        self.stats_box.bind(pos=self._upd_s, size=self._upd_s)
        
        self.unblock_lbl = Label(text=f"{ICO_LOCK} UNBLOCKED: 0", bold=True, font_size='15sp')
        self.speed_lbl = Label(text=f"{ICO_SPEED} 0 KB/s ↓  •  0 KB/s ↑", font_size='13sp', color=(0.7,0.7,0.9,1))
        
        with self.stats_box.canvas:
            Color(0.2, 0.15, 0.4, 1)
            self.prog_bg = Line(points=[0,0,0,0], width=2)
            self.prog_color = Color(0.5, 0.4, 1, 1)
            self.prog_line = Line(points=[0,0,0,0], width=2.5)

        self.stats_box.add_widget(self.unblock_lbl)
        self.stats_box.add_widget(self.speed_lbl)
        self.layout.add_widget(self.stats_box)

        # Server List
        scroll = ScrollView(size_hint=(1, 0.42), pos_hint={'y': 0.01}, do_scroll_x=False, bar_width=0)
        self.list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12, padding=[15, 10])
        self.list.bind(minimum_height=self.list.setter('height'))
        
        servers = [
            ("Russia: Auto-Bypass", "🇷🇺", "Hybrid Mode", "15ms"),
            ("Germany: Premium", "🇩🇪", "Double Fragment", "42ms"),
            ("Netherlands: Ultra", "🇳🇱", "Fake Padding", "48ms"),
            ("USA: Streaming", "🇺🇸", "Random Delay", "110ms")
        ]
        
        for i, (n, f, m, p) in enumerate(servers):
            card = GlassCard(n, f, m, p)
            self.list.add_widget(card)
            Animation(opacity=1, duration=0.4 + (i*0.2)).start(card)
            
        scroll.add_widget(self.list)
        self.layout.add_widget(scroll)

        self.add_widget(self.layout)
        self.active = False
        Clock.schedule_interval(self.update_ui, 1)

    def _upd_s(self, ins, *args):
        self.stats_bg.pos, self.stats_bg.size = ins.pos, ins.size
        y = ins.y + 25
        self.prog_bg.points = [ins.x + 40, y, ins.right - 40, y]
        self.prog_line.points = [ins.x + 40, y, ins.x + 40 + (random.random() * (ins.width - 80)), y]

    def toggle_vpn(self, *args):
        self.active = not self.active
        if self.active:
            self.power_icon.color = (0.4, 1, 0.6, 1)
            self.glow_color.rgba = (0.2, 1, 0.4, 0.2)
            self.p_anim = Animation(size=('290dp', '290dp'), pos=('-15dp', '-15dp'), duration=1.2) + \
                          Animation(size=('260dp', '260dp'), pos=('0dp', '0dp'), duration=1.2)
            self.p_anim.repeat = True
            self.p_anim.start(self.glow)
            threading.Thread(target=self.app.proxy.start, daemon=True).start()
        else:
            Animation.stop_all(self.glow)
            self.power_icon.color = (0.5, 0.4, 1, 1)
            self.glow_color.rgba = (0.4, 0.3, 1, 0.1)
            self.app.proxy.stop()

    def update_ui(self, dt):
        s = self.app.proxy.stats
        self.unblock_lbl.text = f"{ICO_LOCK} UNBLOCKED: {s['unblocked']}"
        self.speed_lbl.text = f"{ICO_SPEED} {s['speed_down']//1024} KB/s ↓  •  {s['speed_up']//1024} KB/s ↑"
        s['speed_down'], s['speed_up'] = 0, 0

# Settings Screen
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        layout = RelativeLayout()
        
        with self.canvas.before:
            Color(0.04, 0.02, 0.08, 1)
            Rectangle(pos=(0,0), size=(Window.width, Window.height))
            
        box = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        back = RippleButton(text="← НАЗАД", size_hint=(None, None), size=('100dp', '50dp'), bold=True)
        back.bind(on_release=lambda x: setattr(self.app.sm, 'current', 'main'))
        box.add_widget(back)
        
        box.add_widget(Label(text="МЕТОД ОБХОДА", bold=True, size_hint_y=None, height='40dp', halign='left'))
        
        methods = ['AUTO (Smart)', 'DOUBLE FRAGMENT', 'RANDOM DELAY', 'FAKE PADDING', 'HYBRID']
        for m in methods:
            btn = RippleButton(text=m, size_hint_y=None, height='60dp')
            with btn.canvas.before:
                Color(1,1,1, 0.05)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[10])
            box.add_widget(btn)
            
        box.add_widget(Label(text="Провайдер: Определение...", color=(0.5,0.5,0.6,1)))
        layout.add_widget(box)
        self.add_widget(layout)

# App
class MyVPNApp(App):
    def build(self):
        self.proxy = DPIProxy()
        self.sm = ScreenManager(transition=FadeTransition(duration=0.4))
        self.sm.add_widget(MainDashboard(name='main'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        return self.sm

if __name__ == '__main__':
    MyVPNApp().run()
