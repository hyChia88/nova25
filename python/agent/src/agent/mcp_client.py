"""
MCP protocol client
Connects to MCP CheatSheet server and provides tool access
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mcp_cheatsheet', 'src'))

from mcp_cheatsheet import MCPCheatSheetServer
from .config import config


class MCPClient:
    """Client for interacting with MCP CheatSheet server"""
    
    def __init__(self):
        """Initialize MCP client"""
        self.server = MCPCheatSheetServer(
            data_dir=config.data_dir,
            api_key=config.api_key,
            openrouter_url=config.llm.openrouter_url
        )
        self.tools = self.server.get_tools()
        self.database = self.server.get_database()
    
    # ============ Tool Access Methods ============
    
    def distribute_data(self, user_profile=None):
        """Call distributeData tool"""
        return self.server.distribute_data(user_profile)
    
    def database_search(self, input_prompt="Learn this course according to the material"):
        """Call databaseSearch tool"""
        return self.server.database_search(input_prompt)
    
    def get_cur_progress(self):
        """Call getCurProgress tool"""
        return self.server.get_cur_progress()
    
    def get_system_prompt(self):
        """Call getSystemPrompt tool"""
        return self.server.get_system_prompt()
    
    def evaluate_answer(self, user_answer, correct_answer, concept_id):
        """Call evaluateAnswer tool"""
        result = self.server.evaluate_answer(user_answer, correct_answer, concept_id)
        if hasattr(result, 'to_dict'):
            return result.to_dict()
        return result
    
    def update_freshness_and_log(self, concept_id, evaluation_result):
        """Call updateFreshnessAndLog tool"""
        from mcp_cheatsheet.models import EvaluationResult
        
        if isinstance(evaluation_result, dict):
            evaluation_result = EvaluationResult.from_dict(evaluation_result)
        
        return self.server.update_freshness_and_log(concept_id, evaluation_result)
    
    def decide_next(self, cur_progress):
        """Call decideNext tool"""
        result = self.server.decide_next(cur_progress)
        if hasattr(result, 'to_dict'):
            return result.to_dict()
        return result
    
    def generate_explaination(self, concept_id):
        """Call generateExplaination tool"""
        return self.server.generate_explaination(concept_id)
    
    def generate_que_single_choice(self, concept_id):
        """Call generateQue_singleChoice tool"""
        result = self.server.generate_que_single_choice(concept_id)
        if result and hasattr(result, 'to_dict'):
            return result.to_dict()
        return result
    
    def generate_que_multi_choice(self, concept_id):
        """Call generateQue_multiChoice tool"""
        result = self.server.generate_que_multi_choice(concept_id)
        if result and hasattr(result, 'to_dict'):
            return result.to_dict()
        return result
    
    def generate_que_short_answer(self, concept_id):
        """Call generateQue_shortAnswer tool"""
        result = self.server.generate_que_short_answer(concept_id)
        if result and hasattr(result, 'to_dict'):
            return result.to_dict()
        return result
    
    # ============ Database Access Methods ============
    
    def get_courses(self):
        """Get list of courses"""
        return self.database.get_courses()
    
    def add_concept(self, course_name, concept):
        """Add a concept to database"""
        return self.database.add_concept(course_name, concept)
    
    def get_concept(self, concept_ref):
        """Get a concept by reference"""
        return self.database.get_concept(concept_ref)
    
    def generate_concept_id(self, course_name, timestamp):
        """Generate unique concept ID"""
        return self.database.generate_concept_id(course_name, timestamp)
    
    def check_duplicate(self, course_name, title):
        """Check if concept already exists"""
        return self.database.check_duplicate(course_name, title)


# Global MCP client instance
mcp_client = MCPClient()

