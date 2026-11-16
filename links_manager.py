# -*- coding: utf-8 -*-
"""
DK Links Manager  -  site ko chalao + links add/edit/delete karo (bina JSON chhue)
Chalane ke liye: START.bat double-click karo  (ya)  python links_manager.py
"""
import functools
import http.server
import json
import os
import re
import socket
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

# ---------- Colors (site jaise hi) ----------
BG = "#060a0c"
CARD = "#10181b"
CARD2 = "#141f23"
LINE = "#1e2b2f"
INK = "#eef4f2"
MUTED = "#7c9490"
ACCENT = "#00c8a0"
ACCENT_DK = "#04110d"
DANGER = "#ff6b6b"

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "manager_config.json")
SHORTENERS = ("bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "t.ly", "is.gd", "goo.gl")


# ---------- helpers ----------
def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()


def clean_url(u):
    u = (u or "").strip()
    if u and not re.match(r"^https?://", u, re.I):
        u = "https://" + u
    return u


def clean_bitly(b):
    return re.sub(r"^https?://", "", (b or "").strip(), flags=re.I).rstrip("/")


def is_short(token):
    t = clean_bitly(token).lower()
    return any(t == s or t.startswith(s + "/") for s in SHORTENERS)


def smart_split(text):
    """Kuch bhi paste karo (bitly + url, kisi bhi order me) - alag-alag nikal dega."""
    bitly, url = "", ""
    for tok in re.split(r"[\s,;]+", text.strip()):
        if not tok:
            continue
        if is_short(tok) and not bitly:
            bitly = clean_bitly(tok)
        elif re.match(r"^(https?://)?[\w-]+(\.[\w-]+)+", tok) and not url:
            url = clean_url(tok)
    return bitly, url


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


# ---------- App ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DK Links Manager")
        self.geometry("980x640")
        self.minsize(860, 560)
        self.configure(bg=BG)
        try:
            self.iconphoto(True, tk.PhotoImage(file=os.path.join(HERE, "favicon.png")))
        except Exception:
            pass

        self.folder = self.load_folder()
        self.links = []
        self.httpd = None
        self.port = 8000
        self.edit_index = None
        self.toast_job = None

        self.setup_style()
        self.build_ui()
        self.load_links()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ----- config -----
    def load_folder(self):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                p = json.load(f).get("folder")
            if p and os.path.isdir(p):
                return p
        except Exception:
            pass
        return HERE

    def save_folder(self):
        try:
            with open(CONFIG, "w", encoding="utf-8") as f:
                json.dump({"folder": self.folder}, f, ensure_ascii=False)
        except Exception:
            pass

    @property
    def json_path(self):
        return os.path.join(self.folder, "links.json")

    # ----- style -----
    def setup_style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=INK,
                     rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        st.map("Treeview", background=[("selected", "#0d3b33")], foreground=[("selected", INK)])
        st.configure("Treeview.Heading", background=CARD2, foreground=ACCENT, relief="flat",
                     font=("Segoe UI", 9, "bold"), padding=8)
        st.map("Treeview.Heading", background=[("active", CARD2)])
        st.configure("Vertical.TScrollbar", background=CARD2, troughcolor=CARD, bordercolor=CARD,
                     arrowcolor=MUTED, relief="flat")

    def btn(self, parent, text, cmd, kind="ghost", **kw):
        colors = {
            "primary": (ACCENT, ACCENT_DK, "#19e0b8"),
            "ghost": (CARD2, INK, LINE),
            "danger": (CARD2, DANGER, "#2a1618"),
        }
        bg, fg, hover = colors[kind]
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=hover,
                      activeforeground=fg, relief="flat", bd=0, cursor="hand2",
                      font=("Segoe UI", 10, "bold"), padx=14, pady=7, **kw)
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def entry(self, parent, var=None):
        e = tk.Entry(parent, textvariable=var, bg=BG, fg=INK, insertbackground=ACCENT,
                     relief="flat", font=("Segoe UI", 11), highlightthickness=1,
                     highlightbackground=LINE, highlightcolor=ACCENT)
        return e

    def label(self, parent, text, color=MUTED, size=9, bold=False, **kw):
        return tk.Label(parent, text=text, bg=kw.pop("bg", parent["bg"]), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"), **kw)

    # ----- UI -----
    def build_ui(self):
        # Header
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=20, pady=(16, 8))
        av = tk.Label(head, text="DK", bg=ACCENT, fg=ACCENT_DK, font=("Segoe UI", 14, "bold"),
                      width=3, pady=4)
        av.pack(side="left")
        t = tk.Frame(head, bg=BG)
        t.pack(side="left", padx=12)
        self.label(t, "Links Manager", INK, 15, True).pack(anchor="w")
        self.folder_lbl = self.label(t, self.folder, MUTED, 9)
        self.folder_lbl.pack(anchor="w")
        self.btn(head, "📁 Folder badlo", self.choose_folder).pack(side="right")

        # Server bar
        bar = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=LINE)
        bar.pack(fill="x", padx=20, pady=6)
        inner = tk.Frame(bar, bg=CARD)
        inner.pack(fill="x", padx=14, pady=10)
        self.dot = tk.Label(inner, text="●", bg=CARD, fg=DANGER, font=("Segoe UI", 14))
        self.dot.pack(side="left")
        self.status = self.label(inner, "Server band hai", INK, 10, True, bg=CARD)
        self.status.pack(side="left", padx=(6, 14))
        self.phone = self.label(inner, "", MUTED, 9, bg=CARD)
        self.phone.pack(side="left")
        self.start_btn = self.btn(inner, "▶  Start", self.toggle_server, "primary")
        self.start_btn.pack(side="right")
        self.open_btn = self.btn(inner, "🌐 Site kholo", self.open_site)
        self.open_btn.pack(side="right", padx=8)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=6)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2, minsize=300)
        body.rowconfigure(0, weight=1)

        # Left: list
        left = tk.Frame(body, bg=CARD, highlightthickness=1, highlightbackground=LINE)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        lh = tk.Frame(left, bg=CARD)
        lh.pack(fill="x", padx=12, pady=(10, 6))
        self.count_lbl = self.label(lh, "Saare links", INK, 11, True, bg=CARD)
        self.count_lbl.pack(side="left")
        self.btn(lh, "▼", lambda: self.move(1)).pack(side="right")
        self.btn(lh, "▲", lambda: self.move(-1)).pack(side="right", padx=4)

        wrap = tk.Frame(left, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=8)
        self.tree = ttk.Treeview(wrap, columns=("title", "bitly", "url"), show="headings",
                                 selectmode="browse")
        for c, txt, w in (("title", "NAAM", 150), ("bitly", "BITLY", 150), ("url", "URL", 220)):
            self.tree.heading(c, text=txt, anchor="w")
            self.tree.column(c, width=w, anchor="w")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())

        act = tk.Frame(left, bg=CARD)
        act.pack(fill="x", padx=12, pady=10)
        self.btn(act, "Copy Bitly", lambda: self.copy_sel("bitly")).pack(side="left")
        self.btn(act, "Copy URL", lambda: self.copy_sel("url")).pack(side="left", padx=6)
        self.btn(act, "✏ Edit", self.edit_selected).pack(side="left")
        self.btn(act, "🗑 Delete", self.delete_selected, "danger").pack(side="right")

        # Right: form
        right = tk.Frame(body, bg=CARD, highlightthickness=1, highlightbackground=LINE)
        right.grid(row=0, column=1, sticky="nsew")
        f = tk.Frame(right, bg=CARD)
        f.pack(fill="both", expand=True, padx=16, pady=14)
        self.form_title = self.label(f, "➕ Naya link", INK, 12, True, bg=CARD)
        self.form_title.pack(anchor="w")

        self.label(f, "⚡ Quick paste (bitly + url ek saath paste karo)", MUTED, 9, bg=CARD)\
            .pack(anchor="w", pady=(12, 3))
        self.quick = self.entry(f)
        self.quick.pack(fill="x", ipady=6)
        self.quick.bind("<KeyRelease>", self.on_quick)
        self.quick.bind("<<Paste>>", lambda e: self.after(50, self.on_quick))

        tk.Frame(f, bg=LINE, height=1).pack(fill="x", pady=14)

        self.v_url, self.v_bitly, self.v_title = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for text, var in (("🔗 URL (zaroori)", self.v_url),
                          ("✂ Bitly (optional)", self.v_bitly),
                          ("🏷 Naam (optional - khali chhodo to khud ban jayega)", self.v_title)):
            self.label(f, text, MUTED, 9, bg=CARD).pack(anchor="w", pady=(0, 3))
            self.entry(f, var).pack(fill="x", ipady=6, pady=(0, 10))

        row = tk.Frame(f, bg=CARD)
        row.pack(fill="x", pady=(4, 0))
        self.save_btn = self.btn(row, "💾  Add link", self.save_form, "primary")
        self.save_btn.pack(side="left", fill="x", expand=True)
        self.btn(row, "Clear", self.clear_form).pack(side="left", padx=(8, 0))

        # Toast
        self.toast = tk.Label(self, text="", bg=BG, fg=ACCENT, font=("Segoe UI", 10, "bold"))
        self.toast.pack(fill="x", pady=(0, 8))

    # ----- toast -----
    def say(self, msg, color=ACCENT):
        self.toast.config(text=msg, fg=color)
        if self.toast_job:
            self.after_cancel(self.toast_job)
        self.toast_job = self.after(2500, lambda: self.toast.config(text=""))

    # ----- data -----
    def load_links(self):
        self.links = []
        try:
            with open(self.json_path, encoding="utf-8") as f:
                raw = json.load(f)
            for o in raw:
                self.links.append({
                    "title": o.get("title", ""),
                    "bitly": clean_bitly(o.get("bitly") or o.get("shortLink") or ""),
                    "url": o.get("url") or o.get("destination") or "",
                })
        except FileNotFoundError:
            self.say("links.json nahi mili - pehla link add karte hi ban jayegi", MUTED)
        except Exception as e:
            messagebox.showerror("Error", "links.json padh nahi paya:\n%s" % e)
        self.refresh()

    def write_links(self):
        out = []
        for l in self.links:
            e = {}
            if l["title"]:
                e["title"] = l["title"]
            if l["bitly"]:
                e["bitly"] = l["bitly"]
            e["url"] = l["url"]
            out.append(e)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

    def auto_title(self, l):
        if l["title"]:
            return l["title"]
        m = re.match(r"https?://(?:www\.)?([^/]+)", l["url"])
        return (m.group(1) if m else l["bitly"]) + "  (auto)"

    def refresh(self, select=None):
        self.tree.delete(*self.tree.get_children())
        for i, l in enumerate(self.links):
            self.tree.insert("", "end", iid=str(i),
                             values=(self.auto_title(l), l["bitly"] or "—", l["url"]))
        self.count_lbl.config(text="Saare links  (%d)" % len(self.links))
        if select is not None and 0 <= select < len(self.links):
            self.tree.selection_set(str(select))
            self.tree.see(str(select))

    def sel(self):
        s = self.tree.selection()
        return int(s[0]) if s else None

    # ----- form -----
    def on_quick(self, e=None):
        text = self.quick.get()
        if not text.strip():
            return
        b, u = smart_split(text)
        if b:
            self.v_bitly.set(b)
        if u:
            self.v_url.set(u)

    def clear_form(self):
        self.edit_index = None
        for v in (self.v_url, self.v_bitly, self.v_title):
            v.set("")
        self.quick.delete(0, "end")
        self.form_title.config(text="➕ Naya link")
        self.save_btn.config(text="💾  Add link")

    def save_form(self):
        url = clean_url(self.v_url.get())
        if not url:
            self.say("URL daalna zaroori hai", DANGER)
            return
        item = {"title": self.v_title.get().strip(),
                "bitly": clean_bitly(self.v_bitly.get()), "url": url}
        if self.edit_index is None:
            self.links.append(item)
            idx = len(self.links) - 1
            self.say("✓ Link add ho gaya")
        else:
            idx = self.edit_index
            self.links[idx] = item
            self.say("✓ Link update ho gaya")
        try:
            self.write_links()
        except Exception as e:
            messagebox.showerror("Error", "Save nahi hua:\n%s" % e)
            return
        self.clear_form()
        self.refresh(idx)

    def edit_selected(self):
        i = self.sel()
        if i is None:
            self.say("Pehle list me se link chuno", MUTED)
            return
        l = self.links[i]
        self.edit_index = i
        self.v_url.set(l["url"])
        self.v_bitly.set(l["bitly"])
        self.v_title.set(l["title"])
        self.form_title.config(text="✏ Link edit ho raha hai")
        self.save_btn.config(text="💾  Update link")

    def delete_selected(self):
        i = self.sel()
        if i is None:
            return
        if messagebox.askyesno("Delete", "Ye link delete karein?\n\n%s" % self.auto_title(self.links[i])):
            del self.links[i]
            self.write_links()
            self.clear_form()
            self.refresh(min(i, len(self.links) - 1))
            self.say("Link delete ho gaya", MUTED)

    def move(self, d):
        i = self.sel()
        if i is None:
            return
        j = i + d
        if 0 <= j < len(self.links):
            self.links[i], self.links[j] = self.links[j], self.links[i]
            self.write_links()
            self.refresh(j)

    def copy_sel(self, key):
        i = self.sel()
        if i is None:
            self.say("Pehle list me se link chuno", MUTED)
            return
        val = self.links[i][key]
        if not val:
            self.say("Is link me %s nahi hai" % key, DANGER)
            return
        if key == "bitly":
            val = "https://" + val
        self.clipboard_clear()
        self.clipboard_append(val)
        self.say("✓ %s copy ho gaya" % ("Bitly" if key == "bitly" else "URL"))

    # ----- folder -----
    def choose_folder(self):
        p = filedialog.askdirectory(initialdir=self.folder, title="Site wala folder chuno")
        if p:
            was = self.httpd is not None
            if was:
                self.stop_server()
            self.folder = os.path.normpath(p)
            self.save_folder()
            self.folder_lbl.config(text=self.folder)
            self.clear_form()
            self.load_links()
            if was:
                self.start_server()

    # ----- server -----
    def toggle_server(self):
        self.stop_server() if self.httpd else self.start_server()

    def start_server(self):
        if not os.path.exists(os.path.join(self.folder, "index.html")):
            messagebox.showwarning("index.html nahi mili", "Is folder me index.html nahi hai:\n%s" % self.folder)
            return
        handler = functools.partial(QuietHandler, directory=self.folder)
        port = 8000
        while port < 8030:
            try:
                self.httpd = http.server.ThreadingHTTPServer(("", port), handler)
                break
            except OSError:
                port += 1
        if not self.httpd:
            messagebox.showerror("Error", "Koi port khali nahi mila")
            return
        self.port = port
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.dot.config(fg=ACCENT)
        self.status.config(text="Chal raha hai  •  localhost:%d" % port)
        ip = get_lan_ip()
        self.phone.config(text=("📱 Phone: http://%s:%d" % (ip, port)) if ip else "")
        self.start_btn.config(text="■  Stop")
        self.open_site()

    def stop_server(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        self.dot.config(fg=DANGER)
        self.status.config(text="Server band hai")
        self.phone.config(text="")
        self.start_btn.config(text="▶  Start")

    def open_site(self):
        if not self.httpd:
            self.start_server()
            return
        webbrowser.open("http://localhost:%d" % self.port)

    def on_close(self):
        self.stop_server()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
