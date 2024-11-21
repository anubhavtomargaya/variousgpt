
import json
from typing import Dict, List, Optional,Any
from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management
from summary_mg import insert_management_intel

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

# summary structured
from store_prompts.create_prompts import prompt_manager
def generate_content_with_prompt(context_json: Dict,
                                prompt_name ="earnings_call_summary",
                                prompt_version=1) -> Dict:
    """
    Generate output based on prompt
    
    Args:
        transcript_json: Dictionary containing text section to be processed 
        
    Returns:
        Dictionary with structured summaries optimized for UI rendering
    """
    
    prompt = prompt_manager.get_prompt(prompt_name) # add version here later on
    if not prompt:
        raise ValueError(f"Required prompt not found in database: {prompt_name} v{prompt_version}")


    def create_summary(transcript: Dict) -> Dict:
        # Build the complete prompt using stored components
        summary_prompt = f"""
        Context:
        {json.dumps(transcript, indent=2)}

        Instructions:
        {prompt['main_prompt']}

        Output Format:
        always return JSON
        {json.dumps(prompt['output_format'], indent=2)}

        Additional Guidelines:
        {json.dumps(prompt['guidelines'], indent=2)}
        """
        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": prompt['system_prompt']
                },
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    def validate_summary(summary: Dict) -> Dict:
        """
        Ensure essential sections are present with required content and validate metric integrity.
        """
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

        def validate_metric(metric_value: Any) -> str:
            """Validate metric values and ensure proper handling of unavailable data."""
            if not metric_value:
                return "Details not provided"
            if isinstance(metric_value, (int, float)):
                return str(metric_value)
            if isinstance(metric_value, str):
                # Check if the string contains a placeholder percentage
                if '%' in metric_value and not any(char.isdigit() for char in metric_value):
                    return "Details not provided"
                # Check if the string is just a placeholder number
                if metric_value.replace('.', '').replace('-', '').isdigit():
                    # if not metric_value.startswith(('$', '€', '£')):  # Allow currency values
                        return "Details not provided"
            return metric_value

        # Validate highlights section
        if "highlights" not in summary:
            summary["highlights"] = {}
        
        for field in required_sections["highlights"]:
            if field not in summary["highlights"]:
                summary["highlights"][field] = "No information provided"
            
            if field == "key_metrics":
                if not isinstance(summary["highlights"][field], list):
                    summary["highlights"][field] = []
                else:
                    # Validate each metric in key_metrics
                    for i, metric in enumerate(summary["highlights"][field]):
                        if isinstance(metric, dict):
                            metric["value"] = validate_metric(metric.get("value"))
                            if "comparison" not in metric:
                                metric["comparison"] = "Comparison not available"
                        else:
                            summary["highlights"][field][i] = {
                                "metric": "Unnamed Metric",
                                "value": "Details not provided",
                                "comparison": "Comparison not available"
                            }

        # Validate main sections
        if "sections" not in summary:
            summary["sections"] = []
        
        existing_sections = {section.get("title"): section for section in summary["sections"]}
        
        for required_section in required_sections["sections"]:
            title = required_section["title"]
            if title not in existing_sections:
                new_section = {"title": title}
                for field in required_section["required"]:
                    if field == "metrics":
                        new_section[field] = {}
                    else:
                        new_section[field] = [] if field in ["highlights", "achievements", "guidance", "risks", "priorities"] else "No information provided"
                summary["sections"].append(new_section)
            else:
                section = existing_sections[title]
                for field in required_section["required"]:
                    if field not in section:
                        if field == "metrics":
                            section[field] = {}
                        else:
                            section[field] = [] if field in ["highlights", "achievements", "guidance", "risks", "priorities"] else "No information provided"
                    
                    # Validate metrics in Performance Overview section
                    if field == "metrics" and title == "Performance Overview":
                        validated_metrics = {}
                        for metric_name, metric_data in section[field].items():
                            if isinstance(metric_data, dict):
                                validated_metrics[metric_name] = {
                                    "value": validate_metric(metric_data.get("value")),
                                    "comparison": metric_data.get("comparison", "Comparison not available")
                                }
                            else:
                                validated_metrics[metric_name] = {
                                    "value": validate_metric(metric_data),
                                    "comparison": "Comparison not available"
                                }
                        section[field] = validated_metrics

        # Ensure context section exists and validate KPIs
        if "context" not in summary:
            summary["context"] = {
                "industry": [],
                "kpis": {},
                "risk_factors": [],
                "initiatives": []
            }
        else:
            if "kpis" in summary["context"]:
                validated_kpis = {}
                for kpi_name, kpi_data in summary["context"]["kpis"].items():
                    if isinstance(kpi_data, dict):
                        validated_kpis[kpi_name] = {
                            "value": validate_metric(kpi_data.get("value")),
                            "context": kpi_data.get("context", "Context not available")
                        }
                    else:
                        validated_kpis[kpi_name] = {
                            "value": validate_metric(kpi_data),
                            "context": "Context not available"
                        }
                summary["context"]["kpis"] = validated_kpis

        return summary

    try:
        summary = create_summary(context_json)
        # validated_summary = validate_summary(summary)
        return summary

    except Exception as e:
        print(f"Error in summary generation: {str(e)}")
        raise
    

if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    f = 'fy2025_q1_adf_foods_limited_quarterly_earnings_call_transcript_adffoods.pdf'
    f = 'fy2024_q4_ultratech_cement_limited_quarterly_earnings_call_transcript_ultracemco.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'
   
    def test_management_struct_summary():
        section = load_ts_section_management(f)
        return generate_content_with_prompt(section)
    
    def test_insert_management_summary():
        key = 'struct_summary'
        section = load_ts_section_management(f)
        s = generate_content_with_prompt(section)
        if s:
            print("inserting")
            return insert_management_intel(f,key,s)
        else:
            print("not found")
            return None
    
   
    print(test_management_struct_summary())
    # print(test_insert_management_summary())
    
    
