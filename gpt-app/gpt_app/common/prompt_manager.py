
from enum import Enum
import json
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

    def get_prompt(self, name: str,version:int=None) -> Optional[Dict]:
        """Get prompt by name"""
        filters = {'name': name}
        if version:
            filters['version'] = version
            
        result = self.supabase.table('prompts').select("*").match(filters).execute()
        # result = self.supabase.table('prompts').select("*").eq('name', name).execute()
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
    
def get_prompt_string(context,prompt:dict):
    return f"""
        Context:
        {json.dumps(context, indent=2)}

        Instructions:
        {prompt['main_prompt']}

        Output Format:
        always return JSON
        {json.dumps(prompt['output_format'], indent=2)}

        Additional Guidelines:
        {json.dumps(prompt['guidelines'], indent=2)}
        """

from supabase_handler import supabase
prompt_manager = PromptManager(supabase_client=supabase)
