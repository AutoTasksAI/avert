import cv2
import time
import numpy as np
import os
import sys
import ctypes
import tkinter as tk
import webbrowser
from tkinter import ttk, filedialog
from threading import Thread
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# --- HIGH DPI FIX ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# --- CONSTANTS ---
SECRET_UNLOCK_KEY = 96    # Backtick Key (`)
WINDOW_LOCK_NAME = "Avert Locked" 
WINDOW_PREVIEW_NAME = "Avert Camera Preview"
PRO_WEBSITE = "https://getavert.app"

# --- RESOURCE PATH LOADER ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- GLOBAL STATE ---
state = {
    "reaction_speed": 0.5,
    "strictness": 5, 
    "min_eyes": 1,        
    "running": True,
    "screen_w": 1920,
    "screen_h": 1080,
    "start_time": 0,        
    "grace_period": 10.0,   
    "fade_duration": 30,  # Ghost Fade
    "status_text": "STARTING...",
    "show_preview": True,
    "brake_until": 0,
    "contrast_boost": 1.2
}

# --- GUI CLASS ---
class AvertControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("AVERT FREE EDITION") 
        self.root.geometry("500x800") 
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.root.configure(bg="#1a1a1a")
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass
        
        FONT_HEADER = ("Segoe UI", 12, "bold")
        FONT_BODY = ("Segoe UI", 10)

        # --- LOGO LOADER ---
        logo_loaded = False
        if HAS_PIL:
            try:
                logo_path = resource_path("avert_logo.png")
                if os.path.exists(logo_path):
                    pil_img = Image.open(logo_path)
                    pil_img = pil_img.resize((100, 100), Image.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(pil_img)
                    lbl_logo = tk.Label(root, image=self.logo_img, bg="#1a1a1a")
                    lbl_logo.pack(pady=(20, 0))
                    logo_loaded = True
            except Exception as e:
                print(f"Logo load error: {e}")
        
        if not logo_loaded:
            tk.Label(root, text="[AVERT FREE]", font=("Segoe UI", 14, "bold"), bg="#1a1a1a", fg="#333").pack(pady=(20,0))

        # Main Title
        lbl_title = tk.Label(root, text="AVERT FREE", font=("Segoe UI", 20, "bold"), fg="#ffffff", bg="#1a1a1a")
        lbl_title.pack(fill="x", pady=(10, 5))
        
        # Upsell Button
        btn_upsell = tk.Button(root, text="⚡ UPGRADE TO PRO ⚡", command=self.open_site, bg="#00aa00", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_upsell.pack(pady=(0, 15), ipadx=10, ipady=5)

        # --- SAFETY REMINDER (NEW) ---
        lbl_safety = tk.Label(root, text="⚠️ EMERGENCY UNLOCK: Press ` (Key below Esc)", font=("Segoe UI", 10, "bold"), fg="#ff5555", bg="#1a1a1a")
        lbl_safety.pack(pady=(0, 20))

        # 1. SENSITIVITY
        self.create_section("1. DETECTION SETTINGS", FONT_HEADER)
        
        self.lbl_sens_title = tk.Label(root, text="Turn Sensitivity", bg="#1a1a1a", fg="#ffffff", font=FONT_BODY)
        self.lbl_sens_title.pack(anchor="w", padx=20)
        
        self.lbl_sens_desc = tk.Label(root, text="Mode: Standard", bg="#1a1a1a", fg="#bbbbbb", font=("Segoe UI", 9), cursor="hand2")
        self.lbl_sens_desc.pack(anchor="w", padx=20)
        self.lbl_sens_desc.bind("<Button-1>", lambda e: self.open_site()) 
        
        self.scale_strictness = ttk.Scale(root, from_=1, to=100, orient="horizontal", command=self.update_settings)
        self.scale_strictness.set(50) 
        self.scale_strictness.pack(padx=20, pady=5, fill="x")

        # SPEED SLIDER
        tk.Label(root, text="Lock Speed", bg="#1a1a1a", fg="#bbbbbb", font=FONT_BODY).pack(anchor="w", padx=20, pady=(15,0))
        self.scale_speed = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_settings)
        self.scale_speed.set(80) 
        self.scale_speed.pack(padx=20, pady=5, fill="x")

        # PREVIEW TOGGLE
        self.var_preview = tk.BooleanVar(value=True)
        chk_preview = tk.Checkbutton(root, text="Show Camera Preview", var=self.var_preview, command=self.toggle_preview, bg="#1a1a1a", fg="white", selectcolor="#333", activebackground="#1a1a1a", activeforeground="white", font=FONT_BODY)
        chk_preview.pack(anchor="w", padx=15, pady=15)

        # 2. DECOY IMAGE (LOCKED)
        self.create_section("2. DECOY IMAGE", FONT_HEADER)
        
        lbl_lock = tk.Label(root, text="🔒 LOCKED FEATURE", font=("Segoe UI", 11, "bold"), fg="#555", bg="#1a1a1a")
        lbl_lock.pack(pady=(10, 0))
        
        btn_lock_sub = tk.Button(root, text="Get Custom Backgrounds in PRO >", command=self.open_site, bg="#1a1a1a", fg="#00aaff", font=("Segoe UI", 9, "underline"), relief="flat", activebackground="#1a1a1a", activeforeground="#ffffff", cursor="hand2")
        btn_lock_sub.pack(pady=(0, 10))
        
        # STATUS INDICATORS
        self.lbl_stat = tk.Label(root, text="STARTING...", font=("Segoe UI", 16, "bold"), fg="#ffff00", bg="#1a1a1a")
        self.lbl_stat.pack(pady=30)

        self.update_settings() 
        self.check_alive()

    def create_section(self, text, font):
        tk.Frame(self.root, height=1, bg="#444").pack(fill="x", padx=10, pady=(20, 10))
        lbl = tk.Label(self.root, text=text, font=font, fg="white", bg="#1a1a1a", anchor="w")
        lbl.pack(fill="x", padx=10, pady=2)

    def open_site(self):
        webbrowser.open(PRO_WEBSITE)

    def update_settings(self, event=None):
        val_sens = self.scale_strictness.get()
        
        state["min_eyes"] = 1
        state["strictness"] = 2 + int(val_sens * 0.23) 
        
        if val_sens > 80:
             self.lbl_sens_desc.config(text=f"⚠ LIMIT REACHED. CLICK FOR HYPER MODE.", fg="#ff4444")
        else:
             self.lbl_sens_desc.config(text=f"Mode: Standard | Strictness: {state['strictness']}", fg="#bbbbbb")

        val_speed = self.scale_speed.get()
        state["reaction_speed"] = max(0.15, 2.0 - (val_speed * 0.0185))

    def toggle_preview(self):
        state["show_preview"] = self.var_preview.get()

    def check_alive(self):
        if not state["running"]:
            self.root.destroy()
            return
        
        self.lbl_stat.config(text=state["status_text"])
        if "WARMING UP" in state["status_text"]:
            self.lbl_stat.config(fg="#ffff00") 
        elif "SAFE MODE" in state["status_text"]:
             self.lbl_stat.config(fg="#00aaff") 
        elif "ARMED" in state["status_text"]:
            self.lbl_stat.config(fg="#ffffff") 
        else:
             self.lbl_stat.config(fg="#ff0000") 

        self.root.after(100, self.check_alive)

    def on_close(self):
        state["running"] = False
        self.root.after(200, self.root.destroy)

# --- ENGINE ---
def avert_engine():
    face_path = resource_path('haarcascade_frontalface_default.xml')
    eye_path = resource_path('haarcascade_eye_tree_eyeglasses.xml')
    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade = cv2.CascadeClassifier(eye_path)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))

    cap = None
    for idx in range(3):
        temp_cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if temp_cap.isOpened():
            temp_cap.set(cv2.CAP_PROP_FPS, 30)
            cap = temp_cap
            break
    
    if cap is None:
        state["status_text"] = "NO CAMERA FOUND"
        return

    state["start_time"] = time.time()
    shield_up = False
    last_good_time = time.time()
    
    black_screen = np.zeros((state["screen_h"], state["screen_w"], 3), dtype=np.uint8)
    
    current_fade_frame = 0
    preview_window_open = False

    while state["running"]:
        ret, frame = cap.read()
        if not ret: 
            time.sleep(0.01)
            continue

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            state["running"] = False
            break

        current_time = time.time()
        
        # --- 1. HANDLE BRAKE / SAFE MODE ---
        time_left_brake = int(state["brake_until"] - current_time)
        if time_left_brake > 0:
            state["status_text"] = f"SAFE MODE: {time_left_brake}s"
            if state["show_preview"]:
                display_frame = frame.copy()
                overlay = display_frame.copy()
                cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (255, 200, 0), -1) 
                display_frame = cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0)
                
                cv2.putText(display_frame, f"SAFE MODE: {time_left_brake}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
                cv2.imshow(WINDOW_PREVIEW_NAME, display_frame)
                preview_window_open = True
            last_good_time = current_time 
            continue 

        # --- 2. HANDLE WARMUP ---
        elapsed = current_time - state["start_time"]
        remaining_warmup = int(state["grace_period"] - elapsed)
        if remaining_warmup > 0:
            state["status_text"] = f"WARMING UP ({remaining_warmup}s)"
            last_good_time = current_time
            if state["show_preview"]:
                disp = frame.copy()
                cv2.putText(disp, f"WARMING UP: {remaining_warmup}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.imshow(WINDOW_PREVIEW_NAME, disp)
                preview_window_open = True
            continue

        # --- 3. SYSTEM ARMED ---
        state["status_text"] = "SYSTEM ARMED"
        display_frame = None
        if state["show_preview"] and not shield_up:
            display_frame = frame.copy()

        small_frame = cv2.resize(frame, (640, 480))
        boosted_frame = cv2.convertScaleAbs(small_frame, alpha=state["contrast_boost"], beta=0)
        gray = cv2.cvtColor(boosted_frame, cv2.COLOR_BGR2GRAY)
        gray = clahe.apply(gray) 

        is_looking = False
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, state["strictness"])
                
                if len(eyes) >= state["min_eyes"]:
                    is_looking = True
                    
                if display_frame is not None:
                    col = (0, 255, 0) if is_looking else (0, 0, 255)
                    h_r = frame.shape[0] / 480
                    w_r = frame.shape[1] / 640
                    orig_x, orig_y = int(x*w_r), int(y*h_r)
                    orig_w, orig_h = int(w*w_r), int(h*h_r)
                    cv2.rectangle(display_frame, (orig_x, orig_y), (orig_x+orig_w, orig_y+orig_h), col, 2)
                    for (ex, ey, ew, eh) in eyes:
                        e_x = int((x + ex) * w_r)
                        e_y = int((y + ey) * h_r)
                        e_w = int(ew * w_r)
                        e_h = int(eh * h_r)
                        cv2.rectangle(display_frame, (e_x, e_y), (e_x+e_w, e_y+e_h), (255, 0, 0), 1)

        if display_frame is not None:
            cv2.putText(display_frame, "SYSTEM ARMED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow(WINDOW_PREVIEW_NAME, display_frame)
            preview_window_open = True
        elif preview_window_open and not state["show_preview"]:
            try: cv2.destroyWindow(WINDOW_PREVIEW_NAME)
            except: pass
            preview_window_open = False

        if is_looking:
            last_good_time = current_time
        
        time_gone = current_time - last_good_time
        
        if time_gone > state["reaction_speed"] and not shield_up:
             shield_up = True
             current_fade_frame = 0 
             if preview_window_open:
                 try: cv2.destroyWindow(WINDOW_PREVIEW_NAME)
                 except: pass
                 preview_window_open = False
             
             cv2.namedWindow(WINDOW_LOCK_NAME, cv2.WND_PROP_FULLSCREEN)
             cv2.setWindowProperty(WINDOW_LOCK_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
             cv2.setWindowProperty(WINDOW_LOCK_NAME, cv2.WND_PROP_TOPMOST, 1)

        if shield_up:
            cv2.imshow(WINDOW_LOCK_NAME, black_screen)

            try:
                hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW_LOCK_NAME)
                if hwnd: ctypes.windll.user32.SetForegroundWindow(hwnd)
            except: pass

            if key == SECRET_UNLOCK_KEY:
                cv2.destroyWindow(WINDOW_LOCK_NAME)
                shield_up = False
                state["brake_until"] = time.time() + 5.0
                last_good_time = time.time() + 5.0
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    state["screen_w"] = root.winfo_screenwidth()
    state["screen_h"] = root.winfo_screenheight()
    app = AvertControlPanel(root)
    t = Thread(target=avert_engine)
    t.start()
    root.mainloop()
    state["running"] = False
    t.join()