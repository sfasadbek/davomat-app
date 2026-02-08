import datetime
import requests
import csv
import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock

# --- KONFIGURATSIYA ---
DB_URL = "https://davomat-fcdac-default-rtdb.firebaseio.com/" 
ALLOWED_USERS = {"Admin": "0", "Asadbek": "1", "Ali": "2", "Vali": "3"}

def init_local_db():
    conn = sqlite3.connect("local_davomat.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                      (id TEXT, ism TEXT, sana TEXT, vaqt TEXT, smena TEXT, holat TEXT)''')
    conn.commit()
    conn.close()

class SmoothButton(Button):
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
        init_local_db()
        self.title = "STATS MB"
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
        box.add_widget(Label(text="STATS MB", font_size=80, color=(0,1,1,1), bold=True))
        self.u = TextInput(hint_text="LOGIN", multiline=False, size_hint_y=None, height=130, font_size=45, padding=[30, 35])
        self.p = TextInput(hint_text="PAROL", password=True, multiline=False, size_hint_y=None, height=130, font_size=45, padding=[30, 35])
        btn = SmoothButton(text="KIRISH", size_hint_y=None, height=160, font_size=50, bold=True)
        btn.bind(on_release=self.auth)
        box.add_widget(self.u); box.add_widget(self.p); box.add_widget(btn)
        self.root.add_widget(box)

    def auth(self, instance):
        name = self.u.text.strip(); pwd = self.p.text.strip()
        if name in ALLOWED_USERS:
            self.user = name; self.id_num = ALLOWED_USERS[name]; self.main_view()
        else: self.u.text = ""; self.u.hint_text = "LOGIN TOPILMADI!"

    def main_view(self):
        self.root.clear_widgets()
        main = BoxLayout(orientation='vertical', padding=[40, 60, 40, 60], spacing=50)
        header = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=15)
        header.add_widget(Label(text=f"ID: {self.id_num} | {self.user}", font_size=55, color=(1,1,0,1), bold=True))
        self.clock = Label(text="00:00:00", font_size=120, color=(0,1,0.8,1), bold=True)
        header.add_widget(self.clock)
        self.status_lbl = Label(text="JARAYONDA...", font_size=40, color=(0,1,0,1), bold=True)
        header.add_widget(self.status_lbl)
        Clock.schedule_interval(self.tick, 1); main.add_widget(header)

        if self.user != "Admin":
            self.work_btn = SmoothButton(text="ISHGA KELDIM", size_hint_y=0.35, font_size=60, bold=True)
            self.work_btn.bind(on_release=self.process_attendance); main.add_widget(self.work_btn)
        else:
            btn = SmoothButton(text="ADMIN PANEL", size_hint_y=0.35, font_size=55, bold=True)
            btn.bind(on_release=self.show_admin_logs); main.add_widget(btn)

        foot = BoxLayout(size_hint_y=0.25, spacing=40) 
        b1 = SmoothButton(text="DAVOMAT", font_size=40); b1.bind(on_release=self.show_my_logs)
        b2 = SmoothButton(text="CHIQISH", font_size=40); b2.bind(on_release=self.login_view)
        foot.add_widget(b1); foot.add_widget(b2); main.add_widget(foot)
        self.root.add_widget(main)

    def tick(self, *args):
        self.clock.text = datetime.datetime.now().strftime("%H:%M:%S")

    def process_attendance(self, instance):
        """Gibrid saqlash: Internet bo'lsa Firebase + SQLite, bo'lmasa faqat SQLite"""
        now = datetime.datetime.now()
        h, m = now.hour, now.minute
        smena = "KUNDUZGI" if 7 <= h < 14 else "KECHKI"
        limit = 8 if smena == "KUNDUZGI" else 19
        is_late = h > limit or (h == limit and m > 0)
        holat = "KECHIKDI" if is_late else "VAQTIDA KELDI"
        
        data = {"id": self.id_num, "ism": self.user, "sana": now.strftime("%Y-%m-%d"), 
                "vaqt": now.strftime("%H:%M:%S"), "smena": smena, "holat": holat}

        # 1. Lokal bazaga har doim saqlaymiz
        try:
            conn = sqlite3.connect("local_davomat.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                           (data['id'], data['ism'], data['sana'], data['vaqt'], data['smena'], data['holat']))
            conn.commit()
            conn.close()
            local_saved = True
        except: local_saved = False

        # 2. Internetga yuborishni sinab ko'ramiz
        try:
            r = requests.post(f"{DB_URL}history.json", json=data, timeout=4)
            if r.status_code == 200:
                self.status_lbl.text = f"ONLINE: {holat}"
                self.status_lbl.color = (0, 1, 0, 1)
            else: raise Exception()
        except:
            self.status_lbl.text = f"OFFLINE MALUMOT SAQLANDI: {holat}"
            self.status_lbl.color = (1, 0.5, 0, 1) # To'q sariq (ogohlantirish)

        instance.disabled = True
        instance.text = "QABUL QILINDI"

    def show_admin_logs(self, *args):
        self.root.clear_widgets()
        lay = BoxLayout(orientation='vertical', padding=30, spacing=25)
        top = BoxLayout(size_hint_y=0.18, spacing=15)
        
        sync_btn = Button(text="SINXRONIZATSIYA\n(QILISH)", size_hint_x=0.4, background_color=(0, 0.5, 0.8, 1), font_size=24, bold=True)
        sync_btn.bind(on_release=self.sync_to_firebase)
        
        down_btn = Button(text="YUKLASH\n(CSV)", size_hint_x=0.35, background_color=(0, 0.7, 0, 1), font_size=24)
        down_btn.bind(on_release=self.export_to_csv)
        
        clear_btn = Button(text="TOZALASH", size_hint_x=0.25, background_color=(0.8, 0, 0, 1), font_size=24)
        clear_btn.bind(on_release=self.clear_local_db)
        
        top.add_widget(sync_btn); top.add_widget(down_btn); top.add_widget(clear_btn); lay.add_widget(top)

        sc = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        box.bind(minimum_height=box.setter('height'))
        
        conn = sqlite3.connect("local_davomat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY rowid DESC")
        logs = cursor.fetchall()
        for d in logs:
            cl = "[color=ff0000]" if d[5] == "KECHIKDI" else "[color=00ff00]"
            box.add_widget(Label(text=f"{d[1]} | {d[3]} | {cl}{d[5]}[/color]", 
                                 size_hint_y=None, height=100, font_size=28, markup=True))
        conn.close()
        
        sc.add_widget(box); lay.add_widget(sc)
        back = SmoothButton(text="ORQAGA", size_hint_y=0.15); back.bind(on_release=lambda x: self.main_view())
        lay.add_widget(back); self.root.add_widget(lay)

    def sync_to_firebase(self, instance):
        try:
            conn = sqlite3.connect("local_davomat.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history")
            logs = cursor.fetchall()
            if not logs: instance.text = "BO'SH"; return
            
            for d in logs:
                data = {"id": d[0], "ism": d[1], "sana": d[2], "vaqt": d[3], "smena": d[4], "holat": d[5]}
                requests.post(f"{DB_URL}history.json", json=data, timeout=5)
            
            instance.text = "YUBORILDI ✅"
            conn.close()
        except: instance.text = "INTERNET YO'Q ❌"

    def export_to_csv(self, instance):
        try:
            conn = sqlite3.connect("local_davomat.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history")
            logs = cursor.fetchall()
            if not logs: instance.text = "BO'SH"; return

            path = "/sdcard/Documents" if os.name == 'posix' else os.path.expanduser("~/Documents")
            if not os.path.exists(path): os.makedirs(path)
            f_name = os.path.join(path, "stats_mb_davomat.csv")
            with open(f_name, mode='w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['ID', 'Ism', 'Sana', 'Vaqt', 'Smena', 'Holat'])
                w.writerows(logs)
            instance.text = "SAQLANDI ✅"
            conn.close()
        except: instance.text = "XATO ❌"

    def clear_local_db(self, instance):
        conn = sqlite3.connect("local_davomat.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        self.show_admin_logs()

    def show_my_logs(self, *args):
        self.root.clear_widgets()
        lay = BoxLayout(orientation='vertical', padding=40, spacing=30)
        lay.add_widget(Label(text="DAVOMATLAR", font_size=50, size_hint_y=0.15, color=(0,1,1,1)))
        sc = ScrollView(); box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        box.bind(minimum_height=box.setter('height'))
        
        conn = sqlite3.connect("local_davomat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history WHERE ism=? ORDER BY rowid DESC", (self.user,))
        logs = cursor.fetchall()
        for d in logs:
            box.add_widget(Label(text=f"{d[2]} | {d[3]} | {d[5]}", size_hint_y=None, height=100, font_size=32))
        conn.close()
        
        sc.add_widget(box); lay.add_widget(sc)
        back = SmoothButton(text="ORQAGA", size_hint_y=0.15); back.bind(on_release=lambda x: self.main_view())
        lay.add_widget(back); self.root.add_widget(lay)

if __name__ == "__main__":
    DavomatApp().run()
        




