"""
MyVPN - красивый VPN клиент с анимацией
Совместимость: Kivy 2.3.0, KivyMD 1.1.1
"""
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivy.core.window import Window

KV = '''
MDScreen:
    md_bg_color: [0.1, 0.02, 0.2, 1]

    MDBoxLayout:
        orientation: "vertical"
        spacing: "30dp"
        padding: "40dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        size_hint: (0.9, 0.8)

        MDLabel:
            text: "MyVPN"
            halign: "center"
            font_style: "H3"
            color: [0.75, 0.55, 1, 1]
            bold: True
            size_hint_y: 0.3

        MDRaisedButton:
            id: vpn_button
            text: "ВКЛЮЧИТЬ VPN"
            md_bg_color: [0.55, 0.25, 0.85, 1]
            size_hint: (0.8, 0.2)
            pos_hint: {"center_x": 0.5}
            font_size: "20sp"
            bold: True
            on_release: app.toggle_vpn()

        MDLabel:
            id: status_label
            text: "⛔ Не активен"
            halign: "center"
            font_size: "16sp"
            color: [0.9, 0.4, 0.4, 1]
            size_hint_y: 0.2

        MDLabel:
            text: "127.0.0.1:8881"
            halign: "center"
            font_size: "12sp"
            color: [0.6, 0.5, 0.7, 1]
            size_hint_y: 0.1
'''

class MyVPN(MDApp):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0f001a')
        self.screen = Builder.load_string(KV)
        return self.screen
    
    def toggle_vpn(self):
        button = self.screen.ids.vpn_button
        status = self.screen.ids.status_label
        
        # Анимация кнопки
        anim1 = Animation(size_hint=(0.85, 0.22), duration=0.08, t='out_quad')
        anim2 = Animation(size_hint=(0.8, 0.2), duration=0.12, t='in_quad')
        (anim1 + anim2).start(button)
        
        # Меняем состояние
        if "Не активен" in status.text:
            status.text = "✅ АКТИВЕН"
            status.color = [0.4, 0.9, 0.4, 1]
            button.md_bg_color = [0.7, 0.4, 1, 1]
            self.start_vpn()
        else:
            status.text = "⛔ Не активен"
            status.color = [0.9, 0.4, 0.4, 1]
            button.md_bg_color = [0.55, 0.25, 0.85, 1]
            self.stop_vpn()
    
    def start_vpn(self):
        print("VPN запущен")
        # TODO: добавить запуск твоего прокси
    
    def stop_vpn(self):
        print("VPN остановлен")
        # TODO: добавить остановку прокси

if __name__ == '__main__':
    MyVPN().run()
