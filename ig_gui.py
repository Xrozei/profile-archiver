"""Profile Archiver - download public profiles (and stories/highlights when logged in) to a folder.
Profil Arşivleyici - herkese açık profilleri (giriş yapınca story/highlights da) klasöre indirir.

Built on Instaloader (MIT). Not affiliated with Instagram/Meta.
"""
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import instaloader
from instaloader.instaloader import get_default_session_filename

APP_NAME = "Profile Archiver"
DEFAULT_DIR = Path.home() / "Downloads" / "ProfileArchiver"
CONFIG = Path.home() / ".ig_indirici_kullanici.txt"
LANG_FILE = Path.home() / ".profile_archiver_lang.txt"
URL_RE = re.compile(r"(?:instagram\.com/|^@?)([A-Za-z0-9._]{1,30})/?(?:\?.*)?$")

BG, CARD, FIELD, BORDER = "#0e0e13", "#17171f", "#1f1f2a", "#2b2b3a"
TEXT, MUTED = "#ececf2", "#8b8ba0"
ACCENT, ACCENT_H = "#c13584", "#e1306c"
OK, ERR = "#3ddc84", "#ff5c6c"

# ------------------------------------------------------------------ languages
STRINGS = {
    "tr": {
        "subtitle": "Profil linkini yapıştır, gerisini bana bırak.",
        "step1": "1  Instagram girişi  (bir kez yapılır)",
        "step2": "2  İndir",
        "lbl_user": "Kullanıcı adın",
        "btn_save": "Girişi kaydet",
        "btn_how": "? Bunları nasıl bulurum",
        "btn_change": "Girişi değiştir",
        "btn_delete": "Oturumu sil",
        "status_ok": "✔  Giriş yapıldı: {user}  (story ve highlights da inecek)",
        "status_no": "✘  Giriş yok. Aşağıyı doldur, 'Girişi kaydet'e bas.",
        "lbl_link": "Profil linki",
        "lbl_folder": "Kayıt klasörü",
        "btn_choose": "Seç",
        "btn_go": "İndir",
        "btn_open": "Klasörü aç",
        "help_title": "Yardım: sessionid ve csrftoken nasıl bulunur?",
        "btn_ok": "Anladım",
        "warn_missing": "Kullanıcı adı, sessionid ve csrftoken'ın üçünü de doldur.",
        "err_save": "Kaydedilemedi:\n{e}",
        "login_saved": "Giriş kaydedildi. Artık profil linkini yapıştırıp İndir'e basabilirsin.",
        "ask_delete": "{user} oturumu bu bilgisayardan silinsin mi?",
        "err_link": "Geçerli bir profil linki yapıştır.\nÖrnek: https://www.instagram.com/kullanici/",
        "starting": "@{u} indiriliyor, bu biraz sürebilir...\n",
        "t429": "Instagram yavaşlattı",
        "m429": ("Instagram bu bağlantıdan çok istek geldiğini düşünüp geçici olarak engelledi.\n\n"
                 "Pencereyi kapatıp 1-2 saat sonra tekrar dene. Giriş yapılmışsa engel daha çabuk kalkar.\n"
                 "Bu süre içinde Instagram'ı da kullanma."),
        "log_logged_in": "[i] Giriş yapıldı: {u}",
        "log_session_fail": "[!] Oturum yüklenemedi: {e}",
        "log_not_logged": "[!] Giriş yok. Yukarıdan girişi yap; yoksa Instagram sık sık engeller.",
        "log_private": "\n[X] Bu profil gizli ve giriş yaptığın hesap onu takip etmiyor.",
        "log_incremental": "[i] Daha önce indirilmiş: sadece yeni içerikler indirilecek.",
        "log_first": "[i] İlk indirme: tüm içerik indirilecek.",
        "part_posts": "gönderiler ve reels",
        "part_stories": "story",
        "part_highlights": "highlights",
        "log_step": "\n[>] {n} indiriliyor...",
        "log_skip": "[!] {n} atlandı: {e}",
        "log_done_all": "\n[✓] BİTTİ. Her şey indirildi.",
        "log_failed": "\n[!] Şu bölümler indirilemedi: {l}",
        "log_failed_note": "[i] Diğer bölümler indirildi. Aynı profili tekrar indirirsen eksikler yeniden denenir.",
        "log_done_partial": "\n[✓] BİTTİ (bazı bölümler eksik).",
        "log_notfound": "\n[X] Profil bulunamadı. Linki kontrol et.",
        "log_error": "\n[X] Hata: {e}",
    },
    "en": {
        "subtitle": "Paste a profile link and leave the rest to me.",
        "step1": "1  Instagram login  (one time only)",
        "step2": "2  Download",
        "lbl_user": "Your username",
        "btn_save": "Save login",
        "btn_how": "? How do I find these",
        "btn_change": "Change login",
        "btn_delete": "Delete session",
        "status_ok": "✔  Logged in: {user}  (stories and highlights will download too)",
        "status_no": "✘  Not logged in. Fill in the fields below and press 'Save login'.",
        "lbl_link": "Profile link",
        "lbl_folder": "Save folder",
        "btn_choose": "Browse",
        "btn_go": "Download",
        "btn_open": "Open folder",
        "help_title": "Help: how to find sessionid and csrftoken",
        "btn_ok": "Got it",
        "warn_missing": "Fill in your username, sessionid and csrftoken.",
        "err_save": "Could not save:\n{e}",
        "login_saved": "Login saved. You can now paste a profile link and press Download.",
        "ask_delete": "Delete the {user} session from this computer?",
        "err_link": "Paste a valid profile link.\nExample: https://www.instagram.com/username/",
        "starting": "Downloading @{u}, this may take a while...\n",
        "t429": "Instagram is rate-limiting",
        "m429": ("Instagram thinks too many requests came from this connection and temporarily blocked it.\n\n"
                 "Close the window and try again in 1-2 hours. Being logged in usually lifts the block sooner.\n"
                 "Do not use Instagram in the meantime."),
        "log_logged_in": "[i] Logged in as {u}",
        "log_session_fail": "[!] Could not load session: {e}",
        "log_not_logged": "[!] Not logged in. Log in above, otherwise Instagram blocks often.",
        "log_private": "\n[X] This profile is private and your logged-in account does not follow it.",
        "log_incremental": "[i] Downloaded before: only new content will be fetched.",
        "log_first": "[i] First download: everything will be fetched.",
        "part_posts": "posts and reels",
        "part_stories": "stories",
        "part_highlights": "highlights",
        "log_step": "\n[>] Downloading {n}...",
        "log_skip": "[!] {n} skipped: {e}",
        "log_done_all": "\n[✓] DONE. Everything downloaded.",
        "log_failed": "\n[!] These parts could not be downloaded: {l}",
        "log_failed_note": "[i] The other parts were downloaded. Download the same profile again to retry the missing ones.",
        "log_done_partial": "\n[✓] DONE (some parts missing).",
        "log_notfound": "\n[X] Profile not found. Check the link.",
        "log_error": "\n[X] Error: {e}",
    },
}

HELP = {
    "tr": [
        ("Bu bilgiler neden gerekli?\n", "h"),
        ("Story ve Highlights'ı indirebilmek ve Instagram'ın seni engellemesini azaltmak için program "
         "Instagram'a giriş yapmış gibi görünmelidir. Şifreni istemiyoruz. Onun yerine tarayıcında zaten açık olan "
         "girişin iki küçük kodunu kullanıyoruz: ", ""), ("sessionid", "code"), (" ve ", ""), ("csrftoken", "code"), (".\n", ""),
        ("Chrome, Edge, Brave ile bulmak\n", "h"),
        ("1. ", "b"), ("Tarayıcıda instagram.com'a git ve hesabına giriş yapmış ol.\n", ""),
        ("2. ", "b"), ("Klavyede F12'ye bas (olmazsa Ctrl+Shift+I). Sağda ya da altta bir panel açılır.\n", ""),
        ("3. ", "b"), ("Panelin üstündeki sekmelerden ", ""), ("Application", "code"),
        (" (Edge'de \"Uygulama\") sekmesine tıkla. Görünmüyorsa ", ""), (">>", "code"), (" işaretine tıkla.\n", ""),
        ("4. ", "b"), ("Soldaki listede ", ""), ("Cookies", "code"), (" satırını aç ve ", ""),
        ("https://www.instagram.com", "code"), (" satırına tıkla.\n", ""),
        ("5. ", "b"), ("Ortadaki listede ", ""), ("sessionid", "code"),
        (" satırına tıkla. Altta açılan \"Cookie Value\" kutusundaki uzun yazıyı kopyala "
         "(üzerine çift tıkla, Ctrl+C) ve programdaki ", ""), ("sessionid", "code"), (" kutusuna yapıştır.\n", ""),
        ("6. ", "b"), ("Aynısını ", ""), ("csrftoken", "code"), (" satırı için yap.\n", ""),
        ("7. ", "b"), ("Instagram kullanıcı adını yaz ve ", ""), ("Girişi kaydet", "b"), ("'e bas.\n", ""),
        ("Firefox ile bulmak\n", "h"),
        ("F12, ardından ", ""), ("Depolama (Storage)", "code"), (" sekmesi, ", ""), ("Çerezler", "code"),
        (", ", ""), ("https://www.instagram.com", "code"), (". Gerisi aynı.\n", ""),
        ("Güvenlik\n", "h"),
        ("• sessionid bir şifre gibidir. Kimseye gönderme, ekran görüntüsüne koyma.\n", "warn"),
        ("• Kodlar yalnızca bu bilgisayarda saklanır ve sadece Instagram'a gönderilir.\n", ""),
        ("• Mümkünse ana hesabın yerine ikinci bir hesap kullan. Çok indirme yapmak Instagram'ın hesabı "
         "kısıtlamasına yol açabilir.\n", ""),
        ("• İşin bitince tarayıcıdan Instagram'dan çıkış yap ya da programdaki \"Oturumu sil\" düğmesini kullan.\n", ""),
        ("Sık görülen sorunlar\n", "h"),
        ("• \"Too Many Requests\" uyarısı: Instagram geçici engel koydu. 1-2 saat bekle.\n", ""),
        ("• Giriş yaptığım halde story gelmiyor: Kodları yeniden kopyalayıp girişi tekrar kaydet.\n", ""),
        ("• Gizli profil: Girişte kullandığın hesap o profili takip ediyorsa iner, yoksa inmez.\n", ""),
    ],
    "en": [
        ("Why is this needed?\n", "h"),
        ("To download Stories and Highlights, and to reduce the chance of Instagram blocking you, the app has to "
         "look logged in. We do not ask for your password. Instead we use two small codes from the login that is "
         "already open in your browser: ", ""), ("sessionid", "code"), (" and ", ""), ("csrftoken", "code"), (".\n", ""),
        ("Find them in Chrome, Edge or Brave\n", "h"),
        ("1. ", "b"), ("Go to instagram.com in your browser and make sure you are logged in.\n", ""),
        ("2. ", "b"), ("Press F12 (or Ctrl+Shift+I). A panel opens on the right or at the bottom.\n", ""),
        ("3. ", "b"), ("In the tabs at the top of the panel, click ", ""), ("Application", "code"),
        (". If you cannot see it, click the ", ""), (">>", "code"), (" icon.\n", ""),
        ("4. ", "b"), ("In the left list, expand ", ""), ("Cookies", "code"), (" and click ", ""),
        ("https://www.instagram.com", "code"), (".\n", ""),
        ("5. ", "b"), ("In the middle list, click the ", ""), ("sessionid", "code"),
        (" row. Copy the long text from the \"Cookie Value\" box at the bottom (double-click it, then Ctrl+C) "
         "and paste it into the ", ""), ("sessionid", "code"), (" box in the app.\n", ""),
        ("6. ", "b"), ("Do the same for the ", ""), ("csrftoken", "code"), (" row.\n", ""),
        ("7. ", "b"), ("Type your Instagram username and press ", ""), ("Save login", "b"), (".\n", ""),
        ("Find them in Firefox\n", "h"),
        ("Press F12, open the ", ""), ("Storage", "code"), (" tab, then ", ""), ("Cookies", "code"),
        (", then ", ""), ("https://www.instagram.com", "code"), (". The rest is the same.\n", ""),
        ("Safety\n", "h"),
        ("• sessionid works like a password. Never send it to anyone or put it in a screenshot.\n", "warn"),
        ("• The codes are stored only on this computer and are sent only to Instagram.\n", ""),
        ("• If possible, use a secondary account instead of your main one. Heavy downloading can get an account "
         "restricted by Instagram.\n", ""),
        ("• When you are done, log out of Instagram in your browser or use the \"Delete session\" button in the app.\n", ""),
        ("Common problems\n", "h"),
        ("• \"Too Many Requests\": Instagram has temporarily blocked requests. Wait 1-2 hours.\n", ""),
        ("• Logged in but no stories: copy the codes again and save the login again.\n", ""),
        ("• Private profile: it only downloads if the logged-in account follows it.\n", ""),
    ],
}


def detect_lang():
    try:
        if LANG_FILE.exists():
            v = LANG_FILE.read_text(encoding="utf-8").strip()
            if v in STRINGS:
                return v
    except Exception:
        pass
    try:
        import ctypes
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "tr" if (lid & 0xFF) == 0x1F else "en"
    except Exception:
        pass
    try:
        import locale
        return "tr" if (locale.getlocale()[0] or "").lower().startswith("tr") else "en"
    except Exception:
        return "en"


LANG = detect_lang()


def T(key, **kw):
    s = STRINGS[LANG][key]
    return s.format(**kw) if kw else s


# ------------------------------------------------------------------ logic
def extract_username(text):
    text = text.strip().split("?")[0].rstrip("/")
    m = URL_RE.search(text)
    if not m or m.group(1) in {"p", "reel", "stories", "explore"}:
        raise ValueError(T("err_link"))
    return m.group(1)


def get_session_user():
    """Name of the saved Instagram session, or ''."""
    try:
        if CONFIG.exists():
            user = CONFIG.read_text(encoding="utf-8").strip()
            if user and os.path.exists(get_default_session_filename(user)):
                return user
        folder = Path(get_default_session_filename("x")).parent
        files = sorted(folder.glob("session-*")) if folder.exists() else []
        if files:
            return files[0].name.replace("session-", "", 1)
    except Exception:
        pass
    return ""


def save_login(user, sessionid, csrftoken):
    loader = instaloader.Instaloader()
    loader.load_session(user, {"sessionid": sessionid, "csrftoken": csrftoken})
    loader.save_session_to_file()
    CONFIG.write_text(user, encoding="utf-8")


def delete_session(user):
    try:
        os.remove(get_default_session_filename(user))
    except OSError:
        pass
    try:
        CONFIG.unlink()
    except OSError:
        pass


def open_path(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class LogWriter:
    def __init__(self, q):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(s)

    def flush(self):
        pass


def download(username, outdir, session_user, q):
    result = None
    try:
        loader = instaloader.Instaloader(
            dirname_pattern=str(Path(outdir) / "{target}"),
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
        )
        if session_user:
            try:
                loader.load_session_from_file(session_user)
                print(T("log_logged_in", u=session_user))
            except Exception as e:
                print(T("log_session_fail", e=repr(e)))
        logged_in = bool(loader.context.username)
        if not logged_in:
            print(T("log_not_logged"))

        profile = instaloader.Profile.from_username(loader.context, username)
        if profile.is_private and not profile.followed_by_viewer:
            print(T("log_private"))
            return

        steps = [(T("part_posts"), dict(profile_pic=True, posts=True, igtv=False))]
        if logged_in:
            steps += [
                (T("part_stories"), dict(profile_pic=False, posts=False, stories=True)),
                (T("part_highlights"), dict(profile_pic=False, posts=False, highlights=True)),
            ]

        marker = Path(outdir) / username / ".tamamlandi"
        fast = marker.exists()
        print(T("log_incremental") if fast else T("log_first"))

        failures = []
        for name, opts in steps:
            try:
                print(T("log_step", n=name))
                loader.download_profiles({profile}, fast_update=fast, **opts)
            except Exception as e:
                failures.append((name, e))
                print(T("log_skip", n=name, e=repr(e)))
        if not failures:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
            print(T("log_done_all"))
        else:
            print(T("log_failed", l=", ".join(n for n, _ in failures)))
            for n, e in failures:
                print(f"    - {n}: {e}")
            print(T("log_failed_note"))
            print(T("log_done_partial"))
        result = str(Path(outdir) / username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(T("log_notfound"))
    except Exception as e:
        print(T("log_error", e=e))
    finally:
        q.put(("done", result))


# ------------------------------------------------------------------ UI
def dark_titlebar(win):
    try:
        import ctypes
        win.update()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        for attr in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(ctypes.c_int(1)), 4)
    except Exception:
        pass


def apply_style(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=BG)
    s.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=CARD)
    s.configure("TLabel", background=BG, foreground=TEXT)
    s.configure("Card.TLabel", background=CARD, foreground=TEXT)
    s.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
    s.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="white")
    s.configure("Sub.TLabel", foreground=MUTED)
    s.configure("TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT,
                bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=7)
    s.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)], darkcolor=[("focus", ACCENT)])
    s.configure("TButton", background=FIELD, foreground=TEXT, bordercolor=BORDER,
                focusthickness=0, focuscolor=FIELD, padding=(14, 7))
    s.map("TButton", background=[("active", BORDER), ("disabled", CARD)], foreground=[("disabled", MUTED)])
    s.configure("Accent.TButton", background=ACCENT, foreground="white", bordercolor=ACCENT,
                padding=(26, 10), font=("Segoe UI", 11, "bold"))
    s.map("Accent.TButton", background=[("active", ACCENT_H), ("disabled", BORDER)],
          foreground=[("disabled", MUTED)], bordercolor=[("active", ACCENT_H)])
    s.configure("Help.TButton", padding=(10, 4), font=("Segoe UI", 11, "bold"))
    s.configure("Lang.TButton", padding=(9, 4), font=("Segoe UI", 9, "bold"), foreground=MUTED)
    s.configure("LangOn.TButton", padding=(9, 4), font=("Segoe UI", 9, "bold"),
                background=ACCENT, foreground="white", bordercolor=ACCENT)
    s.map("LangOn.TButton", background=[("active", ACCENT_H)])
    s.configure("Vertical.TScrollbar", background=FIELD, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)


def hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("760x780")
        self.minsize(640, 640)
        apply_style(self)
        dark_titlebar(self)
        self.q = queue.Queue()
        self.result_dir = None
        self.warned_429 = False
        self.help_win = None
        self.reg = []  # (widget, option, key) for live language switching

        self.strip = tk.Canvas(self, height=5, bd=0, highlightthickness=0, bg=BG)
        self.strip.pack(fill="x")
        self.strip.bind("<Configure>", self.draw_strip)

        head = ttk.Frame(self)
        head.pack(fill="x", padx=18, pady=(14, 4))
        titles = ttk.Frame(head)
        titles.pack(side="left")
        ttk.Label(titles, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        sub = ttk.Label(titles, style="Sub.TLabel")
        sub.pack(anchor="w")
        self.reg.append((sub, "text", "subtitle"))
        ttk.Button(head, text="?", style="Help.TButton", width=3, command=self.show_help).pack(side="right")
        self.btn_en = ttk.Button(head, text="EN", command=lambda: self.set_lang("en"))
        self.btn_en.pack(side="right", padx=(0, 6))
        self.btn_tr = ttk.Button(head, text="TR", command=lambda: self.set_lang("tr"))
        self.btn_tr.pack(side="right", padx=(0, 4))

        # --- step 1: login
        c1 = self.card("step1")
        self.status = ttk.Label(c1, style="Card.TLabel", font=("Segoe UI", 10, "bold"))
        self.status.pack(anchor="w")
        self.fields = ttk.Frame(c1, style="Card.TFrame")
        self.e_user = self.row(self.fields, 0, "lbl_user", False)
        self.e_sid = self.row(self.fields, 1, None, True, "sessionid")
        self.e_csrf = self.row(self.fields, 2, None, True, "csrftoken")
        self.fields.columnconfigure(1, weight=1)
        fb = ttk.Frame(self.fields, style="Card.TFrame")
        fb.grid(row=3, column=1, sticky="w", pady=(8, 0))
        self.mk(ttk.Button, fb, "btn_save", command=self.do_login).pack(side="left")
        self.mk(ttk.Button, fb, "btn_how", command=self.show_help).pack(side="left", padx=8)
        self.logged_btns = ttk.Frame(c1, style="Card.TFrame")
        self.mk(ttk.Button, self.logged_btns, "btn_change", command=self.show_fields).pack(side="left")
        self.mk(ttk.Button, self.logged_btns, "btn_delete", command=self.do_logout).pack(side="left", padx=8)

        # --- step 2: download
        c2 = self.card("step2")
        self.mk(ttk.Label, c2, "lbl_link", style="Muted.TLabel").pack(anchor="w")
        self.url = ttk.Entry(c2, font=("Segoe UI", 11))
        self.url.pack(fill="x", pady=(2, 8))
        self.url.bind("<Return>", lambda e: self.start())
        self.url.focus()
        self.mk(ttk.Label, c2, "lbl_folder", style="Muted.TLabel").pack(anchor="w")
        fr = ttk.Frame(c2, style="Card.TFrame")
        fr.pack(fill="x", pady=(2, 10))
        self.folder = tk.StringVar(value=str(DEFAULT_DIR))
        ttk.Entry(fr, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        self.mk(ttk.Button, fr, "btn_choose", command=self.choose_folder).pack(side="left", padx=(8, 0))
        br = ttk.Frame(c2, style="Card.TFrame")
        br.pack(fill="x")
        self.go = self.mk(ttk.Button, br, "btn_go", style="Accent.TButton", command=self.start)
        self.go.pack(side="left")
        self.open_btn = self.mk(ttk.Button, br, "btn_open", command=self.open_folder, state="disabled")
        self.open_btn.pack(side="left", padx=10)

        # --- log
        lf = ttk.Frame(self)
        lf.pack(fill="both", expand=True, padx=16, pady=(6, 16))
        self.log = tk.Text(lf, height=8, state="disabled", wrap="word", font=("Consolas", 9),
                           bg="#0a0a0f", fg="#cfcfe0", relief="flat", padx=10, pady=8, insertbackground=TEXT)
        sb = ttk.Scrollbar(lf, command=self.log.yview)
        self.log.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        self.refresh_texts()
        sys.stdout = LogWriter(self.q)
        sys.stderr = LogWriter(self.q)
        self.after(100, self.poll)

    # -- helpers
    def mk(self, cls, parent, key, **kw):
        w = cls(parent, **kw)
        self.reg.append((w, "text", key))
        return w

    def draw_strip(self, _=None):
        self.strip.delete("all")
        w = max(self.strip.winfo_width(), 1)
        stops = [hex_to_rgb(c) for c in ("#833ab4", "#fd1d1d", "#fcb045")]
        for x in range(w):
            t = x / w * 2
            i = min(int(t), 1)
            f = t - i
            a, b = stops[i], stops[i + 1]
            col = "#%02x%02x%02x" % tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))
            self.strip.create_line(x, 0, x, 5, fill=col)

    def card(self, title_key):
        outer = ttk.Frame(self)
        outer.pack(fill="x", padx=16, pady=6)
        inner = ttk.Frame(outer, style="Card.TFrame", padding=16)
        inner.pack(fill="x")
        lbl = ttk.Label(inner, style="Card.TLabel", font=("Segoe UI", 11, "bold"))
        lbl.pack(anchor="w", pady=(0, 8))
        self.reg.append((lbl, "text", title_key))
        return inner

    def row(self, parent, r, key, secret, literal=None):
        lbl = ttk.Label(parent, style="Muted.TLabel", text=literal or "")
        lbl.grid(row=r, column=0, sticky="w", padx=(0, 12), pady=3)
        if key:
            self.reg.append((lbl, "text", key))
        e = ttk.Entry(parent, show="•" if secret else "")
        e.grid(row=r, column=1, sticky="ew", pady=3)
        return e

    # -- language
    def set_lang(self, code):
        global LANG
        if code == LANG:
            return
        LANG = code
        try:
            LANG_FILE.write_text(code, encoding="utf-8")
        except Exception:
            pass
        self.refresh_texts()
        if self.help_win is not None and self.help_win.winfo_exists():
            self.help_win.destroy()
            self.show_help()

    def refresh_texts(self):
        for widget, option, key in self.reg:
            widget.config(**{option: T(key)})
        self.btn_tr.config(style="LangOn.TButton" if LANG == "tr" else "Lang.TButton")
        self.btn_en.config(style="LangOn.TButton" if LANG == "en" else "Lang.TButton")
        self.refresh_status()

    # -- login
    def refresh_status(self):
        user = get_session_user()
        if user:
            self.status.config(text=T("status_ok", user=user), foreground=OK)
            self.fields.pack_forget()
            self.logged_btns.pack(anchor="w", pady=(8, 0))
        else:
            self.status.config(text=T("status_no"), foreground=ERR)
            self.logged_btns.pack_forget()
            self.fields.pack(fill="x", pady=(8, 0))

    def show_fields(self):
        self.logged_btns.pack_forget()
        self.fields.pack(fill="x", pady=(8, 0))

    def do_login(self):
        user = self.e_user.get().strip().lstrip("@")
        sid, csrf = self.e_sid.get().strip(), self.e_csrf.get().strip()
        if not (user and sid and csrf):
            messagebox.showwarning(APP_NAME, T("warn_missing"))
            return
        try:
            save_login(user, sid, csrf)
        except Exception as e:
            messagebox.showerror(APP_NAME, T("err_save", e=e))
            return
        self.e_sid.delete(0, "end")
        self.e_csrf.delete(0, "end")
        self.refresh_status()
        messagebox.showinfo(APP_NAME, T("login_saved"))

    def do_logout(self):
        user = get_session_user()
        if user and messagebox.askyesno(APP_NAME, T("ask_delete", user=user)):
            delete_session(user)
            self.refresh_status()

    # -- download
    def choose_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.folder.set(d)

    def start(self):
        if str(self.go.cget("state")) == "disabled":
            return
        try:
            username = extract_username(self.url.get())
        except ValueError as e:
            messagebox.showwarning(APP_NAME, str(e))
            return
        outdir = Path(self.folder.get())
        outdir.mkdir(parents=True, exist_ok=True)
        self.go.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.warned_429 = False
        self.append(T("starting", u=username))
        threading.Thread(target=download, args=(username, outdir, get_session_user(), self.q), daemon=True).start()

    def open_folder(self):
        target = self.result_dir or self.folder.get()
        if os.path.isdir(target):
            open_path(target)

    def append(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")
        if "Too Many Requests" in text and not self.warned_429:
            self.warned_429 = True
            messagebox.showinfo(T("t429"), T("m429"))

    def poll(self):
        try:
            while True:
                item = self.q.get_nowait()
                if isinstance(item, tuple) and item[0] == "done":
                    self.result_dir = item[1]
                    self.go.config(state="normal")
                    self.open_btn.config(state="normal")
                else:
                    self.append(item)
        except queue.Empty:
            pass
        self.after(100, self.poll)

    # -- help window
    def show_help(self):
        if self.help_win is not None and self.help_win.winfo_exists():
            self.help_win.lift()
            return
        w = tk.Toplevel(self)
        self.help_win = w
        w.title(T("help_title"))
        w.configure(bg=BG)
        w.geometry("680x720")
        w.transient(self)
        dark_titlebar(w)
        t = tk.Text(w, wrap="word", bg=CARD, fg=TEXT, relief="flat", padx=20, pady=16,
                    font=("Segoe UI", 10), spacing3=5, cursor="arrow")
        t.tag_configure("h", font=("Segoe UI", 12, "bold"), foreground=ACCENT_H, spacing1=12)
        t.tag_configure("b", font=("Segoe UI", 10, "bold"))
        t.tag_configure("warn", foreground=ERR, font=("Segoe UI", 10, "bold"))
        t.tag_configure("code", font=("Consolas", 10), foreground="#9ad1ff")
        for text, tag in HELP[LANG]:
            t.insert("end", text, tag) if tag else t.insert("end", text)
        t.config(state="disabled")
        ttk.Button(w, text=T("btn_ok"), style="Accent.TButton", command=w.destroy).pack(side="bottom", pady=(4, 12))
        sb = ttk.Scrollbar(w, command=t.yview)
        t.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", pady=(12, 6), padx=(0, 6))
        t.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(12, 6))


if __name__ == "__main__":
    App().mainloop()
