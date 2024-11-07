# create summary of 
#   - the whole call - using chain of density summary tool
#   - or individual segments (mgmt, qa summaries)
    # format full summary from the two section summaries

# store in the same table another key in the json.



import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()
def identify_transcript_tags(transcript_json: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
    def process_transcript(transcript: Dict[str, Dict[str, str]]) -> Dict:
        transcript_chunks = {
            chunk_id: chunk["text"]
            for chunk_id, chunk in transcript.items()
        }
        
        prompt = f"""
        Review these transcript chunks and categorize them into one of these specific tags:
        - Management Address
        - Financial Update 

        Transcript chunks:
        {json.dumps(transcript_chunks)}

        IMPORTANT: DO NOT use "tag_name" as the key. Use one of the exact tags listed above based on the content.
        Each chunk should be assigned to the most relevant tag.
        Respond in JSON format only.

        Required format example:
        {{
            "identified_tags": {{
                "Management Address": ["0", "1"],
                "Financial Update": ["2", "3"]
            }}
        }}
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Use the exact tag names provided (Management Address, Financial Update, or Operational Update) to categorize the content. Do not use generic keys like 'tag_name'."
                },
                {"role": "user", "content": prompt}
            ]
        )

        print('res', response.choices[0].message)
        return json.loads(response.choices[0].message.content)

    result = process_transcript(transcript_json)
    return result["identified_tags"]

def extract_management_insights(transcript_json: Dict[str, Dict[str, str]]) -> Dict:
    """
    Extract structured insights from earnings call transcript focusing on management commentary.
    
    Args:
        transcript_json: Dictionary containing transcript text with speaker segments
        
    Returns:
        Dictionary containing structured summary with categorized insights
    """
    
    def get_base_prompt() -> str:
        return """
        Analyze the provided earnings call transcript and extract key management insights, focusing on strategic direction, sentiment, and important takeaways.

        Focus on extracting insights that reveal:
        - Management's strategic thinking and priorities
        - Their view on challenges and opportunities
        - Notable changes in strategy or outlook
        - Commentary on market conditions and competitive position
        - Forward-looking statements and guidance

        For each insight:
        - Keep it concise but include context (15-25 words)
        - Focus on implications rather than just facts
        - Capture the underlying sentiment
        - Include relevant context when needed
        - Prioritize insights that would be valuable for investment decisions

        Guidelines for insights:
        1. Financial Performance: Focus on management's commentary about financial trends and underlying drivers, not just numbers
        2. Business Operations: Extract insights about operational efficiency, market share, and business health indicators
        3. Growth Initiatives: Capture specific plans, investments, and new business initiatives
        4. Market Dynamics: Include insights about industry trends and competitive landscape
        5. Future Outlook: Focus on both explicit guidance and implied outlook, including risks and opportunities

        Each section should have 1-3 most relevant insights. Skip categories where no meaningful insights are found.
        """

    def get_output_format() -> str:
        return """
        Return a JSON object with exactly this structure:
        {
            "sections": {
                "financial_performance": {
                    "revenue_profits_margins": [
                        {
                            "insight": "string",
                            "sentiment": "positive/neutral/negative",
                            "context": "string (optional)"
                        }
                    ]
                },
                "business_operations": {
                    "core_metrics": [],
                    "market_position": []
                },
                "growth_initiatives": {
                    "expansion_plans": [],
                    "new_launches": []
                },
                "market_dynamics": {
                    "industry_trends": [],
                    "competition": []
                },
                "future_outlook": {
                    "guidance": [],
                    "challenges": []
                }
            }
        }
        """

    def process_transcript(chunk: Dict[str, Dict[str, str]]) -> Dict:
        # Construct the full prompt
        base_prompt = get_base_prompt()
        output_format = get_output_format()
        transcript_text = json.dumps(chunk, indent=2)
        
        full_prompt = f"Transcript:\n{transcript_text}\n\n{base_prompt}\n\n{output_format}"

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": "You are a financial analyst specializing in analyzing earnings calls. \
                        Focus on extracting meaningful management insights rather than surface-level information."
                },
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.2  # Keep it focused and consistent
        )
        
        return json.loads(response.choices[0].message.content)

    def validate_insights(summary: Dict) -> Dict:
        """Validate and clean the generated summary."""
        required_sections = [
            "financial_performance", "business_operations", 
            "growth_initiatives", "market_dynamics", "future_outlook"
        ]
        
        # Ensure all required sections exist
        for section in required_sections:
            if section not in summary["sections"]:
                summary["sections"][section] = {}
        
        # Remove empty insights
        for section in summary["sections"]:
            for subsection in summary["sections"][section]:
                insights = summary["sections"][section][subsection]
                summary["sections"][section][subsection] = [
                    insight for insight in insights 
                    if insight.get("insight") and insight.get("insight").strip()
                ]
        
        return summary

    # def enrich_summary(summary: Dict) -> Dict:
    #     """Add any additional metadata or enrichments."""
    #     # Add generation timestamp
    #     summary["metadata"]["generated_at"] = datetime.now().isoformat()
        
    #     # Add insight counts
    #     insight_counts = {
    #         section: sum(len(subsection) for subsection in summary["sections"][section].values())
    #         for section in summary["sections"]
    #     }
    #     summary["metadata"]["insight_counts"] = insight_counts
        
    #     return summary

    try:
        # Generate initial summary
        summary = process_transcript(transcript_json)
        
        # Validate and clean
        summary = validate_insights(summary)
        
        # Enrich with additional metadata
        # summary = enrich_summary(summary)
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        raise
    
def insert_summary_management(file,mg_summary_guidance:list):
    mg_entry =  {'overview':mg_summary_guidance}
    return update_transcript_intel_entry(file_name=file,
                                         mg_data=mg_entry)

def insert_tags_management_transcript(file: str, tags: dict) -> str:
    if not isinstance(tags, dict):
        raise TypeError("Tags must be a dictionary")
    
    current_mg_data = fetch_management_data(file)
    
    # Add the new tags to the management_data
    current_mg_data['tags'] = tags
    
    # Update the database with the new management_data
    return update_transcript_intel_entry(file_name=file, mg_data=current_mg_data)

if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'

    def test_management_content_get():
        return load_ts_section_management(f)
    
    def test_management_content_summary_idfication():
        section = load_ts_section_management(f)
        return extract_management_insights(section)
    
    def test_management_tags_idfication():
        section = load_ts_section_management(f)
        return identify_transcript_tags(section)
    
    def test_insert_management_content():
        section = load_ts_section_management(f)
        s = extract_management_insights(section)
        if s:
            print("inserting")
            return insert_summary_management(f,s)
        else:
            print("not found")
            return None
    def test_insert_management_tags():
        section = load_ts_section_management(f)
        s = identify_transcript_tags(section)
        if s:
            print("inserting")
            return insert_tags_management_transcript(f,s)
        else:
            print("not found")
            return None
    
    # print(test_management_content_get())
    # print(test_management_tags_idfication())
    # print(test_insert_management_tags())
    # print(test_management_content_summary_idfication())
    print(test_insert_management_content())