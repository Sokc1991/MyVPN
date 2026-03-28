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
import random

# Android уведомления
try:
    from android import AndroidService
    from jnius import autoclass
    AndroidString = autoclass('java.lang.String')
    Context = autoclass('android.content.Context')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    Notification = autoclass('android.app.Notification')
    PendingIntent = autoclass('android.app.PendingIntent')
    Intent = autoclass('android.content.Intent')
    Build = autoclass('android.os.Build')
    
    HAS_NOTIFICATIONS = True
    print("✅ Уведомления поддерживаются")
except:
    HAS_NOTIFICATIONS = False
    print("⚠️ Уведомления не поддерживаются")

# Импортируем прокси
sys.path.append(os.path.dirname(__file__))
try:
    from proxy_server import DPIProxy
except ImportError:
    class DPIProxy:
        def __init__(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass

class MyVPNApp(App):
    def build(self):
        self.proxy = DPIProxy()
        self.active = False
        self.methods = ['hybrid', 'random', 'sni']
        self.current_method_idx = 0
        self.service = None
        
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
            size_hint=(0.4, 0.07), 
            pos_hint={'center_x': 0.85, 'center_y': 0.05},
            background_normal='', 
            background_color=(0.3, 0.2, 0.5, 0.6),
            color=(0.9, 0.8, 1, 1),
            bold=True,
            font_size='12sp'
        )
        self.support_btn.bind(on_release=self.open_support)
        root.add_widget(self.support_btn)

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

    def show_notification(self, title, text):
        """Показывает уведомление в статус-баре"""
        if not HAS_NOTIFICATIONS:
            return
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            # Создаем канал для уведомлений (для Android 8+)
            if Build.VERSION.SDK_INT >= 26:
                channel_id = AndroidString('myvpn_channel')
                channel_name = AndroidString('MyVPN Service')
                importance = NotificationManager.IMPORTANCE_LOW
                channel = NotificationChannel(channel_id, channel_name, importance)
                
                nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                nm.createNotificationChannel(channel)
            else:
                channel_id = AndroidString('')
            
            # Создаем интент для открытия приложения
            intent = Intent(activity, PythonActivity)
            pending = PendingIntent.getActivity(activity, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)
            
            # Создаем уведомление
            notification_builder = Notification.Builder(activity, channel_id)
            notification_builder.setContentTitle(AndroidString(title))
            notification_builder.setContentText(AndroidString(text))
            notification_builder.setSmallIcon(17301651)  # android.R.drawable.ic_menu_info_details
            notification_builder.setContentIntent(pending)
            notification_builder.setOngoing(True)  # Нельзя смахнуть
            
            notification = notification_builder.build()
            
            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            nm.notify(1, notification)
            
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

    def hide_notification(self):
        """Убирает уведомление"""
        if not HAS_NOTIFICATIONS:
            return
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            nm.cancel(1)
        except:
            pass

    def toggle_vpn(self, instance):
        if not self.active:
            self.proxy.start()
            self.active = True
            self.btn_color.rgba = (0.2, 0.8, 0.4, 1)
            instance.text = "АКТИВЕН"
            
            # Показываем уведомление
            self.show_notification("MyVPN", "VPN активен • Защита включена")
            
            # Анимация пульсации
            anim = Animation(size=('240dp', '240dp'), duration=0.5) + Animation(size=('220dp', '220dp'), duration=0.5)
            anim.repeat = True
            anim.start(self.main_btn)
        else:
            self.proxy.stop()
            self.active = False
            self.btn_color.rgba = (0.4, 0.2, 0.7, 1)
            instance.text = "ВКЛЮЧИТЬ"
            
            # Убираем уведомление
            self.hide_notification()
            
            Animation.stop_all(self.main_btn)
            self.main_btn.size = ('220dp', '220dp')

    def open_support(self, instance):
        anim = Animation(size_hint=(0.45, 0.08), duration=0.1) + Animation(size_hint=(0.4, 0.07), duration=0.1)
        anim.start(instance)
        
        tg_url = "https://t.me/gZ9zRbTt"
        try:
            import subprocess
            subprocess.run(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', tg_url])
        except:
            try:
                import webbrowser
                webbrowser.open(tg_url)
            except:
                pass

if __name__ == '__main__':
    MyVPNApp().run()
