
import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management
from generate_concall_summary_parent import generate_structured_summary
from summary_mg import insert_management_intel

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

def generate_engaging_update(financial_data: Dict) -> Dict:
    """
    Transform quarterly financial data into an engaging, UI-friendly corporate update.
    
    Args:
        financial_data: Dictionary containing quarterly performance data
        
    Returns:
        Dictionary with narrative-driven content optimized for front-page presentation
    """
    
    def get_narrative_prompt() -> str:
        return """
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
        """

    def get_output_format() -> str:
        return """
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
        """

    def create_narrative(data: Dict) -> Dict:
        transform_prompt = f"""
        Financial Data:
        {json.dumps(data, indent=2)}

        Instructions:
        {get_narrative_prompt()}

        Output Format ONLY JSON:
        {get_output_format()}

        Key Considerations:
        1. Make every word count - grab attention fast
        2. Build narrative momentum
        3. Connect present results to future potential
        4. Keep language accessible yet impactful
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a strategic business analyst creating \
                        visual-first earnings summaries. Focus on key metrics and \
                        transformational narratives that work well in a modern UI."
                },
                {"role": "user", "content": transform_prompt}
            ],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    def validate_narrative(update: Dict) -> Dict:
        """Ensure the narrative structure is complete and engaging."""
        required_elements = {
            "story": ["headline", "key_theme", "tone"],
            "evidence": ["primary_metric", "supporting_points"],
            "engagement": ["hook", "cta"]
        }

        for section, subsections in required_elements.items():
            if section not in update:
                update[section] = {}
            
            for subsection in subsections:
                if subsection not in update[section]:
                    if section == "metrics":
                        update[section][subsection] = []
                    elif section == "tags":
                        update[section][subsection] = []
                    else:
                        update[section][subsection] = ""

        return update

    try:
        narrative = create_narrative(financial_data)
        validated_update = validate_narrative(narrative)
        return validated_update

    except Exception as e:
        print(f"Error in update generation: {str(e)}")
        raise
    

from gpt_app.common.supabase_handler import  get_itdoc_mg_guidance
if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'
    def test_generate_takeaway():
        m_summary = get_itdoc_mg_guidance(f, key='struct_summary')  
       
        return generate_engaging_update(m_summary)
    
    def test_insert_struct_takeaways():
        key = 'struct_takeaway'
        m_summary = get_itdoc_mg_guidance(f, key='struct_summary')  
        s = generate_engaging_update(m_summary)
        if s:
            print("inserting")
            return insert_management_intel(f,key,s)
        else:
            print("not found")
            return None
    
   
    print(test_generate_takeaway())