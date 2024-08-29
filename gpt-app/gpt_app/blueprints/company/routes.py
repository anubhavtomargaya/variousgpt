from http.client import HTTPException
import re
from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_content_top_questions, get_file_extn_doc, get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.common.supabase_handler import get_company_transcript_data, get_file_extn_doc, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.blueprints.company.format_content import get_faq_content, get_upcoming_content
from . import company_app
## prefix -> /company


def slugify(question):
    return re.sub(r'[^\w\s-]', '', question.lower()).strip().replace(' ', '-')

@company_app.app_template_filter('slugify')
def slugify_filter(s):
    return slugify(s)

@company_app.route('/<company_name>')
@company_app.route('/<company_name>/upcoming')
@company_app.route('/<company_name>/upcoming/<question_slug>')
def upcoming(company_name, question_slug=None):
    upcoming_data = get_upcoming_content(company_name)
    if question_slug:
        valid_slugs = [slugify(q) for q in upcoming_data.keys()]
        if question_slug not in valid_slugs:
            # Redirect to the main FAQ page if the slug is invalid
            return redirect(url_for('company.upcoming', company_name=company_name))
    
    return render_template('company.html', 
                           company_name=company_name.replace('-', ' '), 
                           active_page="upcoming", 
                           upcoming_data=upcoming_data,
                            question_slug=question_slug)
                           

@company_app.route('/<company_name>/historical')
def historical(company_name):
    return render_template('company.html', 
                           company_name=company_name.replace('-', ' '), 
                           active_page="historical", 
                           content=f"Historical data for {company_name.replace('-', ' ').title()}")

@company_app.route('/<company_name>/faq')
@company_app.route('/<company_name>/faq/<question_slug>')
def faq(company_name, question_slug=None):
    faq_data = get_faq_content(company_name)
    
    if question_slug:
        valid_slugs = [slugify(q) for q in faq_data.keys()]
        if question_slug not in valid_slugs:
            # Redirect to the main FAQ page if the slug is invalid
            return redirect(url_for('company.faq', company_name=company_name))
    
    return render_template('company.html', 
                           company_name=company_name.replace('-', ' '), 
                           active_page="faq", 
                           faq_data=faq_data,
                           question_slug=question_slug)

@company_app.route('/<company_name>/links')
def links(company_name):
    return render_template('company.html', 
                           company_name=company_name.replace('-', ' '), 
                           active_page="links", 
                           content=f"Useful links for {company_name.replace('-', ' ').title()}")

@company_app.route('/')
def company_index():
    # data = get_companies_data()
    company_data = {
        'indices': ['S&P500', 'NIFTY50', 'NASDAQ100'],
        'indices_companies': {
            'S&P500': ['Apple', 'Microsoft', 'Amazon', 'Facebook', 'Google'],
            'NIFTY50': ['Reliance', 'TCS', 'HDFC Bank', 'Infosys', 'ICICI Bank'],
            'NASDAQ100': ['Apple', 'Microsoft', 'Amazon', 'Tesla', 'NVIDIA']
        },
        'market_cap': ['Large Cap', 'Mid Cap', 'Small Cap'],
        'market_cap_companies': {
            'Large Cap': ['Apple', 'Microsoft', 'Saudi Aramco', 'Amazon', 'Alphabet'],
            'Mid Cap': ['Occidental Petroleum', 'Spotify', 'Zendesk', 'Zoom', 'DocuSign'],
            'Small Cap': ['Bed Bath & Beyond', 'GameStop', 'AMC Entertainment', 'Tupperware', 'Rite Aid']
        },
        'sectors': ['Technology', 'Finance', 'Healthcare', 'Energy'],
        'sector_companies': {
            'Technology': ['Apple', 'Microsoft', 'Google', 'Facebook', 'NVIDIA'],
            'Finance': ['JPMorgan Chase', 'Bank of America', 'Wells Fargo', 'Citigroup', 'Goldman Sachs'],
            'Healthcare': ['Johnson & Johnson', 'UnitedHealth', 'Pfizer', 'Abbott', 'Merck'],
            'Energy': ['ExxonMobil', 'Chevron', 'Shell', 'BP', 'TotalEnergies']
        },
        'recently_updated': ['Tesla', 'Netflix', 'Uber', 'Airbnb', 'Palantir']
    }
    
    return render_template('companies.html', 
                           active_page="company_index", 
                           company_data=company_data)