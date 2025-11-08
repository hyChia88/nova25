"""
Main agent loop
Tool-calling agent with LLM integration
"""
import requests
import json
from typing import List, Dict, Optional
from .config import config
from .tool_manager import tool_manager
from .mcp_client import mcp_client


class CheatSheetAgent:
    """
    Tool-calling agent for educational quiz system
    Coordinates between LLM and MCP tools
    """
    
    def __init__(self):
        """Initialize agent"""
        self.config = config
        self.tool_manager = tool_manager
        self.mcp = mcp_client
        self.conversation_history = []
    
    def _call_llm(self, messages: List[dict], temperature: float = None) -> str:
        """
        Call LLM via OpenRouter
        
        Args:
            messages: List of message dicts
            temperature: Optional temperature override
        
        Returns:
            LLM response content
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.llm.model,
            "messages": messages,
            "temperature": temperature or self.config.llm.temperature,
            "max_tokens": self.config.llm.max_tokens
        }
        
        response = requests.post(
            self.config.llm.openrouter_url, 
            headers=headers, 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            raise Exception(f"LLM API call failed: {response.status_code} - {response.text}")
    
    def generate_quizzes(self, num_quizzes: int = 10) -> List[dict]:
        """
        Generate quizzes based on current knowledge state
        
        Args:
            num_quizzes: Number of quizzes to generate
        
        Returns:
            List of quiz questions
        """
        print(f"\n[AGENT] Starting quiz generation for {num_quizzes} quizzes...")
        
        # Get concepts to quiz
        concept_refs = self.mcp.database_search()
        print(f"[AGENT] Found {len(concept_refs)} concept references")
        
        if not concept_refs:
            print("[AGENT] No concept references found!")
            return []
        
        # Generate quizzes
        print(f"[AGENT] Generating quizzes for concepts...")
        quizzes = self.tool_manager.generate_quiz_for_concepts(
            concept_refs, 
            max_count=num_quizzes
        )
        
        print(f"[AGENT] Successfully generated {len(quizzes)} quizzes")
        return quizzes
    
    def evaluate_quiz_answer(
        self, 
        user_answer: str, 
        correct_answer: any, 
        concept_id: str
    ) -> dict:
        """
        Evaluate a quiz answer and determine next action
        
        Args:
            user_answer: User's submitted answer
            correct_answer: Expected correct answer
            concept_id: Concept reference
        
        Returns:
            Evaluation result with next decision
        """
        return self.tool_manager.evaluate_and_update(
            user_answer, 
            correct_answer, 
            concept_id
        )
    
    def get_explanation(self, concept_id: str) -> dict:
        """
        Get detailed explanation for a concept
        
        Args:
            concept_id: Concept reference
        
        Returns:
            Explanation text
        """
        return self.mcp.generate_explaination(concept_id)
    
    def initialize_learning_session(self) -> dict:
        """
        Initialize a new learning session
        
        Returns:
            Session context with system prompt and available concepts
        """
        # Distribute knowledge
        self.mcp.distribute_data()
        
        # Get learning context
        context = self.tool_manager.get_learning_context()
        
        return context
    
    def process_uploaded_concepts(
        self, 
        concepts: List[dict], 
        course_name: str
    ) -> dict:
        """
        Process newly uploaded concepts
        
        Args:
            concepts: List of concept dicts with title and content
            course_name: Name of the course
        
        Returns:
            Processing result
        """
        from datetime import datetime
        from mcp_cheatsheet.models import Concept
        
        added_count = 0
        skipped_count = 0
        timestamp = datetime.now().isoformat() + 'Z'
        
        for concept_data in concepts:
            # Check for duplicates
            if self.mcp.check_duplicate(course_name, concept_data['title']):
                skipped_count += 1
                continue
            
            # Generate ID
            concept_id = self.mcp.generate_concept_id(course_name, timestamp)
            
            # Create concept
            concept = Concept(
                concept_id=concept_id,
                title=concept_data['title'],
                content=[concept_data['content']],
                timestamp=timestamp,
                freshness=0.0
            )
            
            # Add to database
            if self.mcp.add_concept(course_name, concept):
                added_count += 1
            else:
                skipped_count += 1
        
        # Update knowledge distribution
        self.mcp.distribute_data()
        
        return {
            'added_count': added_count,
            'skipped_count': skipped_count,
            'course_name': course_name
        }
    
    def get_next_quiz_recommendation(self) -> Optional[dict]:
        """
        Get recommendation for next quiz based on progress
        
        Returns:
            Recommended quiz or None
        """
        cur_progress = self.mcp.get_cur_progress()
        decision = self.mcp.decide_next(cur_progress)
        
        if decision['decision'] == 'generateExplaination':
            return None
        
        # Generate recommended quiz
        target_ref = decision.get('target_ref')
        quiz_type = decision.get('preferred_quiz_type', 'single_choice')
        
        if not target_ref:
            return None
        
        if quiz_type == 'single_choice':
            quiz = self.mcp.generate_que_single_choice(target_ref)
        elif quiz_type == 'multi_choice':
            quiz = self.mcp.generate_que_multi_choice(target_ref)
        else:
            quiz = self.mcp.generate_que_short_answer(target_ref)
        
        return quiz
    
    def reset_session(self):
        """Reset the learning session"""
        self.conversation_history = []
        # Progress is maintained across sessions


# Global agent instance
agent = CheatSheetAgent()

