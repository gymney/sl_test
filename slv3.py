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
plt.style.use('default')
sns.set_palette("husl")

class SoloLevelingGUI:
    def __init__(self):
        self.colors = {
            "bg_main": "#1a1b26",      # Main background
            "bg_frame": "#24283b",     # Inner frames
            "fg_text": "#c0caf5",      # Regular text
            "fg_accent": "#7aa2f7",    # Accent (titles, highlights)
            "button_bg": "#414868",    # Button background
            "button_fg": "#c0caf5",    # Button text
            "highlight": "#bb9af7",    # Special highlights
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
        self.root.configure(bg='#2c3e50')
        
        # Check if first run
        self.is_first_run = self.check_first_run()
        
        self.setup_gui()
        
        # Handle first run
        if self.is_first_run:
            self.root.after(1000, self.show_crystal_ball_welcome)  # Delay to let GUI load
    
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
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎮 SOLO LEVELING SYSTEM 🎮", 
                              font=('Arial', 24, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Overall level display
        self.overall_level_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        self.overall_level_frame.pack(fill=tk.X, pady=(0, 20))
        
        max_level = len(self.attributes) * 100  # 500
        current_level = self.calculate_overall_level()
        self.overall_level_label = tk.Label(self.overall_level_frame, 
                                           text=f"🏆 OVERALL LEVEL: {current_level}/{max_level}",
                                           font=('Arial', 20, 'bold'), fg='#f39c12', bg='#34495e')
        self.overall_level_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_stats_tab()
        self.setup_update_tab()
        self.setup_progress_tab()
        self.setup_history_tab()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Crystal Ball button
        crystal_button = tk.Button(button_frame, text="🔮 Crystal Ball Assessment", 
                                  command=self.show_crystal_ball_dialog,
                                  font=('Arial', 12, 'bold'), bg='#9b59b6', fg='white',
                                  relief=tk.RAISED, bd=3)
        crystal_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_button = tk.Button(button_frame, text="🔄 Refresh All", 
                                  command=self.refresh_all_data,
                                  font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                  relief=tk.RAISED, bd=3)
        refresh_button.pack(side=tk.LEFT)
    
    def setup_stats_tab(self):
        """Setup the current stats tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Current Stats")
        
        # Create canvas and scrollbar for stats
        canvas = tk.Canvas(stats_frame, bg='#ecf0f1')
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')
        
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
        
        # Instructions
        instructions = tk.Label(update_frame, 
                               text="Select skills to update (max +10 levels per session)",
                               font=('Arial', 12), bg='#ecf0f1')
        instructions.pack(pady=10)
        
        # Custom date option
        date_frame = tk.Frame(update_frame, bg='#ecf0f1')
        date_frame.pack(pady=5)
        
        tk.Label(date_frame, text="Custom Date (YYYY-MM-DD):", bg='#ecf0f1').pack(side=tk.LEFT)
        self.custom_date_var = tk.StringVar()
        date_entry = tk.Entry(date_frame, textvariable=self.custom_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        # Create update interface
        self.setup_update_interface(update_frame)
    
    def setup_update_interface(self, parent):
        """Setup the skill update interface"""
        # Create notebook for attributes
        attr_notebook = ttk.Notebook(parent)
        attr_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_entries = {}
        
        for attribute in self.attributes:
            # Create frame for this attribute
            attr_frame = ttk.Frame(attr_notebook)
            attr_name_display = attribute.replace("_", " ").title()
            attr_notebook.add(attr_frame, text=attr_name_display)
            
            # Create scrollable frame
            canvas = tk.Canvas(attr_frame, bg='#ecf0f1')
            scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')
            
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
                skill_frame = tk.Frame(scrollable_frame, bg='#ecf0f1')
                skill_frame.pack(fill=tk.X, padx=10, pady=5)
                
                skill_display = skill.replace("_", " ").title()
                current_level = skills.get(skill, 1)
                
                # Skill label
                label = tk.Label(skill_frame, text=f"{skill_display}:", 
                               font=('Arial', 10), bg='#ecf0f1', width=25, anchor='e')
                label.pack(side=tk.LEFT)
                
                # Current level display
                current_label = tk.Label(skill_frame, text=f"[{current_level}]", 
                                       font=('Arial', 10, 'bold'), bg='#ecf0f1')
                current_label.pack(side=tk.LEFT, padx=5)
                
                # New level entry
                entry_var = tk.StringVar()
                entry = tk.Entry(skill_frame, textvariable=entry_var, width=5)
                entry.pack(side=tk.LEFT, padx=5)
                
                self.update_entries[attribute][skill] = {
                    'var': entry_var,
                    'current': current_level,
                    'label': current_label
                }
        
        # Update button
        update_button = tk.Button(parent, text="💾 Save Updates", 
                                 command=self.process_skill_updates,
                                 font=('Arial', 14, 'bold'), bg='#3498db', fg='white',
                                 relief=tk.RAISED, bd=3)
        update_button.pack(pady=10)
    
    def setup_progress_tab(self):
        """Setup the progress visualization tab"""
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="📈 Progress Charts")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='#ecf0f1')
        self.canvas = FigureCanvasTkAgg(self.fig, progress_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Chart selection buttons
        chart_frame = tk.Frame(progress_frame, bg='#ecf0f1')
        chart_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(chart_frame, text="📊 Attribute Levels", 
                 command=self.show_attribute_chart,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(chart_frame, text="📈 Progress Over Time", 
                 command=self.show_progress_chart,
                 bg='#27ae60', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(chart_frame, text="🎯 Skill Heatmap", 
                 command=self.show_skill_heatmap,
                 bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Show initial chart
        self.show_attribute_chart()
    
    def setup_history_tab(self):
        """Setup the session history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📚 Session History")
        
        # Create treeview for session history
        columns = ('Date', 'Type', 'Total Gains', 'Notes')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(history_frame, orient="horizontal", command=self.history_tree.xview)
        v_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.history_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.refresh_history_display()
    
    def show_crystal_ball_welcome(self):
        """Show welcome dialog for first-time users"""
        result = messagebox.askyesno(
            "🔮 Welcome, New Adventurer! 🔮",
            "Welcome to the Solo Leveling System!\n\n"
            "It seems this is your first time here.\n"
            "Would you like to assess your current abilities\n"
            "with the mystical Crystal Ball?\n\n"
            "This will help establish your starting stats."
        )
        
        if result:
            self.show_crystal_ball_dialog()
    
    def show_crystal_ball_dialog(self):
        """Show crystal ball assessment dialog"""
        crystal_window = tk.Toplevel(self.root)
        crystal_window.title("🔮 Crystal Ball Assessment 🔮")
        crystal_window.geometry("800x600")
        crystal_window.configure(bg='#2c3e50')
        crystal_window.grab_set()  # Make it modal
        
        # Title
        title_label = tk.Label(crystal_window, 
                              text="🔮✨ MYSTICAL STAT ASSESSMENT ✨🔮",
                              font=('Arial', 18, 'bold'), fg='#f39c12', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(crystal_window,
                               text="The ancient crystal reveals your true abilities...\n"
                                    "Rate each skill from 1-100 based on your current level:\n\n"
                                    "• 1-20: Complete beginner\n"
                                    "• 21-40: Some experience/knowledge\n"
                                    "• 41-60: Intermediate proficiency\n"
                                    "• 61-80: Advanced/Skilled\n"
                                    "• 81-100: Expert/Master level",
                               font=('Arial', 10), fg='#ecf0f1', bg='#2c3e50',
                               justify=tk.LEFT)
        instructions.pack(pady=10)
        
        # Create notebook for crystal ball assessment
        crystal_notebook = ttk.Notebook(crystal_window)
        crystal_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        crystal_entries = {}
        
        for attribute in self.attributes:
            attr_frame = ttk.Frame(crystal_notebook)
            attr_name_display = attribute.replace("_", " ").title()
            crystal_notebook.add(attr_frame, text=attr_name_display)
            
            # Create scrollable frame
            canvas = tk.Canvas(attr_frame, bg='#34495e')
            scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#34495e')
            
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
                skill_frame = tk.Frame(scrollable_frame, bg='#34495e')
                skill_frame.pack(fill=tk.X, padx=10, pady=5)
                
                skill_display = skill.replace("_", " ").title()
                
                label = tk.Label(skill_frame, text=f"🔍 {skill_display}:", 
                               font=('Arial', 10), fg='#ecf0f1', bg='#34495e', 
                               width=30, anchor='e')
                label.pack(side=tk.LEFT)
                
                entry_var = tk.StringVar(value="1")
                entry = tk.Entry(skill_frame, textvariable=entry_var, width=5,
                               bg='#ecf0f1', font=('Arial', 10))
                entry.pack(side=tk.LEFT, padx=10)
                
                crystal_entries[attribute][skill] = entry_var
        
        # Buttons
        button_frame = tk.Frame(crystal_window, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_crystal_assessment():
            try:
                self.process_crystal_ball_assessment(crystal_entries)
                crystal_window.destroy()
                messagebox.showinfo("✨ Assessment Complete!", 
                                   "The crystal has revealed your true power!\n"
                                   "Your stats have been updated.")
                self.refresh_all_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save assessment: {str(e)}")
        
        tk.Button(button_frame, text="✨ Complete Assessment", 
                 command=save_crystal_assessment,
                 font=('Arial', 12, 'bold'), bg='#9b59b6', fg='white',
                 relief=tk.RAISED, bd=3).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="❌ Cancel", 
                 command=crystal_window.destroy,
                 font=('Arial', 12), bg='#e74c3c', fg='white',
                 relief=tk.RAISED, bd=3).pack(side=tk.LEFT)
    
    def process_crystal_ball_assessment(self, entries: dict):
        """Process crystal ball assessment results"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create session record
        timestamp = datetime.now().isoformat()
        total_gains = 0
        
        # Calculate total gains and validate entries
        updates = []
        for attribute in entries:
            for skill in entries[attribute]:
                try:
                    new_level = int(entries[attribute][skill].get() or 1)
                    new_level = max(1, min(100, new_level))  # Clamp to 1-100
                    gain = new_level - 1  # Assuming starting from level 1
                    total_gains += gain
                    updates.append((attribute, skill, 1, new_level, gain))
                except ValueError:
                    updates.append((attribute, skill, 1, 1, 0))
        
        cursor.execute('''
            INSERT INTO sessions (session_timestamp, total_gains, session_type, notes)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, total_gains, "crystal_ball_assessment",
              "Initial stat assessment using the mystical crystal ball"))
        
        session_id = cursor.lastrowid
        
        # Update skills and record session updates
        for attribute, skill, old_level, new_level, gain in updates:
            cursor.execute('''
                UPDATE skills 
                SET current_level = ?, last_updated = ? 
                WHERE attribute = ? AND skill_name = ?
            ''', (new_level, timestamp, attribute, skill))
            
            cursor.execute('''
                INSERT INTO session_updates (session_id, attribute, skill_name, old_level, new_level, gain)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, attribute, skill, old_level, new_level, gain))
        
        conn.commit()
        conn.close()
    
    def process_skill_updates(self):
        """Process skill updates from the update tab"""
        updates = []
        total_gains = 0
        
        current_skills = self.get_current_skills()
        
        for attribute in self.update_entries:
            for skill in self.update_entries[attribute]:
                entry_data = self.update_entries[attribute][skill]
                new_value = entry_data['var'].get().strip()
                current_level = entry_data['current']
                
                if new_value:
                    try:
                        new_level = int(new_value)
                        
                        # Validation
                        if new_level < current_level:
                            messagebox.showerror("Error", f"Cannot decrease {skill} level!")
                            return
                        
                        if new_level > current_level + 10:
                            messagebox.showerror("Error", f"Max +10 increase for {skill}!")
                            return
                        
                        if new_level > 100:
                            messagebox.showerror("Error", f"Max level is 100 for {skill}!")
                            return
                        
                        if new_level > current_level:
                            gain = new_level - current_level
                            updates.append((attribute, skill, current_level, new_level, gain))
                            total_gains += gain
                    
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid level for {skill}!")
                        return
        
        if not updates:
            messagebox.showinfo("No Updates", "No changes to save.")
            return
        
        # Get custom date if provided
        custom_date = self.custom_date_var.get().strip()
        if custom_date:
            try:
                datetime.strptime(custom_date, "%Y-%m-%d")
                timestamp = f"{custom_date}T{datetime.now().strftime('%H:%M:%S')}"
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        else:
            timestamp = datetime.now().isoformat()
        
        # Save to database
        self.save_update_session(timestamp, updates, total_gains)
        
        messagebox.showinfo("Success!", f"Updated {len(updates)} skills with +{total_gains} total levels!")
        
        # Clear entries and refresh
        for attribute in self.update_entries:
            for skill in self.update_entries[attribute]:
                self.update_entries[attribute][skill]['var'].set("")
        
        self.custom_date_var.set("")
        self.refresh_all_data()
    
    def save_update_session(self, timestamp: str, updates: list, total_gains: int):
        """Save update session to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_timestamp, total_gains, session_type)
            VALUES (?, ?, ?)
        ''', (timestamp, total_gains, "skill_update"))
        
        session_id = cursor.lastrowid
        
        for attribute, skill, old_level, new_level, gain in updates:
            cursor.execute('''
                UPDATE skills 
                SET current_level = ?, last_updated = ? 
                WHERE attribute = ? AND skill_name = ?
            ''', (new_level, timestamp, attribute, skill))
            
            cursor.execute('''
                INSERT INTO session_updates (session_id, attribute, skill_name, old_level, new_level, gain)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, attribute, skill, old_level, new_level, gain))
        
        conn.commit()
        conn.close()
    
    def refresh_stats_display(self):
        """Refresh the stats display"""
        # Clear existing content
        for widget in self.stats_content_frame.winfo_children():
            widget.destroy()
        
        skills = self.get_current_skills()
        
        for attribute in self.attributes:
            # Attribute frame
            attr_frame = tk.Frame(self.stats_content_frame, bg='#34495e', relief=tk.RAISED, bd=2)
            attr_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Attribute header
            attr_level = self.calculate_attribute_level(attribute)
            attr_display = attribute.replace("_", " ").title()
            
            header_label = tk.Label(attr_frame, 
                                   text=f"📊 {attr_display} - Level {attr_level}/100",
                                   font=('Arial', 14, 'bold'), fg='#f39c12', bg='#34495e')
            header_label.pack(pady=5)
            
            # Skills grid
            skills_frame = tk.Frame(attr_frame, bg='#34495e')
            skills_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Create skills in a grid layout
            attr_skills = skills.get(attribute, {})
            for i, skill in enumerate(self.attributes[attribute]):
                row = i // 2
                col = i % 2
                
                skill_level = attr_skills.get(skill, 1)
                skill_display = skill.replace("_", " ").title()
                
                skill_label = tk.Label(skills_frame,
                                     text=f"{skill_display}: {skill_level}/100",
                                     font=('Arial', 10), fg='#ecf0f1', bg='#34495e',
                                     width=35, anchor='w')
                skill_label.grid(row=row, column=col, padx=5, pady=2, sticky='w')
    
    def show_attribute_chart(self):
        """Show attribute levels chart"""
        self.fig.clear()
        
        # Get attribute levels
        attributes = []
        levels = []
        
        for attribute in self.attributes:
            attr_display = attribute.replace("_", " ").title()
            attributes.append(attr_display)
            levels.append(self.calculate_attribute_level(attribute))
        
        # Create bar chart
        ax = self.fig.add_subplot(111)
        bars = ax.bar(attributes, levels, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'])
        
        ax.set_title('Current Attribute Levels', fontsize=16, fontweight='bold')
        ax.set_ylabel('Level', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, level in zip(bars, levels):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{level}', ha='center', va='bottom', fontweight='bold')
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def show_progress_chart(self):
        """Show progress over time chart"""
        self.fig.clear()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get session data over time
        cursor.execute('''
            SELECT session_timestamp, total_gains
            FROM sessions
            ORDER BY session_timestamp
        ''')
        
        session_data = cursor.fetchall()
        conn.close()
        
        if not session_data:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No session data yet!\nComplete some skill updates to see progress.',
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Progress Over Time', fontsize=16, fontweight='bold')
            self.canvas.draw()
            return
        
        # Convert to pandas for easier plotting
        dates = [datetime.fromisoformat(session[0]) for session in session_data]
        gains = [session[1] for session in session_data]
        
        # Calculate cumulative gains
        cumulative_gains = np.cumsum(gains)
        
        ax = self.fig.add_subplot(111)
        ax.plot(dates, cumulative_gains, marker='o', linewidth=2, markersize=6, color='#3498db')
        ax.fill_between(dates, cumulative_gains, alpha=0.3, color='#3498db')
        
        ax.set_title('Cumulative Level Gains Over Time', fontsize=16, fontweight='bold')
        ax.set_ylabel('Total Level Gains', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def show_skill_heatmap(self):
        """Show skill levels heatmap"""
        self.fig.clear()
        
        skills = self.get_current_skills()
        
        # Prepare data for heatmap
        skill_matrix = []
        skill_labels = []
        
        for attribute in self.attributes:
            attr_skills = skills.get(attribute, {})
            skill_row = []
            for skill in self.attributes[attribute]:
                skill_row.append(attr_skills.get(skill, 1))
            skill_matrix.append(skill_row)
            skill_labels.append(attribute.replace("_", " ").title())
        
        # Create skill names for x-axis (truncated for space)
        max_skills = max(len(self.attributes[attr]) for attr in self.attributes)
        skill_names = []
        for i in range(max_skills):
            skill_names.append(f'Skill {i+1}')
        
        ax = self.fig.add_subplot(111)
        
        # Create heatmap
        im = ax.imshow(skill_matrix, cmap='RdYlGn', aspect='auto', vmin=1, vmax=100)
        
        # Set ticks and labels
        ax.set_xticks(range(max_skills))
        ax.set_xticklabels(skill_names, rotation=45, ha='right')
        ax.set_yticks(range(len(self.attributes)))
        ax.set_yticklabels(skill_labels)
        
        # Add colorbar
        cbar = self.fig.colorbar(im, ax=ax)
        cbar.set_label('Skill Level', rotation=270, labelpad=15)
        
        ax.set_title('Skill Levels Heatmap', fontsize=16, fontweight='bold')
        
        # Add text annotations
        for i in range(len(self.attributes)):
            for j in range(len(skill_matrix[i])):
                text = ax.text(j, i, skill_matrix[i][j],
                             ha="center", va="center", color="black", fontweight='bold')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_history_display(self):
        """Refresh the session history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_timestamp, session_type, total_gains, notes
            FROM sessions
            ORDER BY session_timestamp DESC
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        for session in sessions:
            timestamp, session_type, total_gains, notes = session
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = timestamp
            
            # Format session type
            session_type_display = session_type.replace("_", " ").title()
            
            # Handle None notes
            notes_display = notes if notes else ""
            
            self.history_tree.insert('', 'end', values=(
                formatted_date,
                session_type_display,
                f"+{total_gains}",
                notes_display
            ))
    
    def refresh_all_data(self):
        """Refresh all displays and update overall level"""
        # Update overall level display
        max_level = len(self.attributes) * 100  # 500
        current_level = self.calculate_overall_level()
        self.overall_level_label.config(text=f"🏆 OVERALL LEVEL: {current_level}/{max_level}")
        
        # Refresh all tab displays
        self.refresh_stats_display()
        self.refresh_history_display()
        self.show_attribute_chart()
        
        # Update current levels in update entries
        current_skills = self.get_current_skills()
        for attribute in self.update_entries:
            for skill in self.update_entries[attribute]:
                new_level = current_skills.get(attribute, {}).get(skill, 1)
                self.update_entries[attribute][skill]['current'] = new_level
                self.update_entries[attribute][skill]['label'].config(text=f"[{new_level}]")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the Solo Leveling System"""
    app = SoloLevelingGUI()
    app.run()

if __name__ == "__main__":
    main()
    