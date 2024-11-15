
import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management
from summary_mg import insert_management_intel

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

# summary structured
def generate_structured_summary(transcript_json: Dict) -> Dict:
    """
    Generate a streamlined earnings call summary optimized for UI presentation.
    
    Args:
        transcript_json: Dictionary containing management commentary
        
    Returns:
        Dictionary with structured summaries optimized for UI rendering
    """
    
    def get_summary_prompt() -> str:
        return """
        Create a clear, UI-friendly summary of this earnings call with the following structure:

        1. Highlights Section:
           - Performance rating (one clear statement)
           - 3-4 most important metrics with YoY/QoQ changes
           - Executive summary (2-3 sentences capturing key narrative)
           - Management tone indicator

        2. Main Sections (each with clear narrative and supporting points):

           Performance Overview:
           - Key financial metrics with comparisons
           - Segment performance highlights
           - Notable variances or one-time items
           - Include relevant management quotes on performance

           Business Progress:
           - Operational developments
           - Product/market achievements
           - Strategic initiatives status
           - Customer/market dynamics
           
           Future Outlook:
           - Management guidance
           - Growth initiatives and timelines
           - Risk factors and mitigation
           - Strategic priorities

        3. Supporting Data:
           - Industry context
           - Key performance indicators
           - Risk factors
           - Strategic initiatives

        Guidelines:
        - Keep information factual and specific
        - Include metrics with comparisons where available
        - Use clear, direct language
        - Include brief relevant management quotes
        - Focus on material information
        """

    def get_output_format() -> str:
        return """
        {
            "highlights": {
                "rating": "string (clear performance assessment)",
                "key_metrics": [
                    "string (metric with comparison)"
                ],
                "summary": "string (2-3 sentence narrative)",
                "management_tone": "string (one word)"
            },
            "sections": [
                {
                    "title": "Performance Overview",
                    "narrative": "string (main story)",
                    "metrics": {
                        "key": "value with comparison"
                    },
                    "highlights": [
                        "string (key points)"
                    ],
                    "management_quotes": [
                        "string (relevant quote with attribution)"
                    ]
                },
                {
                    "title": "Business Progress",
                    "narrative": "string (main developments)",
                    "achievements": [
                        "string (key developments)"
                    ],
                    "strategic_updates": [
                        "string (initiative updates)"
                    ]
                },
                {
                    "title": "Future Outlook",
                    "narrative": "string (forward looking summary)",
                    "guidance": [
                        "string (specific guidance points)"
                    ],
                    "risks": [
                        "string (risk factors)"
                    ],
                    "priorities": [
                        "string (strategic priorities)"
                    ]
                }
            ],
            "context": {
                "industry": [
                    "string (relevant trends)"
                ],
                "kpis": {
                    "metric_name": "value with context"
                },
                "risk_factors": [
                    "string (key risks)"
                ],
                "initiatives": [
                    "string (ongoing initiatives)"
                ]
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

        Additional Guidelines:
        1. Focus on narrative flow while maintaining structure
        2. Prioritize information hierarchy for UI presentation
        3. Keep points clear and concise for easy scanning
        4. Include specific metrics and comparisons where available
        5. Add relevant management quotes to support key points
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise summarizer focused on creating \
                        UI-friendly content. Emphasize clarity and narrative flow while \
                        maintaining structural integrity for easy information consumption."
                },
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    def validate_summary(summary: Dict) -> Dict:
        """Ensure essential sections are present with required content."""
        required_sections = {
            "highlights": ["rating", "key_metrics", "summary", "management_tone"],
            "sections": [
                {
                    "title": "Performance Overview",
                    "required": ["narrative", "metrics", "highlights"]
                },
                {
                    "title": "Business Progress",
                    "required": ["narrative", "achievements", "strategic_updates"]
                },
                {
                    "title": "Future Outlook",
                    "required": ["narrative", "guidance", "risks", "priorities"]
                }
            ]
        }

        # Validate highlights section
        if "highlights" not in summary:
            summary["highlights"] = {}
        for field in required_sections["highlights"]:
            print("validating highlight",field)
            if field not in summary["highlights"]:
                summary["highlights"][field] = "No information provided"
            if field == "key_metrics" and not isinstance(summary["highlights"][field], list):
                summary["highlights"][field] = []

        # Validate main sections
        if "sections" not in summary:
            summary["sections"] = []
        
        existing_sections = {section.get("title"): section for section in summary["sections"]}
        
        for required_section in required_sections["sections"]:
            title = required_section["title"]
            if title not in existing_sections:
                new_section = {"title": title}
                for field in required_section["required"]:
                    new_section[field] = [] if field in ["highlights", "achievements", "guidance", "risks", "priorities"] else "No information provided"
                summary["sections"].append(new_section)
            else:
                section = existing_sections[title]
                for field in required_section["required"]:
                    if field not in section:
                        section[field] = [] if field in ["highlights", "achievements", "guidance", "risks", "priorities"] else "No information provided"

        # Ensure context section exists
        if "context" not in summary:
            summary["context"] = {
                "industry": [],
                "kpis": {},
                "risk_factors": [],
                "initiatives": []
            }

        return summary

    try:
        summary = create_summary(transcript_json)
        validated_summary = validate_summary(summary)
        return validated_summary

    except Exception as e:
        print(f"Error in summary generation: {str(e)}")
        raise

    

if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    f = 'fy2025_q1_adf_foods_limited_quarterly_earnings_call_transcript_adffoods.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'
   
    def test_management_struct_summary():
        section = load_ts_section_management(f)
        return generate_structured_summary(section)
    
    def test_insert_management_summary():
        key = 'struct_summary'
        section = load_ts_section_management(f)
        s = generate_structured_summary(section)
        if s:
            print("inserting")
            return insert_management_intel(f,key,s)
        else:
            print("not found")
            return None
    
   
    # print(test_management_struct_summary())
    print(test_insert_management_summary())
    
    
