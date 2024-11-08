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
        - Financial Update 

        Transcript chunks:
        {json.dumps(transcript_chunks)}

        IMPORTANT: DO NOT use "tag_name" as the key. Use one of the exact tags listed above based on the content.
        Each chunk should be assigned to the most relevant tag.
        Respond in JSON format only.

        Required format example:
        {{
            "identified_tags": {{
                "Financial Update": ["2", "3"],
                
                ...
            }}
        }}
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Use the exact tag names provided ( Financial Update, Challenges etc) to categorize the content. Do not use generic keys like 'tag_name'."
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
    Extract structured insights from earnings call transcript, formatted as management quotes.
    """
    
    def get_base_prompt() -> str:
        return """
        Analyze this earnings call transcript and extract key management quotes and insights. 
        Focus on direct statements from management that provide strategic insights, future outlook, or important context.

        For each section, identify the most impactful direct quotes or paraphrased statements that:
        - Reveal management's strategic thinking and sentiment
        - Provide meaningful context about performance or outlook
        - Indicate significant changes or developments
        - Show management's response to challenges or opportunities

        Guidelines for quote selection:
        1. Prioritize actual quotes that sound natural and conversational
        2. Include relevant context and implications
        3. Identify the speaker role (CEO, CFO, etc.) when clear
        4. Note the topic and its broader implications
        5. Assess the sentiment and confidence level in the statement
        """

    def get_output_format() -> str:
        return """
        Return a JSON object with exactly this structure:
        {
            "sections": {
                "financial_performance": {
                    "revenue_profits_margins": [
                        {
                            "quote": "string (the actual management quote or paraphrased statement)",
                            "speaker": "string (role of the speaker, e.g., CEO, CFO)",
                            "context": "string (additional context or implications)",
                            "topic_tags": ["string"],
                            "sentiment": "positive/neutral/negative",
                            "confidence_level": "high/moderate/low",
                            "key_metrics": {
                                "metric_name": "value",
                                "trend": "up/down/stable"
                            }
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
        
        full_prompt = f"""
        Transcript:
        {transcript_text}

        Instructions:
        {base_prompt}

        Required Format:
        {output_format}

        Additional Guidelines:
        1. For each quote, identify:
           - Main topic or theme
           - Broader business implications
           - Level of certainty in statements
           - Any specific metrics or targets mentioned
           
        2. Focus on quotes that:
           - Provide strategic insights
           - Discuss future plans or guidance
           - Address key challenges or opportunities
           - Explain important changes or trends

        3. When paraphrasing:
           - Maintain the original tone and intent
           - Keep management's perspective clear
           - Include essential numbers and metrics
           - Preserve important qualifiers and context
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": "You are a financial analyst specializing in earnings call analysis. \
                        Focus on extracting meaningful quotes and insights from management commentary."
                },
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.2
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
        
        # Validate each quote has required fields
        for section in summary["sections"].values():
            for subsection in section.values():
                for quote in subsection:
                    # Ensure minimum required fields
                    quote["quote"] = quote.get("quote", "")
                    quote["speaker"] = quote.get("speaker", "Management")
                    quote["context"] = quote.get("context", "")
                    quote["sentiment"] = quote.get("sentiment", "neutral")
                    quote["topic_tags"] = quote.get("topic_tags", [])
                    
                    # Remove empty quotes
                    subsection[:] = [q for q in subsection if q["quote"].strip()]
        
        return summary

    # def enrich_summary(summary: Dict) -> Dict:
    #     """Add additional metadata and insights."""
    #     summary["metadata"]["generated_at"] = datetime.now().isoformat()
        
    #     # Add quote statistics
    #     quote_stats = {
    #         "total_quotes": sum(
    #             len(subsection)
    #             for section in summary["sections"].values()
    #             for subsection in section.values()
    #         ),
    #         "sentiment_distribution": {
    #             "positive": 0,
    #             "neutral": 0,
    #             "negative": 0
    #         }
    #     }
        
    #     # Calculate sentiment distribution
    #     for section in summary["sections"].values():
    #         for subsection in section.values():
    #             for quote in subsection:
    #                 quote_stats["sentiment_distribution"][quote["sentiment"]] += 1
        
    #     summary["metadata"]["quote_stats"] = quote_stats
        
    #     return summary

    try:
        summary = process_transcript(transcript_json)
        summary = validate_insights(summary)
        # summary = enrich_summary(summary)
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        raise

    
def insert_summary_management(file,
                              mg_summary_guidance:list,
                              key='overview'):
    mg_entry =  {key:mg_summary_guidance}
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
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'

    def test_management_content_get():
        return load_ts_section_management(f)
    
    def test_management_content_summary_idfication():
        section = load_ts_section_management(f)
        return extract_management_insights(section)
    
    def test_management_tags_idfication():
        section = load_ts_section_management(f)
        return identify_transcript_tags(section)
    
    def test_insert_management_content():
        key = 'structured_guidance'
        # key = 'structured_summary'
        section = load_ts_section_management(f)
        s = extract_management_insights(section)
        if s:
            print("inserting")
            return insert_summary_management(f,s,key=key)
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
    # print(test_insert_management_content())
    print(test_insert_management_tags())
    # print(test_management_content_summary_idfication())