import tkinter as tk
from pypresence import Presence
import time

# Discord App ID (saját Discord Developer App kell, létre kell hozni)
CLIENT_ID = "1424688757705281608"
RPC = Presence(CLIENT_ID)
RPC.connect()

def set_status():
    details = details_entry.get()
    state = state_entry.get()
    RPC.update(details=details, state=state)
    status_label.config(text=f"Státusz beállítva!\nDetails: {details}\nState: {state}")

def clear_status():
    RPC.clear()
    status_label.config(text="Státusz törölve.")

# GUI létrehozása
root = tk.Tk()
root.title("DigiRP Discord Státusz")
root.geometry("400x250")

tk.Label(root, text="Details (pl. Mit csinálsz):").pack()
details_entry = tk.Entry(root, width=40)
details_entry.pack(pady=5)

tk.Label(root, text="State (pl. Helyzet):").pack()
state_entry = tk.Entry(root, width=40)
state_entry.pack(pady=5)

tk.Button(root, text="Státusz beállítása", command=set_status, width=25).pack(pady=5)
tk.Button(root, text="Státusz törlése", command=clear_status, width=25).pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

root.mainloop()
