import datetime
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock

# --- BAZA MANZILI ---
DB_URL = "https://davomat-fcdac-default-rtdb.firebaseio.com/" 
ALLOWED_USERS = {"Admin": "0", "Asadbek": "1", "Ali": "2", "Vali": "3"}
HAFTA_KUNLARI = {0: "Dushanba", 1: "Seshanba", 2: "Chorshanba", 3: "Payshanba", 4: "Juma", 5: "Shanba", 6: "Yakshanba"}

class SmoothButton(Button):
    """Yumaloq ko'k tugma"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(0, 0.5, 0.9, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[30,])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size

class DavomatApp(App):
    def build(self):
        self.user = ""; self.id_num = ""
        self.root = AnchorLayout(anchor_x='center', anchor_y='top')
        with self.root.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            Rectangle(size=(2000, 4000), pos=(0,0))
        self.login_view()
        return self.root

    def login_view(self, *args):
        self.root.clear_widgets()
        box = BoxLayout(orientation='vertical', size_hint=(0.85, None), height=850, spacing=40)
        box.add_widget(Label(text="KIRISH", font_size=75, color=(0,1,1,1), bold=True))
        
        # Standart TextInput - Hech qanday canvas-siz (100% ko'rinadi)
        # padding va background_color orqali qirrasiz ko'rinish beramiz
        self.u = TextInput(
            hint_text="Login", 
            multiline=False, 
            size_hint_y=None, 
            height=130, 
            font_size=45,
            padding=[30, 35],
            background_color=(0.9, 0.9, 0.9, 1), # Oqish-kulrang fon
            foreground_color=(0, 0, 0, 1),       # Qora harflar
            hint_text_color=(0.5, 0.5, 0.5, 1)   # Ko'rinadigan hint
        )
        
        self.p = TextInput(
            hint_text="Parol", 
            password=True, 
            multiline=False, 
            size_hint_y=None, 
            height=130, 
            font_size=45,
            padding=[30, 35],
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        
        btn = SmoothButton(text="KIRISH", size_hint_y=None, height=160, font_size=50, bold=True)
        btn.bind(on_release=self.auth)
        
        box.add_widget(self.u); box.add_widget(self.p); box.add_widget(btn)
        self.root.add_widget(box)

    def auth(self, instance):
        name = self.u.text.strip(); pwd = self.p.text.strip()
        if name in ALLOWED_USERS:
            try:
                r = requests.get(f"{DB_URL}users/{name}.json", timeout=5).json()
                if r is None:
                    requests.put(f"{DB_URL}users/{name}.json", json={"password": pwd})
                    self.user = name; self.id_num = ALLOWED_USERS[name]; self.main_view()
                elif r['password'] == pwd:
                    self.user = name; self.id_num = ALLOWED_USERS[name]; self.main_view()
                else: self.p.text = ""; self.p.hint_text = "PAROL XATO!"
            except: self.u.hint_text = "INTERNET YO'Q!"
        else: self.u.text = ""; self.u.hint_text = "LOGIN TOPILMADI!"

    def main_view(self):
        self.root.clear_widgets()
        main = BoxLayout(orientation='vertical', padding=[40, 60, 40, 60], spacing=50)
        header = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=15)
        header.add_widget(Label(text=f"ID: {self.id_num} | {self.user}", font_size=55, color=(1,1,0,1), bold=True))
        self.clock = Label(text="00:00:00", font_size=120, color=(0,1,0.8,1), bold=True)
        header.add_widget(self.clock)
        
        # OGOHLANTIRISH MATNI UCHUN JOY
        self.status_lbl = Label(text="ONLINE", font_size=35, color=(0,1,0,1), halign="center", bold=True)
        header.add_widget(self.status_lbl)
        
        Clock.schedule_interval(self.tick, 1); main.add_widget(header)

        if self.user != "Admin":
            self.work_btn = SmoothButton(text="ISHGA KELDIM", size_hint_y=0.35, font_size=60, bold=True)
            self.work_btn.bind(on_release=self.send_data); main.add_widget(self.work_btn)
        else:
            btn = SmoothButton(text="ADMIN PANEL", size_hint_y=0.35, font_size=55, bold=True)
            btn.bind(on_release=self.show_admin_logs); main.add_widget(btn)

        foot = BoxLayout(size_hint_y=0.25, spacing=40) 
        b1 = SmoothButton(text="ARXIV", font_size=40); b1.bind(on_release=self.show_my_logs)
        b2 = SmoothButton(text="CHIQISH", font_size=40); b2.bind(on_release=self.login_view)
        foot.add_widget(b1); foot.add_widget(b2); main.add_widget(foot)
        self.root.add_widget(main)

    def tick(self, *args):
        self.clock.text = datetime.datetime.now().strftime("%H:%M:%S")

    def send_data(self, instance):
        now = datetime.datetime.now()
        h, m = now.hour, now.minute
        smena = "Kunduzgi" if 7 <= h < 14 else "Kechki"
        limit = 8 if smena == "Kunduzgi" else 19
        
        # OGOHLANTIRISH MANTIQI (Ekranda ko'rinadi)
        if h > limit or (h == limit and m > 0):
            self.status_lbl.text = "KECH QOLDINGIZ!\nISHGA ETIBORLI BO'LING"
            self.status_lbl.color = (1, 0, 0, 1) # QIZIL
        else:
            self.status_lbl.text = "O'Z VAQTIDA KELDINGIZ!\nBARAKALLA!"
            self.status_lbl.color = (0, 1, 0, 1) # YASHIL

        data = {"id": self.id_num, "ism": self.user, "sana": now.strftime("%Y-%m-%d"), "vaqt": now.strftime("%H:%M:%S"), "smena": smena}
        try:
            requests.post(f"{DB_URL}history.json", json=data, timeout=7)
            instance.disabled = True; instance.text = "QABUL QILINDI"
        except: self.status_lbl.text = "INTERNET YO'Q!"

    def show_admin_logs(self, *args):
        self.root.clear_widgets()
        lay = BoxLayout(orientation='vertical', padding=30, spacing=25)
        top = BoxLayout(size_hint_y=0.15, spacing=30)
        top.add_widget(Label(text="DAVOMAT", font_size=45, color=(0,1,1,1)))
        
        # ADMIN TOZALASH TUGMASI
        clear_btn = Button(text="TOZALASH", size_hint_x=0.4, background_color=(0.8, 0, 0, 1))
        clear_btn.bind(on_release=self.clear_database)
        top.add_widget(clear_btn); lay.add_widget(top)

        sc = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        box.bind(minimum_height=box.setter('height'))
        try:
            r = requests.get(f"{DB_URL}history.json").json()
            if r:
                for k in reversed(list(r.keys())):
                    d = r[k]
                    box.add_widget(Label(text=f"{d['ism']} | {d['sana']} | {d['vaqt']}", size_hint_y=None, height=110, font_size=30))
        except: pass
        sc.add_widget(box); lay.add_widget(sc)
        back = SmoothButton(text="ORQAGA", size_hint_y=0.18); back.bind(on_release=lambda x: self.main_view())
        lay.add_widget(back); self.root.add_widget(lay)

    def clear_database(self, instance):
        try:
            requests.delete(f"{DB_URL}history.json", timeout=7)
            self.show_admin_logs()
        except: pass

    def show_my_logs(self, *args):
        self.root.clear_widgets()
        lay = BoxLayout(orientation='vertical', padding=40, spacing=30)
        lay.add_widget(Label(text="SHAXSIY ARXIV", font_size=50, size_hint_y=0.15, color=(0,1,1,1)))
        sc = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        box.bind(minimum_height=box.setter('height'))
        try:
            r = requests.get(f"{DB_URL}history.json").json()
            if r:
                for k in reversed(list(r.keys())):
                    d = r[k]
                    if d['ism'] == self.user:
                        box.add_widget(Label(text=f"{d['sana']} | {d['vaqt']}", size_hint_y=None, height=110, font_size=34))
        except: pass
        sc.add_widget(box); lay.add_widget(sc)
        back = SmoothButton(text="ORQAGA", size_hint_y=0.2); back.bind(on_release=lambda x: self.main_view())
        lay.add_widget(back); self.root.add_widget(lay)

if __name__ == "__main__":
    DavomatApp().run()
    