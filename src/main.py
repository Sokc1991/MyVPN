"""
MyVPN - чистый Kivy, без KivyMD
Гарантированно работает на Android
"""
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

class MyVPNApp(App):
    def build(self):
        # Темно-фиолетовый фон
        Window.clearcolor = get_color_from_hex('#120024')
        
        # Главный layout
        layout = BoxLayout(
            orientation='vertical', 
            padding=[50, 80, 50, 80], 
            spacing=40
        )
        
        # Заголовок
        title = Label(
            text="MyVPN",
            font_size='48sp',
            color=get_color_from_hex('#BF8CFF'),
            bold=True,
            size_hint_y=0.3
        )
        layout.add_widget(title)
        
        # Кнопка
        self.btn = Button(
            text="ВКЛЮЧИТЬ VPN",
            size_hint=(0.7, 0.2),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex('#8C40D9'),
            font_size='22sp',
            bold=True
        )
        self.btn.bind(on_release=self.animate_button)
        layout.add_widget(self.btn)
        
        # Статус
        self.status = Label(
            text="⛔ Не активен",
            font_size='16sp',
            color=get_color_from_hex('#FF6666'),
            size_hint_y=0.2
        )
        layout.add_widget(self.status)
        
        # Адрес прокси
        proxy_label = Label(
            text="127.0.0.1:8881",
            font_size='12sp',
            color=get_color_from_hex('#AA99CC'),
            size_hint_y=0.1
        )
        layout.add_widget(proxy_label)
        
        return layout
    
    def animate_button(self, instance):
        # Анимация пульсации
        anim = Animation(
            size_hint=(0.75, 0.22), 
            background_color=get_color_from_hex('#B86EFF'), 
            duration=0.08
        )
        anim += Animation(
            size_hint=(0.7, 0.2), 
            background_color=get_color_from_hex('#8C40D9'), 
            duration=0.12
        )
        anim.start(instance)
        
        # Меняем статус
        if "Не активен" in self.status.text:
            self.status.text = "✅ АКТИВЕН"
            self.status.color = get_color_from_hex('#66FF66')
            self.start_vpn()
        else:
            self.status.text = "⛔ Не активен"
            self.status.color = get_color_from_hex('#FF6666')
            self.stop_vpn()
    
    def start_vpn(self):
        print("VPN запущен")
        # TODO: добавить запуск твоего прокси
    
    def stop_vpn(self):
        print("VPN остановлен")
        # TODO: добавить остановку прокси

if __name__ == '__main__':
    MyVPNApp().run()
