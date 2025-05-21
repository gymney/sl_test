import sqlite3
import math
import json
from datetime import datetime
from typing import Dict, List, Tuple
import os

class SoloLevelingSystem:
    def __init__(self):
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
        
        # Check if this is first run
        self.is_first_run = self.check_first_run()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Skills table - stores current skill levels
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
        
        # Sessions table - stores historical update sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_timestamp TIMESTAMP NOT NULL,
                total_gains INTEGER NOT NULL DEFAULT 0,
                session_type TEXT NOT NULL DEFAULT 'update',
                notes TEXT
            )
        ''')
        
        # Session updates table - detailed skill updates per session
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
        
        # Check if any skill has been updated from level 1
        cursor.execute('SELECT COUNT(*) FROM skills WHERE current_level > 1')
        has_progress = cursor.fetchone()[0] > 0
        
        # Check if there are any sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        has_sessions = cursor.fetchone()[0] > 0
        
        conn.close()
        return not (has_progress or has_sessions)
    
    def crystal_ball_assessment(self):
        """🔮 ISEKAI CRYSTAL BALL STAT ASSESSMENT 🔮"""
        print("\n" + "="*70)
        print("🔮✨ WELCOME TO THE MYSTICAL STAT ASSESSMENT CRYSTAL ✨🔮")
        print("="*70)
        print("The ancient crystal ball glows with ethereal light...")
        print("Place your hands upon it to reveal your true abilities!")
        print("\nRate each skill from 1-100 based on your current real-life level:")
        print("• 1-20: Complete beginner")
        print("• 21-40: Some experience/knowledge")
        print("• 41-60: Intermediate proficiency")
        print("• 61-80: Advanced/Skilled")
        print("• 81-100: Expert/Master level")
        print("-" * 70)
        
        initial_assessment = {}
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "updates": {},
            "type": "crystal_ball_assessment"
        }
        
        for attribute_name in self.attributes:
            attr_display = attribute_name.replace("_", " ").title()
            print(f"\n🌟 The crystal reveals your {attr_display} abilities...")
            print("✨" * 30)
            
            initial_assessment[attribute_name] = {}
            session_data["updates"][attribute_name] = {}
            
            for skill in self.attributes[attribute_name]:
                skill_display = skill.replace("_", " ").title()
                
                while True:
                    try:
                        level_input = input(f"🔍 {skill_display}: ").strip()
                        
                        if level_input == "":
                            level = 1  # Default to 1 if blank
                            break
                        
                        level = int(level_input)
                        
                        if level < 1 or level > 100:
                            print("   ❌ The crystal only accepts values between 1-100!")
                            continue
                        
                        break
                    
                    except ValueError:
                        print("   ❌ The crystal requires a numerical offering!")
                
                initial_assessment[attribute_name][skill] = level
                session_data["updates"][attribute_name][skill] = {
                    "old_level": 1,
                    "new_level": level,
                    "gain": level - 1
                }
        
        # Save to database
        self.save_crystal_ball_assessment(initial_assessment, session_data)
        
        print("\n" + "🌟" * 70)
        print("✨ The crystal ball's light fades... Your stats have been revealed! ✨")
        print("🌟" * 70)
        
        # Show the results dramatically
        self.display_crystal_ball_results()
    
    def save_crystal_ball_assessment(self, assessment: dict, session_data: dict):
        """Save the initial crystal ball assessment to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create session record
        cursor.execute('''
            INSERT INTO sessions (session_timestamp, total_gains, session_type, notes)
            VALUES (?, ?, ?, ?)
        ''', (
            session_data["timestamp"], 
            sum(sum(skill["gain"] for skill in attr.values()) for attr in session_data["updates"].values()),
            "crystal_ball_assessment",
            "Initial stat assessment using the mystical crystal ball"
        ))
        
        session_id = cursor.lastrowid
        
        # Update all skills and record session updates
        for attribute in assessment:
            for skill, level in assessment[attribute].items():
                # Update current skill level
                cursor.execute('''
                    UPDATE skills 
                    SET current_level = ?, last_updated = CURRENT_TIMESTAMP 
                    WHERE attribute = ? AND skill_name = ?
                ''', (level, attribute, skill))
                
                # Record session update
                cursor.execute('''
                    INSERT INTO session_updates (session_id, attribute, skill_name, old_level, new_level, gain)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, attribute, skill, 1, level, level - 1))
        
        conn.commit()
        conn.close()
    
    def display_crystal_ball_results(self):
        """Display the mystical results of the crystal ball assessment"""
        print("\n🔮 THE CRYSTAL REVEALS YOUR TRUE POWER 🔮")
        self.display_current_stats()
        
        overall_level = self.calculate_overall_level()
        print(f"\n⚡ The ancient spirits whisper... Your power level is: {overall_level}! ⚡")
        
        if overall_level < 20:
            print("🌱 You are a promising novice with great potential!")
        elif overall_level < 40:
            print("🔥 You show the makings of a true warrior!")
        elif overall_level < 60:
            print("⚔️ Your skills are formidable and well-developed!")
        elif overall_level < 80:
            print("👑 You possess the abilities of a master!")
        else:
            print("🌟 LEGEND! Your power rivals the ancient heroes!")
    
    def sigmoid_level_calculation(self, total_points: int, max_points: int) -> int:
        """Calculate level using sigmoid curve for realistic learning progression"""
        if total_points <= 0:
            return 1
        
        # Normalize to 0-1 scale
        x = total_points / max_points
        
        # Sigmoid function: slower start, rapid middle, slow end
        sigmoid_value = 1 / (1 + math.exp(-10 * (x - 0.5)))
        
        # Scale to 1-100 range
        level = int(1 + sigmoid_value * 99)
        return min(level, 100)
    
    def calculate_attribute_level(self, attribute: str) -> int:
        """Calculate attribute level based on sum of all skills in that attribute"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(current_level) FROM skills WHERE attribute = ?', (attribute,))
        total_skill_points = cursor.fetchone()[0] or 0
        
        conn.close()
        
        max_skill_points = len(self.attributes[attribute]) * 100
        return self.sigmoid_level_calculation(total_skill_points, max_skill_points)
    
    def calculate_overall_level(self) -> int:
        """Calculate overall level based on sum of all attribute levels"""
        total_attribute_points = sum(self.calculate_attribute_level(attr) for attr in self.attributes)
        max_attribute_points = len(self.attributes) * 100
        return self.sigmoid_level_calculation(total_attribute_points, max_attribute_points)
    
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
    
    def display_current_stats(self):
        """Display current player statistics"""
        print("\n" + "="*60)
        print("🎮 SOLO LEVELING SYSTEM - CURRENT STATS 🎮")
        print("="*60)
        
        overall_level = self.calculate_overall_level()
        print(f"🏆 OVERALL LEVEL: {overall_level}/100")
        print("-"*60)
        
        skills = self.get_current_skills()
        
        for attribute_name in self.attributes:
            attr_level = self.calculate_attribute_level(attribute_name)
            attr_display = attribute_name.replace("_", " ").title()
            print(f"\n📊 {attr_display} - Level {attr_level}/100:")
            
            if attribute_name in skills:
                for skill in self.attributes[attribute_name]:
                    skill_display = skill.replace("_", " ").title()
                    skill_level = skills[attribute_name].get(skill, 1)
                    print(f"   • {skill_display}: {skill_level}/100")
    
    def update_skills_session(self):
        """Interactive session to update skill levels"""
        print("\n" + "="*60)
        print("🔄 SKILL UPDATE SESSION")
        print("="*60)
        print("Enter new levels for each skill (max +10 increase per session)")
        print("Press Enter to keep current level")
        
        # Allow custom timestamp
        print("\nWould you like to set a custom date for this session?")
        custom_date = input("Enter date (YYYY-MM-DD) or press Enter for now: ").strip()
        
        if custom_date:
            try:
                # Validate date format
                datetime.strptime(custom_date, "%Y-%m-%d")
                session_timestamp = f"{custom_date}T{datetime.now().strftime('%H:%M:%S')}"
            except ValueError:
                print("Invalid date format, using current timestamp.")
                session_timestamp = datetime.now().isoformat()
        else:
            session_timestamp = datetime.now().isoformat()
        
        session_updates = []
        total_gains = 0
        
        current_skills = self.get_current_skills()
        
        for attribute_name in self.attributes:
            attr_display = attribute_name.replace("_", " ").title()
            print(f"\n🎯 UPDATING: {attr_display}")
            print("-" * 30)
            
            for skill in self.attributes[attribute_name]:
                skill_display = skill.replace("_", " ").title()
                current_level = current_skills.get(attribute_name, {}).get(skill, 1)
                
                while True:
                    try:
                        user_input = input(f"{skill_display} [{current_level}] → ").strip()
                        
                        if user_input == "":
                            new_level = current_level
                            break
                        
                        new_level = int(user_input)
                        
                        if new_level < current_level:
                            print("   ❌ Cannot decrease levels!")
                            continue
                        
                        if new_level > current_level + 10:
                            print("   ❌ Maximum increase of 10 levels per session!")
                            continue
                        
                        if new_level > 100:
                            print("   ❌ Maximum level is 100!")
                            continue
                        
                        break
                    
                    except ValueError:
                        print("   ❌ Please enter a valid number or press Enter to skip")
                
                if new_level > current_level:
                    gain = new_level - current_level
                    session_updates.append({
                        'attribute': attribute_name,
                        'skill': skill,
                        'old_level': current_level,
                        'new_level': new_level,
                        'gain': gain
                    })
                    total_gains += gain
                    print(f"   ✅ +{gain} levels!")
        
        if session_updates:
            self.save_update_session(session_timestamp, session_updates, total_gains)
            print(f"\n🎉 Session complete! Total gains: +{total_gains} levels")
        else:
            print("\n📝 No changes made this session.")
    
    def save_update_session(self, timestamp: str, updates: list, total_gains: int):
        """Save update session to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create session record
        cursor.execute('''
            INSERT INTO sessions (session_timestamp, total_gains, session_type)
            VALUES (?, ?, ?)
        ''', (timestamp, total_gains, "skill_update"))
        
        session_id = cursor.lastrowid
        
        # Update skills and record session updates
        for update in updates:
            # Update current skill level
            cursor.execute('''
                UPDATE skills 
                SET current_level = ?, last_updated = ? 
                WHERE attribute = ? AND skill_name = ?
            ''', (update['new_level'], timestamp, update['attribute'], update['skill']))
            
            # Record session update
            cursor.execute('''
                INSERT INTO session_updates (session_id, attribute, skill_name, old_level, new_level, gain)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, update['attribute'], update['skill'], 
                  update['old_level'], update['new_level'], update['gain']))
        
        conn.commit()
        conn.close()
    
    def view_history(self):
        """View session history from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_timestamp, total_gains, session_type, notes 
            FROM sessions 
            ORDER BY session_timestamp DESC 
            LIMIT 10
        ''')
        
        sessions = cursor.fetchall()
        
        if not sessions:
            print("\n📝 No session history found.")
            conn.close()
            return
        
        print("\n" + "="*60)
        print("📊 SESSION HISTORY (Last 10 Sessions)")
        print("="*60)
        
        for i, (timestamp, gains, session_type, notes) in enumerate(sessions, 1):
            date_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
            type_emoji = "🔮" if session_type == "crystal_ball_assessment" else "📈"
            
            print(f"\n{i}. {type_emoji} {date_str}")
            print(f"   Type: {session_type.replace('_', ' ').title()}")
            print(f"   Total gains: +{gains} levels")
            if notes:
                print(f"   Notes: {notes}")
        
        conn.close()
    
    def main_menu(self):
        """Main menu loop"""
        # First run experience
        if self.is_first_run:
            print("\n🌟 Welcome, new adventurer! 🌟")
            print("It seems this is your first time using the Solo Leveling System.")
            print("Would you like to assess your current abilities with the mystical crystal ball?")
            
            choice = input("\nUse Crystal Ball Assessment? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                self.crystal_ball_assessment()
                self.is_first_run = False
        
        while True:
            print("\n" + "="*50)
            print("🎮 SOLO LEVELING SYSTEM V2")
            print("="*50)
            print("1. 🔮 Crystal Ball Assessment (Initial Stats)")
            print("2. 📊 View Current Stats")
            print("3. 📈 Update Skills")
            print("4. 📚 View History")
            print("5. 🚪 Exit")
            
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == "1":
                print("\n⚠️  Warning: This will overwrite all current progress!")
                confirm = input("Are you sure you want to reassess all stats? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    self.crystal_ball_assessment()
            elif choice == "2":
                self.display_current_stats()
            elif choice == "3":
                self.update_skills_session()
            elif choice == "4":
                self.view_history()
            elif choice == "5":
                print("\n👋 Keep leveling up! See you next time, adventurer!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function to run the Solo Leveling System"""
    print("🚀 Initializing Solo Leveling System V2...")
    print("🔄 Setting up database...")
    system = SoloLevelingSystem()
    system.main_menu()

if __name__ == "__main__":
    main()