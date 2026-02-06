import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import threading

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel()
        self.splash.overrideredirect(True)  # Remove window decorations
        
        # Get screen dimensions
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        
        # Splash window size
        width, height = 500, 400
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        self.splash.configure(bg="#1e1e2e")
        
        # Main frame
        frame = tk.Frame(self.splash, bg="#1e1e2e")
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Load and display logo
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "assets", "logo.jpg")
            
            img = Image.open(logo_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            
            logo_label = tk.Label(frame, image=self.photo, bg="#1e1e2e")
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # App title
        title = tk.Label(
            frame, 
            text="SNEAKER CANVAS BD", 
            font=("Segoe UI", 24, "bold"),
            fg="#00d4ff",
            bg="#1e1e2e"
        )
        title.pack(pady=(0, 5))
        
        # Subtitle
        subtitle = tk.Label(
            frame,
            text="Developed by R4V3N",
            font=("Segoe UI", 12),
            fg="#a0a0a0",
            bg="#1e1e2e"
        )
        subtitle.pack(pady=(0, 30))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=(0, 10))
        self.progress.start(10)
        
        # Loading text
        self.status_label = tk.Label(
            frame,
            text="Loading...",
            font=("Segoe UI", 10),
            fg="#ffffff",
            bg="#1e1e2e"
        )
        self.status_label.pack()
        
        # Simulate loading stages
        self.loading_stages = [
            "Initializing application...",
            "Loading invoice database...",
            "Loading inventory...",
            "Setting up interface...",
            "Almost ready..."
        ]
        self.current_stage = 0
        
        self.splash.update()
    
    def update_status(self, text):
        """Update loading status text"""
        self.status_label.config(text=text)
        self.splash.update()
    
    def next_stage(self):
        """Move to next loading stage"""
        if self.current_stage < len(self.loading_stages):
            self.update_status(self.loading_stages[self.current_stage])
            self.current_stage += 1
            return True
        return False
    
    def close(self):
        """Close the splash screen"""
        self.progress.stop()
        self.splash.destroy()
