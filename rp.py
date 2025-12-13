import customtkinter as ctk
from pypresence import Presence, exceptions
from tkinter import messagebox
import json
import time

# ---------- CONFIG ----------
CLIENT_ID = "IDE_IRD_BE_A_CLIENT_ID_T"
PRESET_FILE = "presets.json"

# ---------- GLOBALS ----------
rpc = None
connected = False
presets = {}

# ---------- Load / Save Presets ----------
def load_presets():
    global presets
    try:
        with open(PRESET_FILE, "r", encoding="utf-8") as f:
            presets = json.load(f)
    except:
        presets = {}
    preset_box.set('')
    preset_box.configure(values=list(presets.keys()))

def save_preset():
    name = preset_name.get().strip()
    if not name:
        messagebox.showwarning("Hiba", "Adj nevet a presetnek!")
        return
    presets[name] = {
        "details": details_entry.get(),
        "state": state_entry.get(),
        "large_image": large_entry.get(),
        "small_image": small_entry.get()
    }
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=4)
    load_presets()
    messagebox.showinfo("Mentés", f"Preset '{name}' elmentve!")

def load_preset(event=None):
    p = presets.get(preset_box.get(), {})
    details_entry.set_text(p.get("details", ""))
    state_entry.set_text(p.get("state", ""))
    large_entry.set_text(p.get("large_image", ""))
    small_entry.set_text(p.get("small_image", ""))

# ---------- Discord RPC ----------
def connect_rpc():
    global rpc, connected
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        connected = True
        status_label.set_text("🟢 Discord csatlakoztatva")
    except exceptions.InvalidID:
        messagebox.showerror("Hiba", "Érvénytelen Client ID!")
    except Exception as e:
        messagebox.showerror("Hiba", str(e))

def set_status():
    if not connected:
        messagebox.showwarning("Hiba", "Előbb csatlakozz a Discordhoz!")
        return
    try:
        rpc.update(
            details=details_entry.get(),
            state=state_entry.get(),
            large_image=large_entry.get() or None,
            small_image=small_entry.get() or None,
            start=time.time()
        )
    except Exception as e:
        messagebox.showerror("Hiba", str(e))

def clear_status():
    if connected:
        rpc.clear()

# ---------- GUI ----------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("DigiRP Modern Edition")
root.geometry("520x520")
root.resizable(False, False)

# Title
ctk.CTkLabel(root, text="DigiRP", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
status_label = ctk.CTkLabel(root, text="🔴 Nincs kapcsolat")
status_label.pack()

# Fields
frame = ctk.CTkFrame(root)
frame.pack(pady=15, padx=20, fill="x")

details_entry = ctk.CTkEntry(frame, placeholder_text="Details")
details_entry.pack(pady=5, fill="x")
state_entry = ctk.CTkEntry(frame, placeholder_text="State")
state_entry.pack(pady=5, fill="x")
large_entry = ctk.CTkEntry(frame, placeholder_text="Large Image Key")
large_entry.pack(pady=5, fill="x")
small_entry = ctk.CTkEntry(frame, placeholder_text="Small Image Key")
small_entry.pack(pady=5, fill="x")

# Presets
preset_box = ctk.CTkComboBox(root, values=[])
preset_box.pack(pady=5, fill="x", padx=20)
preset_box.bind("<<ComboboxSelected>>", load_preset)

preset_name = ctk.CTkEntry(root, placeholder_text="Preset név")
preset_name.pack(pady=5, fill="x", padx=20)
ctk.CTkButton(root, text="Preset mentése", command=save_preset).pack(pady=5)

# Buttons
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=20)
ctk.CTkButton(btn_frame, text="Csatlakozás", command=connect_rpc).grid(row=0, column=0, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="Beállítás", command=set_status).grid(row=0, column=1, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="Törlés", command=clear_status).grid(row=1, column=0, columnspan=2, pady=10)

# Load presets
load_presets()

root.mainloop()
