"""
Presentación animada: Motores de búsqueda y navegadores web
------------------------------------------------------------
Requisitos: solo Python 3 (tkinter viene incluido).
Ejecutar:   python presentacion_buscadores.py

Controles:
  → / Espacio / clic   siguiente diapositiva
  ←                    diapositiva anterior
  A                    activar/desactivar avance automático
  F                    pantalla completa
  Esc                  salir
"""

import math
import random
import time
import tkinter as tk

W, H = 1280, 720
BG = "#0f172a"
CARD = "#1e293b"
FG = "#e2e8f0"
MUTED = "#94a3b8"
ACC = "#38bdf8"
ACC2 = "#f472b6"
GREEN = "#4ade80"
YELLOW = "#facc15"
AUTO_SECONDS = 7


# ---------------------------------------------------------------- utilidades
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(c1, c2, p):
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    r = [int(a[i] + (b[i] - a[i]) * p) for i in range(3)]
    return "#%02x%02x%02x" % tuple(r)


def ease(p):
    return 1 - (1 - p) ** 3


def prog(t, delay, dur=0.6):
    """Progreso 0..1 con suavizado, empezando en `delay` segundos."""
    return ease(min(max((t - delay) / dur, 0), 1))


def round_rect_points(x1, y1, x2, y2, r=18):
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


# ---------------------------------------------------------------- aplicación
class Presentacion:
    def __init__(self, root):
        self.root = root
        root.title("Motores y navegadores de búsqueda")
        self.c = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.c.pack(fill="both", expand=True)

        self.slides = [
            self.s_titulo, self.s_navegador, self.s_motor, self.s_diferencia,
            self.s_funcionamiento, self.s_navegadores, self.s_motores, self.s_final,
        ]
        self.idx = 0
        self.t0 = time.time()
        self.auto = False
        self.particles = [
            [random.uniform(0, W), random.uniform(0, H),
             random.uniform(-12, 12), random.uniform(-12, 12),
             random.uniform(2, 5)] for _ in range(45)
        ]
        self.last = time.time()

        root.bind("<Right>", lambda e: self.go(1))
        root.bind("<space>", lambda e: self.go(1))
        root.bind("<Left>", lambda e: self.go(-1))
        root.bind("<Button-1>", lambda e: self.go(1))
        root.bind("<a>", lambda e: self.toggle_auto())
        root.bind("<f>", lambda e: self.toggle_full())
        root.bind("<Escape>", lambda e: root.destroy())
        self.loop()

    # ---- control
    def go(self, d):
        n = self.idx + d
        if 0 <= n < len(self.slides):
            self.idx = n
            self.t0 = time.time()

    def toggle_auto(self):
        self.auto = not self.auto
        self.t0 = time.time()

    def toggle_full(self):
        full = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not full)

    # ---- bucle de animación (~30 fps)
    def loop(self):
        now = time.time()
        dt = now - self.last
        self.last = now
        t = now - self.t0
        self.c.delete("all")
        self.fondo(dt)
        self.slides[self.idx](t)
        self.pie()
        if self.auto and t > AUTO_SECONDS:
            if self.idx < len(self.slides) - 1:
                self.go(1)
        self.root.after(33, self.loop)

    # ---- elementos comunes
    def fondo(self, dt):
        for p in self.particles:
            p[0] = (p[0] + p[2] * dt) % W
            p[1] = (p[1] + p[3] * dt) % H
            col = blend(BG, "#334155", 0.8)
            self.c.create_oval(p[0] - p[4], p[1] - p[4], p[0] + p[4], p[1] + p[4],
                               fill=col, outline="")

    def pie(self):
        n = len(self.slides)
        x0 = W / 2 - (n - 1) * 14
        for i in range(n):
            col = ACC if i == self.idx else "#334155"
            r = 6 if i == self.idx else 4
            self.c.create_oval(x0 + i * 28 - r, H - 28 - r, x0 + i * 28 + r, H - 28 + r,
                               fill=col, outline="")
        if self.auto:
            self.c.create_text(W - 20, H - 20, text="AUTO", fill=MUTED,
                               font=("Helvetica", 10), anchor="e")

    def txt(self, t, x, y, s, size=28, color=FG, delay=0.0, bold=False,
            anchor="w", rise=30):
        p = prog(t, delay)
        if p <= 0:
            return
        self.c.create_text(x, y + (1 - p) * rise, text=s, fill=blend(BG, color, p),
                           font=("Helvetica", size, "bold" if bold else "normal"),
                           anchor=anchor)

    def titulo(self, t, s):
        self.txt(t, 70, 70, s, size=40, color=ACC, bold=True)
        p = prog(t, 0.2, 0.8)
        self.c.create_line(70, 108, 70 + 420 * p, 108, fill=ACC2, width=4)

    def card(self, t, x1, y1, x2, y2, delay=0.0, fill=CARD, outline="#334155"):
        p = prog(t, delay)
        if p <= 0:
            return 0
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        hw, hh = (x2 - x1) / 2 * p, (y2 - y1) / 2 * p
        self.c.create_polygon(
            round_rect_points(cx - hw, cy - hh, cx + hw, cy + hh, 18),
            smooth=True, fill=fill, outline=outline, width=2)
        return p

    # ============================================================ DIAPOSITIVAS
    def s_titulo(self, t):
        # lupa pulsante
        pulso = 1 + 0.06 * math.sin(t * 3)
        p = prog(t, 0.1, 1.0)
        cx, cy, r = 640, 250, 70 * pulso * p
        self.c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=ACC, width=10)
        self.c.create_line(cx + r * 0.7, cy + r * 0.7, cx + r * 1.6, cy + r * 1.6,
                           fill=ACC2, width=14, capstyle="round")
        self.txt(t, 640, 430, "Motores y Navegadores", 54, FG, 0.6, True, "center")
        self.txt(t, 640, 495, "de Búsqueda", 54, ACC, 0.9, True, "center")
        self.txt(t, 640, 580, "¿Cómo encontramos y vemos la información en Internet?",
                 22, MUTED, 1.5, anchor="center")
        self.txt(t, 640, 640, "→ para comenzar", 14, MUTED, 2.2, anchor="center")

    def s_navegador(self, t):
        self.titulo(t, "¿Qué es un navegador web?")
        # ventana de navegador simulada
        if self.card(t, 70, 150, 700, 600, 0.3, outline=ACC) > 0.9:
            self.c.create_oval(95, 170, 109, 184, fill="#ef4444", outline="")
            self.c.create_oval(118, 170, 132, 184, fill=YELLOW, outline="")
            self.c.create_oval(141, 170, 155, 184, fill=GREEN, outline="")
            self.c.create_polygon(round_rect_points(100, 205, 670, 245, 14),
                                  smooth=True, fill=BG, outline="#334155")
            url = "https://www.ejemplo.com"
            n = int(max(0, t - 1.2) * 14)
            cursor = "|" if int(t * 2) % 2 == 0 else ""
            self.c.create_text(115, 225, text=url[:n] + cursor, fill=FG,
                               font=("Courier", 16), anchor="w")
            if n > len(url):
                q = min(1, (t - 1.2 - len(url) / 14) / 0.8)
                for i in range(4):
                    w = (540 - i * 70) * max(0, min(1, q * 1.4 - i * 0.2))
                    self.c.create_rectangle(100, 280 + i * 55, 100 + w, 305 + i * 55,
                                            fill="#334155", outline="")
        puntos = [
            "Programa que usas para ver páginas web",
            "Pide el contenido a un servidor (HTTP/HTTPS)",
            "Interpreta HTML, CSS y JavaScript",
            "Muestra la página: texto, imágenes y video",
            "Ejemplos: Chrome, Firefox, Safari, Edge",
        ]
        for i, s in enumerate(puntos):
            self.txt(t, 740, 190 + i * 80, "▸ " + s, 21, FG, 1.0 + i * 0.5)

    def s_motor(self, t):
        self.titulo(t, "¿Qué es un motor de búsqueda?")
        self.card(t, 70, 150, 1210, 235, 0.3, outline=ACC2)
        q = "mejores navegadores web"
        n = int(max(0, t - 1.0) * 12)
        cursor = "|" if int(t * 2) % 2 == 0 else ""
        if prog(t, 0.6) > 0.9:
            self.c.create_text(110, 192, text="🔍  " + q[:n] + cursor, fill=FG,
                               font=("Helvetica", 24), anchor="w")
        resultados = [
            ("Comparativa de navegadores 2026", "sitio-tecnologia.com"),
            ("Chrome vs Firefox vs Edge", "blog-informatica.net"),
            ("Navegadores que protegen tu privacidad", "seguridad-digital.org"),
        ]
        base = 1.0 + len(q) / 12 + 0.3
        for i, (ti, url) in enumerate(resultados):
            y = 290 + i * 100
            self.txt(t, 90, y, url, 14, GREEN, base + i * 0.5, rise=15)
            self.txt(t, 90, y + 30, ti, 24, ACC, base + i * 0.5 + 0.15, rise=15)
        self.txt(t, 90, 620,
                 "Es un servicio que busca en un enorme índice de páginas y "
                 "te devuelve las más relevantes.",
                 18, MUTED, base + 2.0)

    def s_diferencia(self, t):
        self.titulo(t, "No son lo mismo")
        # izquierda: navegador
        self.card(t, 70, 160, 560, 560, 0.4, outline=ACC)
        self.txt(t, 315, 210, "NAVEGADOR", 30, ACC, 0.8, True, "center")
        self.txt(t, 315, 280, "El programa para", 22, FG, 1.2, anchor="center")
        self.txt(t, 315, 312, "entrar y ver la web", 22, FG, 1.2, anchor="center")
        for i, s in enumerate(["Chrome", "Firefox", "Safari", "Edge"]):
            self.txt(t, 315, 385 + i * 36, s, 20, MUTED, 1.6 + i * 0.25, anchor="center")
        # derecha: motor
        self.card(t, 720, 160, 1210, 560, 0.8, outline=ACC2)
        self.txt(t, 965, 210, "MOTOR DE BÚSQUEDA", 30, ACC2, 1.2, True, "center")
        self.txt(t, 965, 280, "El servicio que", 22, FG, 1.6, anchor="center")
        self.txt(t, 965, 312, "encuentra páginas", 22, FG, 1.6, anchor="center")
        for i, s in enumerate(["Google", "Bing", "DuckDuckGo", "Brave Search"]):
            self.txt(t, 965, 385 + i * 36, s, 20, MUTED, 2.0 + i * 0.25, anchor="center")
        # símbolo central
        p = prog(t, 1.4, 0.8)
        if p > 0:
            self.c.create_text(640, 360, text="≠", fill=YELLOW,
                               font=("Helvetica", int(70 * p), "bold"))
        self.txt(t, 640, 625,
                 "Usas un navegador (Chrome) para abrir un motor de búsqueda (Google).",
                 19, MUTED, 3.2, anchor="center")

    def s_funcionamiento(self, t):
        self.titulo(t, "¿Cómo funciona un motor de búsqueda?")
        pasos = [
            ("1. RASTREO", "Robots (crawlers)\nrecorren enlaces\ny descubren páginas", ACC),
            ("2. INDEXACIÓN", "Se analiza y guarda\nel contenido en un\ngran índice", ACC2),
            ("3. RANKING", "Se ordenan los\nresultados según\nrelevancia y calidad", GREEN),
        ]
        xs = [70, 470, 870]
        for i, (tit, desc, col) in enumerate(pasos):
            d = 0.4 + i * 0.9
            if self.card(t, xs[i], 200, xs[i] + 340, 470, d, outline=col) > 0.9:
                self.txt(t, xs[i] + 170, 250, tit, 26, col, d + 0.5, True, "center", 10)
                for j, line in enumerate(desc.split("\n")):
                    self.txt(t, xs[i] + 170, 320 + j * 36, line, 20, FG,
                             d + 0.8 + j * 0.15, anchor="center", rise=10)
        # flechas
        for i in range(2):
            if prog(t, 1.0 + i * 0.9) > 0.5:
                x = xs[i] + 340
                self.c.create_line(x + 8, 335, x + 52, 335, fill=MUTED, width=4,
                                   arrow="last", arrowshape=(14, 16, 6))
        # punto viajero (datos fluyendo)
        if t > 3.5:
            f = ((t - 3.5) * 0.25) % 1
            x = 90 + f * (1060 - 90 + 120)
            self.c.create_oval(x - 9, 530 - 9, x + 9, 530 + 9, fill=YELLOW, outline="")
            self.c.create_line(90, 530, 1190, 530, fill="#334155", width=3)
            self.txt(t, 640, 585, "Cuando buscas, el motor consulta su índice "
                     "(no la web en vivo) y responde en milisegundos.",
                     18, MUTED, 0, anchor="center", rise=0)

    def s_navegadores(self, t):
        self.titulo(t, "Navegadores más usados")
        datos = [("Chrome", 65, "#4ade80"), ("Safari", 18, ACC), ("Edge", 5, "#60a5fa"),
                 ("Firefox", 2.5, "#fb923c"), ("Opera", 2, ACC2)]
        escala = 780 / 65
        for i, (n, v, col) in enumerate(datos):
            y = 170 + i * 80
            d = 0.4 + i * 0.35
            self.txt(t, 70, y + 22, n, 24, FG, d, True)
            p = prog(t, d, 1.0)
            w = v * escala * p
            if p > 0:
                self.c.create_polygon(round_rect_points(230, y, 230 + max(w, 12), y + 46, 12),
                                      smooth=True, fill=col, outline="")
                self.c.create_text(240 + w, y + 23, text=f"{v * p:.1f}%", fill=FG,
                                   font=("Helvetica", 18, "bold"), anchor="w")
        self.txt(t, 70, 620,
                 "Cuota de mercado aproximada; varía según la fuente y el año "
                 "(StatCounter, etc.).", 15, MUTED, 2.5)

    def s_motores(self, t):
        self.titulo(t, "Motores de búsqueda populares")
        motores = [
            ("Google", "El más usado del mundo", ACC),
            ("Bing", "De Microsoft; integrado en Edge", "#60a5fa"),
            ("DuckDuckGo", "Enfocado en privacidad", "#fb923c"),
            ("Brave Search", "Independiente y privado", ACC2),
            ("Baidu", "Líder en China", "#f87171"),
            ("Yahoo!", "Clásico de la web", "#a78bfa"),
        ]
        for i, (n, d, col) in enumerate(motores):
            x = 70 + (i % 3) * 395
            y = 160 + (i // 3) * 220
            dl = 0.4 + i * 0.4
            if self.card(t, x, y, x + 365, y + 190, dl, outline=col) > 0.9:
                self.txt(t, x + 182, y + 70, n, 30, col, dl + 0.4, True, "center", 10)
                self.txt(t, x + 182, y + 125, d, 16, FG, dl + 0.6, anchor="center", rise=10)

    def s_final(self, t):
        self.titulo(t, "Conclusiones y consejos")
        items = [
            ("🌐", "El navegador te lleva a la web; el motor te ayuda a encontrar en ella."),
            ("🔎", "Usa palabras clave claras y comillas para frases exactas."),
            ("🔒", "Si te importa la privacidad, prueba DuckDuckGo o Brave."),
            ("✅", "Compara fuentes: los primeros resultados no siempre son los mejores."),
        ]
        for i, (ic, s) in enumerate(items):
            y = 190 + i * 105
            d = 0.5 + i * 0.7
            if self.card(t, 70, y - 35, 1210, y + 45, d) > 0.9:
                self.txt(t, 110, y + 5, ic, 30, FG, d + 0.3, rise=0)
                self.txt(t, 180, y + 5, s, 22, FG, d + 0.4)
        self.txt(t, 640, 650, "¡Gracias!", 36, ACC, 4.0, True, "center")


if __name__ == "_