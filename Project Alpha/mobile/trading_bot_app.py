"""
Trading Bot Mobile App - Kivy Implementation
Full-featured mobile UI with Market Scanner
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbed_panel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
import requests
import logging

logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/api"

class TradingBotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = API_URL
        self.is_connected = False
        self.selected_symbols = []
        self.all_symbols = []

    def build(self):
        self.title = "Trading Bot Pro"
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.tabs = TabbedPanel(do_default_tab=False)

        # Dashboard
        dash_tab = TabbedPanelItem(text='Dashboard')
        dash_tab.content = self.build_dashboard()
        self.tabs.add_widget(dash_tab)
        
        # Scanner (New)
        scanner_tab = TabbedPanelItem(text='Scanner')
        scanner_tab.content = self.build_scanner()
        self.tabs.add_widget(scanner_tab)
        
        # Trading
        trade_tab = TabbedPanelItem(text='Trading')
        trade_tab.content = self.build_trading()
        self.tabs.add_widget(trade_tab)
        
        # Settings
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.content = self.build_settings()
        self.tabs.add_widget(settings_tab)
        
        main_layout.add_widget(self.tabs)
        
        self.status_label = Label(text="Checking connection...", size_hint_y=0.1, markup=True)
        main_layout.add_widget(self.status_label)

        Clock.schedule_interval(self.update_status, 5)
        Clock.schedule_interval(self.fetch_signals, 10)

        return main_layout

    def build_dashboard(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Account Summary", font_size='20sp', bold=True))
        self.balance_label = Label(text="Balance: $0.00", font_size='24sp')
        layout.add_widget(self.balance_label)
        self.active_broker_label = Label(text="Broker: None")
        layout.add_widget(self.active_broker_label)
        return layout

    def build_scanner(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Controls
        ctrls = BoxLayout(size_hint_y=None, height=50, spacing=10)
        ctrls.add_widget(Button(text="Select Pairs", on_press=self.show_pair_selector))
        ctrls.add_widget(Button(text="Refresh Signals", on_press=self.fetch_signals))
        layout.add_widget(ctrls)
        
        layout.add_widget(Label(text="Live Signals", bold=True, size_hint_y=None, height=30))
        
        scroll = ScrollView()
        self.signals_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.signals_layout.bind(minimum_height=self.signals_layout.setter('height'))
        scroll.add_widget(self.signals_layout)
        layout.add_widget(scroll)

        return layout

    def show_pair_selector(self, instance):
        if not self.is_connected:
            self.show_popup("Error", "Connect to a broker first to load symbols.")
            return

        try:
            res = requests.get(f"{self.api_url}/market/symbols", timeout=5)
            self.all_symbols = res.json()
        except:
            self.show_popup("Error", "Failed to fetch symbols from backend.")
            return

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView()
        list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        checkboxes = {}
        for symbol in sorted(self.all_symbols)[:50]: # Limit to 50 for UI performance
            row = BoxLayout(size_hint_y=None, height=40)
            cb = CheckBox(active=(symbol in self.selected_symbols), size_hint_x=0.2)
            row.add_widget(cb)
            row.add_widget(Label(text=symbol, size_hint_x=0.8, halign='left'))
            list_layout.add_widget(row)
            checkboxes[symbol] = cb

        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        
        save_btn = Button(text="Save Selection", size_hint_y=None, height=50)
        content.add_widget(save_btn)
        
        popup = Popup(title="Select Pairs to Scan", content=content, size_hint=(0.9, 0.9))

        def save(inst):
            self.selected_symbols = [s for s, cb in checkboxes.items() if cb.active]
            requests.post(f"{self.api_url}/scanner/configure", json={"symbols": self.selected_symbols})
            popup.dismiss()
            self.fetch_signals(None)

        save_btn.bind(on_press=save)
        popup.open()

    def fetch_signals(self, dt=None):
        if not self.is_connected: return
        try:
            res = requests.get(f"{self.api_url}/scanner/signals", timeout=5)
            signals = res.json()
            self.signals_layout.clear_widgets()
            if not signals:
                self.signals_layout.add_widget(Label(text="No signals found. Scanning...", size_hint_y=None, height=40))
            for sig in signals:
                color = "00ff00" if sig['type'] == "BUY" else "ff0000"
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=5)
                box.add_widget(Label(text=f"[b]{sig['symbol']}[/b] - [color={color}]{sig['type']}[/color]", markup=True))
                box.add_widget(Label(text=sig['reason'], font_size='12sp'))
                self.signals_layout.add_widget(box)
        except: pass

    def build_trading(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        form = GridLayout(cols=2, spacing=10, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        form.add_widget(Label(text="Symbol:"))
        self.symbol_input = TextInput(text="EURUSD", multiline=False)
        form.add_widget(self.symbol_input)
        
        form.add_widget(Label(text="Stake/Lot:"))
        self.stake_input = TextInput(text="0.1", multiline=False)
        form.add_widget(self.stake_input)
        
        layout.add_widget(form)
        
        btn_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        btn_box.add_widget(Button(text="BUY", background_color=(0,1,0,1), on_press=lambda x: self.place_order("BUY")))
        btn_box.add_widget(Button(text="SELL", background_color=(1,0,0,1), on_press=lambda x: self.place_order("SELL")))
        layout.add_widget(btn_box)
        
        return layout

    def build_settings(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=10, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        form.add_widget(Label(text="Broker Type:"))
        self.broker_spinner = Spinner(text='exness', values=('deriv', 'exness', 'xm', 'mt5'))
        form.add_widget(self.broker_spinner)
        
        form.add_widget(Label(text="MT5 Login / Token:"))
        self.login_input = TextInput(multiline=False)
        form.add_widget(self.login_input)
        
        form.add_widget(Label(text="Password:"))
        self.pass_input = TextInput(password=True, multiline=False)
        form.add_widget(self.pass_input)
        
        form.add_widget(Label(text="Server:"))
        self.server_input = TextInput(text="Exness-MT5-Real", multiline=False)
        form.add_widget(self.server_input)
        
        scroll.add_widget(form)
        layout.add_widget(scroll)
        
        layout.add_widget(Button(text="Connect", size_hint_y=None, height=50, on_press=self.connect_broker))
        return layout

    def connect_broker(self, instance):
        b_type = self.broker_spinner.text
        config = {
            "primary_broker": b_type,
            "deriv_token": self.login_input.text if b_type == 'deriv' else None,
            "mt5_login": int(self.login_input.text) if b_type != 'deriv' else None,
            "mt5_password": self.pass_input.text,
            "mt5_server": self.server_input.text
        }
        try:
            res = requests.post(f"{self.api_url}/broker/configure", json=config, timeout=15)
            if res.status_code == 200:
                self.show_popup("Success", "Connected!")
                self.update_status()
            else:
                self.show_popup("Error", res.json().get('detail', 'Failed'))
        except Exception as e:
            self.show_popup("Error", str(e))

    def place_order(self, direction):
        if not self.is_connected: return
        data = {
            "symbol": self.symbol_input.text,
            "direction": direction,
            "entry_price": 0, "stake": float(self.stake_input.text),
            "stop_loss": 0, "take_profit": 0
        }
        try:
            res = requests.post(f"{self.api_url}/orders/place", json=data)
            self.show_popup("Order", res.json().get('message'))
        except Exception as e:
            self.show_popup("Error", str(e))

    def update_status(self, dt=None):
        try:
            res = requests.get(f"{self.api_url}/broker/status", timeout=3)
            status = res.json()
            self.is_connected = status.get('connected', False)
            if self.is_connected:
                self.status_label.text = f"[color=00ff00]Connected: {status.get('active_broker')}[/color]"
                self.active_broker_label.text = f"Broker: {status.get('active_broker')}"
                self.balance_label.text = f"Balance: ${status.get('balance', 0):,.2f}"
            else:
                self.status_label.text = "[color=ff0000]Not Connected[/color]"
        except:
            self.status_label.text = "[color=ff0000]Backend Offline[/color]"

    def show_popup(self, title, msg):
        p = Popup(title=title, content=Label(text=msg), size_hint=(0.8, 0.4))
        p.open()

if __name__ == '__main__':
    TradingBotApp().run()
