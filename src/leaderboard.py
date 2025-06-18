import os
import json
import time
from datetime import datetime

class Leaderboard:
    def __init__(self, filename="leaderboard.json"):
        self.filename = filename
        self.scores = []
        self.max_entries = 10
        self.load_scores()
    
    def load_scores(self):
        """Load scores from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self.scores = []
    
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def add_score(self, name, score, day_count, zombies_killed):
        """Add a new score to the leaderboard"""
        # Create a new score entry
        entry = {
            "name": name,
            "score": score,
            "day_count": day_count,
            "zombies_killed": zombies_killed,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timestamp": time.time()
        }
        
        # Add to scores list
        self.scores.append(entry)
        
        # Sort by score (descending)
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Keep only top scores
        if len(self.scores) > self.max_entries:
            self.scores = self.scores[:self.max_entries]
        
        # Save to file
        self.save_scores()
        
        # Return position (1-based)
        return self.get_position(score)
    
    def get_position(self, score):
        """Get the position of a score in the leaderboard (1-based)"""
        for i, entry in enumerate(self.scores):
            if entry["score"] == score:
                return i + 1
        return len(self.scores) + 1
    
    def get_top_scores(self, count=10):
        """Get the top N scores"""
        return self.scores[:min(count, len(self.scores))]
    
    def is_high_score(self, score):
        """Check if a score qualifies for the leaderboard"""
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1]["score"]
