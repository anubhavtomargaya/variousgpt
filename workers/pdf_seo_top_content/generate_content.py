#utils 
from load_pdf import download_pdf_from_bucket
import fitz
from utils_em import split_document, create_seo_content_doc_for_file
from db_supabase import insert_content_doc_entry, upsert_content_doc_entry
import generate_seo
import json
APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'
CHUNK_PARAMS  = (13000,100)

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extracts text from a PDF file in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text.replace('\n',' ')

def get_pdf_txt(file):
    bdata = download_pdf_from_bucket(file,bucket=PROC_PDF_BUCKET)
    txt = extract_text_from_pdf_bytes(bdata)
    print('text')
    # print(txt)
    return txt 


def service_extract_seo_top_questions(file_name, added_by=None):
    txt = get_pdf_txt(file_name)
    print("Generating SEO content for file:", file_name)
    
    chunks = split_document(txt, CHUNK_PARAMS[0], CHUNK_PARAMS[1])
    big_chunk = chunks[0]  # only take first chunk
    
    # try:
# First extract key information in JSON format
    key_info = extract_key_information(big_chunk)
    
    # Generate all questions
    questions = generate_seo.top_questions(big_chunk, num_questions=6)
    
    # Generate answers using both the full context and extracted key info
    seo_top_qa = generate_contextual_answers(big_chunk, key_info, questions, file_name)
    print("seo top qa",seo_top_qa)
    # return seo_top_qa
        
    # except Exception as e:
        # raise Exception("Error in generate.seo : %s",e)
# 
    
    try:
        doc = create_seo_content_doc_for_file(filename=file_name,
                                              top_questions=seo_top_qa,
                                              addn_content = key_info
                                            )
        sp = upsert_content_doc_entry(doc=doc,added_by=added_by)
        print(sp)
        return True
    except Exception as e:
        print("dbError: alreayd exists?",e)
        return False

def extract_key_information(text):
    """
    Extract key information from the earnings call in JSON format
    """
    extraction_prompt = """
    Extract key information from this earnings call transcript and return it in the following JSON format:
    {
        "financial_highlights": {
            "revenue": "",
            "growth_rate": "",
            "profit": "",
            "key_metrics": []
        },
        "business_updates": {
            "major_achievements": [],
            "new_initiatives": [],
            "market_position": ""
        },
        "future_outlook": {
            "guidance": "",
            "expected_growth": "",
            "strategic_priorities": []
        },
        "key_challenges": {
            "risks": [],
            "mitigation_strategies": []
        }
    }
    
    Fill in all fields with specific information from the transcript. Include numbers and percentages where available.
    Format the response as valid JSON only, with no additional text.
    """
    
    # Get JSON response
    json_response = generate_seo.generate_answer(
        pdf_content=text,
        question=extraction_prompt,
        output_format="json"  # Add this parameter to your generate_answer function
    )
    
    try:
        if not isinstance(json_response,dict):
            key_info = json.loads(json_response)
        else:
            key_info = json_response
    except json.JSONDecodeError:
        # Fallback to an empty structure if JSON parsing fails
        key_info = {
            "financial_highlights": {},
            "business_updates": {},
            "future_outlook": {},
            "key_challenges": {}
        }
    print("key info",key_info)
    return key_info

def generate_contextual_answers(context, key_info, questions, file_name):
    """
    Generate answers using both full context and extracted key information
    """
    qa_pairs = {}
    questions_context = "Questions to be answered:\n" + "\n".join(questions)
    
    for i, question in enumerate(questions):
        print(f"Generating answer for question: {question}")
        
        # Format key info for the prompt
        key_info_formatted = json.dumps(key_info, indent=2)
        
        answer_prompt = f"""
            Use this key information and the full transcript to answer the question concisely:

            Key Information:
            {key_info_formatted}

            Question: {question}

            Guidelines:
            1. Be direct and concise - avoid phrases like "I would say" or "It's worth noting"
            2. Focus on information not covered in other questions: {questions_context}
            3. If this information relates to a previous question, reference it briefly instead of repeating
            4. Provide specific numbers and facts where relevant
        """
        
        answer = generate_seo.generate_answer(
            pdf_content=context,
            question=answer_prompt,
            max_tokens=150
   
        ).strip()
        
        qa_pairs[question] = answer
        questions_context += f"\nQ{i+1}: {question}\nA{i+1}: {answer}\n"
    
    return qa_pairs
        # return seo_content
        



if __name__=='__main__':
    # f = 'fy-2025_q1_earnings_call_transcript_amara_raja_energy_&_mobility_limited_are&m.pdf'
    # f = 'fy2/025_q1_fortis_healthcare_limited_quarterly_earnings_call_transcript_fortis.pdf'
    # f = 'fy2025_q1_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    files = ['fy2024_q2_morepen_laboratories_limited_earnings_conference_call_transcript_morepenlab.pdf',
    'fy2024_q3_morepen_laboratories_limited_quarterly_earnings_call_transcript_morepenlab.pdf',
    'fy2025_q1_morepen_laboratories_limited_earnings_conference_call_transcript_morepenlab.pdf',
    'fy2025_q2_cipla_limited_annual_general_meeting_transcript_cipla.pdf',
    'fy2025_q1_cipla_limited_quarterly_earnings_call_transcript_cipla.pdf',
    'fy2024_q2_bosch_limited_quarterly_earnings_call_transcript_boschltd.pdf',
    'fy2024_q4_bosch_limited_quarterly_earnings_call_transcript_boschltd.pdf',
    'fy2025_q1_bosch_limited_quarterly_earnings_call_transcript_boschltd.pdf',
    'fy2024_q4_ambuja_cements_limited_quarterly_earnings_call_transcript_ambujacem.pdf',
    'fy2025_q1_ambuja_cements_limited_quarterly_earnings_call_transcript_ambujacem.pdf',
    'fy2024_q3_bharat_petroleum_corporation_limited_quarterly_earnings_call_transcript_bpcl.pdf',
    'fy2024_q4_bharat_petroleum_corporation_limited_quarterly_earnings_call_transcript_bpcl.pdf',
    'fy2025_q1_bharat_petroleum_corporation_limited_quarterly_earnings_call_transcript_bpcl.pdf',
    'fy-2024_q2_earnings_call_transcript_avenue_supermarts_limited_dmart.pdf',
    'fy2024_q1_berger_paints_india_limited_quarterly_earnings_call_transcript_bergepaint.pdf',
    'fy2023_q4_berger_paints_india_limited_quarterly_earnings_call_transcript_bergepaint.pdf',
    'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf',
    'fy-2024_q4_earnings_call_transcript_asian_paints_500820.pdf',
    'fy-2024_q2_earnings_call_transcript_hindustan_unilever_hindunilvr.pdf',
    'fy-2024_q4_earnings_call_transcript_hindustan_unilever_hindunilvr.pdf',
    'fy-2024_q4_earnings_call_transcript_ghcl_ghcl.pdf',
    'fy-2025_q1_earnings_call_transcript_ghcl_500171.pdf',
    'fy-2025_q2_earnings_call_transcript_ghcl_limited_500171.pdf']
    fss = [ 
        'fy-2024_q1_earnings_call_transcript_schneider_electric_infrastructure_limited_534139.pdf',
        'fy-2024_q1_earnings_call_transcript_tata_consumer_products_limited_tataconsum.pdf',
        'fy-2024_q1_earnings_call_transcript_tata_consumer_products_limited_500800.pdf',
        'fy-2024_q2_earnings_call_transcript_ashok_leyland_limited_ashokley.pdf',
        'fy-2024_q4_earnings_call_transcript_reliance_industries_reliance.pdf',
        'fy-2024_q1_earnings_call_transcript_reliance_industries_limited_reliance.pdf',
        'fy-2023_q4_earnings_call_transcript_kirloskar_oil_engines_limited_koel.pdf',
        'fy-2024_q1_earnings_call_transcript_cummins_india_cumminsind.pdf',
        'fy-2024_q4_earnings_call_transcript_kirloskar_oil_engines_limited_koel.pdf',
        'fy24_q2_earnings_call_transcript_escorts_kubota_limited_escorts.pdf',
        'fy-2024_q1_earnings_call_transcript_pcbl_limited_pcbl.pdf',
        'fy-2024_q1_investor_conference_transcript_raymond_500330.pdf',
        'Raymond_Conference_Call_TranscripQ4-fy24.pdf',
        'fy-2024_q4_Earnings_Conference_Raymond Limited.pdf',
        'Q4_FY23_Earnings_Conference_Raymond_Limited.pdf',
        'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf',
        'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf',
        'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf',
        'fy-2025_q1_earnings_call_transcript_escorts_kubota_limited_escorts.pdf',
        'fy2024_q3_earnings_call_transcript_escorts_kubota_limited_escorts.pdf',
        'fy-2024_q3_earnings_call_transcript_pvr_inox_532689.pdf',
        'fy-2024_q2_earnings_call_transcript_abb_india_limited_bse:abbind.pdf',
        'fy-2024_q1_earnings_call_transcript_sanofi_500674.pdf',
        'fy-2023_q1_earnings_call_transcript_aegis_logistics_limited_aegischem.pdf'
        ]
    def test_get_text_chunk():
        txt= get_pdf_txt(f)
        return split_document(txt)
    
    def test_generate_questions():
        txt = get_pdf_txt(f)
        big_chunk = split_document(txt,CHUNK_PARAMS[0])[0]
        questions = generate_seo.top_questions(big_chunk)
        return questions
    
    def test_generate_seo_qa():
        txt = get_pdf_txt(f)
        big_chunk = split_document(txt,CHUNK_PARAMS[0])[0]
        questions = generate_seo.top_questions(big_chunk)
        seo_content = generate_seo.generate_answers(big_chunk,questions)
        return seo_content
    
# ----------------- # 

    def test_service_seo_content():
        # for f in fss:
            # try:
            # f='fy2025_q1_pvr_inox_limited_quarterly_earnings_call_transcript_pvrinox.pdf'
            f='fy2024_q3_fortis_healthcare_limited_quarterly_earnings_call_transcript_fortis.pdf'
            f='fy2024_q4_fortis_healthcare_limited_quarterly_earnings_call_transcript_fortis.pdf'
            print("rnning file,",f)
            s = service_extract_seo_top_questions(f)
            print(s)
            # except Exception as e:
            #     print("error",e)
        # return
# ----------------- # 


    # print(test_get_text_chunk())
    # print(test_generate_questions())
    # print(test_generate_seo_qa())
    print(test_service_seo_content())

    