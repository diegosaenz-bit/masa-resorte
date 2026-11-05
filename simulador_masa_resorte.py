"""Simulador educativo de movimiento armónico simple masa-resorte.
Ejecutar: python simulador_masa_resorte.py (Python 3, sin librerías externas).
"""
import math
import time
import tkinter as tk
from tkinter import ttk, messagebox

class Simulador:
    def __init__(self, root):
        self.root = root
        root.title('Laboratorio virtual | Sistema masa-resorte')
        root.geometry('1050x680')
        root.minsize(850, 570)
        root.configure(bg='#0b1220')
        self.running = False
        self.t = 0.0
        self.last_tick = time.monotonic()
        self.m = 0.5
        self.k = 20.0
        self.A = 0.12
        self.speed = 1.0
        self.make_ui()
        self.read_settings()
        self.draw()
        self.tick()

    def make_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TScale', background='#17243a')
        style.configure('TButton', padding=8, font=('Segoe UI', 10, 'bold'))
        header = tk.Frame(self.root, bg='#0b1220')
        header.pack(fill='x', padx=24, pady=(16, 12))
        tk.Label(header, text='SISTEMA MASA–RESORTE', font=('Segoe UI', 21, 'bold'),
                 fg='#edf3ff', bg='#0b1220').pack(anchor='w')
        tk.Label(header, text='Movimiento armónico simple • modelo ideal sin fricción',
                 font=('Segoe UI', 10), fg='#9badc8', bg='#0b1220').pack(anchor='w')
        main = tk.Frame(self.root, bg='#0b1220')
        main.pack(fill='both', expand=True, padx=24, pady=(0, 20))
        side = tk.Frame(main, bg='#17243a', width=267)
        side.pack(side='left', fill='y', padx=(0, 14))
        side.pack_propagate(False)
        tk.Label(side, text='Parámetros', fg='#f5f8ff', bg='#17243a',
                 font=('Segoe UI', 15, 'bold')).pack(anchor='w', padx=17, pady=(18, 10))
        self.vars = {}
        for key, title, lo, hi, initial, unit in [
            ('m', 'Masa', 0.1, 5.0, 0.5, 'kg'),
            ('k', 'Constante del resorte', 1.0, 100.0, 20.0, 'N/m'),
            ('A', 'Amplitud', 0.02, 0.25, 0.12, 'm'),
            ('speed', 'Velocidad de visualización', 0.25, 3.0, 1.0, '×'),
        ]:
            frame = tk.Frame(side, bg='#17243a')
            frame.pack(fill='x', padx=17, pady=9)
            lab = tk.Label(frame, fg='#dce7fa', bg='#17243a', font=('Segoe UI', 10))
            lab.pack(anchor='w')
            v = tk.DoubleVar(value=initial)
            self.vars[key] = v
            v.trace_add('write', lambda *a: self.update_labels())
            scale = ttk.Scale(frame, from_=lo, to=hi, variable=v, command=lambda _: self.on_change())
            scale.pack(fill='x', pady=(4, 0))
            self.vars[key+'_label'] = (lab, title, unit)
        controls = tk.Frame(side, bg='#17243a')
        controls.pack(fill='x', padx=17, pady=(23, 7))
        self.start_btn = ttk.Button(controls, text='▶ Iniciar', command=self.toggle)
        self.start_btn.pack(side='left', fill='x', expand=True, padx=(0, 6))
        ttk.Button(controls, text='↺ Reiniciar', command=self.reset).pack(side='left', fill='x', expand=True)
        tk.Label(side, text='Desplazamiento inicial x(0) = A\nVelocidad inicial v(0) = 0',
                 fg='#a7bad5', bg='#17243a', justify='left', font=('Segoe UI', 9)).pack(anchor='w', padx=17, pady=(15, 0))
        right = tk.Frame(main, bg='#0b1220')
        right.pack(side='left', fill='both', expand=True)
        self.canvas = tk.Canvas(right, bg='#101d30', highlightthickness=0, height=320)
        self.canvas.pack(fill='both', expand=True)
        metrics = tk.Frame(right, bg='#0b1220')
        metrics.pack(fill='x', pady=(12, 0))
        self.metrics = {}
        for i, (key, title) in enumerate([('t','Tiempo'),('x','Posición'),('v','Velocidad'),('a','Aceleración'),('T','Período'),('E','Energía total')]):
            box = tk.Frame(metrics, bg='#17243a', padx=12, pady=12)
            box.grid(row=i//3, column=i%3, sticky='nsew', padx=(0 if i%3==0 else 7, 0), pady=(0 if i<3 else 7, 0))
            metrics.columnconfigure(i%3, weight=1)
            tk.Label(box, text=title, fg='#9badc8', bg='#17243a', font=('Segoe UI', 9)).pack(anchor='w')
            val = tk.Label(box, text='—', fg='#ecf5ff', bg='#17243a', font=('Segoe UI', 14, 'bold'))
            val.pack(anchor='w', pady=(3, 0))
            self.metrics[key] = val
        self.update_labels()

    def read_settings(self):
        self.m = float(self.vars['m'].get())
        self.k = float(self.vars['k'].get())
        self.A = float(self.vars['A'].get())
        self.speed = float(self.vars['speed'].get())
        self.w = math.sqrt(self.k/self.m)
        self.T = 2*math.pi/self.w
        self.E = 0.5*self.k*self.A**2

    def update_labels(self):
        for key in ('m', 'k', 'A', 'speed'):
            if key+'_label' not in self.vars:
                continue
            lab, title, unit = self.vars[key+'_label']
            lab.config(text=f'{title}: {self.vars[key].get():.2f} {unit}')

    def on_change(self):
        if not hasattr(self, 'canvas'):
            return
        self.read_settings()
        self.t = 0.0
        self.last_tick = time.monotonic()
        self.draw()

    def toggle(self):
        self.running = not self.running
        self.last_tick = time.monotonic()
        self.start_btn.config(text='❚❚ Pausar' if self.running else '▶ Iniciar')

    def reset(self):
        self.running = False
        self.start_btn.config(text='▶ Iniciar')
        self.t = 0.0
        self.last_tick = time.monotonic()
        self.draw()

    def tick(self):
        now = time.monotonic()
        dt = min(now-self.last_tick, 0.08)
        self.last_tick = now
        if self.running:
            self.t += dt*self.speed
            self.draw()
        self.root.after(25, self.tick)

    def draw(self):
        c = self.canvas
        c.delete('all')
        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 310)
        x = self.A*math.cos(self.w*self.t)
        v = -self.A*self.w*math.sin(self.w*self.t)
        a = -self.w*self.w*x
        y = min(h*0.38, h-155)
        anchor = 58
        equilibrium = w*0.57
        block_x = equilibrium + x*min(w*0.8, 850)
        block_w = 72
        c.create_text(20, 20, anchor='nw', text='Oscilación horizontal', font=('Segoe UI', 13, 'bold'), fill='#e2ecff')
        c.create_line(anchor, y-65, anchor, y+60, fill='#9badc8', width=7)
        for i in range(9):
            c.create_line(anchor-15,y-62+i*15,anchor,y-47+i*15,fill='#768ba6',width=2)
        c.create_line(anchor, y+42, w-34, y+42, fill='#53657e', width=3)
        c.create_line(equilibrium, y-76, equilibrium, y+80, fill='#4c779a', dash=(5,5), width=2)
        c.create_text(equilibrium,y+96,text='Equilibrio (x = 0)',fill='#8ca6c6',font=('Segoe UI',9))
        left = anchor+7
        right = block_x-block_w/2
        n = 15
        coords = [left,y]
        length = right-left
        for j in range(1,2*n):
            coords.extend([left+length*j/(2*n),y+(-15 if j%2 else 15)])
        coords.extend([right,y])
        c.create_line(*coords, fill='#65d0ef', width=3, smooth=False)
        c.create_rectangle(block_x-block_w/2,y-40,block_x+block_w/2,y+40,
                           fill='#4d92ed',outline='#9bcbff',width=2)
        c.create_text(block_x,y,text='m',font=('Segoe UI',19,'bold'),fill='white')
        c.create_text(w-18,22,anchor='ne',text=f'ω = {self.w:.2f} rad/s',font=('Segoe UI',10),fill='#b6cbe6')
        chart_left, chart_right = 52,w-30
        chart_top, chart_bottom = h-119,h-35
        c.create_text(23,chart_top-22,anchor='w',text='Posición x(t)',font=('Segoe UI',10,'bold'),fill='#e2ecff')
        c.create_line(chart_left,(chart_top+chart_bottom)/2,chart_right,(chart_top+chart_bottom)/2,fill='#4b617b')
        c.create_line(chart_left,chart_top,chart_left,chart_bottom,fill='#7288a8')
        # Dibuja una ventana temporal equivalente a tres períodos.
        period_window = 3*self.T
        t0 = max(0,self.t-period_window*.5)
        points=[]
        for i in range(250):
            tt=t0+period_window*i/249
            xx=self.A*math.cos(self.w*tt)
            points.extend([chart_left+(chart_right-chart_left)*i/249,
                           (chart_top+chart_bottom)/2 - (xx/max(self.A,.01))*30])
        c.create_line(*points,fill='#60e5b4',width=2,smooth=True)
        idx=(self.t-t0)/period_window
        if 0<=idx<=1:
            px=chart_left+idx*(chart_right-chart_left)
            py=(chart_top+chart_bottom)/2-(x/self.A)*30
            c.create_oval(px-5,py-5,px+5,py+5,fill='#fff1a6',outline='')
        for key,value in [('t',f'{self.t:.2f} s'),('x',f'{x:+.3f} m'),('v',f'{v:+.3f} m/s'),
                          ('a',f'{a:+.3f} m/s²'),('T',f'{self.T:.3f} s'),('E',f'{self.E:.4f} J')]:
            self.metrics[key].config(text=value)

if __name__ == '__main__':
    root=tk.Tk()
    Simulador(root)
    root.mainloop()
