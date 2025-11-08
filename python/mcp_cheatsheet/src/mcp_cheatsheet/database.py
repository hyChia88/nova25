"""
JSON database manager for CheatSheet
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from .models import (
    Concept, Course, UserProfile, KnowledgeDistribution, 
    ProgressEntry
)


class Database:
    """Manages JSON file-based database operations"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'db.json')
        self.knowledge_map_path = os.path.join(data_dir, 'knowledge_distributed_map.json')
        self.progress_path = os.path.join(data_dir, 'cur_progress.json')
    
    # ============ Database Operations ============
    
    def load_db(self) -> dict:
        """Load main database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"USER_PROFILE": {}, "COURSES": {}}
    
    def save_db(self, db: dict):
        """Save main database"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    
    def load_knowledge_map(self) -> KnowledgeDistribution:
        """Load knowledge distribution map"""
        try:
            with open(self.knowledge_map_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return KnowledgeDistribution.from_dict(data)
        except FileNotFoundError:
            return KnowledgeDistribution()
    
    def save_knowledge_map(self, knowledge_map: KnowledgeDistribution):
        """Save knowledge distribution map"""
        with open(self.knowledge_map_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_map.to_dict(), f, ensure_ascii=False, indent=2)
    
    def load_progress(self) -> dict:
        """Load current progress"""
        try:
            with open(self.progress_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"AI_FEEDBACK": {}}
    
    def save_progress(self, progress: dict):
        """Save current progress"""
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    # ============ User Profile Operations ============
    
    def get_user_profile(self) -> UserProfile:
        """Get user profile"""
        db = self.load_db()
        profile_data = db.get('USER_PROFILE', {})
        return UserProfile.from_dict(profile_data)
    
    def save_user_profile(self, profile: UserProfile):
        """Save user profile"""
        db = self.load_db()
        db['USER_PROFILE'] = profile.to_dict()
        self.save_db(db)
    
    # ============ Course Operations ============
    
    def get_courses(self) -> List[str]:
        """Get list of course names"""
        db = self.load_db()
        return list(db.get('COURSES', {}).keys())
    
    def get_course(self, course_name: str) -> Optional[Course]:
        """Get a specific course"""
        db = self.load_db()
        course_data = db.get('COURSES', {}).get(course_name)
        if not course_data:
            return None
        
        course = Course(name=course_name)
        for concept_id, concept_data in course_data.items():
            concept = Concept.from_dict(concept_id, concept_data)
            course.add_concept(concept)
        return course
    
    def save_course(self, course: Course):
        """Save a course"""
        db = self.load_db()
        if 'COURSES' not in db:
            db['COURSES'] = {}
        db['COURSES'][course.name] = course.to_dict()
        self.save_db(db)
    
    def course_exists(self, course_name: str) -> bool:
        """Check if course exists"""
        db = self.load_db()
        return course_name in db.get('COURSES', {})
    
    # ============ Concept Operations ============
    
    def add_concept(self, course_name: str, concept: Concept) -> bool:
        """Add a concept to a course"""
        db = self.load_db()
        
        if 'COURSES' not in db:
            db['COURSES'] = {}
        
        if course_name not in db['COURSES']:
            db['COURSES'][course_name] = {}
        
        # Check for duplicates
        if self.check_duplicate(course_name, concept.title):
            return False
        
        db['COURSES'][course_name][concept.concept_id] = concept.to_dict()
        self.save_db(db)
        return True
    
    def get_concept(self, concept_ref: str) -> Optional[Concept]:
        """Get a concept by reference (e.g., 'COURSES/COURSE_NAME/concept-id')"""
        parts = concept_ref.split('/')
        if len(parts) != 3 or parts[0] != 'COURSES':
            return None
        
        course_name = parts[1]
        concept_id = parts[2]
        
        db = self.load_db()
        concept_data = db.get('COURSES', {}).get(course_name, {}).get(concept_id)
        if not concept_data:
            return None
        
        return Concept.from_dict(concept_id, concept_data)
    
    def check_duplicate(self, course_name: str, title: str) -> bool:
        """Check if a concept with this title already exists in the course"""
        db = self.load_db()
        course_concepts = db.get('COURSES', {}).get(course_name, {})
        
        title_lower = title.lower()
        for concept_data in course_concepts.values():
            if concept_data.get('title', '').lower() == title_lower:
                return True
        return False
    
    def generate_concept_id(self, course_name: str, timestamp: str) -> str:
        """Generate unique concept ID"""
        date_str = timestamp.split('T')[0]
        db = self.load_db()
        course_concepts = db.get('COURSES', {}).get(course_name, {})
        
        # Count existing concepts for this date
        prefix = f"{course_name.lower()[:2]}-{date_str}-"
        count = sum(1 for key in course_concepts.keys() if key.startswith(prefix))
        
        return f"{prefix}{count + 1:03d}"
    
    # ============ Knowledge Distribution ============
    
    def distribute_knowledge(self) -> KnowledgeDistribution:
        """
        Distribute concepts to TODAY, SHORT_TERM, and LONG_TERM 
        based on timestamps
        """
        db = self.load_db()
        knowledge_map = KnowledgeDistribution()
        
        from datetime import timezone
        current_date = datetime.now(timezone.utc)
        
        for course_name, concepts in db.get('COURSES', {}).items():
            for concept_id, concept_data in concepts.items():
                concept_ref = f"COURSES/{course_name}/{concept_id}"
                timestamp_str = concept_data.get('timestamp', '')
                
                if timestamp_str:
                    concept_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    days_diff = (current_date - concept_date).days
                    
                    # TODAY: concepts added today
                    if days_diff == 0:
                        knowledge_map.today.append(concept_ref)
                    # SHORT_TERM: concepts from the last 30 days
                    elif days_diff <= 30:
                        knowledge_map.short_term.append(concept_ref)
                    # LONG_TERM: older concepts
                    else:
                        knowledge_map.long_term.append(concept_ref)
        
        self.save_knowledge_map(knowledge_map)
        return knowledge_map
    
    # ============ Progress Operations ============
    
    def get_progress_entry(self, concept_ref: str) -> Optional[ProgressEntry]:
        """Get progress entry for a concept"""
        progress = self.load_progress()
        entry_data = progress.get('AI_FEEDBACK', {}).get(concept_ref)
        if not entry_data:
            return None
        return ProgressEntry.from_dict(entry_data)
    
    def update_progress(self, concept_ref: str, entry: ProgressEntry):
        """Update progress for a concept"""
        progress = self.load_progress()
        
        if 'AI_FEEDBACK' not in progress:
            progress['AI_FEEDBACK'] = {}
        
        progress['AI_FEEDBACK'][concept_ref] = entry.to_dict()
        self.save_progress(progress)
    
    def get_all_concepts_refs(self) -> List[str]:
        """Get all concept references"""
        db = self.load_db()
        refs = []
        for course_name, concepts in db.get('COURSES', {}).items():
            for concept_id in concepts.keys():
                refs.append(f"COURSES/{course_name}/{concept_id}")
        return refs

