"""
MCP tool aggregation
Manages and coordinates tool calls
"""
from typing import Dict, List, Optional, Callable
from .mcp_client import mcp_client


class ToolManager:
    """Manages MCP tools and provides unified interface"""
    
    def __init__(self):
        """Initialize tool manager"""
        self.mcp = mcp_client
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        self.tools: Dict[str, Callable] = {
            # Data management tools
            'distributeData': self.mcp.distribute_data,
            'databaseSearch': self.mcp.database_search,
            'getCurProgress': self.mcp.get_cur_progress,
            'getSystemPrompt': self.mcp.get_system_prompt,
            
            # Quiz evaluation tools
            'evaluateAnswer': self.mcp.evaluate_answer,
            'updateFreshnessAndLog': self.mcp.update_freshness_and_log,
            'decideNext': self.mcp.decide_next,
            
            # Quiz generation tools
            'generateExplaination': self.mcp.generate_explaination,
            'generateQue_singleChoice': self.mcp.generate_que_single_choice,
            'generateQue_multiChoice': self.mcp.generate_que_multi_choice,
            'generateQue_shortAnswer': self.mcp.generate_que_short_answer,
        }
    
    def call_tool(self, tool_name: str, **kwargs):
        """
        Call a specific tool with arguments
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific arguments
        
        Returns:
            Tool execution result
        
        Raises:
            ValueError: If tool doesn't exist
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")
        
        tool = self.tools[tool_name]
        return tool(**kwargs)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if tool exists"""
        return tool_name in self.tools
    
    # ============ High-level tool operations ============
    
    def generate_quiz_for_concepts(self, concept_refs: List[str], max_count: int = 10) -> List[dict]:
        """
        Generate quizzes for multiple concepts
        
        Args:
            concept_refs: List of concept references
            max_count: Maximum number of quizzes to generate
        
        Returns:
            List of quiz questions
        """
        print(f"\n[TOOL_MANAGER] Generating quizzes for {min(len(concept_refs), max_count)} concepts...")
        
        quizzes = []
        quiz_types = ['singleChoice', 'multiChoice', 'shortAnswer']
        
        for i, ref in enumerate(concept_refs[:max_count]):
            quiz_type = quiz_types[i % 3]
            print(f"[TOOL_MANAGER] Generating {quiz_type} quiz for concept {i+1}/{min(len(concept_refs), max_count)}: {ref}")
            
            try:
                if quiz_type == 'singleChoice':
                    quiz = self.mcp.generate_que_single_choice(ref)
                elif quiz_type == 'multiChoice':
                    quiz = self.mcp.generate_que_multi_choice(ref)
                else:
                    quiz = self.mcp.generate_que_short_answer(ref)
                
                if quiz:
                    print(f"[TOOL_MANAGER] Successfully generated quiz for {ref}")
                    quizzes.append(quiz)
                else:
                    print(f"[TOOL_MANAGER] Warning: No quiz returned for {ref}")
            except Exception as e:
                print(f"[TOOL_MANAGER] Error generating quiz for {ref}: {e}")
        
        print(f"[TOOL_MANAGER] Total quizzes generated: {len(quizzes)}")
        return quizzes
    
    def evaluate_and_update(self, user_answer: str, correct_answer: any, concept_id: str) -> dict:
        """
        Evaluate answer and update progress in one call
        
        Args:
            user_answer: User's submitted answer
            correct_answer: Expected correct answer
            concept_id: Concept reference
        
        Returns:
            Evaluation result with next decision
        """
        # Evaluate answer
        evaluation = self.mcp.evaluate_answer(user_answer, correct_answer, concept_id)
        
        # Update progress
        self.mcp.update_freshness_and_log(concept_id, evaluation)
        
        # Decide next action
        cur_progress = self.mcp.get_cur_progress()
        next_decision = self.mcp.decide_next(cur_progress)
        
        return {
            'evaluation': evaluation,
            'next_decision': next_decision
        }
    
    def get_learning_context(self) -> dict:
        """
        Get complete learning context including system prompt and progress
        
        Returns:
            Complete learning context
        """
        return {
            'system_prompt': self.mcp.get_system_prompt(),
            'progress': self.mcp.get_cur_progress(),
            'knowledge_map': self.mcp.distribute_data()
        }


# Global tool manager instance
tool_manager = ToolManager()

