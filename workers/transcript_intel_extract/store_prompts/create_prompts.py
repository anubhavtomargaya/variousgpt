
from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

class PromptCategory(str, Enum):
    EXTRACTION = 'extraction'
    SUMMARIZATION = 'summarization'
    ANALYSIS = 'analysis'
    TRANSFORMATION = 'transformation'
    CLASSIFICATION = 'classification'
    OTHER = 'other'

class PromptStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    TESTING = 'testing'

@dataclass
class PromptData:
    name: str
    display_name: str
    category: PromptCategory
    main_prompt: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    output_format: Optional[Dict] = None
    input_schema: Optional[Dict] = None
    guidelines: Optional[List[str]] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: PromptStatus = PromptStatus.DRAFT
    ui_section_order: Optional[Dict] = None
    created_by: Optional[str] = None

class PromptManager:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def save_prompt(self, prompt_data: PromptData, user_id: str) -> Dict:
        """Save or update a prompt with all metadata"""
        
        data = {
            "name": prompt_data.name,
            "display_name": prompt_data.display_name,
            "description": prompt_data.description,
            "category": prompt_data.category,
            "status": prompt_data.status,
            "system_prompt": prompt_data.system_prompt,
            "main_prompt": prompt_data.main_prompt,
            "output_format": prompt_data.output_format,
            "input_schema": prompt_data.input_schema,
            "guidelines": prompt_data.guidelines,
            "example_input": prompt_data.example_input,
            "example_output": prompt_data.example_output,
            "notes": prompt_data.notes,
            "tags": prompt_data.tags,
            "ui_section_order": prompt_data.ui_section_order,
            "last_edited_by": user_id
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        # Check if prompt exists
        result = self.supabase.table('prompts').select("*").eq('name', prompt_data.name).execute()
        
        if len(result.data) == 0:
            data["created_by"] = user_id
            result = self.supabase.table('prompts').insert(data).execute()
        else:
            current_version = result.data[0]['version']
            data['version'] = current_version + 1
            result = self.supabase.table('prompts').update(data).eq('name', prompt_data.name).execute()
            
        return result.data[0]

    def get_prompt(self, name: str) -> Optional[Dict]:
        """Get prompt by name"""
        result = self.supabase.table('prompts').select("*").eq('name', name).execute()
        return result.data[0] if result.data else None

    def list_prompts(self, 
                    category: Optional[PromptCategory] = None,
                    status: Optional[PromptStatus] = None,
                    tags: Optional[List[str]] = None,
                    search_term: Optional[str] = None) -> List[Dict]:
        """List prompts with optional filtering"""
        query = self.supabase.table('prompts').select("*")
        
        if category:
            query = query.eq('category', category)
        if status:
            query = query.eq('status', status)
        if tags:
            query = query.contains('tags', tags)
        if search_term:
            query = query.or_(f"display_name.ilike.%{search_term}%,description.ilike.%{search_term}%")
            
        result = query.order('updated_at', desc=True).execute()
        return result.data

    def toggle_favorite(self, name: str, user_id: str) -> Dict:
        """Toggle favorite status of a prompt"""
        prompt = self.get_prompt(name)
        if not prompt:
            raise ValueError(f"Prompt {name} not found")
            
        result = self.supabase.table('prompts').update({
            "is_favorite": not prompt["is_favorite"],
            "last_edited_by": user_id
        }).eq('name', name).execute()
        
        return result.data[0]

# Example usage for your earnings call prompt
from .supabase_client import supabase
prompt_manager = PromptManager(supabase_client=supabase)

def store_earnings_prompt(user_id: str):
    prompt_data = PromptData(
        name="earnings_call_takeaway",
        display_name="Earnings Call Takeaway Summary Generator",
        description="Generates structured short summary from earnings call parent summary in structure format focusing on a CTA & hook",
        category=PromptCategory.SUMMARIZATION,
        status=PromptStatus.ACTIVE,
        system_prompt="""You are a strategic business analyst creating \
                        visual-first earnings summaries. Focus on key metrics and \
                        transformational narratives that work well in a modern UI.""",
    
    main_prompt="""
        Transform this quarterly financial data into an engaging narrative by identifying:

        1. Core Story:
           - What's the dominant theme this quarter?
           - What single narrative thread connects the numbers?
           - How does performance reflect company's journey?
           - What makes this update newsworthy?

        2. Supporting Evidence:
           - Which metric best illustrates the main story?
           - What achievements reinforce this narrative?
           - How do the numbers support our story?

        3. Future Momentum:
           - Which initiatives show most promise?
           - What developments signal future growth?
           - How is the company positioning for tomorrow?

        Narrative Guidelines:
        - Lead with impact - what matters most?
        - Connect performance to potential
        - Make numbers tell a story
        - Focus on momentum and direction
        - Keep language crisp and engaging
        - Keep the CTA as a 1-2 words or 3-4 words MAXIMUM. IT SHOULD BE LIKE A Call to Action.
        """,

    output_format=
        {
            "story": {
                "headline": {
                    "main": "string (impactful 4-5 word statement)",
                    "supporting": "string (context, max 8 words)"
                },
                "key_theme": "string (one sentence narrative)",
                "tone": "string (growth/resilience/transformation)"
            },
            "evidence": {
                "primary_metric": {
                    "label": "string (metric name)",
                    "value": "string (with comparison)",
                    "significance": "string (why this matters)"
                },
                "supporting_points": [
                    {
                        "text": "string (forward-looking achievement)",
                        "category": "string (growth/strategy/innovation)"
                    }
                ]
            },
            "engagement": {
                "hook": "string (why readers should care)",
                "cta": "string (action prompt)"
            }
        }
    ,

    input_schema={
        "type": "object",
        "properties": {
            "parent_summary_json": {
                "type": "object",
                "description": "Dictionary containing structured summary extracted from management commentary"
            }
        }
    },

    guidelines=[
        'Make every word count - grab attention fast',
        'Build narrative momentum',
        'Connect present results to future potential',
        'Keep language accessible yet impactful'
    ],

  
    notes="",
    
    tags=["earnings", "financial","short", "metrics", "summarization"],
    

)

# Save the prompt
    prompt_manager.save_prompt(prompt_data, user_id)


if __name__ == '__main__':
    print(store_earnings_prompt('test@gmail.com'))
    