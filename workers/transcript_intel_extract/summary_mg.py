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

# summary structured
def generate_structured_summary(transcript_json: Dict) -> Dict:
    """
    Generate a comprehensive earnings call summary with performance context and TLDR.
    
    Args:
        transcript_json: Dictionary containing management commentary
        
    Returns:
        Dictionary with structured summaries and performance assessment
    """
    
    def get_summary_prompt() -> str:
        return """
        Create a comprehensive summary of this earnings call that includes:

        TLDR (2-3 lines):
        - Overall quarter assessment with key metrics vs expectations
        - Key Highlights & Major developments with their business impact
        - Forward outlook with key growth drivers/concerns
        - overall sentiment or guidance


        Then summarize under these headings with performance context:

        1. Financial Performance
           - Revenue, Profits, Margins
           - Compare with previous quarters/years
            - Segment-wise performance and key drivers
           - Any exceptional/one-off items
           - Sustainable vs temporary improvements
           - Performance vs market expectations
           - Management's tone on numbers
           
        2. Business Operations
           - Core business metrics vs historical trend
           - Market position changes
           - Changes in business mix/strategy
           - Operational improvements/challenges
           - Key products/clients performance

        3. Growth Initiatives
           - Progress on previous announcements
           - Status of ongoing projects
           - New initiatives announced
           - Timeline and expected impact
           - Management confidence in execution
           - Investment and return expectations


        4. Market Dynamics
           - Key industry trends and their specific impact on company
           - Company's response to market changes
           - Competitive strengths/challenges
           - Market share movements
           - Geographic/segment opportunities
           - Customer behavior changes
        
          

        5. Future Outlook
           - Guidance vs previous statements
           - Specific guidance for near/medium term
           - Key growth drivers
           - Potential risks and mitigation
           - Management confidence indicators

        For each section, whenever possible try to:
        - Include YoY and QoQ comparisons
        - Note performance vs expectations
        - Capture management sentiment
        - Flag any concerns or positive developments
        """

    def get_output_format() -> str:
        return """
        {
            "tldr": {
                "summary": "string (2-3 line overall assessment)",
                "performance_rating": "string (good/mixed/concerning)",
                "key_developments": []
            },
            "summary": {
               "financial_performance": {
                    "revenue_profits_margins": {
                        "content": "string (with comparatives)",
                        "key_figures": {},
                        "segment_performance": {},
                        "management_tone": "string"
                    }
                },
                "business_operations": {
                    "core_metrics": {
                         "content": "string (operational details)",
                        "segment_highlights": {},
                        "key_developments": [],
                        "concerns": []
                    },
                    "market_position": {
                        "content": "string (with competitive context)",
                        "key_changes": []
                    }
                },
                "growth_initiatives": {
                    "expansion_plans": {
                        "content": "string (with progress updates)",
                        "status": "string (on-track/delayed/ahead)",
                        "execution_confidence": "string"
                    },
                    "new_launches": {
                        "content": "string (with timeline context)",
                        "key_points": [],
                        "risk_assessment": "string"
                    }
                },
                "market_dynamics": {
                    "industry_trends": {
                        "content": "string (with impact assessment)",
                        "key_points": [],
                        "company_positioning": "string"
                    },
                    "competition": {
                        "content": "string (with market share context)",
                        "key_points": [],
                        "competitive_advantage": "string"
                    }
                },
                "future_outlook": {
                    "guidance": {
                        "content": "string (with previous context)",
                        "key_figures": {},
                        "confidence_level": "string",
                        "risk_factors": []
                    },
                    "challenges": {
                        "content": "string (with mitigation plans)",
                        "key_points": [],
                        "management_preparedness": "string"
                    }
                }
            },
            "metadata": {
                "industry_tags": [],
                "company_tags": [],
                "key_themes": []
                "key_concerns": [],
                "positive_developments": []
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
        1. Keep summaries factual and direct
        2. Include specific metrics when stated
        3. Maintain objective tone
        4. Focus on key information without interpretation
        5. Use clear, straightforward language
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise summarizer. Create clear, structured \
                        summaries organized by specific headings. Focus on facts and key points \
                        without analysis."
                },
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    def validate_summary(summary: Dict) -> Dict:
        """Ensure all sections have required content."""
        required_sections = {
            "financial_performance": ["revenue_profits_margins"],
            "business_operations": ["core_metrics", "market_position"],
            "growth_initiatives": ["expansion_plans", "new_launches"],
            "market_dynamics": ["industry_trends", "competition"],
            "future_outlook": ["guidance", "challenges"]
        }

        for section, subsections in required_sections.items():
            if section not in summary["summary"]:
                summary["summary"][section] = {}
            
            for subsection in subsections:
                if subsection not in summary["summary"][section]:
                    summary["summary"][section][subsection] = {
                        "content": "No information provided.",
                        "key_points" if "points" in subsection else "key_figures": {}
                    }

        if "metadata" not in summary:
            summary["metadata"] = {
                "industry_tags": [],
                "company_tags": []
            }

        return summary

    try:
        summary = create_summary(transcript_json)
        validated_summary = validate_summary(summary)
        return validated_summary

    except Exception as e:
        print(f"Error in summary generation: {str(e)}")
        raise

def save_structured_summary(file_name: str, 
                          summary_data: Dict,
                          key: str = 'structured_summary') -> Dict:
    """Save the structured summary to the transcript file."""
    summary_entry = {key: summary_data}
    return update_transcript_intel_entry(file_name=file_name,
                                       mg_data=summary_entry)


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
    
    def test_management_struct_summary():
        section = load_ts_section_management(f)
        return generate_structured_summary(section)
    
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
    print(test_management_struct_summary())
    # print(test_insert_management_content())
    # print(test_insert_management_tags())
    # print(test_management_content_summary_idfication())