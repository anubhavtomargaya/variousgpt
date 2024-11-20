
import json
from typing import Dict

from create_prompts import prompt_manager
def generate_structured_summary(transcript_json: Dict) -> Dict:
    """Modified function to use database prompt parts"""
    prompt = prompt_manager.get_prompt("earnings_call_summary")
    if not prompt:
        raise ValueError("Prompt not found in database")
        
    summary_prompt = f"""
    Transcript:
    {json.dumps(transcript_json, indent=2)}

    Instructions:
    {prompt['main_prompt']}

    Output Format:
    {json.dumps(prompt['output_format'], indent=2)}
    """

        
    return summary_prompt


if __name__ == '__main__':
    ts  = {"some text":'mote text',"unless":"tis all fake"}
    print(generate_structured_summary(ts)
    )