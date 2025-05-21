import json
import math
from datetime import datetime
from typing import Dict, List, Tuple

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
        
        # Initialize skill levels (starting at level 1)
        self.skill_levels = {}
        for attribute in self.attributes:
            self.skill_levels[attribute] = {}
            for skill in self.attributes[attribute]:
                self.skill_levels[attribute][skill] = 1
        
        self.data_file = "leveling_data.json"
        self.load_data()
    
    def sigmoid_level_calculation(self, total_points: int, max_points: int) -> int:
        """
        Calculate level using sigmoid curve for realistic learning progression
        - Slow start (learning curve)
        - Rapid middle growth (proficiency building)
        - Plateauing at high levels (mastery difficulty)
        """
        if total_points <= 0:
            return 1
        
        # Normalize to 0-1 scale
        x = total_points / max_points
        
        # Sigmoid function: slower start, rapid middle, slow end
        # Using steepness factor of 10 and shifting to start at level 1
        sigmoid_value = 1 / (1 + math.exp(-10 * (x - 0.5)))
        
        # Scale to 1-100 range
        level = int(1 + sigmoid_value * 99)
        return min(level, 100)
    
    def calculate_attribute_level(self, attribute: str) -> int:
        """Calculate attribute level based on sum of all skills in that attribute"""
        total_skill_points = sum(self.skill_levels[attribute].values())
        max_skill_points = len(self.attributes[attribute]) * 100  # 10 skills * 100 max each
        return self.sigmoid_level_calculation(total_skill_points, max_skill_points)
    
    def calculate_overall_level(self) -> int:
        """Calculate overall level based on sum of all attribute levels"""
        total_attribute_points = sum(self.calculate_attribute_level(attr) for attr in self.attributes)
        max_attribute_points = len(self.attributes) * 100  # 5 attributes * 100 max each
        return self.sigmoid_level_calculation(total_attribute_points, max_attribute_points)
    
    def display_current_stats(self):
        """Display current player statistics"""
        print("\n" + "="*60)
        print("🎮 SOLO LEVELING SYSTEM - CURRENT STATS 🎮")
        print("="*60)
        
        overall_level = self.calculate_overall_level()
        print(f"🏆 OVERALL LEVEL: {overall_level}/100")
        print("-"*60)
        
        for attribute_name in self.attributes:
            attr_level = self.calculate_attribute_level(attribute_name)
            attr_display = attribute_name.replace("_", " ").title()
            print(f"\n📊 {attr_display} - Level {attr_level}/100:")
            
            for skill in self.attributes[attribute_name]:
                skill_display = skill.replace("_", " ").title()
                skill_level = self.skill_levels[attribute_name][skill]
                print(f"   • {skill_display}: {skill_level}/100")
    
    def update_skills_session(self):
        """Interactive session to update skill levels"""
        print("\n" + "="*60)
        print("🔄 SKILL UPDATE SESSION")
        print("="*60)
        print("Enter new levels for each skill (max +10 increase per session)")
        print("Press Enter to keep current level")
        
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "updates": {}
        }
        
        for attribute_name in self.attributes:
            attr_display = attribute_name.replace("_", " ").title()
            print(f"\n🎯 UPDATING: {attr_display}")
            print("-" * 30)
            
            session_data["updates"][attribute_name] = {}
            
            for skill in self.attributes[attribute_name]:
                skill_display = skill.replace("_", " ").title()
                current_level = self.skill_levels[attribute_name][skill]
                
                while True:
                    try:
                        user_input = input(f"{skill_display} [{current_level}] → ").strip()
                        
                        if user_input == "":
                            # Keep current level
                            new_level = current_level
                            break
                        
                        new_level = int(user_input)
                        
                        # Validate constraints
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
                
                # Update the skill level
                old_level = self.skill_levels[attribute_name][skill]
                self.skill_levels[attribute_name][skill] = new_level
                session_data["updates"][attribute_name][skill] = {
                    "old_level": old_level,
                    "new_level": new_level,
                    "gain": new_level - old_level
                }
                
                if new_level > old_level:
                    print(f"   ✅ +{new_level - old_level} levels!")
        
        # Save session data
        self.save_session(session_data)
        self.save_data()
        
        print("\n🎉 Session complete! Progress saved.")
        self.display_session_summary(session_data)
    
    def display_session_summary(self, session_data: dict):
        """Display summary of the update session"""
        print("\n" + "="*50)
        print("📈 SESSION SUMMARY")
        print("="*50)
        
        total_gains = 0
        for attribute_name in session_data["updates"]:
            attr_gains = sum(update["gain"] for update in session_data["updates"][attribute_name].values())
            if attr_gains > 0:
                attr_display = attribute_name.replace("_", " ").title()
                print(f"{attr_display}: +{attr_gains} total levels")
                total_gains += attr_gains
        
        if total_gains > 0:
            print(f"\n🚀 Total session gains: +{total_gains} levels")
            old_overall = self.calculate_overall_level() # This might not be accurate since we already updated
            print(f"🏆 Current Overall Level: {self.calculate_overall_level()}/100")
        else:
            print("No changes made this session.")
    
    def save_data(self):
        """Save current skill levels to JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"skill_levels": {}, "sessions": []}
        
        data["skill_levels"] = self.skill_levels
        data["last_updated"] = datetime.now().isoformat()
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_session(self, session_data: dict):
        """Save session data for historical tracking"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"skill_levels": {}, "sessions": []}
        
        if "sessions" not in data:
            data["sessions"] = []
        
        data["sessions"].append(session_data)
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load skill levels from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                if "skill_levels" in data:
                    # Merge saved data with default structure
                    for attribute in data["skill_levels"]:
                        if attribute in self.skill_levels:
                            for skill in data["skill_levels"][attribute]:
                                if skill in self.skill_levels[attribute]:
                                    self.skill_levels[attribute][skill] = data["skill_levels"][attribute][skill]
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is corrupted, use defaults
            pass
    
    def view_history(self):
        """View session history"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                sessions = data.get("sessions", [])
        except (FileNotFoundError, json.JSONDecodeError):
            sessions = []
        
        if not sessions:
            print("\n📝 No session history found.")
            return
        
        print("\n" + "="*60)
        print("📊 SESSION HISTORY")
        print("="*60)
        
        for i, session in enumerate(sessions[-10:], 1):  # Show last 10 sessions
            timestamp = datetime.fromisoformat(session["timestamp"]).strftime("%Y-%m-%d %H:%M")
            print(f"\n{i}. Session: {timestamp}")
            
            total_gains = 0
            for attribute in session["updates"]:
                attr_gains = sum(update["gain"] for update in session["updates"][attribute].values())
                total_gains += attr_gains
            
            print(f"   Total gains: +{total_gains} levels")
    
    def main_menu(self):
        """Main menu loop"""
        while True:
            print("\n" + "="*50)
            print("🎮 SOLO LEVELING SYSTEM")
            print("="*50)
            print("1. View Current Stats")
            print("2. Update Skills")
            print("3. View History")
            print("4. Exit")
            
            choice = input("\nChoose an option (1-4): ").strip()
            
            if choice == "1":
                self.display_current_stats()
            elif choice == "2":
                self.update_skills_session()
            elif choice == "3":
                self.view_history()
            elif choice == "4":
                print("\n👋 Keep leveling up! See you next time.")
                break
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function to run the Solo Leveling System"""
    print("🚀 Initializing Solo Leveling System...")
    system = SoloLevelingSystem()
    system.main_menu()

if __name__ == "__main__":
    main()