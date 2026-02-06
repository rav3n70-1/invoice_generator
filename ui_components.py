"""
UI Components for SneakerCanvasBD
Reusable UI elements: Toast notifications, Confirmation dialogs, Loading spinners, Keyboard shortcuts
"""

import tkinter as tk
from tkinter import ttk
import threading
import time


class ToastNotification:
    """Slide-in toast notification widget"""
    
    # Toast types with colors
    TYPES = {
        'success': {'bg': '#22c55e', 'icon': '✓'},
        'error': {'bg': '#dc2626', 'icon': '✗'},
        'warning': {'bg': '#f59e0b', 'icon': '⚠'},
        'info': {'bg': '#3b82f6', 'icon': 'ℹ'}
    }
    
    def __init__(self, parent, message: str, toast_type: str = 'info', duration: int = 3000):
        self.parent = parent
        self.duration = duration
        
        config = self.TYPES.get(toast_type, self.TYPES['info'])
        
        # Create toast window
        self.toast = tk.Toplevel(parent)
        self.toast.overrideredirect(True)
        self.toast.attributes('-topmost', True)
        self.toast.configure(bg=config['bg'])
        
        # Position at top-right of parent
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        
        toast_width = 300
        toast_height = 50
        x = parent_x + parent_width - toast_width - 20
        y = parent_y + 20
        
        self.toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # Content
        frame = tk.Frame(self.toast, bg=config['bg'], padx=15, pady=10)
        frame.pack(fill='both', expand=True)
        
        icon_label = tk.Label(frame, text=config['icon'], bg=config['bg'], fg='white', 
                             font=('Segoe UI', 14, 'bold'))
        icon_label.pack(side='left', padx=(0, 10))
        
        msg_label = tk.Label(frame, text=message, bg=config['bg'], fg='white',
                            font=('Segoe UI', 10), wraplength=230, justify='left')
        msg_label.pack(side='left', fill='x', expand=True)
        
        # Close button
        close_btn = tk.Label(frame, text='×', bg=config['bg'], fg='white',
                            font=('Segoe UI', 14), cursor='hand2')
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e: self.dismiss())
        
        # Auto-dismiss after duration
        self.toast.after(duration, self.dismiss)
    
    def dismiss(self):
        """Close the toast"""
        try:
            self.toast.destroy()
        except:
            pass


class ConfirmDialog:
    """Styled confirmation dialog"""
    
    def __init__(self, parent, title: str, message: str, 
                 confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                 confirm_color: str = '#dc2626', icon: str = '⚠'):
        self.result = False
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Colors
        bg_color = '#1e293b'
        card_color = '#334155'
        text_color = 'white'
        dim_color = '#94a3b8'
        
        self.dialog.configure(bg=bg_color)
        
        # Center on parent
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 400
        dialog_height = 200
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Content
        main_frame = tk.Frame(self.dialog, bg=bg_color, padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Icon and title
        header = tk.Frame(main_frame, bg=bg_color)
        header.pack(fill='x', pady=(0, 15))
        
        tk.Label(header, text=icon, bg=bg_color, fg=confirm_color,
                font=('Segoe UI', 28)).pack(side='left', padx=(0, 15))
        
        title_frame = tk.Frame(header, bg=bg_color)
        title_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(title_frame, text=title, bg=bg_color, fg=text_color,
                font=('Segoe UI', 14, 'bold'), anchor='w').pack(fill='x')
        tk.Label(title_frame, text=message, bg=bg_color, fg=dim_color,
                font=('Segoe UI', 10), anchor='w', wraplength=280, 
                justify='left').pack(fill='x', pady=(5, 0))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=bg_color)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = tk.Button(btn_frame, text=cancel_text, bg=card_color, fg=text_color,
                              relief='flat', padx=20, pady=8, font=('Segoe UI', 10),
                              cursor='hand2', command=self._cancel)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        confirm_btn = tk.Button(btn_frame, text=confirm_text, bg=confirm_color, fg='white',
                               relief='flat', padx=20, pady=8, font=('Segoe UI', 10, 'bold'),
                               cursor='hand2', command=self._confirm)
        confirm_btn.pack(side='right')
        
        # Key bindings
        self.dialog.bind('<Return>', lambda e: self._confirm())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
        
        # Focus on dialog
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def _confirm(self):
        self.result = True
        self.dialog.destroy()
    
    def _cancel(self):
        self.result = False
        self.dialog.destroy()


class LoadingSpinner:
    """Loading overlay with spinner for long operations"""
    
    def __init__(self, parent, message: str = "Loading..."):
        self.parent = parent
        self.running = False
        self.overlay = None
        self.message = message
    
    def show(self):
        """Show the loading overlay"""
        if self.overlay:
            return
        
        self.running = True
        
        # Create overlay
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost', True)
        
        # Semi-transparent background
        bg_color = '#0f172a'
        self.overlay.configure(bg=bg_color)
        self.overlay.wm_attributes('-alpha', 0.9)
        
        # Position over parent
        self.parent.update_idletasks()
        x = self.parent.winfo_rootx()
        y = self.parent.winfo_rooty()
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Content
        frame = tk.Frame(self.overlay, bg=bg_color)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.spinner_label = tk.Label(frame, text="◐", bg=bg_color, fg='#ef4444',
                                      font=('Segoe UI', 48))
        self.spinner_label.pack()
        
        tk.Label(frame, text=self.message, bg=bg_color, fg='white',
                font=('Segoe UI', 12)).pack(pady=(10, 0))
        
        # Start animation
        self._animate()
    
    def _animate(self):
        """Animate the spinner"""
        if not self.running or not self.overlay:
            return
        
        symbols = ['◐', '◓', '◑', '◒']
        try:
            current = self.spinner_label.cget('text')
            idx = symbols.index(current) if current in symbols else 0
            next_idx = (idx + 1) % len(symbols)
            self.spinner_label.config(text=symbols[next_idx])
            self.overlay.after(150, self._animate)
        except:
            pass
    
    def hide(self):
        """Hide the loading overlay"""
        self.running = False
        if self.overlay:
            try:
                self.overlay.destroy()
            except:
                pass
            self.overlay = None


class KeyboardShortcuts:
    """Mixin class for keyboard shortcut handling"""
    
    @staticmethod
    def setup_shortcuts(root, shortcuts: dict):
        """
        Setup keyboard shortcuts.
        shortcuts: dict of {key_combo: callback}
        Example: {'<Control-n>': self.new_invoice, '<Control-s>': self.save}
        """
        for key_combo, callback in shortcuts.items():
            root.bind_all(key_combo, lambda e, cb=callback: cb())
    
    @staticmethod
    def setup_common_shortcuts(root, new_callback=None, save_callback=None, 
                               cancel_callback=None, refresh_callback=None):
        """Setup common shortcuts: Ctrl+N (new), Ctrl+S (save), Esc (cancel), F5 (refresh)"""
        shortcuts = {}
        
        if new_callback:
            shortcuts['<Control-n>'] = new_callback
            shortcuts['<Control-N>'] = new_callback
        
        if save_callback:
            shortcuts['<Control-s>'] = save_callback
            shortcuts['<Control-S>'] = save_callback
        
        if cancel_callback:
            shortcuts['<Escape>'] = cancel_callback
        
        if refresh_callback:
            shortcuts['<F5>'] = refresh_callback
        
        for key_combo, callback in shortcuts.items():
            root.bind_all(key_combo, lambda e, cb=callback: cb())


class KPICard(tk.Frame):
    """KPI display card for dashboard"""
    
    def __init__(self, parent, title: str, value: str, subtitle: str = "",
                 trend: str = None, trend_positive: bool = True, 
                 bg_color: str = '#334155', accent_color: str = '#ef4444', **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.configure(padx=15, pady=15)
        
        # Title
        title_label = tk.Label(self, text=title, bg=bg_color, fg='#94a3b8',
                              font=('Segoe UI', 9))
        title_label.pack(anchor='w')
        
        # Value with trend
        value_frame = tk.Frame(self, bg=bg_color)
        value_frame.pack(anchor='w', pady=(5, 0))
        
        value_label = tk.Label(value_frame, text=value, bg=bg_color, fg='white',
                              font=('Segoe UI', 24, 'bold'))
        value_label.pack(side='left')
        
        if trend:
            trend_color = '#22c55e' if trend_positive else '#dc2626'
            trend_icon = '↑' if trend_positive else '↓'
            trend_label = tk.Label(value_frame, text=f"{trend_icon} {trend}", 
                                  bg=bg_color, fg=trend_color, font=('Segoe UI', 10))
            trend_label.pack(side='left', padx=(10, 0))
        
        # Subtitle
        if subtitle:
            subtitle_label = tk.Label(self, text=subtitle, bg=bg_color, fg='#64748b',
                                     font=('Segoe UI', 9))
            subtitle_label.pack(anchor='w', pady=(5, 0))
    
    def update_value(self, value: str, trend: str = None, trend_positive: bool = True):
        """Update the card's value and trend"""
        # This would need internal label references to work properly
        pass


class TreeviewHelper:
    """Helper for styled Treeview with zebra striping and conditional colors"""
    
    @staticmethod
    def configure_style(tree: ttk.Treeview, 
                       bg_color: str = '#1e293b',
                       alt_color: str = '#0f172a',
                       select_color: str = '#ef4444',
                       text_color: str = 'white'):
        """Configure Treeview styling"""
        style = ttk.Style()
        
        # Configure Treeview
        style.configure("Custom.Treeview",
                       background=bg_color,
                       foreground=text_color,
                       fieldbackground=bg_color,
                       rowheight=30)
        
        style.configure("Custom.Treeview.Heading",
                       background='#334155',
                       foreground=text_color,
                       font=('Segoe UI', 10, 'bold'))
        
        style.map("Custom.Treeview",
                 background=[('selected', select_color)])
        
        tree.configure(style="Custom.Treeview")
        
        # Configure tags for conditional formatting
        tree.tag_configure('oddrow', background=alt_color)
        tree.tag_configure('evenrow', background=bg_color)
        tree.tag_configure('low_stock', background='#4a1c1c')  # Dark red
        tree.tag_configure('aging_warning', background='#4a3d1c')  # Dark amber
        tree.tag_configure('aging_critical', background='#4a1c1c')  # Dark red
        tree.tag_configure('high_profit', background='#1c4a2e')  # Dark green
    
    @staticmethod
    def apply_zebra_striping(tree: ttk.Treeview):
        """Apply zebra striping to Treeview rows"""
        for idx, item in enumerate(tree.get_children()):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            current_tags = list(tree.item(item, 'tags'))
            # Remove existing row tags
            current_tags = [t for t in current_tags if t not in ('oddrow', 'evenrow')]
            current_tags.append(tag)
            tree.item(item, tags=current_tags)
    
    @staticmethod
    def apply_conditional_color(tree: ttk.Treeview, item_id: str, condition_tag: str):
        """Apply a conditional color tag to an item"""
        current_tags = list(tree.item(item_id, 'tags'))
        if condition_tag not in current_tags:
            current_tags.append(condition_tag)
            tree.item(item_id, tags=current_tags)


def show_toast(parent, message: str, toast_type: str = 'info', duration: int = 3000):
    """Convenience function to show a toast notification"""
    ToastNotification(parent, message, toast_type, duration)


def confirm_action(parent, title: str, message: str, 
                  confirm_text: str = "Confirm", icon: str = '⚠') -> bool:
    """Convenience function to show confirmation dialog and return result"""
    dialog = ConfirmDialog(parent, title, message, confirm_text=confirm_text, icon=icon)
    return dialog.result


def with_loading(parent, func, message: str = "Loading..."):
    """Execute a function with loading overlay. Returns function result."""
    spinner = LoadingSpinner(parent, message)
    
    result = [None]
    error = [None]
    
    def run():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e
        finally:
            parent.after(0, spinner.hide)
    
    spinner.show()
    thread = threading.Thread(target=run)
    thread.start()
    
    # Wait for completion (with UI updates)
    while thread.is_alive():
        parent.update()
        time.sleep(0.05)
    
    if error[0]:
        raise error[0]
    
    return result[0]
