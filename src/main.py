"""
MyVPN - простой VPN клиент
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.animation import Animation

KV = '''
MDScreen:
    md_bg_color: [0.08, 0.04, 0.16, 1]

    MDBoxLayout:
        orientation: "vertical"
        padding: "30dp"
        spacing: "30dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        size_hint: (0.9, 0.7)

        MDLabel:
            text: "MyVPN"
            halign: "center"
            font_style: "H3"
            color: [0.7, 0.5, 1, 1]
            bold: True

        MDRaisedButton:
            id: vpn_button
            text: "ВКЛЮЧИТЬ VPN"
            md_bg_color: [0.3, 0.2, 0.5, 1]
            size_hint: (0.7, 0.15)
            pos_hint: {"center_x": 0.5}
            font_size: "18sp"
            on_release: app.start_vpn()

        MDLabel:
            id: status_label
            text: "⛔ Не активен"
            halign: "center"
            font_size: "16sp"
            color: [0.8, 0.3, 0.3, 1]
'''

class MyVPN(MDApp):
    def build(self):
        self.screen = Builder.load_string(KV)
        return self.screen
    
    def start_vpn(self):
        button = self.screen.ids.vpn_button
        status = self.screen.ids.status_label
        
        # Анимация
        anim = Animation(size_hint=(0.72, 0.17), duration=0.08)
        anim += Animation(size_hint=(0.7, 0.15), duration=0.08)
        anim.start(button)
        
        # Меняем статус
        if status.text == "⛔ Не активен":
            status.text = "✅ АКТИВЕН"
            status.color = [0.3, 0.8, 0.3, 1]
            button.md_bg_color = [0.4, 0.3, 0.6, 1]
        else:
            status.text = "⛔ Не активен"
            status.color = [0.8, 0.3, 0.3, 1]
            button.md_bg_color = [0.3, 0.2, 0.5, 1]

if __name__ == '__main__':
    MyVPN().run()
