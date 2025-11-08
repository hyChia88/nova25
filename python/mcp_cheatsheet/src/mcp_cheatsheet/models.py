"""
Data models for CheatSheet MCP server
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Concept:
    """Represents a knowledge concept"""
    concept_id: str
    title: str
    content: List[str]
    timestamp: str
    freshness: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'content': self.content,
            'timestamp': self.timestamp,
            'freshness': self.freshness
        }
    
    @classmethod
    def from_dict(cls, concept_id: str, data: dict):
        return cls(
            concept_id=concept_id,
            title=data.get('title', ''),
            content=data.get('content', []),
            timestamp=data.get('timestamp', ''),
            freshness=data.get('freshness', 0.0)
        )


@dataclass
class Course:
    """Represents a course with concepts"""
    name: str
    concepts: Dict[str, Concept] = field(default_factory=dict)
    
    def add_concept(self, concept: Concept):
        self.concepts[concept.concept_id] = concept
    
    def get_concept(self, concept_id: str) -> Optional[Concept]:
        return self.concepts.get(concept_id)
    
    def to_dict(self) -> dict:
        return {
            concept_id: concept.to_dict() 
            for concept_id, concept in self.concepts.items()
        }


@dataclass
class UserProfile:
    """User profile data"""
    major: str = ""
    career_goal: str = ""
    profile: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'major': self.major,
            'career_goal': self.career_goal,
            'profile': self.profile
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            major=data.get('major', ''),
            career_goal=data.get('career_goal', ''),
            profile=data.get('profile', [])
        )


@dataclass
class KnowledgeDistribution:
    """Knowledge distribution across time periods"""
    today: List[str] = field(default_factory=list)
    short_term: List[str] = field(default_factory=list)
    long_term: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'TODAY': self.today,
            'SHORT_TERM': self.short_term,
            'LONG_TERM': self.long_term
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            today=data.get('TODAY', []),
            short_term=data.get('SHORT_TERM', []),
            long_term=data.get('LONG_TERM', [])
        )


@dataclass
class QuizQuestion:
    """Represents a quiz question"""
    question_type: str  # single_choice, multi_choice, short_answer
    question: str
    options: Optional[List[str]] = None
    correct_answer: Optional[any] = None
    expected_answer: Optional[str] = None
    concept_ref: Optional[str] = None
    concept: Optional[dict] = None
    
    def to_dict(self) -> dict:
        result = {
            'type': self.question_type,
            'question': self.question
        }
        if self.options:
            result['options'] = self.options
        if self.correct_answer is not None:
            result['correct_answer'] = self.correct_answer
        if self.expected_answer:
            result['expected_answer'] = self.expected_answer
        if self.concept_ref:
            result['concept_ref'] = self.concept_ref
        if self.concept:
            result['concept'] = self.concept
        return result


@dataclass
class EvaluationResult:
    """Result of answer evaluation"""
    score: int
    is_correct: bool
    feedback: str
    
    def to_dict(self) -> dict:
        return {
            'score': self.score,
            'is_correct': self.is_correct,
            'feedback': self.feedback
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            score=data.get('score', 0),
            is_correct=data.get('is_correct', False),
            feedback=data.get('feedback', '')
        )


@dataclass
class ProgressEntry:
    """Progress entry for a concept"""
    freshness: float
    log: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'freshness': self.freshness,
            'log': self.log
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            freshness=data.get('freshness', 0.0),
            log=data.get('log', [])
        )


@dataclass
class DecisionResult:
    """Result of decide_next decision"""
    decision: str
    reason: str
    target_ref: Optional[str] = None
    preferred_quiz_type: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'decision': self.decision,
            'reason': self.reason,
            'target_ref': self.target_ref,
            'preferred_quiz_type': self.preferred_quiz_type
        }

