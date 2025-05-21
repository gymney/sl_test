import sqlite3
import math
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set style for better looking plots
plt.style.use('dark_background')
sns.set_palette("husl")

class SoloLevelingGUI:
    def __init__(self):
        self.colors = {
            "bg_main": "#1a1b26",      # Main background
            "bg_frame": "#24283b",     # Inner frames
            "bg_secondary": "#16161e", # Secondary background
            "fg_text": "#c0caf5",      # Regular text
            "fg_accent": "#7aa2f7",    # Accent (titles, highlights)
            "fg_secondary": "#9aa5ce", # Secondary text
            "button_bg": "#414868",    # Button background
            "button_fg": "#c0caf5",    # Button text
            "button_hover": "#565f89", # Button hover
            "highlight": "#bb9af7",    # Special highlights
            "success": "#9ece6a",      # Success color
            "warning": "#e0af68",      # Warning color
            "error": "#f7768e",        # Error color
            "border": "#414868",       # Border color
        }

        self.attributes = {
            "life_skills": [
                "communication", "critical_thinking_problem_solving", "time_management",
                "self_care_emotional_regulation", "cooking_nutrition", "car_home_maintenance",
                "digital_literacy", "interpersonal_social_skills", "independence", "learning_efficiency"
            ],
            "content_creation": [
                "seo_literacy", "video_editing", "streaming", "long_form_content_output",
                "short_form_content_output", "charisma", "personality_authenticity",
                "online_presence", "consistency", "backlog_management"
            ],
            "financial_literacy": [
                "budgeting_savings", "emergency_fund_management", "investment_knowledge",
                "retirement_contributions_roth", "401k_optimization", "hsa_utilization",
                "insurance_literacy", "loan_understanding", "tax_optimization", "financial_goal_tracking"
            ],
            "career": [
                "technical_mastery", "soft_skills_work", "time_management_work",
                "growth_milestones", "professional_networking", "contribution_tracking",
                "performance_feedback", "industry_knowledge", "leadership_development", "project_management"
            ],
            "vision_strategy": [
                "daily_goal_setting", "weekly_planning", "monthly_goal_review",
                "quarterly_assessment", "yearly_vision_alignment", "system_design",
                "reflection_reviewing", "strategic_thinking", "priority_management", "personal_roadmapping"
            ]
        }
        
        self.db_file = "solo_leveling.db"
        self.init_database()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("🎮 Solo Leveling System V3 🎮")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors["bg_main"])
        
        # Configure ttk style for Tokyo Night theme
        self.setup_ttk_style()
        
        # Check if first run
        self.is_first_run = self.check_first_run()
        
        self.setup_gui()
        
        # Handle first run
        if self.is_first_run:
            self.root.after(1000, self.show_crystal_ball_welcome)  # Delay to let GUI load
    
    def setup_ttk_style(self):
        """Configure ttk styles for Tokyo Night theme"""
        style = ttk.Style()
        
        # Configure Notebook style
        style.theme_use('clam')
        style.configure('TNotebook', 
                       background=self.colors["bg_frame"],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.colors["button_bg"],
                       foreground=self.colors["fg_text"],
                       padding=[20, 8],
                       borderwidth=1,
                       focuscolor='none')
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors["fg_accent"]),
                           ('active', self.colors["button_hover"])],
                 foreground=[('selected', self.colors["bg_main"]),
                           ('active', self.colors["fg_text"])])
        
        # Configure Frame style
        style.configure('TFrame', background=self.colors["bg_frame"])
        
        # Configure Treeview style
        style.configure('Treeview',
                       background=self.colors["bg_frame"],
                       foreground=self.colors["fg_text"],
                       fieldbackground=self.colors["bg_frame"],
                       borderwidth=1,
                       relief='solid')
        style.configure('Treeview.Heading',
                       background=self.colors["button_bg"],
                       foreground=self.colors["fg_text"],
                       borderwidth=1,
                       relief='solid')
        style.map('Treeview',
                 background=[('selected', self.colors["fg_accent"])],
                 foreground=[('selected', self.colors["bg_main"])])
        
        # Configure Scrollbar style
        style.configure('TScrollbar',
                       background=self.colors["button_bg"],
                       troughcolor=self.colors["bg_secondary"],
                       borderwidth=0,
                       arrowcolor=self.colors["fg_text"])
        style.map('TScrollbar',
                 background=[('active', self.colors["button_hover"])])
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Skills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attribute TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                current_level INTEGER NOT NULL DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(attribute, skill_name)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_timestamp TIMESTAMP NOT NULL,
                total_gains INTEGER NOT NULL DEFAULT 0,
                session_type TEXT NOT NULL DEFAULT 'update',
                notes TEXT
            )
        ''')
        
        # Session updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                attribute TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                old_level INTEGER NOT NULL,
                new_level INTEGER NOT NULL,
                gain INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Initialize skills if empty
        cursor.execute('SELECT COUNT(*) FROM skills')
        if cursor.fetchone()[0] == 0:
            for attribute in self.attributes:
                for skill in self.attributes[attribute]:
                    cursor.execute('''
                        INSERT OR IGNORE INTO skills (attribute, skill_name, current_level)
                        VALUES (?, ?, ?)
                    ''', (attribute, skill, 1))
        
        conn.commit()
        conn.close()
    
    def check_first_run(self) -> bool:
        """Check if this is the user's first time running the system"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM skills WHERE current_level > 1')
        has_progress = cursor.fetchone()[0] > 0
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        has_sessions = cursor.fetchone()[0] > 0
        
        conn.close()
        return not (has_progress or has_sessions)
    
    def sigmoid_level_calculation(self, total_points: int, max_points: int) -> int:
        """Calculate level using sigmoid curve"""
        if total_points <= 0:
            return 1
        
        x = total_points / max_points
        sigmoid_value = 1 / (1 + math.exp(-10 * (x - 0.5)))
        level = int(1 + sigmoid_value * 99)
        return min(level, 100)
    
    def calculate_attribute_level(self, attribute: str) -> int:
        """Calculate attribute level based on sum of all skills"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(current_level) FROM skills WHERE attribute = ?', (attribute,))
        total_skill_points = cursor.fetchone()[0] or 0
        
        conn.close()
        
        max_skill_points = len(self.attributes[attribute]) * 100
        return self.sigmoid_level_calculation(total_skill_points, max_skill_points)
    
    def calculate_overall_level(self) -> int:
        """Calculate overall level based on sum of all attribute levels (out of 500)"""
        total_attribute_points = sum(self.calculate_attribute_level(attr) for attr in self.attributes)
        max_attribute_points = len(self.attributes) * 100  # 5 attributes × 100 = 500
        return total_attribute_points  # Return raw sum for display as X/500
    
    def get_current_skills(self) -> dict:
        """Get current skill levels from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT attribute, skill_name, current_level FROM skills ORDER BY attribute, skill_name')
        rows = cursor.fetchall()
        
        skills = {}
        for attribute, skill_name, level in rows:
            if attribute not in skills:
                skills[attribute] = {}
            skills[attribute][skill_name] = level
        
        conn.close()
        return skills
    
    def create_tokyo_button(self, parent, text, command, bg_color=None, width=None):
        """Create a Tokyo Night themed button"""
        if bg_color is None:
            bg_color = self.colors["button_bg"]
        
        button = tk.Button(parent, 
                          text=text,
                          command=command,
                          font=('Segoe UI', 10, 'bold'),
                          bg=bg_color,
                          fg=self.colors["button_fg"],
                          activebackground=self.colors["button_hover"],
                          activeforeground=self.colors["fg_text"],
                          relief=tk.FLAT,
                          bd=0,
                          padx=15,
                          pady=8,
                          cursor='hand2')
        
        if width:
            button.config(width=width)
        
        # Add hover effects
        def on_enter(e):
            button.config(bg=self.colors["button_hover"])
        
        def on_leave(e):
            button.config(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="🎮 SOLO LEVELING SYSTEM 🎮", 
                              font=('Segoe UI', 26, 'bold'), 
                              fg=self.colors["fg_accent"], 
                              bg=self.colors["bg_main"])
        title_label.pack(pady=(0, 25))
        
        # Overall level display
        self.overall_level_frame = tk.Frame(main_frame, 
                                           bg=self.colors["bg_frame"], 
                                           relief=tk.FLAT, 
                                           bd=2)
        self.overall_level_frame.pack(fill=tk.X, pady=(0, 25))
        
        max_level = len(self.attributes) * 100  # 500
        current_level = self.calculate_overall_level()
        self.overall_level_label = tk.Label(self.overall_level_frame, 
                                           text=f"🏆 OVERALL LEVEL: {current_level}/{max_level}",
                                           font=('Segoe UI', 22, 'bold'), 
                                           fg=self.colors["warning"], 
                                           bg=self.colors["bg_frame"])
        self.overall_level_label.pack(pady=15)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_stats_tab()
        self.setup_update_tab()
        self.setup_progress_tab()
        self.setup_history_tab()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Crystal Ball button
        crystal_button = self.create_tokyo_button(button_frame, 
                                                 "🔮 Crystal Ball Assessment", 
                                                 self.show_crystal_ball_dialog,
                                                 self.colors["highlight"])
        crystal_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Refresh button
        refresh_button = self.create_tokyo_button(button_frame, 
                                                 "🔄 Refresh All", 
                                                 self.refresh_all_data,
                                                 self.colors["success"])
        refresh_button.pack(side=tk.LEFT)
    
    def setup_stats_tab(self):
        """Setup the current stats tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Current Stats")
        
        # Create canvas and scrollbar for stats
        canvas = tk.Canvas(stats_frame, bg=self.colors["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_main"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.stats_content_frame = scrollable_frame
        self.refresh_stats_display()
    
    def setup_update_tab(self):
        """Setup the skill update tab"""
        update_frame = ttk.Frame(self.notebook)
        self.notebook.add(update_frame, text="📈 Update Skills")
        
        # Main container
        main_container = tk.Frame(update_frame, bg=self.colors["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Instructions
        instructions = tk.Label(main_container, 
                               text="Select skills to update (max +10 levels per session)",
                               font=('Segoe UI', 12), 
                               fg=self.colors["fg_text"],
                               bg=self.colors["bg_main"])
        instructions.pack(pady=(0, 15))
        
        # Custom date option
        date_frame = tk.Frame(main_container, bg=self.colors["bg_frame"])
        date_frame.pack(pady=(0, 15), fill=tk.X)
        
        tk.Label(date_frame, 
                text="Custom Date (YYYY-MM-DD):", 
                bg=self.colors["bg_frame"],
                fg=self.colors["fg_text"],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.custom_date_var = tk.StringVar()
        date_entry = tk.Entry(date_frame, 
                             textvariable=self.custom_date_var, 
                             width=12,
                             bg=self.colors["bg_secondary"],
                             fg=self.colors["fg_text"],
                             insertbackground=self.colors["fg_text"],
                             font=('Segoe UI', 10),
                             relief=tk.FLAT,
                             bd=5)
        date_entry.pack(side=tk.LEFT, padx=(5, 10), pady=10)
        
        # Create update interface
        self.setup_update_interface(main_container)
    
    def setup_update_interface(self, parent):
        """Setup the skill update interface"""
        # Create notebook for attributes
        attr_notebook = ttk.Notebook(parent)
        attr_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.update_entries = {}
        
        for attribute in self.attributes:
            # Create frame for this attribute
            attr_frame = ttk.Frame(attr_notebook)
            attr_name_display = attribute.replace("_", " ").title()
            attr_notebook.add(attr_frame, text=attr_name_display)
            
            # Create scrollable frame
            canvas = tk.Canvas(attr_frame, bg=self.colors["bg_main"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_main"])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add skills to this attribute
            self.update_entries[attribute] = {}
            skills = self.get_current_skills().get(attribute, {})
            
            for i, skill in enumerate(self.attributes[attribute]):
                skill_frame = tk.Frame(scrollable_frame, bg=self.colors["bg_frame"])
                skill_frame.pack(fill=tk.X, padx=15, pady=8)
                
                skill_display = skill.replace("_", " ").title()
                current_level = skills.get(skill, 1)
                
                # Skill label
                label = tk.Label(skill_frame, 
                               text=f"{skill_display}:", 
                               font=('Segoe UI', 10), 
                               bg=self.colors["bg_frame"],
                               fg=self.colors["fg_text"],
                               width=30, 
                               anchor='e')
                label.pack(side=tk.LEFT, padx=(10, 5), pady=10)
                
                # Current level display
                current_label = tk.Label(skill_frame, 
                                       text=f"[{current_level}]", 
                                       font=('Segoe UI', 10, 'bold'), 
                                       bg=self.colors["bg_frame"],
                                       fg=self.colors["fg_accent"])
                current_label.pack(side=tk.LEFT, padx=10, pady=10)
                
                # New level entry
                entry_var = tk.StringVar()
                entry = tk.Entry(skill_frame, 
                               textvariable=entry_var, 
                               width=8,
                               bg=self.colors["bg_secondary"],
                               fg=self.colors["fg_text"],
                               insertbackground=self.colors["fg_text"],
                               font=('Segoe UI', 10),
                               relief=tk.FLAT,
                               bd=5)
                entry.pack(side=tk.LEFT, padx=(10, 15), pady=10)
                
                self.update_entries[attribute][skill] = {
                    'var': entry_var,
                    'current': current_level,
                    'label': current_label
                }
        
        # Update button
        update_button = self.create_tokyo_button(parent, 
                                                "💾 Save Updates", 
                                                self.process_skill_updates,
                                                self.colors["fg_accent"])
        update_button.pack(pady=15)
        update_button.config(font=('Segoe UI', 14, 'bold'))
    
    def setup_progress_tab(self):
        """Setup the progress visualization tab"""
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="📈 Progress Charts")
        
        # Main container
        main_container = tk.Frame(progress_frame, bg=self.colors["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure with Tokyo Night colors
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor=self.colors["bg_main"])
        self.canvas = FigureCanvasTkAgg(self.fig, main_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Chart selection buttons
        chart_frame = tk.Frame(main_container, bg=self.colors["bg_main"])
        chart_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_tokyo_button(chart_frame, "📊 Attribute Levels", 
                                self.show_attribute_chart,
                                self.colors["fg_accent"]).pack(side=tk.LEFT, padx=(15, 10))
        
        self.create_tokyo_button(chart_frame, "📈 Progress Over Time", 
                                self.show_progress_chart,
                                self.colors["success"]).pack(side=tk.LEFT, padx=5)
        
        self.create_tokyo_button(chart_frame, "🎯 Skill Heatmap", 
                                self.show_skill_heatmap,
                                self.colors["error"]).pack(side=tk.LEFT, padx=5)
        
        # Show initial chart
        self.show_attribute_chart()
    
    def setup_history_tab(self):
        """Setup the session history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📚 Session History")
        
        # Main container
        main_container = tk.Frame(history_frame, bg=self.colors["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create treeview for session history
        columns = ('Date', 'Type', 'Total Gains', 'Notes')
        self.history_tree = ttk.Treeview(main_container, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(main_container, orient="horizontal", command=self.history_tree.xview)
        v_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.refresh_history_display()
    
    def show_crystal_ball_welcome(self):
        """Show welcome dialog for first-time users"""
        # Create custom dialog with Tokyo Night theme
        welcome_window = tk.Toplevel(self.root)
        welcome_window.title("🔮 Welcome, New Adventurer! 🔮")
        welcome_window.geometry("500x300")
        welcome_window.configure(bg=self.colors["bg_main"])
        welcome_window.grab_set()
        welcome_window.transient(self.root)
        
        # Center the window
        welcome_window.geometry("+{}+{}".format(
            int(self.root.winfo_x() + self.root.winfo_width()/2 - 250),
            int(self.root.winfo_y() + self.root.winfo_height()/2 - 150)
        ))
        
        # Title
        title_label = tk.Label(welcome_window,
                              text="🔮 Welcome, New Adventurer! 🔮",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors["fg_accent"],
                              bg=self.colors["bg_main"])
        title_label.pack(pady=20)
        
        # Message
        message_text = ("Welcome to the Solo Leveling System!\n\n"
                       "It seems this is your first time here.\n"
                       "Would you like to assess your current abilities\n"
                       "with the mystical Crystal Ball?\n\n"
                       "This will help establish your starting stats.")
        
        message_label = tk.Label(welcome_window,
                               text=message_text,
                               font=('Segoe UI', 11),
                               fg=self.colors["fg_text"],
                               bg=self.colors["bg_main"],
                               justify=tk.CENTER)
        message_label.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(welcome_window, bg=self.colors["bg_main"])
        button_frame.pack(pady=20)
        
        def on_yes():
            welcome_window.destroy()
            self.show_crystal_ball_dialog()
        
        def on_no():
            welcome_window.destroy()
        
        self.create_tokyo_button(button_frame, "✨ Yes, Let's Begin!", 
                                on_yes, self.colors["success"]).pack(side=tk.LEFT, padx=10)
        
        self.create_tokyo_button(button_frame, "❌ Maybe Later", 
                                on_no, self.colors["error"]).pack(side=tk.LEFT, padx=10)
    
    def show_crystal_ball_dialog(self):
        """Show crystal ball assessment dialog"""
        crystal_window = tk.Toplevel(self.root)
        crystal_window.title("🔮 Crystal Ball Assessment 🔮")
        crystal_window.geometry("900x700")
        crystal_window.configure(bg=self.colors["bg_main"])
        crystal_window.grab_set()  # Make it modal
        
        # Title
        title_label = tk.Label(crystal_window, 
                              text="🔮✨ MYSTICAL STAT ASSESSMENT ✨🔮",
                              font=('Segoe UI', 20, 'bold'), 
                              fg=self.colors["warning"], 
                              bg=self.colors["bg_main"])
        title_label.pack(pady=15)
        
        # Instructions frame
        instructions_frame = tk.Frame(crystal_window, bg=self.colors["bg_frame"])
        instructions_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        instructions = tk.Label(instructions_frame,
                               text="The ancient crystal reveals your true abilities...\n"
                                    "Rate each skill from 1-100 based on your current level:\n\n"
                                    "• 1-20: Complete beginner\n"
                                    "• 21-40: Some experience/knowledge\n"
                                    "• 41-60: Intermediate proficiency\n"
                                    "• 61-80: Advanced/Skilled\n"
                                    "• 81-100: Expert/Master level",
                               font=('Segoe UI', 10), 
                               fg=self.colors["fg_text"], 
                               bg=self.colors["bg_frame"],
                               justify=tk.LEFT)
        instructions.pack(pady=15)
        
        # Create notebook for crystal ball assessment
        crystal_notebook = ttk.Notebook(crystal_window)
        crystal_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        crystal_entries = {}
        
        for attribute in self.attributes:
            attr_frame = ttk.Frame(crystal_notebook)
            attr_name_display = attribute.replace("_", " ").title()
            crystal_notebook.add(attr_frame, text=attr_name_display)
            
            # Create scrollable frame
            canvas = tk.Canvas(attr_frame, bg=self.colors["bg_main"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_main"])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            crystal_entries[attribute] = {}
            
            for skill in self.attributes[attribute]:
                skill_frame = tk.Frame(scrollable_frame, bg=self.colors["bg_frame"])
                skill_frame.pack(fill=tk.X, padx=15, pady=8)
                
                skill_display = skill.replace("_", " ").title()
                
                label = tk.Label(skill_frame, 
                               text=f"🔍 {skill_display}:", 
                               font=('Segoe UI', 10), 
                