from datetime import datetime
from http.client import HTTPException
import re
from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_company_file_names, get_company_list, get_content_top_questions, get_file_extn_doc, get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_latest_transcripts, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records, get_search_suggestions
from gpt_app.common.supabase_handler import get_company_transcript_data, get_file_extn_doc, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.blueprints.company.format_content import get_faq_content, get_upcoming_content
from . import company_app
## prefix -> /company
from .post import *

def slugify(question):
    return re.sub(r'[^\w\s-]', '', question.lower()).strip().replace(' ', '-')

@company_app.app_template_filter('slugify')
def slugify_filter(s):
    return slugify(s)
from flask import render_template, redirect, url_for


@company_app.route('/api/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    try:
        suggestions = get_search_suggestions(query,limit=3)
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error in search suggestions route: {str(e)}")
        return jsonify([]), 500
    
@company_app.route('/<company_name>')
def historical(company_name):
    try:
        canonical_url = url_for('company_app.historical',
                              company_name=company_name,
                              _external=True)

        file_names = get_company_file_names(company_name)
        if not file_names:
            return redirect(url_for('company_app.company_index'))

        historical_data = []
        def adjust_to_latest_friday(date):
            while date.weekday() > 4:
                date -= timedelta(days=1)
            return date

        for file_name in file_names:
            if file_name:
                top_questions = get_content_top_questions(file_name)
                details = get_file_meta(file_name)
                historical_data.append({
                    'file_name': file_name,
                    'company_name': details['company_name'],
                    'quarter': details['quarter'],
                    'date': adjust_to_latest_friday(datetime.utcnow().date() if not details['date'] else datetime.strptime(details['date'], '%Y-%m-%d').date()),
                    'financial_year': details['financial_year'],
                    'top_questions': top_questions,
                    'structured_content': get_itdoc_mg_guidance(file_name, key='struct_summary')  ,
                    'struct_takeaway': get_itdoc_mg_guidance(file_name, key='struct_takeaway')  

                })

        latest_transcripts = get_latest_transcripts(limit=5)
        company_latest_transcripts = []
        for transcript in latest_transcripts:
            if transcript['date'] and isinstance(transcript['date'], str):
                try:
                    transcript['date'] = datetime.strptime(transcript['date'], '%Y-%m-%d').date()
                    # transcript['structured_content'] =  get_itdoc_mg_guidance(file_name, key='structured_guidance')
                except ValueError:
                    pass
            company_latest_transcripts.append(transcript)

        return render_template('company.html',
                            canonical_url=canonical_url,
                            company_name=company_name.replace('-', ' '),
                            active_page="historical",
                            ticker=details['ticker'],
                            historical_data=historical_data,
                            latest_transcripts=company_latest_transcripts)
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500
    # return render_template('company.html', 
    #                        company_name=company_name.replace('-', ' '), 
    #                        active_page="historical", 
    #                        content=f"Historical data for {company_name.replace('-', ' ').title()}")

@company_app.route('/landing')
def company_landing():
    return render_template('newlp.html')

from datetime import datetime

@company_app.route('/')
def company_index():
    data = get_company_list()
    # Get all latest transcripts
    latest_transcripts = get_latest_transcripts(limit=5)
    
    # Convert date strings to datetime objects
    for transcript in latest_transcripts:
        if transcript['date'] and isinstance(transcript['date'], str):
            try:
                # Assuming the date is in ISO format (YYYY-MM-DD)
                transcript['date'] = datetime.strptime(transcript['date'], '%Y-%m-%d')
            except ValueError:
                # If date conversion fails, keep it as string
                pass
    
    
    company_data = {
        'indices': ['NIFTY100',  'OTHERS', 'NASDAQ100'],
        'indices_companies': {
            'NIFTY100': [],
            # 'NIFTY50': [],
            'OTHERS': [],
            'NASDAQ100': []
        },
        'market_cap': ['Large Cap', 'Mid Cap', 'Small Cap'],
        'market_cap_companies': {
            'Large Cap': [],
            'Mid Cap': [],
            'Small Cap': []
        },
        'sectors': ['Technology', 'Finance', 'Healthcare', 'Energy'],
        'sector_companies': {
            'Technology': [],
            'Finance': [],
            'Healthcare': [],
            'Energy': []
        },
        'recently_updated': latest_transcripts
    }
 # Process the data
    for item in data:
        print("item",item)
        company_name = item['company_name']
        tags = item['tags']

        if tags:
            print("tags",tags)
            # Process indices
            if 'indices' in tags:
                if not len(tags['indices'])>0:
                    print("tagsss",tags['indices'])
                    company_data['indices_companies']['OTHERS'].append(company_name)
                else:
                    for index in tags['indices']:
                        if index in company_data['indices_companies']:
                            company_data['indices_companies'][index].append(company_name)
            
            # Process market cap
            if 'market_cap' in tags:
                for cap in tags['market_cap']:
                    if cap in company_data['market_cap_companies']:
                        company_data['market_cap_companies'][cap].append(company_name)
            
            # Process sectors
            if 'sectors' in tags:
                for sector in tags['sectors']:
                    if sector in company_data['sector_companies']:
                        company_data['sector_companies'][sector].append(company_name)
            
    return render_template('companies.html', 
                         active_page="company_index", 
                         company_data=company_data)