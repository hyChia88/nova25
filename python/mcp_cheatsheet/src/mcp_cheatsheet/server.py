"""
FastMCP server factory for CheatSheet educational system
"""
from .database import Database
from .tools import CheatSheetTools


class MCPCheatSheetServer:
    """MCP Server for educational quiz system"""
    
    def __init__(self, data_dir: str, api_key: str, openrouter_url: str):
        self.database = Database(data_dir)
        self.tools = CheatSheetTools(self.database, api_key, openrouter_url)
    
    def get_tools(self) -> CheatSheetTools:
        """Get the tools instance"""
        return self.tools
    
    def get_database(self) -> Database:
        """Get the database instance"""
        return self.database
    
    # Expose all 11 MCP tools as server methods
    
    def distribute_data(self, user_profile: dict = None):
        """Tool 1: Distribute data"""
        return self.tools.distribute_data(user_profile)
    
    def database_search(self, input_prompt: str = "Learn this course according to the material"):
        """Tool 2: Database search"""
        return self.tools.database_search(input_prompt)
    
    def get_cur_progress(self):
        """Tool 3: Get current progress"""
        return self.tools.get_cur_progress()
    
    def get_system_prompt(self):
        """Tool 4: Get system prompt"""
        return self.tools.get_system_prompt()
    
    def evaluate_answer(self, user_answer: str, correct_answer: any, concept_id: str):
        """Tool 5: Evaluate answer"""
        return self.tools.evaluate_answer(user_answer, correct_answer, concept_id)
    
    def update_freshness_and_log(self, concept_id: str, evaluation_result):
        """Tool 6: Update freshness and log"""
        return self.tools.update_freshness_and_log(concept_id, evaluation_result)
    
    def decide_next(self, cur_progress: dict):
        """Tool 7: Decide next action"""
        return self.tools.decide_next(cur_progress)
    
    def generate_explaination(self, concept_id: str):
        """Tool 8: Generate explanation"""
        return self.tools.generate_explaination(concept_id)
    
    def generate_que_single_choice(self, concept_id: str):
        """Tool 9: Generate single choice question"""
        return self.tools.generate_que_single_choice(concept_id)
    
    def generate_que_multi_choice(self, concept_id: str):
        """Tool 10: Generate multiple choice question"""
        return self.tools.generate_que_multi_choice(concept_id)
    
    def generate_que_short_answer(self, concept_id: str):
        """Tool 11: Generate short answer question"""
        return self.tools.generate_que_short_answer(concept_id)

