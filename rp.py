#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigiRP - Modern Discord Rich Presence Manager
Version: 2.0
"""

import sys
import traceback

# Debug mode
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DigiRP] {msg}")

# Import modules
try:
    debug_print("Importing modules...")
    
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    debug_print("✓ Tkinter imported")
    
    import pypresence
    from pypresence import Presence
    debug_print("✓ pypresence imported")
    
    import time
    import threading
    import json
    import os
    debug_print("✓ All modules loaded successfully")
    
except ImportError as e:
    print(f"ERROR: Missing module - {e}")
    print("\nPlease install pypresence:")
    print("  pip install pypresence")
    input("\nPress Enter to exit...")
    sys.exit(1)

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, icon="", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.icon = icon
        self.bg_color = kwargs.get('bg', '#5865F2')
        self.hover_color = self.lighten_color(self.bg_color)
        self.text_color = 'white'
        self.enabled = True
        
        self.create_rectangle(0, 0, kwargs['width'], kwargs['height'], 
                            fill=self.bg_color, outline='', tags='bg', width=0)
        
        display_text = f"{icon} {text}" if icon else text
        self.create_text(kwargs['width']//2, kwargs['height']//2, 
                        text=display_text, fill=self.text_color, 
                        font=('Segoe UI', 9, 'bold'), tags='text')
        
        self.bind('<Button-1>', lambda e: self.on_click())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def lighten_color(self, color):
        """Return lighter version of color for hover effect"""
        color_map = {
            '#43B581': '#4CCF8F',
            '#F04747': '#F56565', 
            '#5865F2': '#6B75FF',
            '#747F8D': '#8A95A5'
        }
        return color_map.get(color, color)
        
    def on_click(self):
        if self.enabled:
            try:
                self.command()
            except Exception as e:
                debug_print(f"Button error: {e}")
        
    def on_enter(self, e):
        if self.enabled:
            self.itemconfig('bg', fill=self.hover_color)
        
    def on_leave(self, e):
        if self.enabled:
            self.itemconfig('bg', fill=self.bg_color)
        
    def set_state(self, state):
        if state == 'disabled':
            self.itemconfig('bg', fill='#4E5058')
            self.itemconfig('text', fill='#72767d')
            self.enabled = False
        else:
            self.itemconfig('bg', fill=self.bg_color)
            self.itemconfig('text', fill='white')
            self.enabled = True

class ModernEntry(tk.Entry):
    """Custom styled entry widget"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=('Segoe UI', 9), bg='#40444B', 
                        fg='#DCDDDE', insertbackground='#FFFFFF',
                        relief='flat', bd=0, **kwargs)
        self.configure(highlightthickness=1, highlightbackground='#202225', 
                      highlightcolor='#5865F2')

class ScrollableFrame(tk.Frame):
    """Scrollable frame container"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(self, bg='#36393F', highlightthickness=0)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", 
                       background="#2F3136",
                       troughcolor="#202225",
                       bordercolor="#202225",
                       arrowcolor="#72767d")
        
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#36393F')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        self.bind_mousewheel()
    
    def bind_mousewheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

class DiscordRPApp:
    """Main application class"""
    def __init__(self, root):
        debug_print("Initializing DigiRP...")
        self.root = root
        self.root.title("DigiRP - Discord Rich Presence Manager")
        self.root.geometry("800x680")
        self.root.configure(bg='#36393F')
        self.root.minsize(750, 600)
        
        # Variables
        self.rpc = None
        self.connected = False
        self.update_thread = None
        self.running = False
        self.start_timestamp = None
        self.config_file = "digirp_config.json"
        
        # Load last config
        self.load_last_config()
        
        # Try to set icon
        try:
            if os.path.exists('icon.ico'):
                self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Create UI
        self.create_ui()
        debug_print("✓ UI created successfully")
        
    def create_ui(self):
        """Create the user interface"""
        # Header
        header = tk.Frame(self.root, bg='#202225', height=90)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo section
        logo_frame = tk.Frame(header, bg='#202225')
        logo_frame.pack(side='left', padx=25, pady=18)
        
        # Logo
        logo_canvas = tk.Canvas(logo_frame, width=50, height=50, bg='#202225', highlightthickness=0)
        logo_canvas.pack(side='left')
        logo_canvas.create_oval(5, 5, 45, 45, fill='#5865F2', outline='#4752C4', width=2)
        logo_canvas.create_text(25, 25, text="D", font=('Segoe UI', 24, 'bold'), fill='white')
        
        # Title
        title_frame = tk.Frame(logo_frame, bg='#202225')
        title_frame.pack(side='left', padx=(15, 0))
        
        tk.Label(title_frame, text="DigiRP", font=('Segoe UI', 18, 'bold'),
                bg='#202225', fg='#FFFFFF').pack(anchor='w')
        tk.Label(title_frame, text="Custom Discord Rich Presence Manager", 
                font=('Segoe UI', 9), bg='#202225', fg='#B9BBBE').pack(anchor='w')
        
        # Status indicator
        self.status_frame = tk.Frame(header, bg='#202225')
        self.status_frame.pack(side='right', padx=25)
        
        status_container = tk.Frame(self.status_frame, bg='#2F3136', relief='flat')
        status_container.pack(padx=12, pady=8)
        
        self.status_dot = tk.Canvas(status_container, width=14, height=14, 
                                   bg='#2F3136', highlightthickness=0)
        self.status_dot.pack(side='left', padx=(8, 10), pady=8)
        self.status_dot.create_oval(2, 2, 12, 12, fill='#F04747', outline='', tags='dot')
        
        self.status_label = tk.Label(status_container, text="Disconnected",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#2F3136', fg='#F04747')
        self.status_label.pack(side='left', padx=(0, 12), pady=8)
        
        # Main content area
        content_bg = tk.Frame(self.root, bg='#2F3136')
        content_bg.pack(fill='both', expand=True, padx=12, pady=12)
        
        # Scrollable content
        scroll_container = ScrollableFrame(content_bg)
        scroll_container.pack(fill='both', expand=True)
        
        content = scroll_container.scrollable_frame
        
        # Two columns layout
        columns_container = tk.Frame(content, bg='#36393F')
        columns_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_col = tk.Frame(columns_container, bg='#36393F')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        right_col = tk.Frame(columns_container, bg='#36393F')
        right_col.pack(side='right', fill='both', expand=True, padx=(8, 0))
        
        # === LEFT COLUMN ===
        self.create_section(left_col, "⚙️", "Application Settings")
        self.create_label(left_col, "Client ID *")
        self.client_id = self.create_input(left_col)
        
        self.create_section(left_col, "📝", "Presence Text")
        self.create_label(left_col, "Details (First Line)")
        self.details = self.create_input(left_col)
        self.create_label(left_col, "State (Second Line)")
        self.state = self.create_input(left_col)
        
        self.create_section(left_col, "⏰", "Timestamps")
        
        ts_frame = tk.Frame(left_col, bg='#36393F')
        ts_frame.pack(fill='x', padx=8, pady=8)
        
        self.show_timestamp = tk.BooleanVar(value=False)
        check_frame = tk.Frame(ts_frame, bg='#40444B', relief='flat')
        check_frame.pack(fill='x', pady=2)
        tk.Checkbutton(check_frame, text="Show Timestamp", variable=self.show_timestamp,
                      bg='#40444B', fg='#DCDDDE', selectcolor='#2F3136',
                      activebackground='#40444B', activeforeground='#FFFFFF',
                      font=('Segoe UI', 9), command=self.toggle_timestamp).pack(anchor='w', padx=8, pady=8)
        
        self.ts_options = tk.Frame(left_col, bg='#36393F')
        self.ts_options.pack(fill='x', padx=8, pady=4)
        
        self.timestamp_type = tk.StringVar(value="elapsed")
        radio_frame = tk.Frame(self.ts_options, bg='#40444B')
        radio_frame.pack(fill='x')
        tk.Radiobutton(radio_frame, text="⏱️ Elapsed", value="elapsed",
                      variable=self.timestamp_type, bg='#40444B', fg='#DCDDDE',
                      selectcolor='#2F3136', activebackground='#40444B',
                      font=('Segoe UI', 9), state='disabled').pack(side='left', padx=8, pady=6)
        tk.Radiobutton(radio_frame, text="⏲️ Remaining", value="remaining",
                      variable=self.timestamp_type, bg='#40444B', fg='#DCDDDE',
                      selectcolor='#2F3136', activebackground='#40444B',
                      font=('Segoe UI', 9), state='disabled').pack(side='left', padx=8, pady=6)
        
        self.create_section(left_col, "👥", "Party Size")
        party_container = tk.Frame(left_col, bg='#36393F')
        party_container.pack(fill='x', padx=8, pady=8)
        
        party_left = tk.Frame(party_container, bg='#36393F')
        party_left.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.create_label(party_left, "Current", small=True)
        self.party_size = self.create_input(party_left)
        
        party_right = tk.Frame(party_container, bg='#36393F')
        party_right.pack(side='right', expand=True, fill='x', padx=(5, 0))
        self.create_label(party_right, "Max", small=True)
        self.party_max = self.create_input(party_right)
        
        # === RIGHT COLUMN ===
        self.create_section(right_col, "🖼️", "Images")
        self.create_label(right_col, "Large Image Key")
        self.large_key = self.create_input(right_col)
        self.create_label(right_col, "Large Image Text (Hover)")
        self.large_text = self.create_input(right_col)
        
        tk.Frame(right_col, bg='#36393F', height=12).pack()
        
        self.create_label(right_col, "Small Image Key")
        self.small_key = self.create_input(right_col)
        self.create_label(right_col, "Small Image Text (Hover)")
        self.small_text = self.create_input(right_col)
        
        self.create_section(right_col, "🔗", "Buttons")
        self.create_label(right_col, "Button 1 Label")
        self.button1_text = self.create_input(right_col)
        self.create_label(right_col, "Button 1 URL")
        self.button1_url = self.create_input(right_col)
        
        tk.Frame(right_col, bg='#36393F', height=12).pack()
        
        self.create_label(right_col, "Button 2 Label")
        self.button2_text = self.create_input(right_col)
        self.create_label(right_col, "Button 2 URL")
        self.button2_url = self.create_input(right_col)
        
        # Bottom control panel
        bottom = tk.Frame(self.root, bg='#202225', height=75)
        bottom.pack(fill='x', side='bottom')
        bottom.pack_propagate(False)
        
        btn_container = tk.Frame(bottom, bg='#202225')
        btn_container.pack(pady=18)
        
        self.connect_btn = ModernButton(btn_container, "Connect", self.connect,
                                       icon="🔌", width=115, height=42, bg='#43B581')
        self.connect_btn.pack(side='left', padx=4)
        
        self.update_btn = ModernButton(btn_container, "Update", self.update_presence,
                                      icon="🔄", width=115, height=42, bg='#5865F2')
        self.update_btn.pack(side='left', padx=4)
        self.update_btn.set_state('disabled')
        
        self.disconnect_btn = ModernButton(btn_container, "Disconnect", self.disconnect,
                                          icon="⏹️", width=115, height=42, bg='#F04747')
        self.disconnect_btn.pack(side='left', padx=4)
        self.disconnect_btn.set_state('disabled')
        
        clear_btn = ModernButton(btn_container, "Clear", self.clear_all,
                               icon="🗑️", width=100, height=42, bg='#747F8D')
        clear_btn.pack(side='left', padx=4)
        
        save_btn = ModernButton(btn_container, "Save", self.save_preset,
                               icon="💾", width=100, height=42, bg='#5865F2')
        save_btn.pack(side='left', padx=4)
        
        load_btn = ModernButton(btn_container, "Load", self.load_preset,
                               icon="📂", width=100, height=42, bg='#5865F2')
        load_btn.pack(side='left', padx=4)
        
        # Menu bar
        menubar = tk.Menu(self.root, bg='#2F3136', fg='white')
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2F3136', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Preset...", command=self.save_preset)
        file_menu.add_command(label="Load Preset...", command=self.load_preset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2F3136', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About DigiRP", command=self.show_about)
        
    def create_section(self, parent, icon, title):
        """Create a section header"""
        frame = tk.Frame(parent, bg='#2F3136', relief='flat')
        frame.pack(fill='x', pady=(18, 10), padx=8)
        inner = tk.Frame(frame, bg='#2F3136')
        inner.pack(fill='x', padx=10, pady=10)
        tk.Label(inner, text=f"{icon}  {title}", font=('Segoe UI', 11, 'bold'),
                bg='#2F3136', fg='#FFFFFF').pack(anchor='w')
        tk.Frame(inner, bg='#5865F2', height=2).pack(fill='x', pady=(6, 0))
        
    def create_label(self, parent, text, small=False):
        """Create a label"""
        frame = tk.Frame(parent, bg='#36393F')
        frame.pack(fill='x', padx=8, pady=(10 if not small else 5, 3))
        tk.Label(frame, text=text, font=('Segoe UI', 8 if small else 9),
                bg='#36393F', fg='#B9BBBE').pack(anchor='w')
        
    def create_input(self, parent):
        """Create an input field"""
        frame = tk.Frame(parent, bg='#202225', relief='flat')
        frame.pack(fill='x', padx=8, pady=(0, 5))
        entry = ModernEntry(frame)
        entry.pack(fill='x', padx=2, pady=2)
        return entry
    
    def toggle_timestamp(self):
        """Toggle timestamp options"""
        state = 'normal' if self.show_timestamp.get() else 'disabled'
        for child in self.ts_options.winfo_children():
            for widget in child.winfo_children():
                try:
                    widget.configure(state=state)
                except:
                    pass
    
    def connect(self):
        """Connect to Discord"""
        debug_print("Connect button clicked")
        client_id = self.client_id.get().strip()
        
        if not client_id:
            messagebox.showerror("Error", "Please enter a Client ID!\n\nGet one at:\ndiscord.com/developers/applications")
            return
        
        try:
            debug_print(f"Connecting with Client ID: {client_id}")
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.connected = True
            self.start_timestamp = int(time.time())
            debug_print("✓ Connected successfully")
            
            self.update_presence()
            
            # Update UI
            self.status_dot.delete('dot')
            self.status_dot.create_oval(2, 2, 12, 12, fill='#43B581', outline='', tags='dot')
            self.status_label.config(text="Connected", fg='#43B581')
            
            self.connect_btn.set_state('disabled')
            self.disconnect_btn.set_state('normal')
            self.update_btn.set_state('normal')
            
            # Start keep-alive thread
            self.running = True
            self.update_thread = threading.Thread(target=self.keep_alive, daemon=True)
            self.update_thread.start()
            
            self.save_last_config()
            messagebox.showinfo("Success", "✅ Successfully connected to Discord!\n\nYour Rich Presence is now live!")
            
        except Exception as e:
            debug_print(f"Connection error: {e}")
            error_msg = str(e)
            if "FileNotFoundError" in error_msg or "DiscordNotFound" in error_msg:
                messagebox.showerror("Discord Not Running", 
                                   "❌ Discord is not running!\n\nPlease:\n1. Start Discord\n2. Wait for it to fully load\n3. Try connecting again")
            else:
                messagebox.showerror("Connection Error", 
                                   f"❌ Failed to connect:\n\n{error_msg}\n\nMake sure:\n• Discord is running\n• Client ID is correct")
    
    def disconnect(self):
        """Disconnect from Discord"""
        debug_print("Disconnect button clicked")
        try:
            self.running = False
            if self.rpc and self.connected:
                self.rpc.close()
            
            self.connected = False
            self.rpc = None
            
            # Update UI
            self.status_dot.delete('dot')
            self.status_dot.create_oval(2, 2, 12, 12, fill='#F04747', outline='', tags='dot')
            self.status_label.config(text="Disconnected", fg='#F04747')
            
            self.connect_btn.set_state('normal')
            self.disconnect_btn.set_state('disabled')
            self.update_btn.set_state('disabled')
            
            debug_print("✓ Disconnected successfully")
            messagebox.showinfo("Disconnected", "✅ Rich Presence has been stopped.")
            
        except Exception as e:
            debug_print(f"Disconnect error: {e}")
            messagebox.showerror("Error", f"❌ Error disconnecting:\n{str(e)}")
    
    def update_presence(self):
        """Update the Rich Presence"""
        debug_print("Updating presence...")
        if not self.connected or not self.rpc:
            messagebox.showwarning("Not Connected", "⚠️ Please connect to Discord first!")
            return
        
        try:
            kwargs = {}
            
            # Text fields
            if self.details.get().strip():
                kwargs['details'] = self.details.get().strip()
            if self.state.get().strip():
                kwargs['state'] = self.state.get().strip()
            
            # Images
            if self.large_key.get().strip():
                kwargs['large_image'] = self.large_key.get().strip()
                if self.large_text.get().strip():
                    kwargs['large_text'] = self.large_text.get().strip()
            
            if self.small_key.get().strip():
                kwargs['small_image'] = self.small_key.get().strip()
                if self.small_text.get().strip():
                    kwargs['small_text'] = self.small_text.get().strip()
            
            # Party size
            try:
                if self.party_size.get().strip() and self.party_max.get().strip():
                    kwargs['party_size'] = [int(self.party_size.get()), int(self.party_max.get())]
            except ValueError:
                messagebox.showwarning("Invalid Input", "⚠️ Party size must be numbers!")
                return
            
            # Timestamps
            if self.show_timestamp.get():
                if self.timestamp_type.get() == "elapsed":
                    kwargs['start'] = self.start_timestamp
                else:
                    kwargs['end'] = int(time.time()) + 3600
            
            # Buttons
            buttons = []
            if self.button1_text.get().strip() and self.button1_url.get().strip():
                buttons.append({"label": self.button1_text.get().strip()[:32], 
                              "url": self.button1_url.get().strip()})
            if self.button2_text.get().strip() and self.button2_url.get().strip():
                buttons.append({"label": self.button2_text.get().strip()[:32], 
                              "url": self.button2_url.get().strip()})
            if buttons:
                kwargs['buttons'] = buttons
            
            # Update presence
            self.rpc.update(**kwargs)
            self.save_last_config()
            debug_print("✓ Presence updated successfully")
            
        except Exception as e:
            debug_print(f"Update error: {e}")
            messagebox.showerror("Update Error", f"❌ Failed to update presence:\n\n{str(e)}")
    
    def keep_alive(self):
        """Keep the connection alive"""
        while self.running and self.connected:
            time.sleep(15)
    
    def clear_all(self):
        """Clear all input fields"""
        if messagebox.askyesno("Clear All Fields", "Are you sure you want to clear all fields?"):
            for entry in [self.details, self.state, self.large_key, self.large_text,
                         self.small_key, self.small_text, self.button1_text,
                         self.button1_url, self.button2_text, self.button2_url,
                         self.party_size, self.party_max]:
                entry.delete(0, tk.END)
            self.show_timestamp.set(False)
            self.toggle_timestamp()
    
    def save_preset(self):
        """Save current configuration as preset"""
        filename = filedialog.asksaveasfilename(
            title="Save Preset",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            preset = self.get_current_config()
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(preset, f, indent=2)
                messagebox.showinfo("Success", f"✅ Preset saved successfully!\n\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to save preset:\n{str(e)}")
    
    def load_preset(self):
        """Load a preset configuration"""
        filename = filedialog.askopenfilename(
            title="Load Preset",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    preset = json.load(f)
                self.apply_config(preset)
                messagebox.showinfo("Success", f"✅ Preset loaded successfully!\n\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to load preset:\n{str(e)}")
    
    def get_current_config(self):
        """Get current configuration as dictionary"""
        return {
            'client_id': self.client_id.get(),
            'details': self.details.get(),
            'state': self.state.get(),
            'large_key': self.large_key.get(),
            'large_text': self.large_text.get(),
            'small_key': self.small_key.get(),
            'small_text': self.small_text.get(),
            'button1_text': self.button1_text.get(),
            'button1_url': self.button1_url.get(),
            'button2_text': self.button2_text.get(),
            'button2_url': self.button2_url.get(),
            'party_size': self.party_size.get(),
            'party_max': self.party_max.get(),
            'show_timestamp': self.show_timestamp.get(),
            'timestamp_type': self.timestamp_type.get()
        }
    
    def apply_config(self, config):
        """Apply a configuration dictionary"""
        entries_map = {
            'client_id': self.client_id,
            'details': self.details,
            'state': self.state,
            'large_key': self.large_key,
            'large_text': self.large_text,
            'small_key': self.small_key,
            'small_text': self.small_text,
            'button1_text': self.button1_text,
            'button1_url': self.button1_url,
            'button2_text': self.button2_text,
            'button2_url': self.button2_url,
            'party_size': self.party_size,
            'party_max': self.party_max
        }
        
        for key, entry in entries_map.items():
            entry.delete(0, tk.END)
            entry.insert(0, config.get(key, ''))
        
        self.show_timestamp.set(config.get('show_timestamp', False))
        self.timestamp_type.set(config.get('timestamp_type', 'elapsed'))
        #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DigiRP - Modern Discord Rich Presence Manager
Version: 2.0
"""

import sys
import traceback

# Debug mode
DEBUG = False

def debug_print(msg):
    if DEBUG:
        print(f"[DigiRP] {msg}")

# Import modules
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import pypresence
    from pypresence import Presence
    import time
    import threading
    import json
    import os
    
except ImportError as e:
    print(f"ERROR: Missing module - {e}")
    print("\nPlease install pypresence:")
    print("  pip install pypresence")
    input("\nPress Enter to exit...")
    sys.exit(1)

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, icon="", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.text = text
        self.icon = icon
        self.bg_color = kwargs.get('bg', '#5865F2')
        self.hover_color = self.lighten_color(self.bg_color)
        self.text_color = 'white'
        self.enabled = True
        
        # Rounded corners effect
        self.create_rectangle(0, 0, kwargs['width'], kwargs['height'], 
                            fill=self.bg_color, outline='', tags='bg', width=0)
        
        display_text = f"{icon} {text}" if icon else text
        self.create_text(kwargs['width']//2, kwargs['height']//2, 
                        text=display_text, fill=self.text_color, 
                        font=('Segoe UI', 10, 'bold'), tags='text')
        
        self.bind('<Button-1>', lambda e: self.on_click())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def lighten_color(self, color):
        color_map = {
            '#43B581': '#4CCF8F',
            '#F04747': '#F56565', 
            '#5865F2': '#6B75FF',
            '#747F8D': '#8A95A5'
        }
        return color_map.get(color, color)
        
    def on_click(self):
        if self.enabled:
            try:
                self.command()
            except Exception as e:
                debug_print(f"Button error: {e}")
        
    def on_enter(self, e):
        if self.enabled:
            self.itemconfig('bg', fill=self.hover_color)
        
    def on_leave(self, e):
        if self.enabled:
            self.itemconfig('bg', fill=self.bg_color)
        
    def set_state(self, state):
        if state == 'disabled':
            self.itemconfig('bg', fill='#4E5058')
            self.itemconfig('text', fill='#72767d')
            self.enabled = False
        else:
            self.itemconfig('bg', fill=self.bg_color)
            self.itemconfig('text', fill='white')
            self.enabled = True

class ModernEntry(tk.Entry):
    """Custom styled entry widget"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=('Segoe UI', 10), bg='#40444B', 
                        fg='#DCDDDE', insertbackground='#FFFFFF',
                        relief='flat', bd=0, **kwargs)
        self.configure(highlightthickness=1, highlightbackground='#202225', 
                      highlightcolor='#5865F2')

class DiscordRPApp:
    """Main application class"""
    def __init__(self, root):
        self.root = root
        self.root.title("DigiRP - Discord Rich Presence Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#36393F')
        self.root.minsize(850, 650)
        
        # Variables
        self.rpc = None
        self.connected = False
        self.update_thread = None
        self.running = False
        self.start_timestamp = None
        self.config_file = "digirp_config.json"
        
        # Load last config
        self.load_last_config()
        
        # Try to set icon
        try:
            if os.path.exists('icon.ico'):
                self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        # Header
        header = tk.Frame(self.root, bg='#202225', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo and title (centered)
        header_content = tk.Frame(header, bg='#202225')
        header_content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo
        logo_canvas = tk.Canvas(header_content, width=60, height=60, bg='#202225', highlightthickness=0)
        logo_canvas.pack(side='left', padx=(0, 15))
        logo_canvas.create_oval(5, 5, 55, 55, fill='#5865F2', outline='#4752C4', width=3)
        logo_canvas.create_text(30, 30, text="D", font=('Segoe UI', 28, 'bold'), fill='white')
        
        # Title
        title_frame = tk.Frame(header_content, bg='#202225')
        title_frame.pack(side='left')
        
        tk.Label(title_frame, text="DigiRP", font=('Segoe UI', 24, 'bold'),
                bg='#202225', fg='#FFFFFF').pack()
        tk.Label(title_frame, text="Custom Discord Rich Presence Manager", 
                font=('Segoe UI', 10), bg='#202225', fg='#B9BBBE').pack()
        
        # Status indicator (top right)
        status_container = tk.Frame(header, bg='#2F3136')
        status_container.place(relx=0.98, rely=0.5, anchor='e')
        
        self.status_dot = tk.Canvas(status_container, width=16, height=16, 
                                   bg='#2F3136', highlightthickness=0)
        self.status_dot.pack(side='left', padx=(12, 10), pady=10)
        self.status_dot.create_oval(3, 3, 13, 13, fill='#F04747', outline='', tags='dot')
        
        self.status_label = tk.Label(status_container, text="Disconnected",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='#2F3136', fg='#F04747')
        self.status_label.pack(side='left', padx=(0, 15), pady=10)
        
        # Main content container with max width
        main_container = tk.Frame(self.root, bg='#36393F')
        main_container.pack(fill='both', expand=True, pady=20)
        
        # Content frame (centered with max width)
        content_frame = tk.Frame(main_container, bg='#36393F')
        content_frame.place(relx=0.5, rely=0.5, anchor='center', width=850, height=500)
        
        # Two columns layout
        left_col = tk.Frame(content_frame, bg='#2F3136')
        left_col.place(relx=0, rely=0, relwidth=0.48, relheight=1)
        
        right_col = tk.Frame(content_frame, bg='#2F3136')
        right_col.place(relx=0.52, rely=0, relwidth=0.48, relheight=1)
        
        # Create canvas for scrolling
        left_canvas = tk.Canvas(left_col, bg='#2F3136', highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_col, orient='vertical', command=left_canvas.yview)
        left_scrollable = tk.Frame(left_canvas, bg='#2F3136')
        
        left_scrollable.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_scrollable, anchor='nw')
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_canvas.pack(side='left', fill='both', expand=True)
        left_scrollbar.pack(side='right', fill='y')
        
        right_canvas = tk.Canvas(right_col, bg='#2F3136', highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_col, orient='vertical', command=right_canvas.yview)
        right_scrollable = tk.Frame(right_canvas, bg='#2F3136')
        
        right_scrollable.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
        right_canvas.create_window((0, 0), window=right_scrollable, anchor='nw')
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        right_canvas.pack(side='left', fill='both', expand=True)
        right_scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel binding
        def _on_mousewheel(event, canvas):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        left_canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e, left_canvas))
        right_canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e, right_canvas))
        
        # === LEFT COLUMN ===
        self.create_section(left_scrollable, "⚙️", "Application Settings")
        self.create_label(left_scrollable, "Client ID *")
        self.client_id = self.create_input(left_scrollable)
        
        self.create_section(left_scrollable, "📝", "Presence Text")
        self.create_label(left_scrollable, "Details (First Line)")
        self.details = self.create_input(left_scrollable)
        self.create_label(left_scrollable, "State (Second Line)")
        self.state = self.create_input(left_scrollable)
        
        self.create_section(left_scrollable, "⏰", "Timestamps")
        
        ts_frame = tk.Frame(left_scrollable, bg='#2F3136')
        ts_frame.pack(fill='x', padx=15, pady=8)
        
        self.show_timestamp = tk.BooleanVar(value=False)
        check_frame = tk.Frame(ts_frame, bg='#40444B')
        check_frame.pack(fill='x', pady=5)
        tk.Checkbutton(check_frame, text="Show Timestamp", variable=self.show_timestamp,
                      bg='#40444B', fg='#DCDDDE', selectcolor='#2F3136',
                      activebackground='#40444B', activeforeground='#FFFFFF',
                      font=('Segoe UI', 10), command=self.toggle_timestamp).pack(anchor='w', padx=10, pady=10)
        
        self.ts_options = tk.Frame(left_scrollable, bg='#2F3136')
        self.ts_options.pack(fill='x', padx=15, pady=5)
        
        self.timestamp_type = tk.StringVar(value="elapsed")
        radio_frame = tk.Frame(self.ts_options, bg='#40444B')
        radio_frame.pack(fill='x')
        tk.Radiobutton(radio_frame, text="⏱️ Elapsed", value="elapsed",
                      variable=self.timestamp_type, bg='#40444B', fg='#DCDDDE',
                      selectcolor='#2F3136', activebackground='#40444B',
                      font=('Segoe UI', 10), state='disabled').pack(side='left', padx=10, pady=8)
        tk.Radiobutton(radio_frame, text="⏲️ Remaining", value="remaining",
                      variable=self.timestamp_type, bg='#40444B', fg='#DCDDDE',
                      selectcolor='#2F3136', activebackground='#40444B',
                      font=('Segoe UI', 10), state='disabled').pack(side='left', padx=10, pady=8)
        
        self.create_section(left_scrollable, "👥", "Party Size")
        party_container = tk.Frame(left_scrollable, bg='#2F3136')
        party_container.pack(fill='x', padx=15, pady=8)
        
        party_left = tk.Frame(party_container, bg='#2F3136')
        party_left.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.create_label(party_left, "Current")
        self.party_size = self.create_input(party_left)
        
        party_right = tk.Frame(party_container, bg='#2F3136')
        party_right.pack(side='right', expand=True, fill='x', padx=(5, 0))
        self.create_label(party_right, "Max")
        self.party_max = self.create_input(party_right)
        
        # === RIGHT COLUMN ===
        self.create_section(right_scrollable, "🖼️", "Images")
        self.create_label(right_scrollable, "Large Image Key")
        self.large_key = self.create_input(right_scrollable)
        self.create_label(right_scrollable, "Large Image Text (Hover)")
        self.large_text = self.create_input(right_scrollable)
        
        tk.Frame(right_scrollable, bg='#2F3136', height=15).pack()
        
        self.create_label(right_scrollable, "Small Image Key")
        self.small_key = self.create_input(right_scrollable)
        self.create_label(right_scrollable, "Small Image Text (Hover)")
        self.small_text = self.create_input(right_scrollable)
        
        self.create_section(right_scrollable, "🔗", "Buttons")
        self.create_label(right_scrollable, "Button 1 Label")
        self.button1_text = self.create_input(right_scrollable)
        self.create_label(right_scrollable, "Button 1 URL")
        self.button1_url = self.create_input(right_scrollable)
        
        tk.Frame(right_scrollable, bg='#2F3136', height=15).pack()
        
        self.create_label(right_scrollable, "Button 2 Label")
        self.button2_text = self.create_input(right_scrollable)
        self.create_label(right_scrollable, "Button 2 URL")
        self.button2_url = self.create_input(right_scrollable)
        
        # Bottom control panel (centered)
        bottom = tk.Frame(self.root, bg='#202225', height=85)
        bottom.pack(fill='x', side='bottom')
        bottom.pack_propagate(False)
        
        btn_container = tk.Frame(bottom, bg='#202225')
        btn_container.place(relx=0.5, rely=0.5, anchor='center')
        
        self.connect_btn = ModernButton(btn_container, "Connect", self.connect,
                                       icon="🔌", width=120, height=45, bg='#43B581')
        self.connect_btn.pack(side='left', padx=5)
        
        self.update_btn = ModernButton(btn_container, "Update", self.update_presence,
                                      icon="🔄", width=120, height=45, bg='#5865F2')
        self.update_btn.pack(side='left', padx=5)
        self.update_btn.set_state('disabled')
        
        self.disconnect_btn = ModernButton(btn_container, "Disconnect", self.disconnect,
                                          icon="⏹️", width=130, height=45, bg='#F04747')
        self.disconnect_btn.pack(side='left', padx=5)
        self.disconnect_btn.set_state('disabled')
        
        clear_btn = ModernButton(btn_container, "Clear", self.clear_all,
                               icon="🗑️", width=100, height=45, bg='#747F8D')
        clear_btn.pack(side='left', padx=5)
        
        save_btn = ModernButton(btn_container, "Save", self.save_preset,
                               icon="💾", width=100, height=45, bg='#5865F2')
        save_btn.pack(side='left', padx=5)
        
        load_btn = ModernButton(btn_container, "Load", self.load_preset,
                               icon="📂", width=100, height=45, bg='#5865F2')
        load_btn.pack(side='left', padx=5)
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Preset...", command=self.save_preset)
        file_menu.add_command(label="Load Preset...", command=self.load_preset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About DigiRP", command=self.show_about)
        
    def create_section(self, parent, icon, title):
        """Create a section header"""
        frame = tk.Frame(parent, bg='#2F3136')
        frame.pack(fill='x', pady=(20, 10), padx=15)
        
        tk.Label(frame, text=f"{icon}  {title}", font=('Segoe UI', 12, 'bold'),
                bg='#2F3136', fg='#FFFFFF').pack(anchor='w')
        
        tk.Frame(frame, bg='#5865F2', height=3).pack(fill='x', pady=(8, 0))
        
    def create_label(self, parent, text):
        """Create a label"""
        tk.Label(parent, text=text, font=('Segoe UI', 9),
                bg='#2F3136', fg='#B9BBBE').pack(anchor='w', padx=15, pady=(10, 5))
        
    def create_input(self, parent):
        """Create an input field"""
        entry = ModernEntry(parent)
        entry.pack(fill='x', padx=15, pady=(0, 5))
        entry.configure(bd=8)
        return entry
    
    def toggle_timestamp(self):
        """Toggle timestamp options"""
        state = 'normal' if self.show_timestamp.get() else 'disabled'
        for child in self.ts_options.winfo_children():
            for widget in child.winfo_children():
                try:
                    widget.configure(state=state)
                except:
                    pass
    
    def connect(self):
        """Connect to Discord"""
        client_id = self.client_id.get().strip()
        
        if not client_id:
            messagebox.showerror("Error", "Please enter a Client ID!\n\nGet one at:\ndiscord.com/developers/applications")
            return
        
        try:
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.connected = True
            self.start_timestamp = int(time.time())
            
            self.update_presence()
            
            # Update UI
            self.status_dot.delete('dot')
            self.status_dot.create_oval(3, 3, 13, 13, fill='#43B581', outline='', tags='dot')
            self.status_label.config(text="Connected", fg='#43B581')
            
            self.connect_btn.set_state('disabled')
            self.disconnect_btn.set_state('normal')
            self.update_btn.set_state('normal')
            
            # Start keep-alive thread
            self.running = True
            self.update_thread = threading.Thread(target=self.keep_alive, daemon=True)
            self.update_thread.start()
            
            self.save_last_config()
            messagebox.showinfo("Success", "✅ Connected to Discord!\n\nYour Rich Presence is now live!")
            
        except Exception as e:
            error_msg = str(e)
            if "FileNotFoundError" in error_msg or "DiscordNotFound" in error_msg:
                messagebox.showerror("Discord Not Running", 
                                   "❌ Discord is not running!\n\nPlease start Discord first.")
            else:
                messagebox.showerror("Error", f"❌ Failed to connect:\n\n{error_msg}")
    
    def disconnect(self):
        """Disconnect from Discord"""
        try:
            self.running = False
            if self.rpc and self.connected:
                self.rpc.close()
            
            self.connected = False
            self.rpc = None
            
            # Update UI
            self.status_dot.delete('dot')
            self.status_dot.create_oval(3, 3, 13, 13, fill='#F04747', outline='', tags='dot')
            self.status_label.config(text="Disconnected", fg='#F04747')
            
            self.connect_btn.set_state('normal')
            self.disconnect_btn.set_state('disabled')
            self.update_btn.set_state('disabled')
            
            messagebox.showinfo("Disconnected", "✅ Rich Presence stopped.")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error: {str(e)}")
    
    def update_presence(self):
        """Update the Rich Presence"""
        if not self.connected or not self.rpc:
            messagebox.showwarning("Warning", "⚠️ Please connect first!")
            return
        
        try:
            kwargs = {}
            
            if self.details.get().strip():
                kwargs['details'] = self.details.get().strip()
            if self.state.get().strip():
                kwargs['state'] = self.state.get().strip()
            
            if self.large_key.get().strip():
                kwargs['large_image'] = self.large_key.get().strip()
                if self.large_text.get().strip():
                    kwargs['large_text'] = self.large_text.get().strip()
            
            if self.small_key.get().strip():
                kwargs['small_image'] = self.small_key.get().strip()
                if self.small_text.get().strip():
                    kwargs['small_text'] = self.small_text.get().strip()
            
            try:
                if self.party_size.get().strip() and self.party_max.get().strip():
                    kwargs['party_size'] = [int(self.party_size.get()), int(self.party_max.get())]
            except ValueError:
                messagebox.showwarning("Invalid Input", "⚠️ Party size must be numbers!")
                return
            
            if self.show_timestamp.get():
                if self.timestamp_type.get() == "elapsed":
                    kwargs['start'] = self.start_timestamp
                else:
                    kwargs['end'] = int(time.time()) + 3600
            
            buttons = []
            if self.button1_text.get().strip() and self.button1_url.get().strip():
                buttons.append({"label": self.button1_text.get().strip()[:32], 
                              "url": self.button1_url.get().strip()})
            if self.button2_text.get().strip() and self.button2_url.get().strip():
                buttons.append({"label": self.button2_text.get().strip()[:32], 
                              "url": self.button2_url.get().strip()})
            if buttons:
                kwargs['buttons'] = buttons
            
            self.rpc.update(**kwargs)
            self.save_last_config()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to update:\n\n{str(e)}")
    
    def keep_alive(self):
        """Keep the connection alive"""
        while self.running and self.connected:
            time.sleep(15)
    
    def clear_all(self):
        """Clear all input fields"""
        if messagebox.askyesno("Clear All", "Clear all fields?"):
            for entry in [self.details, self.state, self.large_key, self.large_text,
                         self.small_key, self.small_text, self.button1_text,
                         self.button1_url, self.button2_text, self.button2_url,
                         self.party_size, self.party_max]:
                entry.delete(0, tk.END)
            self.show_timestamp.set(False)
            self.toggle_timestamp()
    
    def save_preset(self):
        """Save current configuration as preset"""
        filename = filedialog.asksaveasfilename(
            title="Save Preset",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            preset = self.get_current_config()
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(preset, f, indent=2)
                messagebox.showinfo("Success", f"✅ Preset saved!\n\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to save:\n{str(e)}")
    
    def load_preset(self):
        """Load a preset configuration"""
        filename = filedialog.askopenfilename(
            title="Load Preset",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    preset = json.load(f)
                self.apply_config(preset)
                messagebox.showinfo("Success", f"✅ Preset loaded!\n\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to load:\n{str(e)}")
    
    def get_current_config(self):
        """Get current configuration as dictionary"""
        return {
            'client_id': self.client_id.get(),
            'details': self.details.get(),
            'state': self.state.get(),
            'large_key': self.large_key.get(),
            'large_text': self.large_text.get(),
            'small_key': self.small_key.get(),
            'small_text': self.small_text.get(),
            'button1_text': self.button1_text.get(),
            'button1_url': self.button1_url.get(),
            'button2_text': self.button2_text.get(),
            'button2_url': self.button2_url.get(),
            'party_size': self.party_size.get(),
            'party_max': self.party_max.get(),
            'show_timestamp': self.show_timestamp.get(),
            'timestamp_type': self.timestamp_type.get()
        }
    
    def apply_config(self, config):
        """Apply a configuration dictionary"""
        entries_map = {
            'client_id': self.client_id,
            'details': self.details,
            'state': self.state,
            'large_key': self.large_key,
            'large_text': self.large_text,
            'small_key': self.small_key,
            'small_text': self.small_text,
            'button1_text': self.button1_text,
            'button1_url': self.button1_url,
            'button2_text': self.button2_text,
            'button2_url': self.button2_url,
            'party_size': self.party_size,
            'party_max': self.party_max
        }
        
        for key, entry in entries_map.items():
            entry.delete(0, tk.END)
            entry.insert(0, config.get(key, ''))
        
        self.show_timestamp.set(config.get('show_timestamp', False))
        self.timestamp_type.set(config.get('timestamp_type', 'elapsed'))
        self.toggle_timestamp()
    
    def save_last_config(self):
        """Save current configuration to file"""
        try:
            config = self.get_current_config()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def load_last_config(self):
        """Load last saved configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.last_config = json.load(f)
            else:
                self.last_config = None
        except:
            self.last_config = None
    
    def show_help(self):
        """Show help dialog"""
        help_text = """📖 How to Use DigiRP

1️⃣ Create Discord Application:
   • Go to: discord.com/developers/applications
   • Click "New Application"
   • Copy the Client ID

2️⃣ Upload Images (Optional):
   • Go to "Rich Presence" → "Art Assets"
   • Upload images (1024x1024 PNG)
   • Use the asset name as the key

3️⃣ Configure and Connect:
   • Enter Client ID
   • Fill in Details, State, etc.
   • Click Connect button

4️⃣ Update Anytime:
   • Change fields
   • Click Update button"""
        
        messagebox.showinfo("How to Use", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """🎮 DigiRP v2.0

Modern Discord Rich Presence Manager

✨ Features:
• Custom text
• Images support
• Clickable buttons
• Timestamps
• Party size
• Save/Load presets

Created with Python & pypresence"""
        
        messagebox.showinfo("About DigiRP", about_text)
    
    def on_closing(self):
        """Handle window close event"""
        if self.connected:
            if messagebox.askyesno("Exit", "Disconnect and exit?"):
                self.disconnect()
                time.sleep(0.3)
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = DiscordRPApp(root)
        
        # Load last config
        if hasattr(app, 'last_config') and app.last_config:
            app.apply_config(app.last_config)
        
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        messagebox.showerror("Fatal Error", f"Failed to start:\n\n{str(e)}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
