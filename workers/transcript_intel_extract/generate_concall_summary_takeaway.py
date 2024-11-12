
import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management
from summary_mg import generate_structured_summary

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

def generate_concall_takeaway(transcript_json: Dict) -> Dict:
    """
    Generate a focused, design-friendly earnings call summary optimized for visual presentation.
    
    Args:
        transcript_json: Dictionary containing management commentary
        
    Returns:
        Dictionary with streamlined insights and key metrics
    """
    
    def get_summary_prompt() -> str:
        return """
    Create a punchy, UI-optimized summary focusing on brevity and impact:

    1. Highlight Section (Keep it ultra-concise):
       - Metric: Just the number and label (e.g., "21.7% YoY Growth")
       - Title: Max 3-4 words, focus on transformation
       - Context: Single clear sentence, lead with specific numbers
       
    2. Metrics (Keep everything brief):
       Promises (2-3):
       - Remove words like "Complete", "Achieve", "Implement"
       - Just state the item and timeline
       - No auxiliary words like "by", "in", "during"
       
       Concerns (2-3):
       - Focus on the core issue
       - One-line descriptions
       - Clear severity marking
       
       Drivers (2-3):
       - Lead with numbers when available
       - Direct impact statements
       - No unnecessary elaboration

    3. Tags:
       - Maximum 3 per category
       - Single or two-word tags only
       - No elaborate descriptions

    Remember:
    - Minimize words, maximize impact
    - Focus on numbers and concrete facts
    - Avoid business jargon
    - Think in terms of UI cards and quick scanning
    - Each item should fit in one line on a card
    """

    def get_output_format() -> str:
        return """
        {
            "highlight": {
                "metric": "string (e.g., '21.7% YoY Growth')",
                "title": "string (3-5 words, strategic focus)",
                "context": "string (one clear sentence about transformation)"
            },
            "metrics": {
                "promises": [
                    {
                        "text": "string (clear, concise commitment)",
                        "timeline": "string",
                        "category": "string"
                    }
                ],
                "concerns": [
                    {
                        "text": "string (clear risk statement)",
                        "severity": "string (High/Moderate/Low)"
                    }
                ],
                "drivers": [
                    {
                        "text": "string (growth driver)",
                        "impact": "string (quantifiable result)"
                    }
                ]
            },
            "tags": {
                "industry": ["string"],
                "business": ["string"],
                "themes": ["string"]
            },
            "stats": {
                "promise_count": "integer",
                "concern_count": "integer",
                "driver_count": "integer"
            }
        }
        """

    def create_summary(transcript: Dict) -> Dict:
        summary_prompt = f"""
        Transcript:
        {json.dumps(transcript, indent=2)}

        Instructions:
        {get_summary_prompt()}

        Output Format:
        RETURN IN FOLLOWING JSON FORMAT
        {get_output_format()}

        Guidelines:
        1. Optimize for visual presentation and scannability
        2. Focus on quantitative metrics whenever possible
        3. Keep all text concise and impactful
        4. Each section should work independently in a card-based layout
        5. Ensure content is suitable for at-a-glance consumption
        6. Prioritize strategic transformation narrative
        7. Keep total promises/concerns/drivers to 2-3 each maximum
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
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    def validate_summary(summary: Dict) -> Dict:
        """Ensure all required sections are present with proper structure."""
        required_sections = {
            "highlight": ["metric", "title", "context"],
            "metrics": ["promises", "concerns", "drivers"],
            "tags": ["industry", "business", "themes"],
            "stats": ["promise_count", "concern_count", "driver_count"]
        }

        for section, subsections in required_sections.items():
            if section not in summary:
                summary[section] = {}
            
            for subsection in subsections:
                if subsection not in summary[section]:
                    if section == "metrics":
                        summary[section][subsection] = []
                    elif section == "tags":
                        summary[section][subsection] = []
                    else:
                        summary[section][subsection] = ""

        return summary

    try:
        summary = create_summary(transcript_json)
        validated_summary = validate_summary(summary)
        return validated_summary

    except Exception as e:
        print(f"Error in takeaway generation: {str(e)}")
        raise
def save_concall_takeaway(file_name: str, 
                         takeaway_data: Dict,
                         key: str = 'concall_takeaway') -> Dict:
    """Save the structured concall takeaway to the transcript file."""
    takeaway_entry = {key: takeaway_data}
    return update_transcript_intel_entry(file_name=file_name,
                                       mg_data=takeaway_entry)


if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'
    def test_management_struct_summary():
        section = load_ts_section_management(f)
        return generate_structured_summary(section)
    
    def test_generate_takeaway():
        section = load_ts_section_management(f)
        xl_summary = generate_structured_summary(section)
        return generate_concall_takeaway(xl_summary)
    
    
    print(test_generate_takeaway())