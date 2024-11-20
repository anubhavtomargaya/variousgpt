
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
        name="earnings_call_summary",
        display_name="Earnings Call Summary Generator",
        description="Generates structured summaries from earnings call transcripts with financial metrics and key highlights",
        category=PromptCategory.SUMMARIZATION,
        status=PromptStatus.ACTIVE,
        system_prompt="""You are a precise summarizer focused on creating UI-friendly content...""",
    
    main_prompt="""
         Create a clear, UI-friendly summary of this earnings call with the following structure:

        1. Highlights Section:
           - Performance rating (one clear statement, indicate if assessment limited by data)
           - 3-4 most important metrics with YoY/QoQ changes
             * For each metric, ONLY include if explicitly mentioned with specific numbers
             * If a metric is discussed but exact numbers aren't provided, note as "Details not provided"
             * If YoY/QoQ changes aren't specified, note as "Comparison not available"
           - Executive summary (2-3 sentences capturing key narrative)
           - Management tone indicator

        2. Main Sections (each with clear narrative and supporting points):

           Performance Overview:
           - Key financial metrics with comparisons
             * ONLY include metrics explicitly stated in the transcript
             * For any referenced metric without specific numbers, note as "Details not provided"
             * For any metric without comparison data, note as "Comparison not available"
           - Segment performance highlights (only include explicitly stated results)
           - Notable variances or one-time items
           - Include relevant management quotes on performance

           Business Progress:
           - Operational developments (specific achievements only)
           - Product/market achievements (concrete results only)
           - Strategic initiatives status (specific updates only)
           - Customer/market dynamics (verified trends only)
           
           Future Outlook:
           - Management guidance (only specific, stated projections)
           - Growth initiatives and timelines (concrete plans only)
           - Risk factors and mitigation
           - Strategic priorities

        3. Supporting Data:
           - Industry context (verified trends only)
           - Key performance indicators (only explicitly stated metrics)
           - Risk factors
           - Strategic initiatives

        Guidelines:
        - NEVER generate or estimate numbers - only use explicitly stated metrics
        - For any referenced metric without specific numbers, mark as "Details not provided"
        - For any metric without comparison data, mark as "Comparison not available"
        - Use clear, direct language
        - Include brief relevant management quotes
        - Focus on material information
        - Maintain data integrity - no placeholder percentages or metrics
        """,

    output_format={
        "highlights": {
            "rating": "string (clear performance assessment, well chosen brevity is key)",
            "key_metrics": [
                {
                    "metric": "string (metric name)",
                    "value": "string (exact value with comparison or 'Details not provided')"
                }
            ],
            "summary": "string (2-3 sentence narrative)",
            "management_tone": "string (one word)"
        },
        "sections": [
            {
                "title": "Performance Overview",
                "narrative": "string (main story)",
                "metrics": {
                    "metric_name": {
                        "value": "string (exact value or 'Details not provided')",
                        "comparison": "string (specific change or 'Comparison not available')"
                    }
                },
                "highlights": ["string (key points with data)"],
                "management_quotes": ["string (relevant quote with attribution)"]
            },
            {
                "title": "Business Progress",
                "narrative": "string (main developments)",
                "achievements": ["string (specific, verified developments only)"],
                "strategic_updates": ["string (specific initiative updates only)"]
            },
            {
                "title": "Future Outlook",
                "narrative": "string (forward looking summary)",
                "guidance": [
                    {
                        "metric": "string (metric name)",
                        "projection": "string (specific projection or 'Details not provided')"
                    }
                ],
                "risks": ["string (risk factors)"],
                "priorities": ["string (strategic priorities)"]
            }
        ],
        "context": {
            "category_tags": ["string (industry/sector/segment tags)"],
            "industry": ["string (verified trends only)"],
            "kpis": {
                "metric_name": {
                    "value": "string (exact value or 'Details not provided')",
                    "context": "string (context or 'Context not available')"
                }
            },
            "risk_factors": ["string (key risks)"],
            "initiatives": ["string (ongoing initiatives)"]
        }
    },

    input_schema={
        "type": "object",
        "properties": {
            "transcript_json": {
                "type": "object",
                "description": "Dictionary containing management commentary"
            }
        }
    },

    guidelines=[
        "Always indicate when specific data is not available",
        "Never generate placeholder metrics",
        "Include relevant management quotes for key points",
        "Focus on material information"
    ],

    example_input='''
    {
        "speaker": "CEO",
        "content": "Our Q4 revenue grew 15% year-over-year..."
    }
    ''',

    example_output='''
    {
        "highlights": {
            "rating": "Strong Performance amidst...",
            "key_metrics": [
                {
                    "metric": "Revenue",
                    "value": "+15% YoY"
                }
            ]
        }
    }
    ''',

    notes="Updated to include management tone analysis",
    
    tags=["earnings", "financial", "metrics", "summarization"],
    

)

# Save the prompt
    prompt_manager.save_prompt(prompt_data, user_id)


if __name__ == '__main__':
    print(store_earnings_prompt('test@gmail.com'))
    