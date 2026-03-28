from kivy.animation import Animation
#!/usr/bin/env python3

import json
import os
from kivy.utils import platform
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.clock import Clock, mainthread
from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
    MDDialogSupportingText,
)

__version__ = "1.0"

kv = Builder.load_string(
    """
<MainScreen>:
    md_bg_color: self.theme_cls.secondaryContainerColor

    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            type: "small"

            MDTopAppBarTitle:
                text: "NoDPI for Android"
                halign: "center"

            MDTopAppBarTrailingButtonContainer:

                MDActionTopAppBarButton:
                    icon: "shield"
                    on_release: root.show_about_dialog()  # Добавлен обработчик

        MDBoxLayout:
            orientation: "vertical"
            padding: "12dp"
            spacing: "12dp"

            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True
                pos_hint: {"center_x": .5, "center_y": .5}

                MDLabel:
                    text: 'Enjoy watching!'
                    font_style: "Headline"
                    halign: "center"
                    adaptive_size: True
                    bold: True

            MDCard:
                on_release: root.toggle_service(self)
                style: "outlined"
                padding: "4dp"
                size: "240dp", "100dp"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "10dp"
                    adaptive_height: True
                    pos_hint: {"center_x": .5, "center_y": .5}

                    MDLabel:
                        id: start_mlabel
                        text: 'START SERVER'
                        font_style: "Title"
                        halign: "center"
                        adaptive_size: True
                        color: "grey"
                        bold: True

                    MDLabel:
                        id: start_llabel
                        text: 'Now is not running'
                        halign: "center"
                        adaptive_size: True
                        color: "grey"
            MDCard:
                id: proxy_setup_card
                on_release: root.show_proxy_dialog()
                style: "outlined"
                padding: "4dp"
                size: "240dp", "100dp"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "10dp"
                    adaptive_height: True
                    pos_hint: {"center_x": .5, "center_y": .5}

                    MDLabel:
                        text: 'SETUP PROXY'
                        font_style: "Title"
                        halign: "center"
                        adaptive_size: True
                        color: "grey"
                        bold: True

                    MDLabel:
                        id: proxy_address_label
                        text: 'Now setup on 0.0.0.0:8881'
                        halign: "center"
                        adaptive_size: True
                        color: "grey"
            MDCard:
                id: blacklist_card
                on_release: app.switch_screen('blacklist')
                style: "outlined"
                padding: "4dp"
                size: "240dp", "100dp"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "10dp"
                    adaptive_height: True
                    pos_hint: {"center_x": .5, "center_y": .5}

                    MDLabel:
                        text: 'EDIT BLACKLIST'
                        font_style: "Title"
                        halign: "center"
                        adaptive_size: True
                        color: "grey"
                        bold: True

                    MDLabel:
                        id: blacklist_count_label
                        text: 'Now contains 0 domains'
                        halign: "center"
                        adaptive_size: True
                        color: "grey"

<ProxyDialogContent>:
    spacing: "12dp"

    MDTextField:
        id: host_input
        hint_text: "Host"

    MDTextField:
        id: port_input
        hint_text: "Port"
        input_filter: "int"

<BlacklistScreen>:

    name: "blacklist"
    md_bg_color: self.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            type: "small"
            elevation: 0

            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "close"
                    on_release: root.cancel_editing()

            MDTopAppBarTitle:
                text: "Edit Blacklist"
                halign: "center"

            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "check"
                    on_release: root.save_blacklist()

        ScrollView:
            MDTextField:
                id: blacklist_input
                mode: "filled"
                multiline: True
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(100))
                hint_text: "Enter domains (one per line)"
                helper_text: "Changes require server restart"
                helper_text_mode: "persistent"
                padding: "12dp"

"""
)


class ProxyDialogContent(MDDialogContentContainer):
    pass


class BlacklistScreen(MDScreen):
    BLACKLIST_PATH = os.path.join(MDApp().user_data_dir, "blacklist.txt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        """Loads the blacklist when the screen is entered"""

        self.load_blacklist()

    def load_blacklist(self):
        """Loads the blacklist from a file"""

        if os.path.exists(self.BLACKLIST_PATH):
            try:
                with open(self.BLACKLIST_PATH, "r", encoding="utf-8") as f:
                    self.ids.blacklist_input.text = f.read()
            except Exception as e:
                print(f"Error loading blacklist: {e}")
                self.ids.blacklist_input.text = ""
        else:
            self.ids.blacklist_input.text = ""

    def save_blacklist(self):
        """Saves the blacklist to a file"""

        text = self.ids.blacklist_input.text.strip()
        try:
            with open(self.BLACKLIST_PATH, "w", encoding="utf-8") as f:
                f.write(text)

            main_screen = self.app.root.get_screen("main")
            main_screen.blacklist_count = len(
                [line for line in text.splitlines() if line.strip()]
            )
            main_screen.update_blacklist_label()

            main_screen.show_restart_warning()

            self.app.switch_screen("main")
        except Exception as e:
            print(f"Error saving blacklist: {e}")

    def cancel_editing(self):
        """Cancels the editing and returns to the main screen"""

        self.app.switch_screen("main")


class MainScreen(MDScreen):
    PROXY_CONFIG_PATH = os.path.join(
        MDApp().user_data_dir, "proxy_config.json")
    BLACKLIST_PATH = os.path.join(MDApp().user_data_dir, "blacklist.txt")
    SETTINGS_PATH = os.path.join(MDApp().user_data_dir, "app_settings.json")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_dialog = None
        self.blacklist_dialog = None
        self.about_dialog = None
        self.disclaimer_dialog = None
        self.host = "0.0.0.0"
        self.port = "8881"
        self.blacklist_count = 0

        self.check_service_status()
        self.load_proxy_settings()
        self.load_blacklist()

    def on_enter(self, *args):
        self.check_first_run()

    def check_first_run(self):
        """Checks if this is the first run of the app"""

        settings = self.load_app_settings()

        if settings.get("first_run", True):
            Clock.schedule_once(self.show_disclaimer_dialog, 3)
            settings["first_run"] = False
            self.save_app_settings(settings)

    def load_app_settings(self):
        """Loads app settings"""

        if os.path.exists(self.SETTINGS_PATH):
            try:
                with open(self.SETTINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"first_run": True}
        return {"first_run": True}

    def save_app_settings(self, settings):
        """Saves app settings"""

        try:
            with open(self.SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving app settings: {e}")

    def load_blacklist(self):
        """Loads the blacklist from a file"""

        if os.path.exists(self.BLACKLIST_PATH):
            try:
                with open(self.BLACKLIST_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.blacklist_count = len(
                        [line for line in content.splitlines() if line.strip()]
                    )
            except Exception as e:
                self.blacklist_count = 0
        else:
            with open(self.BLACKLIST_PATH, "w", encoding="utf-8") as f:
                f.write(
                    """youtube.com
youtu.be
yt.be
googlevideo.com
ytimg.com
ggpht.com
gvt1.com
youtube-nocookie.com
youtube-ui.l.google.com
youtubeembeddedplayer.googleapis.com
youtube.googleapis.com
youtubei.googleapis.com
yt-video-upload.l.google.com
wide-youtube.l.google.com
"""
                )
                self.blacklist_count = 14
        self.update_blacklist_label()

    def update_blacklist_label(self):
        """Updates the blacklist label"""

        self.ids.blacklist_count_label.text = (
            f"Now contains {self.blacklist_count} domains"
        )

    def save_blacklist(self, content):
        """Saves the blacklist to a file"""

        text = content.ids.blacklist_input.text
        try:
            with open(self.BLACKLIST_PATH, "w", encoding="utf-8") as f:
                f.write(text)

            self.blacklist_count = len(
                [line for line in text.splitlines() if line.strip()]
            )
            self.update_blacklist_label()
        except Exception as e:
            print(f"Error saving blacklist: {e}")
        self.blacklist_dialog.dismiss()

    def load_proxy_settings(self):
        """Loads proxy settings from a file"""

        if os.path.exists(self.PROXY_CONFIG_PATH):
            try:
                with open(self.PROXY_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.host = config.get("host", "0.0.0.0")
                    self.port = str(config.get("port", "8881"))
                    self.update_proxy_label()
            except Exception as e:
                print(f"Error loading proxy config: {e}")

    def save_proxy_settings(self):
        """Saves proxy settings to a file"""

        try:
            with open(self.PROXY_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"host": self.host, "port": self.port}, f)
        except Exception as e:
            print(f"Error saving proxy config: {e}")

    def update_proxy_label(self):
        """Updates the proxy label"""

        self.ids.proxy_address_label.text = f"Now setup on {self.host}:{self.port}"

    def show_proxy_dialog(self):
        """Shows the proxy dialog"""

        if self.proxy_dialog:
            self.proxy_dialog.dismiss()

        content = ProxyDialogContent()
        content.ids.host_input.text = self.host
        content.ids.port_input.text = self.port

        self.proxy_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Edit Proxy",
            ),
            content,
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda _: self.proxy_dialog.dismiss(),
                ),
                MDButton(
                    MDButtonText(text="Accept"),
                    style="text",
                    on_release=lambda _: self.save_proxy_config(content),
                ),
                spacing="8dp",
            ),
        )
        self.proxy_dialog.open()

    def save_proxy_config(self, content):
        """Saves the proxy config"""

        self.host = content.ids.host_input.text.strip()
        self.port = content.ids.port_input.text.strip()

        self.save_proxy_settings()
        self.update_proxy_label()
        self.proxy_dialog.dismiss()
        self.show_restart_warning()

    def check_service_status(self):
        """Checks if the service is running"""

        if platform == "android":
            from lib.android.service import is_service_running

            if is_service_running("com.gvcoder.nodpi.ServiceProxy"):
                self.update_button_state("STOP SERVER", "Now is working")
            else:
                self.update_button_state("START SERVER", "Now is not running")
        else:
            self.update_button_state("START SERVER", "Now is not running")

    def toggle_service(self):
        """Toggles the service running state"""

        if self.ids.start_mlabel.text == "START SERVER":
            self.start_service()
        else:
            self.stop_service()

    def start_service(self):
        """Starts the service"""

        self.update_button_state("STOP SERVER", "Now is working")
        if platform == "android":
            from lib.android.service import start_service

            start_service("Proxy")

    def stop_service(self):
        """Stops the service"""

        self.update_button_state("START SERVER", "Now is not running")
        if platform == "android":
            from lib.android.service import stop_service

            stop_service("Proxy")

    @mainthread
    def update_button_state(self, text, subtext):
        """Updates the button state"""

        self.ids.start_mlabel.text = text
        self.ids.start_llabel.text = subtext

    def show_restart_warning(self):
        """Shows a warning message that the server needs to be restarted for changes to take effect"""

        MDSnackbar(
            MDSnackbarText(
                text="Server restart required to apply changes!",
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def show_about_dialog(self):
        """Shows the about dialog"""

        if self.about_dialog:
            self.about_dialog.dismiss()

        self.about_dialog = MDDialog(
            MDDialogHeadlineText(
                text="About NoDPI",
            ),
            MDDialogSupportingText(
                text=f"""
Version: {__version__}

NoDPI for Android - graphical add-on for the NoDPI utility. NoDPI is a utility for bypassing the DPI (Deep Packet Inspection) system, which allows blocking access to Internet resources. This utility allows you to bypass such blockings and freely use the Internet.
The utility works on the principle of HTTP proxy. It analyzes TCP-handshakes and fragments them, which allows you to deceive DPI. The utility does not collect or send any data.

This application is written in Python using graphical libraries Kivy and KivyMD and compiled using Python4Android and Buildozer.
""",
                halign="left",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    style="text",
                    on_release=lambda _: self.about_dialog.dismiss(),
                ),
            ),
        )
        self.about_dialog.open()

    def show_disclaimer_dialog(self, _):
        """Shows the disclaimer dialog"""

        if self.disclaimer_dialog:
            self.disclaimer_dialog.dismiss()

        self.disclaimer_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Disclaimer",
            ),
            MDDialogSupportingText(
                text="""
The developer and/or supplier of this software shall not be liable for any loss or damage, including but not limited to direct, indirect, incidental, punitive or consequential damages arising out of the use of or inability to use this software, even if the developer or supplier has been advised of the possibility of such damages.

The developer and/or supplier of this software shall not be liable for any legal consequences arising out of the use of this software. This includes, but is not limited to, violation of laws, rules or regulations, as well as any claims or suits arising out of the use of this software. The user is solely responsible for compliance with all applicable laws and regulations when using this software.
""",
                halign="left",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="I Understand"),
                    style="text",
                    on_release=lambda _: self.disclaimer_dialog.dismiss(),
                ),
            ),
        )
        print("open")
        self.disclaimer_dialog.open()


class ProxyApp(MDApp):

    def build(self):

        self.sm = MDScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(BlacklistScreen(name="blacklist"))

        return self.sm

    def switch_screen(self, screen_name):
        """Switches the screen"""

        self.sm.current = screen_name


if __name__ == "__main__":
    ProxyApp().run()
