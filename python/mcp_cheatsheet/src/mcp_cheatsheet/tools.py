"""
11 MCP tools implementation for CheatSheet educational system
"""
import requests
import json
import re
from typing import List, Dict, Optional
from .database import Database
from .models import (
    QuizQuestion, EvaluationResult, DecisionResult, ProgressEntry
)


class CheatSheetTools:
    """Implementation of 11 MCP tools for educational quiz system"""
    
    def __init__(self, database: Database, api_key: str, openrouter_url: str):
        self.db = database
        self.api_key = api_key
        self.openrouter_url = openrouter_url
    
    # ============ Tool 1: distributeData ============
    
    def distribute_data(self, user_profile: dict = None) -> dict:
        """
        Rewrite knowledge_distributed_map.json after new concepts are inserted
        
        Args:
            user_profile: User profile from db.json (optional)
        
        Returns:
            Updated knowledge distribution map
        """
        knowledge_map = self.db.distribute_knowledge()
        return knowledge_map.to_dict()
    
    # ============ Tool 2: databaseSearch ============
    
    def database_search(
        self, 
        input_prompt: str = "Learn this course according to the material"
    ) -> List[str]:
        """
        Retrieve actual reference set for generation/quiz based on user intent
        
        Args:
            input_prompt: User's learning intent
        
        Returns:
            Array of concept IDs (e.g., ["COURSES/SOFTWARE_CONSTRUCTION/sc-2025-08-11-001", ...])
        """
        knowledge_map = self.db.load_knowledge_map()
        
        # Prioritize TODAY and SHORT_TERM
        references = knowledge_map.today + knowledge_map.short_term
        
        # Fallback: return all available concepts
        if not references:
            references = self.db.get_all_concepts_refs()
        
        # TODO: In future, use LLM to filter based on input_prompt
        
        return references
    
    # ============ Tool 3: getCurProgress ============
    
    def get_cur_progress(self) -> dict:
        """
        Generate runtime database for current quiz session
        
        Returns:
            cur_progress.json with session state
        """
        return self.db.load_progress()
    
    # ============ Tool 4: getSystemPrompt ============
    
    def get_system_prompt(self) -> dict:
        """
        Generate system prompt by resolving references from knowledge_distributed_map
        
        Returns:
            System prompt with resolved TODAY, LONG_TERM, SHORT_TERM, and USER_PROFILE data
        """
        db_data = self.db.load_db()
        knowledge_map = self.db.load_knowledge_map()
        
        prompt_data = {
            "TODAY": [],
            "LONG_TERM": [],
            "SHORT_TERM": [],
            "USER_PROFILE": db_data.get('USER_PROFILE', {})
        }
        
        # Resolve references for each category
        for category, refs in [
            ('TODAY', knowledge_map.today),
            ('LONG_TERM', knowledge_map.long_term),
            ('SHORT_TERM', knowledge_map.short_term)
        ]:
            for ref in refs:
                concept = self.db.get_concept(ref)
                if concept:
                    prompt_data[category].append({
                        'ref': ref,
                        'title': concept.title,
                        'content': concept.content,
                        'freshness': concept.freshness
                    })
        
        return prompt_data
    
    # ============ Tool 5: evaluateAnswer ============
    
    def evaluate_answer(
        self, 
        user_answer: str, 
        correct_answer: any, 
        concept_id: str
    ) -> EvaluationResult:
        """
        Evaluate user's quiz answer
        
        Args:
            user_answer: User's submitted answer
            correct_answer: Expected correct answer
            concept_id: ID of the concept being tested
        
        Returns:
            Evaluation result with score, feedback, and is_correct flag
        """
        concept = self.db.get_concept(concept_id)
        if not concept:
            return EvaluationResult(
                score=0,
                is_correct=False,
                feedback="Concept not found"
            )
        
        # Use LLM for evaluation
        return self._evaluate_with_llm(user_answer, concept)
    
    def _evaluate_with_llm(self, user_answer: str, concept) -> EvaluationResult:
        """Evaluate answer using LLM"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            content_str = concept.content[0] if concept.content else ""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an educational assessment AI. Evaluate student answers and provide constructive feedback."
                },
                {
                    "role": "user",
                    "content": f"""Evaluate this student answer:

Concept: {concept.title}
Expected Understanding: {content_str}

Student Answer: {user_answer}

Provide a JSON response with:
{{
    "score": <0-100>,
    "is_correct": <true/false>,
    "feedback": "<brief feedback>"
}}"""
                }
            ]
            
            payload = {
                "model": "openai/gpt-4o",
                "messages": messages,
                "temperature": 0.3
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Parse JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    eval_data = json.loads(json_match.group(0))
                    return EvaluationResult.from_dict(eval_data)
            
            # Fallback
            return EvaluationResult(
                score=50,
                is_correct=False,
                feedback="Unable to evaluate answer"
            )
            
        except Exception as e:
            return EvaluationResult(
                score=50,
                is_correct=False,
                feedback=f"Evaluation error: {str(e)}"
            )
    
    # ============ Tool 6: updateFreshnessAndLog ============
    
    def update_freshness_and_log(
        self, 
        concept_id: str, 
        evaluation_result: EvaluationResult
    ):
        """
        Update freshness score and log in cur_progress.json
        
        Args:
            concept_id: Concept reference
            evaluation_result: Result from evaluateAnswer
        """
        # Get existing progress or create new
        entry = self.db.get_progress_entry(concept_id)
        
        if entry is None:
            entry = ProgressEntry(
                freshness=evaluation_result.score / 100.0,
                log=[]
            )
        else:
            # Average with previous freshness
            new_freshness = evaluation_result.score / 100.0
            entry.freshness = (entry.freshness + new_freshness) / 2
        
        # Generate intelligent log entry using LLM
        log_entry = self._generate_intelligent_log(
            concept_id, 
            evaluation_result, 
            entry
        )
        entry.log.append(log_entry)
        
        # Save updated progress
        self.db.update_progress(concept_id, entry)
    
    def _generate_instant_feedback(
        self,
        concept: dict,
        is_correct: bool,
        user_answer: str
    ) -> str:
        """
        Generate instant, concise feedback for immediate display
        
        Args:
            concept: Concept dictionary with title and content
            is_correct: Whether the answer was correct
            user_answer: User's submitted answer
        
        Returns:
            Brief, encouraging feedback string (1-2 sentences)
        """
        try:
            concept_title = concept.get('title', '')
            concept_content = concept.get('content', [''])[0] if isinstance(concept.get('content'), list) else concept.get('content', '')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            if is_correct:
                prompt = f"""Generate brief, encouraging feedback (1-2 sentences, max 30 words) for a student who answered correctly.

Concept: {concept_title}
Description: {concept_content}

Acknowledge their understanding and optionally mention a key insight they demonstrated.

Your feedback:"""
            else:
                prompt = f"""Generate brief, constructive feedback (1-2 sentences, max 30 words) for a student who answered incorrectly.

Concept: {concept_title}
Description: {concept_content}
Their answer: {user_answer}

Be encouraging and hint at what to review, without giving away the full answer.

Your feedback:"""

            messages = [
                {
                    "role": "system",
                    "content": "You are a supportive educational AI that provides concise, actionable feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            payload = {
                "model": "openai/gpt-4o",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 80
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                feedback = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                feedback = feedback.strip('"').strip()
                print(f"[FEEDBACK] Generated: {feedback}")
                return feedback
                
        except Exception as e:
            print(f"[FEEDBACK] Error generating feedback: {e}")
        
        # Fallback
        return "Great job!" if is_correct else "Not quite right. Review the concept and try to identify the key distinctions."
    
    def _generate_intelligent_log(
        self,
        concept_id: str,
        evaluation_result: EvaluationResult,
        progress_entry: ProgressEntry
    ) -> str:
        """
        Generate intelligent, context-aware log entry using LLM
        
        Args:
            concept_id: Concept reference
            evaluation_result: Current evaluation result
            progress_entry: Existing progress entry
        
        Returns:
            Detailed log entry string
        """
        try:
            # Get concept details
            concept = self.db.get_concept(concept_id)
            if not concept:
                return f"[Score: {evaluation_result.score}] {evaluation_result.feedback}"
            
            # Get related concepts from knowledge map
            knowledge_map = self.db.load_knowledge_map()
            db_data = self.db.load_db()
            
            # Build context for LLM
            context = {
                "concept_title": concept.title,
                "concept_content": concept.content[0] if concept.content else "",
                "current_score": evaluation_result.score,
                "is_correct": evaluation_result.is_correct,
                "feedback": evaluation_result.feedback,
                "previous_freshness": progress_entry.freshness if progress_entry else 0,
                "attempt_count": len(progress_entry.log) if progress_entry else 0,
                "previous_logs": progress_entry.log[-2:] if progress_entry and len(progress_entry.log) > 0 else []
            }
            
            # Call LLM to generate insightful log
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""As an educational AI tutor, analyze this student's learning progress and generate a concise, insightful log entry.

Concept: {context['concept_title']}
Description: {context['concept_content']}

Current Performance:
- Score: {context['current_score']}/100
- Correct: {context['is_correct']}
- Feedback: {context['feedback']}

Learning History:
- Previous Freshness: {context['previous_freshness']:.2f}
- Attempt #: {context['attempt_count'] + 1}
- Recent Progress: {context['previous_logs']}

Generate a single-line log entry (60-100 words) that captures:
1. What the student understands or misunderstands
2. Specific learning progress or patterns observed
3. Actionable next steps if needed

Format: [Category] Detailed observation with specific examples and next steps.
Categories: [Concept], [Vocabulary], [Examples], [Mental Model], [Workflow], [Habits], [Pitfall], [Recognition], [Next]

Example: "[Concept] Initially conflated concurrency with parallelism; after timeline + interleaving demo, can now define both distinctly but still occasionally says 'simultaneous' for concurrency."

Your log entry:"""

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert educational AI that provides detailed, actionable learning insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            payload = {
                "model": "openai/gpt-4o",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                log_content = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                
                # Clean up the response (remove extra quotes, etc)
                log_content = log_content.strip('"').strip()
                
                print(f"[LOG] Generated intelligent log: {log_content[:80]}...")
                return log_content
            else:
                print(f"[LOG] LLM call failed, using simple log")
                
        except Exception as e:
            print(f"[LOG] Error generating intelligent log: {e}")
        
        # Fallback to simple log
        return f"[Score: {evaluation_result.score}] {evaluation_result.feedback}"
    
    # ============ Tool 7: decideNext ============
    
    def decide_next(self, cur_progress: dict) -> DecisionResult:
        """
        Tutor policy—choose next step: another quiz vs summary
        
        Args:
            cur_progress: Current progress from cur_progress.json
        
        Returns:
            Decision object with next action and reasoning
        """
        knowledge_map = self.db.load_knowledge_map()
        all_refs = knowledge_map.today + knowledge_map.short_term
        
        # Get already quizzed concepts
        quizzed = set(cur_progress.get('AI_FEEDBACK', {}).keys())
        
        # Find concepts that need more practice (low freshness)
        needs_practice = []
        for ref, data in cur_progress.get('AI_FEEDBACK', {}).items():
            if data.get('freshness', 0) < 0.7:
                needs_practice.append(ref)
        
        if needs_practice:
            target_ref = needs_practice[0]
            return DecisionResult(
                decision="generateQue_shortAnswer",
                reason="Low freshness score; retry with short-answer to test articulation",
                target_ref=target_ref,
                preferred_quiz_type="short_answer"
            )
        
        # Check if there are unquizzed concepts
        unquizzed = [ref for ref in all_refs if ref not in quizzed]
        if unquizzed:
            target_ref = unquizzed[0]
            return DecisionResult(
                decision="generateQue_singleChoice",
                reason="Continue with new concept",
                target_ref=target_ref,
                preferred_quiz_type="single_choice"
            )
        
        # All done, generate explanation
        return DecisionResult(
            decision="generateExplaination",
            reason="All concepts covered; provide summary",
            target_ref=None,
            preferred_quiz_type=None
        )
    
    # ============ Tool 8: generateExplaination ============
    
    def generate_explaination(self, concept_id: str) -> dict:
        """
        Produce a detailed explain recap for the user
        
        Args:
            concept_id: Concept reference
        
        Returns:
            Formatted explanation text
        """
        concept = self.db.get_concept(concept_id)
        
        if not concept:
            return {"explanation": "No explanation available"}
        
        content_str = concept.content[0] if concept.content else ""
        
        return {
            "title": concept.title,
            "content": content_str,
            "explanation": f"This concept covers {concept.title}. {content_str}"
        }
    
    # ============ Tool 9: generateQue_singleChoice ============
    
    def generate_que_single_choice(self, concept_id: str) -> Optional[QuizQuestion]:
        """
        Create a single-choice quiz per concept
        
        Args:
            concept_id: Concept reference
        
        Returns:
            Quiz question with options and correct answer
        """
        return self._generate_quiz(concept_id, 'single_choice')
    
    # ============ Tool 10: generateQue_multiChoice ============
    
    def generate_que_multi_choice(self, concept_id: str) -> Optional[QuizQuestion]:
        """
        Create a multiple-choice quiz per concept
        
        Args:
            concept_id: Concept reference
        
        Returns:
            Quiz question with options and multiple correct answers
        """
        return self._generate_quiz(concept_id, 'multi_choice')
    
    # ============ Tool 11: generateQue_shortAnswer ============
    
    def generate_que_short_answer(self, concept_id: str) -> Optional[QuizQuestion]:
        """
        Create short answer quiz per concept
        
        Args:
            concept_id: Concept reference
        
        Returns:
            Quiz question with expected answer
        """
        return self._generate_quiz(concept_id, 'short_answer')
    
    # ============ Helper Method for Quiz Generation ============
    
    def _generate_quiz(self, concept_ref: str, quiz_type: str) -> Optional[QuizQuestion]:
        """Generate quiz using LLM"""
        concept = self.db.get_concept(concept_ref)
        if not concept:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            content_str = concept.content[0] if concept.content else ""
            
            if quiz_type == 'single_choice':
                prompt = f"""Create a single-choice quiz question for this concept:

Title: {concept.title}
Content: {content_str}

Generate a JSON response with:
{{
    "question": "<question text>",
    "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
    "correct_answer": <index 0-3>
}}

Make sure one option is clearly correct and others are plausible but incorrect."""

            elif quiz_type == 'multi_choice':
                prompt = f"""Create a multiple-choice quiz question for this concept:

Title: {concept.title}
Content: {content_str}

Generate a JSON response with:
{{
    "question": "<question text>",
    "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
    "correct_answer": [<indices of correct options>]
}}

Make sure 2-3 options are correct and others are incorrect."""

            else:  # short_answer
                prompt = f"""Create a short-answer quiz question for this concept:

Title: {concept.title}
Content: {content_str}

Generate a JSON response with:
{{
    "question": "<question text>",
    "expected_answer": "<expected answer>"
}}

The question should test deep understanding."""

            messages = [
                {
                    "role": "system",
                    "content": "You are an educational quiz generator. Create high-quality assessment questions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            payload = {
                "model": "openai/gpt-4o",
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                print(f"\n[DEBUG] LLM Response for {quiz_type}:")
                print(f"Content: {content[:200]}...")  # Print first 200 chars
                
                # Parse JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    quiz_data = json.loads(json_match.group(0))
                    print(f"[DEBUG] Successfully parsed quiz data")
                    
                    return QuizQuestion(
                        question_type=quiz_type,
                        question=quiz_data.get('question', ''),
                        options=quiz_data.get('options'),
                        correct_answer=quiz_data.get('correct_answer'),
                        expected_answer=quiz_data.get('expected_answer'),
                        concept_ref=concept_ref,
                        concept=concept.to_dict()
                    )
                else:
                    print(f"[DEBUG] Failed to parse JSON from response")
            else:
                print(f"[DEBUG] API request failed with status: {response.status_code}")
                print(f"[DEBUG] Response: {response.text[:200]}")
            
            # Fallback: simple question
            print(f"[DEBUG] Using fallback quiz for {concept.title}")
            return QuizQuestion(
                question_type=quiz_type,
                question=f"What is {concept.title}?",
                options=[content_str, "Incorrect answer", "Another wrong answer", "Not this one"] if quiz_type != 'short_answer' else None,
                correct_answer=0 if quiz_type == 'single_choice' else ([0] if quiz_type == 'multi_choice' else content_str),
                expected_answer=content_str if quiz_type == 'short_answer' else None,
                concept_ref=concept_ref,
                concept=concept.to_dict()
            )
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None

