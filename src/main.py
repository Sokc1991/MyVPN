"""
MyVPN - собственный VPN клиент
"""
import os
import sys
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.animation import Animation

KV = '''
MDScreen:
    md_bg_color: [0.08, 0.04, 0.16, 1]

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        size_hint: (0.9, 0.8)

        MDCard:
            id: start_card
            md_bg_color: [0.2, 0.12, 0.3, 1]
            size_hint: (0.8, 0.3)
            pos_hint: {"center_x": 0.5}
            on_release: app.start_server()

            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True

                MDLabel:
                    id: start_mlabel
                    text: 'ВКЛЮЧИТЬ VPN'
                    font_style: "Title"
                    halign: "center"
                    adaptive_size: True
                    color: [0.7, 0.5, 1, 1]
                    bold: True

                MDLabel:
                    id: start_llabel
                    text: '⛔ Не активен'
                    halign: "center"
                    adaptive_size: True
                    color: [0.8, 0.3, 0.3, 1]

        MDCard:
            id: proxy_setup_card
            style: "outlined"
            padding: "4dp"
            size: "240dp", "100dp"
            md_bg_color: [0.15, 0.1, 0.25, 1]
            pos_hint: {"center_x": 0.5}

            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True

                MDLabel:
                    text: 'НАСТРОЙКА ПРОКСИ'
                    font_style: "Title"
                    halign: "center"
                    adaptive_size: True
                    color: [0.7, 0.5, 1, 1]
                    bold: True

                MDLabel:
                    id: proxy_address_label
                    text: '127.0.0.1:8881'
                    halign: "center"
                    adaptive_size: True
                    color: [0.6, 0.6, 0.8, 1]

        MDCard:
            id: blacklist_card
            style: "outlined"
            padding: "4dp"
            size: "240dp", "80dp"
            md_bg_color: [0.15, 0.1, 0.25, 1]
            pos_hint: {"center_x": 0.5}

            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True

                MDLabel:
                    text: 'BLACKLIST'
                    font_style: "Title"
                    halign: "center"
                    adaptive_size: True
                    color: [0.7, 0.5, 1, 1]
                    bold: True

                MDLabel:
                    text: '151 домен'
                    halign: "center"
                    adaptive_size: True
                    color: [0.6, 0.6, 0.8, 1]
'''

class MainScreen(Screen):
    pass

class MyVPNApp(MDApp):
    def build(self):
        self.screen = Builder.load_string(KV)
        return self.screen
    
    def start_server(self):
        card = self.root.ids.get('start_card')
        if card:
            anim = Animation(size_hint=(0.85, 0.85), duration=0.08)
            anim += Animation(size_hint=(0.8, 0.8), duration=0.08)
            anim.start(card)
        
        label = self.root.ids.get('start_llabel')
        if label:
            if label.text == '⛔ Не активен':
                label.text = '✅ АКТИВЕН'
                label.color = [0.3, 0.8, 0.3, 1]
                if card:
                    card.md_bg_color = [0.3, 0.2, 0.45, 1]
            else:
                label.text = '⛔ Не активен'
                label.color = [0.8, 0.3, 0.3, 1]
                if card:
                    card.md_bg_color = [0.2, 0.12, 0.3, 1]

if __name__ == '__main__':
    MyVPNApp().run()
