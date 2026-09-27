import json, os, urllib.request
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp


ITEM_NAME_TO_ID = {
    "Куртка наёмника": "ARMOR_LEATHER_SET1",
    "Куртка убийцы": "ARMOR_LEATHER_SET3",
    "Боевой топор": "MAIN_AXE",
    "Парные мечи": "2H_DUALSWORD",
    "Лёгкий арбалет": "MAIN_1HCROSSBOW",
    "Сапоги солдата": "SHOES_PLATE_SET1"
}

CITY_BACKGROUNDS = {
    "Lymhurst": '#1A241A', "Caerleon": '#241A24', "Martlock": '#1A2424',
    "Thetford": '#24241A', "Fort Sterling": '#202428', "Bridgewatch": '#2A2015'
}

DEFAULT_PORTFOLIO = {
    "T4_ARMOR_LEATHER_SET1@1": {"name": "Куртка наёмника", "tier": "4.1", "qual": "Хорошее", "limit": 500000},
    "T4_MAIN_AXE@1": {"name": "Боевой топор", "tier": "4.1", "qual": "Хорошее", "limit": 500000}
}

MARKET_SCANNER_ITEMS = {
    "T7_MEAL_ROAST": {"name": "Жареная свинина", "tier": "7.0"},
    "T8_MEAL_STEW": {"name": "Жаркое из говядины", "tier": "8.0"}
}


def _cfg_path(name):
    try:
        base = App.get_running_app().user_data_dir
    except Exception:
        base = "."
    return os.path.join(base, name)

CONFIG_FILE = "portfolio_config.json"
PROFILE_FILE = "profile_config.json"


def load_p():
    p = _cfg_path(CONFIG_FILE)
    if os.path.exists(p):
        try:
            return json.load(open(p, "r", encoding="utf-8"))
        except Exception:
            return dict(DEFAULT_PORTFOLIO)
    return dict(DEFAULT_PORTFOLIO)

def save_p(d):
    try:
        json.dump(d, open(_cfg_path(CONFIG_FILE), "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    except Exception:
        pass

def load_b():
    p = _cfg_path(PROFILE_FILE)
    if os.path.exists(p):
        try:
            return json.load(open(p))["balance"]
        except Exception:
            return 25000000
    return 25000000

def save_b(b):
    try:
        json.dump({"balance": b}, open(_cfg_path(PROFILE_FILE), "w"))
    except Exception:
        pass


class LargeButton(Button):
    def __init__(self, is_active=False, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.font_size = sp(13)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(55)
        self.background_color = get_color_from_hex('#D4AF37' if is_active else '#2A2A2A')
        self.color = get_color_from_hex('#111111' if is_active else '#AAAAAA')


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.portfolio_items = load_p()
        self.total_silver_balance = load_b()
        self.raw_api_data = []
        self.current_tab = 1

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))

        cb = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), padding=dp(5))
        cb.add_widget(Label(text="Город рынка:", font_size=sp(14), bold=True))
        self.city_spinner = Spinner(
            text='Lymhurst',
            values=('Lymhurst', 'Caerleon', 'Martlock', 'Thetford', 'Fort Sterling', 'Bridgewatch'),
            background_color=get_color_from_hex('#333333')
        )
        self.city_spinner.bind(text=self.on_city_change)
        cb.add_widget(self.city_spinner)
        self.main_layout.add_widget(cb)

        self.nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(2))
        self.btn_t1 = LargeButton(True, text="ПОРТФЕЛЬ")
        self.btn_t2 = LargeButton(False, text="РЫНОК")
        self.btn_t3 = LargeButton(False, text="НАСТРОЙКА")
        self.btn_t4 = LargeButton(False, text="ПРОФИЛЬ")
        self.btn_t1.bind(on_press=lambda x: self.switch_tab(1))
        self.btn_t2.bind(on_press=lambda x: self.switch_tab(2))
        self.btn_t3.bind(on_press=lambda x: self.switch_tab(3))
        self.btn_t4.bind(on_press=lambda x: self.switch_tab(4))
        for b in [self.btn_t1, self.btn_t2, self.btn_t3, self.btn_t4]:
            self.nav_bar.add_widget(b)
        self.main_layout.add_widget(self.nav_bar)

        self.content_area = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.content_area)

        self.btn_refresh = Button(
            text="ОБНОВИТЬ ЦЕНЫ", font_size=sp(15), bold=True,
            size_hint_y=None, height=dp(55), background_normal='',
            background_color=get_color_from_hex('#D4AF37'),
            color=get_color_from_hex('#111111')
        )
        self.btn_refresh.bind(on_press=self.fetch_market_data)
        self.main_layout.add_widget(self.btn_refresh)

        self.add_widget(self.main_layout)
        self.update_background()
        self.render_current_tab()

    def on_city_change(self, spinner, text):
        self.update_background()
        self.render_current_tab()

    def update_background(self):
        Window.clearcolor = get_color_from_hex(CITY_BACKGROUNDS.get(self.city_spinner.text, '#121212'))

    def switch_tab(self, t):
        self.current_tab = t
        for b, active in [(self.btn_t1, t == 1), (self.btn_t2, t == 2), (self.btn_t3, t == 3), (self.btn_t4, t == 4)]:
            b.background_color = get_color_from_hex('#D4AF37' if active else '#2A2A2A')
            b.color = get_color_from_hex('#111111' if active else '#AAAAAA')
        self.render_current_tab()

    def fetch_market_data(self, instance):
        self.portfolio_items = load_p()
        all_ids = list(self.portfolio_items.keys()) + list(MARKET_SCANNER_ITEMS.keys())
        if not all_ids:
            return
        self.btn_refresh.text = "ЗАГРУЗКА..."
        self.btn_refresh.disabled = True
        city = self.city_spinner.text
        url = f"https://albion-online-data.com/api/v2/stats/prices/{','.join(all_ids)}?locations={city}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                self.raw_api_data = json.loads(response.read().decode())
            self.btn_refresh.text = f"ОБНОВИТЬ ({city})"
        except Exception:
            self.btn_refresh.text = "ОШИБКА СЕТИ"
        self.btn_refresh.disabled = False
        self.render_current_tab()

    def render_current_tab(self):
        self.content_area.clear_widgets()
        if self.current_tab == 3:
            self.render_t3()
            return
        if self.current_tab == 4:
            self.render_t4()
            return
        if not self.raw_api_data:
            self.content_area.add_widget(Label(text="Нет данных. Нажмите 'ОБНОВИТЬ'.", font_size=sp(15)))
            return

        p_dict = {}
        for e in self.raw_api_data:
            key = f"{e['item_id']}_Q3" if e.get("quality", 1) == 3 else e['item_id']
            p_dict[key] = e

        scr = ScrollView(effect_cls='DampedScrollEffect')
        g = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(10))
        g.bind(minimum_height=g.setter('height'))

        if self.current_tab == 1:
            for i_id, meta in load_p().items():
                d = p_dict.get(i_id, {})
                s = d.get("sell_price_min", 0)
                b = d.get("buy_price_max", 0)
                prof = (s * 0.895) - b
                card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110), padding=dp(8))
                if prof > 0 and b > 0:
                    card.background_color = get_color_from_hex('#1A351A')
                    qty = int(meta.get("limit", 500000) / b) if b > 0 else 0
                    text_b = (f"Закуп: [color=FFD700]{b + 1}[/color] | Кол-во: [color=66BB6A]{qty} шт.[/color]\n"
                              f"Селл: [color=FFD700]{s - 1}[/color] | Профит: [color=66BB6A]+{int(prof*qty):,} сер.[/color] ({(prof/b)*100:.1f}%)")
                else:
                    card.background_color = get_color_from_hex('#351A1A')
                    text_b = "НЕ ПОДХОДИТ. Низкий спред или нет ордеров."
                l1 = Label(text=f"[b]{meta['name']} Т{meta['tier']} ({meta['qual']})[/b]",
                           markup=True, font_size=sp(16), size_hint_y=None, height=dp(25), halign='left')
                l2 = Label(text=text_b, markup=True, font_size=sp(13),
                           size_hint_y=None, height=dp(60), halign='left', valign='top')
                l1.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
                l2.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
                card.add_widget(l1)
                card.add_widget(l2)
                g.add_widget(card)

        elif self.current_tab == 2:
            for i_id, meta in MARKET_SCANNER_ITEMS.items():
                d = p_dict.get(i_id, {})
                s = d.get("sell_price_min", 0)
                b = d.get("buy_price_max", 0)
                if b <= 0 or s <= 0:
                    continue
                sp_pct = (((s * 0.895) - b) / b) * 100
                if sp_pct >= 15.0:
                    card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90), padding=dp(8))
                    card.background_color = get_color_from_hex('#1A351A')
                    l1 = Label(text=f"[b]{meta['name']} Т{meta['tier']}[/b]", markup=True,
                               font_size=sp(16), size_hint_y=None, height=dp(25), halign='left')
                    l2 = Label(text=f"Чистый спред: [color=66BB6A]{sp_pct:.1f}%[/color]\nSell: {s} | Buy: {b}",
                               markup=True, font_size=sp(13), size_hint_y=None, height=dp(45), halign='left')
                    l1.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
                    l2.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
                    card.add_widget(l1)
                    card.add_widget(l2)
                    g.add_widget(card)

        scr.add_widget(g)
        self.content_area.add_widget(scr)

    def render_t3(self):
        f = GridLayout(cols=2, size_hint_y=None, height=dp(180), spacing=dp(5), padding=dp(5))
        self.i_name_spinner = Spinner(text='Куртка убийцы', values=list(ITEM_NAME_TO_ID.keys()))
        self.i_t_spinner = Spinner(text='4.1', values=('4.0', '4.1', '5.1', '6.1'))
        self.i_q = Spinner(text='Хорошее', values=('Хорошее', 'Отличное'))
        self.i_l = TextInput(text="500000", multiline=False)
        for lbl, w in [("Выбор вещи:", self.i_name_spinner), ("Выбор тира:", self.i_t_spinner),
                       ("Качество:", self.i_q), ("Лимит лота:", self.i_l)]:
            f.add_widget(Label(text=lbl, font_size=sp(12)))
            f.add_widget(w)
        self.content_area.add_widget(f)

        b_add = Button(text="ДОБАВИТЬ В ПОРТФЕЛЬ", size_hint_y=None, height=dp(45),
                       background_color=get_color_from_hex('#66BB6A'), bold=True,
                       background_normal='')
        b_add.bind(on_press=self.add_item)
        self.content_area.add_widget(b_add)

        scr = ScrollView()
        lg = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        lg.bind(minimum_height=lg.setter('height'))
        for k, m in load_p().items():
            r = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
            lbl = Label(text=f"• {m['name']} T{m['tier']} ({m['qual']})", font_size=sp(13),
                        size_hint_x=0.7, halign='left')
            lbl.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
            b_del = Button(text="Удалить", size_hint_x=0.3,
                           background_color=get_color_from_hex('#E57373'),
                           background_normal='', bold=True)
            b_del.bind(on_press=lambda x, key=k: self.del_item(key))
            r.add_widget(lbl)
            r.add_widget(b_del)
            lg.add_widget(r)
        scr.add_widget(lg)
        self.content_area.add_widget(scr)

    def render_t4(self):
        p_lay = GridLayout(cols=1, spacing=dp(12), padding=dp(12))
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        box.add_widget(Label(text="Баланс серебра:", font_size=sp(14), bold=True))
        self.prof_b = TextInput(text=str(load_b()), multiline=False)
        box.add_widget(self.prof_b)
        p_lay.add_widget(box)

        p_dict = {}
        if self.raw_api_data:
            for entry in self.raw_api_data:
                key = f"{entry['item_id']}_Q3" if entry.get("quality", 1) == 3 else entry['item_id']
                p_dict[key] = entry

        frozen = 0
        prof_all = 0
        for k, m in load_p().items():
            lim = m.get("limit", 500000)
            frozen += lim
            d = p_dict.get(k, {})
            b_max = d.get("buy_price_max", 0)
            prof = (d.get("sell_price_min", 0) * 0.895) - b_max
            if prof > 0 and b_max > 0:
                prof_all += int(prof * (lim / b_max))

        cur_b = load_b()
        texts = [
            f"Серебро в лимитах лотов: [color=FFD700]{frozen:,}[/color]",
            f"Подушка безопасности (20%): [color=E57373]{int(cur_b*0.2):,}[/color]",
            f"Профит с круга: [color=66BB6A]+{prof_all:,}[/color]",
            f"Банк после круга: [color=66BB6A]{cur_b + prof_all:,}[/color]"
        ]
        for text in texts:
            lbl = Label(text=text, markup=True, font_size=sp(14), halign='left')
            lbl.bind(size=lambda w, v: setattr(w, 'text_size', (v[0], None)))
            p_lay.add_widget(lbl)

        b_save = Button(text="СОХРАНИТЬ ИЗМЕНЕНИЯ БАЛАНСА", size_hint_y=None, height=dp(50),
                        background_color=get_color_from_hex('#D4AF37'),
                        color=get_color_from_hex('#111111'),
                        background_normal='', bold=True)
        b_save.bind(on_press=self.save_balance_click)
        p_lay.add_widget(b_save)
        self.content_area.add_widget(p_lay)

    def save_balance_click(self, inst):
        try:
            save_b(int(self.prof_b.text.strip().replace(",", "")))
        except Exception:
            pass
        self.render_current_tab()

    def add_item(self, inst):
        name = self.i_name_spinner.text
        tier = self.i_t_spinner.text
        qual = self.i_q.text
        base_id = ITEM_NAME_TO_ID.get(name, "")
        t_prefix = "T" + tier.split(".")[0]
        parts = tier.split(".")
        c_suffix = "@" + parts[1] if len(parts) > 1 and parts[1] != "0" else ""
        raw_id = f"{t_prefix}_{base_id}{c_suffix}"
        k = f"{raw_id}_Q3" if qual == "Отличное" else raw_id
        items = load_p()
        try:
            lim = int(self.i_l.text.strip() or 500000)
        except Exception:
            lim = 500000
        items[k] = {"name": name, "tier": tier, "qual": qual, "limit": lim}
        save_p(items)
        self.render_current_tab()

    def del_item(self, key):
        items = load_p()
        if key in items:
            del items[key]
            save_p(items)
        self.render_current_tab()


class AlbionFlippingApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    AlbionFlippingApp().run()
