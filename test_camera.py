import cv2
import time
import numpy as np
import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread

# --- HIGH DPI FIX ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# --- CONSTANTS ---
SECRET_UNLOCK_KEY = 96    # Backtick Key (`)
WINDOW_NAME = "Ghost Protocol View"
DEBUG_WINDOW = "Ghost Debug"

# --- RESOURCE PATH LOADER (Crucial for EXE) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- GLOBAL STATE ---
state = {
    "camera_index": 0,
    "motion_thresh": 1500,  
    "fast_lock": 0.5,       
    "slow_lock": 4.0,       
    "strictness": 3,        
    "fade_speed": 15,
    "running": True,       # The Master Switch
    "decoy_img": None,
    "lock_active": False,
    "camera_changed": False,
    "screen_w": 1920, 
    "screen_h": 1080,
    "start_time": time.time(),    
    "grace_period": 30.0           
}

# --- GUI CLASS ---
class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghost Protocol Settings")
        self.root.geometry("350x650+50+50") 
        self.root.attributes('-topmost', True)
        
        # 1. HANDLE "X" BUTTON CLICK
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        style = ttk.Style()
        try: style.theme_use('clam')
        except: pass
        
        lbl_title = ttk.Label(root, text="GHOST PROTOCOL", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Camera
        frame_cam = ttk.LabelFrame(root, text="Camera Source")
        frame_cam.pack(padx=10, pady=5, fill="x")
        self.cam_var = tk.StringVar()
        self.cam_combo = ttk.Combobox(frame_cam, textvariable=self.cam_var, state="readonly")
        self.cam_combo.pack(padx=10, pady=10, fill="x")
        self.cam_combo.bind("<<ComboboxSelected>>", self.change_camera)
        self.refresh_cameras()

        # Sensitivity
        frame_sense = ttk.LabelFrame(root, text="Sensitivity (Motion & Eyes)")
        frame_sense.pack(padx=10, pady=5, fill="x")
        self.sense_var = tk.IntVar(value=50) 
        self.scale_sense = ttk.Scale(frame_sense, from_=0, to=100, variable=self.sense_var, command=self.update_logic)
        self.scale_sense.pack(padx=10, pady=(10, 0), fill="x")
        self.lbl_sense = ttk.Label(frame_sense, text="Normal (Office Mode)")
        self.lbl_sense.pack(pady=5)

        # Speed
        frame_speed = ttk.LabelFrame(root, text="Panic Reaction Speed")
        frame_speed.pack(padx=10, pady=5, fill="x")
        self.speed_var = tk.IntVar(value=50) 
        self.scale_speed = ttk.Scale(frame_speed, from_=0, to=100, variable=self.speed_var, command=self.update_logic)
        self.scale_speed.pack(padx=10, pady=(10, 0), fill="x")
        self.lbl_speed = ttk.Label(frame_speed, text="Balanced (0.5s)")
        self.lbl_speed.pack(pady=5)

        # Fade
        frame_fade = ttk.LabelFrame(root, text="Fade Smoothness")
        frame_fade.pack(padx=10, pady=5, fill="x")
        self.fade_var = tk.IntVar(value=15)
        self.scale_fade = ttk.Scale(frame_fade, from_=0, to=60, variable=self.fade_var, command=self.update_logic)
        self.scale_fade.pack(padx=10, pady=10, fill="x")

        # Decoy
        btn_decoy = ttk.Button(root, text="📂 Load Safe Image (Decoy)", command=self.load_decoy)
        btn_decoy.pack(padx=10, pady=20, fill="x", ipady=5)
        
        self.lbl_stat = ttk.Label(root, text="Status: Ready", foreground="blue")
        self.lbl_stat.pack(pady=5)
        self.update_logic()
        
        # 2. START HEARTBEAT CHECK
        self.check_alive()

    def check_alive(self):
        """ Check if the camera thread is still running. If not, close UI. """
        if not state["running"]:
            self.root.destroy()
            return
        # Run this check again in 500ms
        self.root.after(500, self.check_alive)

    def on_close(self):
        """ User closed the Settings Window -> Kill Camera """
        state["running"] = False
        self.root.destroy()

    def refresh_cameras(self):
        available = ["Camera 0"]
        for i in range(1, 3):
            available.append(f"Camera {i}")
        self.cam_combo['values'] = available
        self.cam_combo.current(0)

    def change_camera(self, event):
        try:
            idx = int(self.cam_var.get().split(" ")[1])
            state["camera_index"] = idx
            state["camera_changed"] = True
            self.lbl_stat.config(text=f"Switching to Camera {idx}...", foreground="orange")
        except: pass

    def load_decoy(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            img = cv2.imread(path)
            if img is not None:
                state["decoy_img"] = cv2.resize(img, (state["screen_w"], state["screen_h"]))
                self.lbl_stat.config(text="Decoy Loaded!", foreground="green")

    def update_logic(self, _=None):
        s_val = self.sense_var.get()
        if s_val < 30:
            self.lbl_sense.config(text="Low (Relaxed Reading)")
            state["motion_thresh"] = 3000
            state["strictness"] = 2
        elif s_val < 70:
            self.lbl_sense.config(text="Normal (Office Mode)")
            state["motion_thresh"] = 1500
            state["strictness"] = 3
        else:
            self.lbl_sense.config(text="High (Gamer/Paranoid)")
            state["motion_thresh"] = 800
            state["strictness"] = 4

        sp_val = self.speed_var.get()
        delay = 2.0 - (sp_val / 50.0) 
        if delay < 0: delay = 0
        state["fast_lock"] = delay
        self.lbl_speed.config(text=f"Lock Speed: {round(delay, 2)}s")
        state["fade_speed"] = int(self.fade_var.get())


# --- ENGINE (Background Thread) ---
def ghost_engine():
    # Load XMLs (Safe for EXE)
    face_path = resource_path('haarcascade_frontalface_default.xml')
    eye_path = resource_path('haarcascade_eye_tree_eyeglasses.xml')
    
    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade = cv2.CascadeClassifier(eye_path)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    cap = cv2.VideoCapture(state["camera_index"])
    last_good_time = time.time()
    prev_frame = None
    shield_up = False
    bad_frame_count = 0 
    
    # Initialize Windows
    cv2.namedWindow(DEBUG_WINDOW)

    if state["decoy_img"] is None:
        state["decoy_img"] = np.full((state["screen_h"], state["screen_w"], 3), 0, dtype=np.uint8)

    while state["running"]:
        if state["camera_changed"]:
            cap.release()
            time.sleep(0.5) 
            cap = cv2.VideoCapture(state["camera_index"])
            state["camera_changed"] = False
            bad_frame_count = 0

        ret, frame = cap.read()
        if not ret: 
            bad_frame_count += 1
            time.sleep(0.1)
            if bad_frame_count > 20:
                state["camera_index"] = 0
                state["camera_changed"] = True 
                bad_frame_count = 0
            continue
        bad_frame_count = 0 

        # --- CHECK IF USER CLOSED CAMERA WINDOW ---
        # If the window property returns -1 or 0, it means the window is gone.
        try:
            if cv2.getWindowProperty(DEBUG_WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                print("Camera Window Closed -> Shutting Down.")
                state["running"] = False
                break
        except:
            pass

        process_frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(process_frame, cv2.COLOR_BGR2GRAY)
        gray = clahe.apply(gray) 

        is_moving = False
        motion_score = 0
        if prev_frame is None:
            prev_frame = gray
        else:
            diff = cv2.absdiff(prev_frame, gray)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_score = np.sum(thresh) // 255
            if motion_score > state["motion_thresh"]:
                is_moving = True
            prev_frame = gray

        is_safe = False
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, state["strictness"])
                if len(eyes) >= 1:
                    is_safe = True
                
                h_r = frame.shape[0] / 480
                w_r = frame.shape[1] / 640
                orig_x, orig_y = int(x*w_r), int(y*h_r)
                orig_w, orig_h = int(w*w_r), int(h*h_r)
                col = (0, 255, 0) if is_safe else (0, 165, 255)
                cv2.rectangle(frame, (orig_x, orig_y), (orig_x+orig_w, orig_y+orig_h), col, 2)

        # LOGIC
        current_time = time.time()
        elapsed_startup = current_time - state["start_time"]
        in_grace_period = elapsed_startup < state["grace_period"]
        
        if is_safe:
            last_good_time = current_time
            status = "SAFE"
            color = (0, 255, 0)
        else:
            time_gone = current_time - last_good_time
            
            if is_moving:
                limit = state["fast_lock"]
                status = "PANIC"
                color = (0, 0, 255)
            else:
                limit = state["slow_lock"]
                status = "BUFFER"
                color = (0, 255, 255)
            
            if time_gone > limit and not shield_up:
                if in_grace_period:
                    status = f"IMMUNE ({int(state['grace_period'] - elapsed_startup)}s)"
                    color = (255, 0, 255) 
                else:
                    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                        cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
                        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
                    
                    frames = state["fade_speed"]
                    if frames <= 1:
                        cv2.imshow(WINDOW_NAME, state["decoy_img"])
                    else:
                        black = np.zeros_like(state["decoy_img"])
                        for i in range(0, frames, 2): 
                            alpha = i / frames
                            faded = cv2.addWeighted(state["decoy_img"], alpha, black, 1.0-alpha, 0)
                            cv2.imshow(WINDOW_NAME, faded)
                            cv2.waitKey(1)
                        cv2.imshow(WINDOW_NAME, state["decoy_img"])
                    shield_up = True
                    force_focus(WINDOW_NAME)
        
        # UNLOCK
        key = cv2.waitKey(1) & 0xFF
        if shield_up:
            force_focus(WINDOW_NAME)
            cv2.imshow(WINDOW_NAME, state["decoy_img"])
            if key == SECRET_UNLOCK_KEY:
                cv2.destroyWindow(WINDOW_NAME)
                shield_up = False
                last_good_time = time.time()
        else:
            cv2.putText(frame, f"STATUS: {status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            bar_len = int((motion_score / 3000) * 200)
            thresh_len = int((state["motion_thresh"] / 3000) * 200)
            cv2.rectangle(frame, (20, 80), (220, 100), (50,50,50), -1)
            bar_col = (0,0,255) if is_moving else (255,200,0)
            cv2.rectangle(frame, (20, 80), (20+bar_len, 100), bar_col, -1)
            cv2.line(frame, (20+thresh_len, 75), (20+thresh_len, 105), (255,255,255), 2)
            cv2.imshow(DEBUG_WINDOW, frame)

        if key == ord('q'):
            state["running"] = False
            break

    cap.release()
    cv2.destroyAllWindows()

def force_focus(name):
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, name)
        if hwnd:
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
    except: pass

if __name__ == "__main__":
    root = tk.Tk()
    state["screen_w"] = root.winfo_screenwidth()
    state["screen_h"] = root.winfo_screenheight()
    app = ControlPanel(root)
    t = Thread(target=ghost_engine)
    t.start()
    root.mainloop()
    state["running"] = False
    t.join()