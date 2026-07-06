import tkinter as tk
import tkinter.font
import threading, time, math, random
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk

# ── Mock ──
def record_audio():       time.sleep(0.8)
def stop_recording():     pass
def audio_to_text():      time.sleep(0.5); return "一幅山水风景画"
def generate_draw(on_image=None, prompt=None):
    images = []
    colors = [(139,92,246),(6,182,212),(236,72,153)]
    for i,c in enumerate(colors):
        img = Image.new("RGBA",(300,300),(*c,255))
        d=ImageDraw.Draw(img)
        d.rounded_rectangle([15,15,285,285],radius=36,outline="white",width=2)
        images.append(f"gen_{i}.png"); img.save(images[-1])
        if on_image: on_image(images[-1], i)
    return images
def limit_image_height(p): pass
def print_final_image():   time.sleep(1)

# ── 拍照 Mock ──
_preview_img = None
_captured_img = None

def make_preview():
    """生成模拟摄像头预览画面"""
    global _preview_img
    img = Image.new("RGB", (640, 400), (135, 180, 235))
    d = ImageDraw.Draw(img)
    # 地面
    d.rectangle([(0, 310), (640, 400)], fill=(80, 140, 70))
    # 太阳
    d.ellipse([(530, 25), (600, 95)], fill=(255, 220, 80))
    # 房子
    d.rectangle([(200, 230), (350, 380)], fill=(210, 170, 130))
    d.polygon([(180, 230), (275, 150), (370, 230)], fill=(160, 60, 40))
    d.rectangle([(250, 310), (300, 380)], fill=(100, 60, 30))
    # 山
    d.polygon([(50, 310), (200, 180), (350, 310)], fill=(100, 140, 90))
    d.polygon([(300, 310), (450, 200), (600, 310)], fill=(90, 130, 80))
    # 树
    d.rectangle([(480, 290), (500, 380)], fill=(100, 60, 30))
    d.ellipse([(430, 200), (550, 300)], fill=(50, 140, 50))
    d.ellipse([(460, 180), (520, 250)], fill=(60, 150, 60))
    # 白云
    d.ellipse([(80, 40), (160, 80)], fill=(240, 240, 250))
    d.ellipse([(120, 30), (200, 70)], fill=(245, 245, 255))
    # 十字参考线
    d.line([(320, 60), (320, 350)], fill=(255, 255, 255, 50), width=1)
    d.line([(180, 205), (460, 205)], fill=(255, 255, 255, 50), width=1)
    # 取景框
    d.rectangle([(60, 50), (580, 360)], outline=(255, 255, 255, 120), width=2)
    _preview_img = img
    return _preview_img

def capture_photo():
    """模拟拍照：把当前预览图保存"""
    global _captured_img
    if _preview_img is None:
        make_preview()
    _captured_img = _preview_img.copy()
    _captured_img.save("cap.jpg")
    return True, "ok"

def convert_to_line_art():
    """模拟 AI 处理：生成卡通风格图片"""
    if _captured_img is None:
        return False, None, "没有照片"
    result = _captured_img.copy()
    d = ImageDraw.Draw(result)
    # 在照片上叠加手绘线条效果
    for i in range(50):
        x0 = random.randint(20, 620)
        y0 = random.randint(20, 380)
        x1 = x0 + random.randint(-60, 60)
        y1 = y0 + random.randint(-60, 60)
        d.line([(x0, y0), (x1, y1)], fill=(0, 0, 0), width=random.randint(1, 3))
    # 外框
    d.rectangle([(10, 10), (630, 390)], outline=(0, 0, 0), width=3)
    result.save("processed_cap.jpg")
    return True, result, ""

def print_camera_photo():  time.sleep(1.0)

# ── 拼音数据（fallback）──
try:
    from pinyin_data import PINYIN_MAP
except ImportError:
    PINYIN_MAP = {
        "shui": "水谁睡税", "fu": "服父复富",
        "shan": "山删闪善", "feng": "风封冯奉",
        "jing": "经京精景", "hua": "画华话花",
    }

# ── 配色 ──
BG       = "#0a0a0f"
SURFACE  = "#14141f"
ACCENT   = "#8b5cf6"
ACCENT2  = "#06b6d4"
TEXT1    = "#f8fafc"
TEXT2    = "#64748b"
SUCCESS  = "#22c55e"
WARN     = "#f59e0b"
FONT     = "Microsoft YaHei UI"

# ── 工具函数 ──
def lerp_color(c1,c2,t): return tuple(int(a+(b-a)*t) for a,b in zip(c1,c2))
def hex2rgb(h): return int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)

# ── 渐变按钮 ──
class GradientButton(tk.Canvas):
    def __init__(self,master,text,size=16,w=260,h=54,color=ACCENT,command=None,**kw):
        r=kw.pop("radius",h//2); super().__init__(master,width=w,height=h,bg=BG,highlightthickness=0,cursor="hand2",**kw)
        self.color,self.command,self.r,self.w,self.h=color,command,r,w,h
        self._normal(); self.bind("<Enter>",self._hover); self.bind("<Leave>",self._normal)
        self.bind("<Button-1>",lambda e:command and command())
        self.tx=self.create_text(w//2,h//2,text=text,font=(FONT,size,"bold"),fill="#fff",tags="txt")
    def _normal(self,e=None):
        self.delete("btn"); r,w,h=self.r,self.w,self.h
        steps=20
        for i in range(steps):
            t=i/steps; y0=h*i//steps; y1=h*(i+1)//steps
            rgb=lerp_color(hex2rgb(self.color),hex2rgb("#4c1d95"),t*0.4)
            self.create_rectangle(0,y0,w,y1,fill=f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",outline="",tags="btn")
        pts=self._pts(r,w,h,0)
        self.create_polygon(pts,smooth=True,fill="",outline=self._lighten(self.color,20),width=1,tags="btn")
        self.tag_raise("txt")
    def _hover(self,e):
        self.delete("btn"); r,w,h=self.r,self.w,self.h
        steps=20
        for i in range(steps):
            t=i/steps; y0=h*i//steps; y1=h*(i+1)//steps
            rgb=lerp_color(hex2rgb(self.color),hex2rgb("#6d28d9"),t*0.5)
            self.create_rectangle(0,y0,w,y1,fill=f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",outline="",tags="btn")
        self.create_polygon(self._pts(r,w,h,2),smooth=True,fill="",outline=self._lighten(self.color,60),width=3,tags="btn")
        self.tag_raise("txt")
    def _pts(self,r,w,h,pad):
        p=pad; return [r+p,p,w-r-p,p,w-p,p,w-p,r+p,w-p,h-r-p,w-p,h-p,w-r-p,h-p,r+p,h-p,p,h-p,p,h-r-p,p,r+p,p,p,r+p,p]
    def _lighten(self,h,a): r=min(255,int(h[1:3],16)+a); g=min(255,int(h[3:5],16)+a); b=min(255,int(h[5:7],16)+a); return f"#{r:02x}{g:02x}{b:02x}"

# ── 品牌图标 ──
class BrandIcon(tk.Canvas):
    def __init__(self,master,**kw):
        super().__init__(master,width=140,height=120,bg=BG,highlightthickness=0,**kw)
        c=ACCENT
        self.create_rounded_rect(25,30,115,95,r=14,fill=c,outline="")
        self.create_rounded_rect(35,40,105,65,r=8,fill="#1a1a2e",outline="")
        self.create_rectangle(45,10,70,38,fill="#e2e8f0",outline=c,width=2)
        self.create_line(50,20,65,20,fill=c,width=2); self.create_line(50,27,62,27,fill=c,width=2)
        self.create_oval(102,72,112,82,fill=ACCENT2,outline="")
        self.create_oval(102,55,112,65,fill=WARN,outline="")
    def create_rounded_rect(self,x1,y1,x2,y2,r=10,**kw):
        pts=[x1+r,y1,x2-r,y1, x2,y1,x2,y1+r, x2,y2-r,x2,y2, x2-r,y2,x1+r,y2, x1,y2,x1,y2-r, x1,y1+r,x1,y1, x1+r,y1]
        return self.create_polygon(pts,smooth=True,**kw)

# ── 图片卡片 ──
class ImageCard(tk.Canvas):
    def __init__(self,master,index,command,**kw):
        super().__init__(master,width=220,height=220,bg=SURFACE,highlightthickness=0,cursor="hand2",**kw)
        self.index,self.command,self.selected=index,command,False
        self.img_id=None; self._ox=110; self._oy=110
        self.border=self.create_rectangle(2,2,218,218,outline=ACCENT,width=0)
        self.placeholder=self.create_text(110,110,text=f"图片 {index+1}",font=(FONT,13),fill=TEXT2)
        self.bind("<Button-1>",self._click)
        self.bind("<Enter>",self._enter); self.bind("<Leave>",self._leave)
    def _enter(self,e):
        if not self.selected: self.itemconfig(self.border,width=2,outline=ACCENT2)
    def _leave(self,e):
        if not self.selected: self.itemconfig(self.border,width=0)
    def _click(self,e): self.command(self.index)
    def set_image(self,photo):
        if self.img_id:self.delete(self.img_id)
        self.img_id=self.create_image(110,110,image=photo)
        self.itemconfig(self.placeholder,state="hidden")
    def select(self):
        self.selected=True; self.itemconfig(self.border,width=5,outline="#fbbf24")
        self._animate_select(1.0)
    def deselect(self):
        self.selected=False; self._animate_deselect(1.05)
    def _animate_select(self,t):
        if t<1.14:
            s=1+0.14*math.sin(t*math.pi/2)
            self.scale(t,self._ox,self._oy,s,s)
            self.after(16,self._animate_select,t+0.08)
        else: self.scale(t,self._ox,self._oy,1.14,1.14)
    def _animate_deselect(self,t):
        if t>1.0:
            self.scale(t,self._ox,self._oy,t,t)
            self.after(16,self._animate_deselect,t-0.02)
        else:
            if not self.selected:
                self.itemconfig(self.border,width=0)
            self.scale(t,self._ox,self._oy,1,1)
    def scale(self,origin,ox,oy,sx,sy): pass
    def reset(self):
        if self.img_id: self.delete(self.img_id); self.img_id=None
        self.itemconfig(self.placeholder,state="normal")
        self.itemconfig(self.border,width=0); self.selected=False

# ── 声波动画 ──
class Waveform(tk.Canvas):
    def __init__(self,master,**kw):
        super().__init__(master,width=300,height=80,bg=BG,highlightthickness=0,**kw)
        self.bars=[self.create_rectangle(0,0,0,0,fill=ACCENT,outline="") for _ in range(9)]
        self.running=False
    def start(self):
        self.running=True; self._tick()
    def stop(self):
        self.running=False
        for b in self.bars: self.coords(b,0,0,0,0)
    def _tick(self):
        if not self.running: return
        w=300; gap=w//9
        for i,b in enumerate(self.bars):
            h=random.randint(6,60)
            x=gap*i+6; self.coords(b,x,40-h//2,x+gap-12,40+h//2)
        self.after(80,self._tick)

# ── 旋转 Spinner ──
class Spinner(tk.Canvas):
    def __init__(self,master,size=60,**kw):
        super().__init__(master,width=size+10,height=size+10,bg=BG,highlightthickness=0,**kw)
        self.size,self.angle,self.running=size,0,False
    def start(self):
        self.running=True; self._spin()
    def stop(self):
        self.running=False; self.delete("all")
    def _spin(self):
        if not self.running: return
        self.angle=(self.angle+20)%360
        self.delete("all")
        self.create_arc(5,5,self.size+5,self.size+5,start=self.angle,extent=100,outline=ACCENT2,width=3,style="arc")
        self.after(40,self._spin)

# ── 根窗口 ──
root=tk.Tk()
root.overrideredirect(True)
root.geometry("1024x668+200+60"); root.configure(bg=BG)

bar=tk.Frame(root,bg="#050508",height=38); bar.pack(fill="x"); bar.propagate(False)
cbtn=tk.Label(bar,text="×",font=(FONT,16),fg=TEXT2,bg="#050508",padx=18,cursor="hand2")
cbtn.pack(side="right",fill="y")
cbtn.bind("<Enter>",lambda e:cbtn.config(bg="#dc2626",fg="#fff"))
cbtn.bind("<Leave>",lambda e:cbtn.config(bg="#050508",fg=TEXT2))
cbtn.bind("<Button-1>",lambda e:root.destroy())
tk.Label(bar,text="  AI 打印机  v2.0",font=(FONT,10),fg=TEXT2,bg="#050508").pack(side="left")
def move_start(e): root.x,root.y=e.x,e.y
def move_do(e): root.geometry(f"+{e.x_root-root.x}+{e.y_root-root.y}")
bar.bind("<Button-1>",move_start); bar.bind("<B1-Motion>",move_do)

main=tk.Canvas(root,bg=BG,highlightthickness=0); main.pack(fill="both",expand=True)
for i in range(40):
    t=i/40; r=int(10+5*t); g=int(10+6*t); b=int(15+12*t)
    y0=630*i//40; y1=630*(i+1)//40
    main.create_rectangle(0,y0,1024,y1,fill=f"#{r:02x}{g:02x}{b:02x}",outline="")

container=tk.Frame(main,bg=""); container.place(relwidth=1,relheight=1)

gen_imgs=[]; sel_img=None; rec_text=""
p1=p2=p3=None

_timer=None
def dots(label,base):
    def s(n=0):
        global _timer
        if not getattr(label,"_r",True):return
        d="."*(n%4); label.config(text=base+d+" "*(3-len(d)))
        _timer=label.after(350,s,n+1)
    label._r=True;s()
def stop_d(label):
    global _timer; label._r=False
    if _timer:label.after_cancel(_timer);_timer=None

def switch(page):
    page.tkraise()

# ═══════════ 语音模式业务 ═══════════
def go_record():
    switch(p2)
    end_rec_btn.pack(side="bottom", pady=60)
    rb2.pack_forget()
    wave.start()
    dots(rlbl,"正在录音")
    threading.Thread(target=do_record,daemon=True).start()

def end_recording():
    stop_recording()
    end_rec_btn.pack_forget()
    stop_d(rlbl)
    rlbl.config(text="正在识别")
    dots(rlbl, "正在识别")

def do_record():
    global rec_text
    try:
        record_audio()
        rec_text=audio_to_text()
    except Exception as e:
        rec_text=f"错误：{e}"
    finally:
        root.after(600,lambda t=rec_text: show_text(t))

def show_text(t):
    try: stop_d(rlbl); wave.stop()
    except: pass
    try:
        end_rec_btn.pack_forget()
        rb2.pack(side="bottom", pady=24)
    except: pass
    res.delete(0,'end'); res.insert(0, t); reset_pinyin(); switch(p3)

def go_gen():
    switch(pg); spin.start(); dots(glbl,"正在绘制")
    threading.Thread(target=do_gen,daemon=True).start()

def do_gen():
    global gen_imgs
    gen_imgs=[]
    prompt = res.get().strip()
    try:
        def on_img(path,idx):
            gen_imgs.append(path)
            root.after(0,lambda p=path,i=idx:on_one_img(p,i))
        generate_draw(on_image=on_img, prompt=prompt)
    except Exception as e: print(e)
    finally: root.after(0,on_gen_done)

def on_one_img(path,idx):
    global pi1,pi2,pi3
    if idx==0:
        try:stop_d(glbl);spin.stop()
        except:pass
        switch(p4)
    img=Image.open(path).resize((180,180))
    photo=ImageTk.PhotoImage(img)
    if idx==0:pi1=photo;c1.set_image(photo)
    elif idx==1:pi2=photo;c2.set_image(photo)
    else:pi3=photo;c3.set_image(photo)

def on_gen_done(): pass

def pick(i):
    global sel_img; sel_img=gen_imgs[i]
    for ci in(c1,c2,c3):ci.deselect()
    [c1,c2,c3][i].select(); stat.config(text=f"已选择图片 {i+1}",font=(FONT,15,"bold"),fg="#fbbf24")

def go_print():
    if not sel_img: stat.config(text="请先选择一张图片",font=(FONT,15,"bold"),fg=WARN); return
    switch(p5); threading.Thread(target=do_print,daemon=True).start()

def do_print():
    try: limit_image_height(sel_img); print_final_image()
    except Exception as e: print(e)
    finally: root.after(0,fin)

def fin():
    prt.config(text="打印完成",fg=SUCCESS); root.after(2500,home)

# ═══════════ 拍照模式业务 ═══════════
_preview_photo = None  # 保存当前预览的 PhotoImage 引用

def go_camera():
    """进入拍照预览页"""
    global _preview_photo
    make_preview()
    img = _preview_img.resize((640, 400))
    _preview_photo = ImageTk.PhotoImage(img)
    preview_cv.delete("all")
    preview_cv.create_image(322, 160, image=_preview_photo)
    cam_status.config(text="对准画面，点击拍照", fg=TEXT2)
    switch(pc)

def do_capture():
    """拍照：抓取当前帧"""
    capture_photo()
    global _preview_photo
    img = Image.open("cap.jpg").resize((640, 400))
    _preview_photo = ImageTk.PhotoImage(img)
    shot_cv.delete("all")
    shot_cv.create_image(322, 160, image=_preview_photo)
    switch(ps)

def retake_photo():
    """重新拍照：回到预览页"""
    go_camera()

def confirm_photo():
    """确认照片：进入 AI 处理"""
    switch(pl)
    spin2.pack(pady=15); llbl.pack(pady=8)
    spin2.start()
    dots(llbl, "正在生成卡通图片")
    threading.Thread(target=do_line_art_gen, daemon=True).start()

def do_line_art_gen():
    try:
        ok, result_img, err = convert_to_line_art()
    except Exception as e:
        ok, err = False, str(e); result_img = None
    root.after(0, lambda: on_line_art_done(ok, result_img))

def on_line_art_done(ok, result_img, err=""):
    global _preview_photo
    try: stop_d(llbl); spin2.stop()
    except: pass
    spin2.pack_forget(); llbl.pack_forget()
    if ok:
        result_img = result_img.resize((644, 320))
        _preview_photo = ImageTk.PhotoImage(result_img)
        art_cv.delete("all")
        art_cv.create_image(322, 160, image=_preview_photo)
        art_status.config(text="满意效果即可打印", fg=TEXT2)
        switch(pl)
    else:
        llbl.pack(pady=8)
        llbl.config(text=f"生成失败: {err}", fg=WARN)
        root.after(3000, home)

def confirm_print():
    """确认打印"""
    switch(pr)
    dots(cprt, "正在打印")
    threading.Thread(target=do_camera_print, daemon=True).start()

def do_camera_print():
    try: print_camera_photo()
    except Exception as e: print(e)
    root.after(0, fin_camera)

def fin_camera():
    try: stop_d(cprt)
    except: pass
    cprt.config(text="打印完成", fg=SUCCESS)
    root.after(2500, home)

def home():
    global sel_img,rec_text,gen_imgs
    sel_img=None;rec_text="";gen_imgs=[]
    try: stop_d(rlbl); wave.stop()
    except: pass
    try: stop_d(glbl); spin.stop()
    except: pass
    try: stop_d(llbl); spin2.stop()
    except: pass
    try: stop_d(cprt)
    except: pass
    try:
        end_rec_btn.pack_forget()
        rb2.pack(side="bottom", pady=24)
    except: pass
    c1.reset();c2.reset();c3.reset(); stat.config(text="点击图片选择",fg=TEXT2)
    res.delete(0,'end'); rlbl.config(text=""); glbl.config(text=""); prt.config(text="")
    reset_pinyin()
    switch(p1)

# ═══════════ 拼音输入法 ═══════════
pinyin_mode = "拼音"; pinyin_buf = ""; candidate_page = 0; current_candidates = []

def kb_clear():
    global pinyin_buf, current_candidates, candidate_page
    try: res.delete(0, 'end')
    except: pass
    pinyin_buf = ""; current_candidates = []; candidate_page = 0
    update_pinyin_display()

def kb_commit(ch):
    try: res.insert(tk.INSERT, ch)
    except: pass

def update_pinyin_display():
    if pinyin_mode == "拼音":
        mode_btn.config(text="中", bg="#06b6d4", fg="#fff")
        pbuf.config(text=pinyin_buf if pinyin_buf else "输入拼音")
        if current_candidates:
            start = candidate_page * 10
            page = current_candidates[start:start + 10]
            cand.config(text=" ".join(f"{i+1}.{c}" for i, c in enumerate(page)))
            total_pages = (len(current_candidates) - 1) // 10 + 1
            page_lbl.config(text=f"{candidate_page+1}/{total_pages}" if total_pages else "")
        else:
            cand.config(text=""); page_lbl.config(text="")
    else:
        mode_btn.config(text="En", bg="#8b5cf6", fg="#fff")
        pbuf.config(text="英文输入"); cand.config(text=""); page_lbl.config(text="")

def kb_keypress(key):
    global pinyin_buf, current_candidates, candidate_page
    if pinyin_mode == "拼音":
        if len(key) == 1 and 'a' <= key <= 'z':
            pinyin_buf += key
            matches = []
            if pinyin_buf in PINYIN_MAP: matches = list(PINYIN_MAP[pinyin_buf])
            else:
                for py, chars in PINYIN_MAP.items():
                    if py.startswith(pinyin_buf): matches.extend(list(chars))
                seen = set(); matches = [c for c in matches if not (c in seen or seen.add(c))]
            current_candidates = matches[:50]; candidate_page = 0; update_pinyin_display()
        elif key == 'back':
            if pinyin_buf:
                pinyin_buf = pinyin_buf[:-1]
                if pinyin_buf:
                    matches = []
                    if pinyin_buf in PINYIN_MAP: matches = list(PINYIN_MAP[pinyin_buf])
                    else:
                        for py, chars in PINYIN_MAP.items():
                            if py.startswith(pinyin_buf): matches.extend(list(chars))
                        seen = set(); matches = [c for c in matches if not (c in seen or seen.add(c))]
                    current_candidates = matches[:50]
                else: current_candidates = []
                candidate_page = 0
            else:
                try:
                    pos = res.index(tk.INSERT)
                    if pos > 0: res.delete(pos - 1)
                except: pass
            update_pinyin_display()
        elif key == ' ':
            if current_candidates: kb_commit(current_candidates[candidate_page * 10]); pinyin_buf = ""; current_candidates = []; candidate_page = 0
            else: kb_commit(' ')
            update_pinyin_display()
        elif '1' <= key <= '9':
            idx = int(key) - 1; start = candidate_page * 10
            if start + idx < len(current_candidates): kb_commit(current_candidates[start + idx]); pinyin_buf = ""; current_candidates = []; candidate_page = 0
            update_pinyin_display()
        elif key == '0':
            idx = 9; start = candidate_page * 10
            if start + idx < len(current_candidates): kb_commit(current_candidates[start + idx]); pinyin_buf = ""; current_candidates = []; candidate_page = 0
            update_pinyin_display()
        elif key == ',': kb_commit('，'); pinyin_buf = ""; current_candidates = []; candidate_page = 0; update_pinyin_display()
        elif key == '.': kb_commit('。'); pinyin_buf = ""; current_candidates = []; candidate_page = 0; update_pinyin_display()
    elif pinyin_mode == "En":
        if len(key) == 1 and 'a' <= key <= 'z': kb_commit(key)
        elif key == ' ': kb_commit(' ')
        elif key == 'back':
            try:
                pos = res.index(tk.INSERT)
                if pos > 0: res.delete(pos - 1)
            except: pass
        elif key == ',': kb_commit(',')
        elif key == '.': kb_commit('.')
        elif '0' <= key <= '9': kb_commit(key)

def reset_pinyin():
    global pinyin_mode, pinyin_buf, current_candidates, candidate_page
    if kb.winfo_ismapped():
        kb.pack_forget(); cand_frame.pack_forget(); pbuf.pack_forget()
        kb_toggle_btn.config(text="⌨ 打开键盘")
    pinyin_mode = "拼音"; pinyin_buf = ""; current_candidates = []; candidate_page = 0
    update_pinyin_display()

def switch_mode():
    global pinyin_mode, pinyin_buf, current_candidates, candidate_page
    pinyin_mode = "En" if pinyin_mode == "拼音" else "拼音"
    pinyin_buf = ""; current_candidates = []; candidate_page = 0; update_pinyin_display()

def cand_prev():
    global candidate_page
    if candidate_page > 0: candidate_page -= 1; update_pinyin_display()

def cand_next():
    global candidate_page
    if (candidate_page + 1) * 10 < len(current_candidates): candidate_page += 1; update_pinyin_display()

def toggle_keyboard():
    if kb.winfo_ismapped():
        kb.pack_forget(); cand_frame.pack_forget(); pbuf.pack_forget()
        kb_toggle_btn.config(text="⌨ 打开键盘")
    else:
        pbuf.pack(pady=1, before=kb_toggle_btn)
        cand_frame.pack(pady=1, before=kb_toggle_btn)
        kb.pack(pady=3, before=kb_toggle_btn)
        kb_toggle_btn.config(text="▲ 收起键盘")

# ═══════════ 页面 ═══════════
def mk(): f=tk.Frame(container,bg=BG); f.place(relwidth=1,relheight=1); return f

# P1 首页
p1=mk()
tk.Frame(p1,bg=BG,height=70).pack()
BrandIcon(p1).pack(pady=10)
tk.Label(p1,text="AI 打印机",font=(FONT,44,"bold"),fg=TEXT1,bg=BG).pack(pady=6)
tk.Label(p1,text="语音输入  ·  拍照线稿  ·  AI 绘图  ·  热敏打印",font=(FONT,14),fg=TEXT2,bg=BG).pack(pady=4)
GradientButton(p1,"开始录音",size=22,w=300,h=60,command=go_record).pack(pady=30)
GradientButton(p1,"拍照打印",size=22,w=300,h=60,color=ACCENT2,command=go_camera).pack(pady=10)
tk.Label(p1,text="Powered by RK3588",font=(FONT,9),fg="#333",bg=BG).pack(side="bottom",pady=20)

# P2 录音
p2=mk()
tk.Frame(p2,bg=BG,height=100).pack()
tk.Label(p2,text="🎤",font=(FONT,56),bg=BG).pack(pady=20)
wave=Waveform(p2); wave.pack(pady=10)
rlbl=tk.Label(p2,text="",font=(FONT,22,"bold"),fg=ACCENT,bg=BG); rlbl.pack()
rb2=tk.Label(p2,text="返回",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rb2.pack(side="bottom",pady=24)
rb2.bind("<Enter>",lambda e:rb2.config(fg=ACCENT2))
rb2.bind("<Leave>",lambda e:rb2.config(fg=TEXT2))
rb2.bind("<Button-1>",lambda e:home())

end_rec_btn = GradientButton(p2, "结束录音", size=18, w=200, color=WARN,
                              command=lambda: end_recording())
end_rec_btn.pack_forget()

# P3 结果
p3=mk()
tk.Frame(p3,bg=BG,height=10).pack()
tk.Label(p3,text="识别结果",font=(FONT,14),fg=TEXT2,bg=BG).pack(pady=2)
cf=tk.Frame(p3,bg=SURFACE); cf.pack(pady=4,ipadx=60,ipady=10)
res=tk.Entry(cf,font=(FONT,20,"bold"),fg=TEXT1,bg=SURFACE,width=30,justify="center",relief="flat"); res.pack()

_cursor_line = tk.Frame(cf, bg="#8b5cf6", width=3, height=20)
_cursor_font = tk.font.Font(font=(FONT, 20, "bold"))
_cursor_visible = True; _last_cursor_pos = -1

def _draw_cursor_at(pos):
    if pos < 0 or not _cursor_visible: _cursor_line.place_forget(); return
    try:
        text = res.get(); ex, ey = res.winfo_x(), res.winfo_y()
        ew, eh = res.winfo_width(), res.winfo_height()
        fh = _cursor_font.metrics("linespace")
        tw = _cursor_font.measure(text)
        ctr_off = max(0, (ew - tw) // 2)
        cx = ctr_off + _cursor_font.measure(text[:pos])
        cy = (eh - fh) // 2
        _cursor_line.place(x=ex + cx, y=ey + cy + 2, width=3, height=fh - 4)
    except: _cursor_line.place_forget()

def _cursor_poll():
    global _last_cursor_pos
    try:
        pos = int(res.index(tk.INSERT))
        if pos != _last_cursor_pos: _last_cursor_pos = pos; _draw_cursor_at(pos)
    except: pass
    root.after(80, _cursor_poll)

def _cursor_blink():
    global _cursor_visible
    _cursor_visible = not _cursor_visible; _draw_cursor_at(_last_cursor_pos)
    root.after(500, _cursor_blink)

def _sync_click_pos():
    global _last_cursor_pos
    try: _last_cursor_pos = int(res.index(tk.INSERT)); _draw_cursor_at(_last_cursor_pos)
    except: pass

def _on_res_click(e):
    res.focus_set(); res.selection_clear()
    global _cursor_visible; _cursor_visible = True
    try: e.widget.tk.call(e.widget._w, "icursor", f"@{e.x},{e.y}")
    except: pass
    root.after(50, _sync_click_pos)

res.bind("<Button-1>", _on_res_click)
_cursor_poll(); _cursor_blink()

kb_toggle_btn = tk.Label(p3, text="⌨ 打开键盘", font=(FONT, 12), fg=ACCENT2, bg=BG, cursor="hand2")
kb_toggle_btn.pack(pady=4)
kb_toggle_btn.bind("<Button-1>", lambda e: toggle_keyboard())
kb_toggle_btn.bind("<Enter>", lambda e: kb_toggle_btn.config(fg=ACCENT))
kb_toggle_btn.bind("<Leave>", lambda e: kb_toggle_btn.config(fg=ACCENT2))

pbuf=tk.Label(p3,text="输入拼音",font=(FONT,12),fg="#94a3b8",bg=BG)

cand_frame=tk.Frame(p3,bg=BG)
cand_prev_btn=tk.Label(cand_frame,text="◀",font=(FONT,11),fg=TEXT2,bg=BG,cursor="hand2",width=2)
cand_prev_btn.pack(side="left",padx=2)
cand=tk.Label(cand_frame,text="",font=(FONT,13),fg=TEXT1,bg=BG); cand.pack(side="left")
page_lbl=tk.Label(cand_frame,text="",font=(FONT,9),fg=TEXT2,bg=BG); page_lbl.pack(side="left",padx=4)
cand_next_btn=tk.Label(cand_frame,text="▶",font=(FONT,11),fg=TEXT2,bg=BG,cursor="hand2",width=2)
cand_next_btn.pack(side="right",padx=2)
cand_prev_btn.bind("<Button-1>",lambda e:cand_prev())
cand_next_btn.bind("<Button-1>",lambda e:cand_next())

kb=tk.Frame(p3,bg=BG)
kb_close_btn = tk.Label(kb, text="▲ 收起键盘", font=(FONT, 11), fg=TEXT2, bg=BG, cursor="hand2")
kb_close_btn.pack(pady=1)
kb_close_btn.bind("<Button-1>", lambda e: toggle_keyboard())
kb_close_btn.bind("<Enter>", lambda e: kb_close_btn.config(fg=ACCENT2))
kb_close_btn.bind("<Leave>", lambda e: kb_close_btn.config(fg=TEXT2))
mr=tk.Frame(kb,bg=BG); mr.pack()
mode_btn=tk.Label(mr,text="中",font=(FONT,12,"bold"),fg="#fff",bg="#06b6d4",width=4,height=1,cursor="hand2")
mode_btn.pack(side="left",padx=2)
mode_btn.bind("<Button-1>",lambda e:switch_mode())
for n in range(1, 11):
    b=tk.Label(mr,text=str(n % 10),font=(FONT,11),fg=TEXT1,bg="#1e293b",width=3,height=1,cursor="hand2")
    b.pack(side="left",padx=1)
    b.bind("<Button-1>",lambda e,d=str(n % 10):kb_keypress(d))
    b.bind("<Enter>",lambda e,b=b:b.config(bg=ACCENT,fg="#fff"))
    b.bind("<Leave>",lambda e,b=b:b.config(bg="#1e293b",fg=TEXT1))
qwerty_rows=[list("QWERTYUIOP"),list("ASDFGHJKL"),["Z","X","C","V","B","N","M",",","."],]
for row in qwerty_rows:
    rf=tk.Frame(kb,bg=BG); rf.pack()
    for ch in row:
        b=tk.Label(rf,text=ch,font=(FONT,13),fg=TEXT1,bg=SURFACE,width=4,height=2,cursor="hand2")
        b.pack(side="left",padx=1,pady=1)
        b.bind("<Button-1>",lambda e,c=ch.lower():kb_keypress(c))
        b.bind("<Enter>",lambda e,b=b:b.config(bg=ACCENT,fg="#fff"))
        b.bind("<Leave>",lambda e,b=b:b.config(bg=SURFACE,fg=TEXT1))
fr=tk.Frame(kb,bg=BG); fr.pack()
for text,cmd,w in [("空格",lambda:kb_keypress(' '),10),("删除",lambda:kb_keypress('back'),5),("清空",lambda:kb_clear(),5)]:
    b=tk.Label(fr,text=text,font=(FONT,12),fg=TEXT1,bg="#1e293b",width=w,height=2,cursor="hand2")
    b.pack(side="left",padx=2,pady=2)
    b.bind("<Button-1>",lambda e,f=cmd:f())
    b.bind("<Enter>",lambda e,b=b:b.config(bg=ACCENT,fg="#fff"))
    b.bind("<Leave>",lambda e,b=b:b.config(bg="#1e293b",fg=TEXT1))

GradientButton(p3,"重新录音",size=16,w=200,color=ACCENT,command=go_record).pack(pady=(6,4))
GradientButton(p3,"开始生成图片",size=18,w=280,color=ACCENT2,command=go_gen).pack(pady=(4,16))
rb3=tk.Label(p3,text="返回",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rb3.pack(side="bottom",pady=20)
rb3.bind("<Enter>",lambda e:rb3.config(fg=ACCENT2))
rb3.bind("<Leave>",lambda e:rb3.config(fg=TEXT2))
rb3.bind("<Button-1>",lambda e:home())

# PG 生成中
pg=mk()
tk.Frame(pg,bg=BG,height=80).pack()
tk.Label(pg,text="AI 正在创作",font=(FONT,24,"bold"),fg=TEXT1,bg=BG).pack(pady=20)
spin=Spinner(pg); spin.pack(pady=15)
glbl=tk.Label(pg,text="",font=(FONT,16),fg=ACCENT,bg=BG); glbl.pack(pady=8)
rbg=tk.Label(pg,text="返回",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rbg.pack(side="bottom",pady=24)
rbg.bind("<Enter>",lambda e:rbg.config(fg=ACCENT2))
rbg.bind("<Leave>",lambda e:rbg.config(fg=TEXT2))
rbg.bind("<Button-1>",lambda e:home())

# P4 选图
p4=mk()
tk.Frame(p4,bg=BG,height=25).pack()
tk.Label(p4,text="选择喜欢的图片",font=(FONT,22,"bold"),fg=TEXT1,bg=BG).pack(pady=12)
row=tk.Frame(p4,bg=BG); row.pack(pady=6)
c1=ImageCard(row,0,pick);c1.grid(row=0,column=0,padx=16)
c2=ImageCard(row,1,pick);c2.grid(row=0,column=1,padx=16)
c3=ImageCard(row,2,pick);c3.grid(row=0,column=2,padx=16)
stat=tk.Label(p4,text="点击图片选择",font=(FONT,13),fg=TEXT2,bg=BG); stat.pack(pady=10)
GradientButton(p4,"开始打印",size=18,w=240,command=go_print).pack(pady=4)
rb4=tk.Label(p4,text="返回",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rb4.pack(side="bottom",pady=24)
rb4.bind("<Enter>",lambda e:rb4.config(fg=ACCENT2))
rb4.bind("<Leave>",lambda e:rb4.config(fg=TEXT2))
rb4.bind("<Button-1>",lambda e:home())

# P5 打印
p5=mk()
tk.Frame(p5,bg=BG,height=100).pack()
tk.Label(p5,text="正在打印",font=(FONT,26,"bold"),fg=TEXT1,bg=BG).pack(pady=20)
tk.Label(p5,text="🖨",font=(FONT,56),bg=BG).pack()
prt=tk.Label(p5,text="",font=(FONT,16),fg=WARN,bg=BG); prt.pack(pady=12)
rb5=tk.Label(p5,text="返回",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rb5.pack(side="bottom",pady=24)
rb5.bind("<Enter>",lambda e:rb5.config(fg=ACCENT2))
rb5.bind("<Leave>",lambda e:rb5.config(fg=TEXT2))
rb5.bind("<Button-1>",lambda e:home())

# ═══════════ 拍照模式页面 ═══════════

# PC 实时预览
pc=mk()
tk.Frame(pc,bg=BG,height=20).pack()
tk.Label(pc,text="摄像头实时预览",font=(FONT,18,"bold"),fg=TEXT1,bg=BG).pack(pady=4)
# 预览画布
preview_cv = tk.Canvas(pc, width=644, height=320, bg="#0a0a14", highlightthickness=2,
                        highlightbackground=ACCENT2)
preview_cv.pack(pady=4)
cam_status = tk.Label(pc, text="", font=(FONT, 14), fg=TEXT2, bg=BG)
cam_status.pack(pady=4)
GradientButton(pc, "📷 拍照", size=20, w=260, color=ACCENT2, command=do_capture).pack(pady=8)
rbc=tk.Label(pc,text="返回首页",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rbc.pack(side="bottom",pady=18)
rbc.bind("<Enter>",lambda e:rbc.config(fg=ACCENT2))
rbc.bind("<Leave>",lambda e:rbc.config(fg=TEXT2))
rbc.bind("<Button-1>",lambda e:home())

# PS 拍照结果确认
ps=mk()
tk.Frame(ps,bg=BG,height=20).pack()
tk.Label(ps,text="拍照结果",font=(FONT,18,"bold"),fg=TEXT1,bg=BG).pack(pady=4)
shot_cv = tk.Canvas(ps, width=644, height=320, bg="#0a0a14", highlightthickness=2,
                     highlightbackground=SUCCESS)
shot_cv.pack(pady=4)
btn_row_ps = tk.Frame(ps, bg=BG); btn_row_ps.pack(pady=10)
GradientButton(btn_row_ps, "🔄 重新拍照", size=16, w=200, color=ACCENT, command=retake_photo).pack(side="left", padx=14)
GradientButton(btn_row_ps, "✓ 确定", size=16, w=200, color=SUCCESS, command=confirm_photo).pack(side="left", padx=14)
rbs=tk.Label(ps,text="返回首页",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rbs.pack(side="bottom",pady=18)
rbs.bind("<Enter>",lambda e:rbs.config(fg=ACCENT2))
rbs.bind("<Leave>",lambda e:rbs.config(fg=TEXT2))
rbs.bind("<Button-1>",lambda e:home())

# PL AI 卡通结果预览
pl=mk()
tk.Frame(pl,bg=BG,height=20).pack()
tk.Label(pl,text="AI 卡通效果",font=(FONT,18,"bold"),fg=TEXT1,bg=BG).pack(pady=4)
art_cv = tk.Canvas(pl, width=644, height=320, bg="#0a0a14", highlightthickness=2,
                    highlightbackground=ACCENT)
art_cv.pack(pady=4)
art_status = tk.Label(pl, text="", font=(FONT, 14), fg=TEXT2, bg=BG)
art_status.pack(pady=2)
# 处理中动画（初始隐藏）
spin2=Spinner(pl)
llbl=tk.Label(pl,text="",font=(FONT,16),fg=ACCENT,bg=BG)
# 确认打印按钮
GradientButton(pl, "🖨 确定打印", size=18, w=240, color=ACCENT2, command=confirm_print).pack(pady=8)
rbl=tk.Label(pl,text="返回首页",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rbl.pack(side="bottom",pady=18)
rbl.bind("<Enter>",lambda e:rbl.config(fg=ACCENT2))
rbl.bind("<Leave>",lambda e:rbl.config(fg=TEXT2))
rbl.bind("<Button-1>",lambda e:home())

# PR 打印中
pr=mk()
tk.Frame(pr,bg=BG,height=100).pack()
tk.Label(pr,text="正在打印",font=(FONT,26,"bold"),fg=TEXT1,bg=BG).pack(pady=20)
tk.Label(pr,text="🖨",font=(FONT,56),bg=BG).pack()
cprt=tk.Label(pr,text="",font=(FONT,16),fg=WARN,bg=BG); cprt.pack(pady=12)
rbpr=tk.Label(pr,text="返回首页",font=(FONT,13),fg=TEXT2,bg=BG,cursor="hand2")
rbpr.pack(side="bottom",pady=24)
rbpr.bind("<Enter>",lambda e:rbpr.config(fg=ACCENT2))
rbpr.bind("<Leave>",lambda e:rbpr.config(fg=TEXT2))
rbpr.bind("<Button-1>",lambda e:home())

p1.tkraise()
root.mainloop()
