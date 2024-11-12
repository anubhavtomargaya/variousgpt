from datetime import datetime
from http.client import HTTPException
import re
from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_company_file_names, get_company_list, get_content_top_questions, get_file_extn_doc, get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_latest_transcripts, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
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


@company_app.route('/<company_name>')
@company_app.route('/<company_name>/historical')
def historical(company_name):
    print('com',company_name)
    file_names = get_company_file_names(company_name)  # Implement this function
    print("filen ames",file_names)
    if not file_names:
        return redirect(url_for('company_app.company_index'))
    historical_data = []
    
    print("names",file_names)
    def adjust_to_latest_friday(date):
    # If it's Saturday (5) or Sunday (6), adjust to the latest Friday
        while date.weekday() > 4:
            date -= timedelta(days=1)
        return date

    # Mock insights data
    mock_insights = {'highlight': {'metric': '21.7% YoY Growth', 'title': 'Strong Revenue Surge', 'context': 'Total income reached Rs. 444.4 crores, up from Rs. 365 crores.'}, 'metrics': {'promises': [{'text': 'New production blocks', 'timeline': 'FY25', 'category': 'Expansion'}, {'text': 'Specialty product launches', 'timeline': 'H2 FY26', 'category': 'Innovation'}], 'concerns': [{'text': 'Market volatility risks', 'severity': 'High'}, {'text': 'Product performance variability', 'severity': 'Moderate'}], 'drivers': [{'text': 'CMS revenues', 'impact': 'Rs. 235 crores from commercial molecules'}, {'text': 'Profit after tax', 'impact': 'Rs. 98.3 crores, up from Rs. 62.2 crores'}]}, 'tags': {'industry': ['Pharmaceuticals', 'API', 'CDMO'], 'business': ['Neuland Laboratories'], 'themes': ['Financial Growth', 'Market Positioning', 'Operational Efficiency']}, 'stats': {'promise_count': 2, 'concern_count': 2, 'driver_count': 2}}

    for file_name in file_names:
        print("name",file_name)
        if file_name:
            top_questions = get_content_top_questions(file_name)  # Fetch top questions
            details = get_file_meta(file_name)  # Fetch file details
            
            historical_data.append({
                'file_name': file_name,
                'company_name': details['company_name'],
                'quarter': details['quarter'],
                'date': adjust_to_latest_friday(datetime.utcnow().date() if not details['date'] else datetime.strptime(details['date'], '%Y-%m-%d').date()),
                'financial_year': details['financial_year'],
                'top_questions': top_questions,
                'insights': mock_insights  # Add mock insights to each historical data entry
            })
    latest_transcripts = get_latest_transcripts(limit=5)  # Get 5 latest transcripts
    
    # Filter latest transcripts for current company
    company_latest_transcripts = []
    for transcript in latest_transcripts:
        if transcript['date'] and isinstance(transcript['date'], str):
            try:
                transcript['date'] = datetime.strptime(transcript['date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        company_latest_transcripts.append(transcript)
    print("Latest transcripts:", company_latest_transcripts)
    
    return render_template('company.html', 
                         company_name=company_name.replace('-', ' '), 
                         active_page="historical", 
                         ticker=details['ticker'],
                         historical_data=historical_data,
                         latest_transcripts=company_latest_transcripts)

    # return render_template('company.html', 
    #                        company_name=company_name.replace('-', ' '), 
    #                        active_page="historical", 
    #                        content=f"Historical data for {company_name.replace('-', ' ').title()}")




@company_app.route('/sample')
def company_sample():
    return render_template('sample.html')

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
        'indices': ['NIFTY100', 'NIFTY50', 'OTHERS', 'NASDAQ100'],
        'indices_companies': {
            'NIFTY100': [],
            'NIFTY50': [],
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