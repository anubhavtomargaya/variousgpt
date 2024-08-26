from http.client import HTTPException
import re
from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_content_top_questions, get_file_extn_doc, get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.common.supabase_handler import get_company_transcript_data, get_file_extn_doc, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.blueprints.gptube.service_embed_text import get_analyst_questions
from gpt_app.blueprints.gptube.service_process_pdf import get_pdf_txt, get_transcript_text
from . import company_app
## prefix -> /company

# @company_app.route('/')
# # #@login_required
# def index():
#     return redirect(url_for('company_app.chat_app'))

# @company_app.route('/<company_name>/latest')
# def faq_page(company_name):
#     faq_data = {
#         "What is your return policy?": "We offer a 30-day money-back guarantee on all our products.",
#         "How long does shipping take?": "Shipping typically takes 3-5 business days within the continental US.",
#         # Add more questions and answers as needed
#     }
#     return render_template('company.html', company_name=company_name, faq_data=faq_data)


def slugify(question):
    return re.sub(r'[^\w\s-]', '', question.lower()).strip().replace(' ', '-')

@company_app.app_template_filter('slugify')
def slugify_filter(s):
    return slugify(s)

@company_app.route('/<company_name>')
@company_app.route('/<company_name>/upcoming')
@company_app.route('/<company_name>/upcoming/<question_slug>')
def upcoming(company_name, question_slug=None):
    upcoming_data = {
        "When is the next earnings call?": "The next earnings call is scheduled for August 15, 2024, at 2:00 PM EST.",
        "What is the current stock price?": "The current stock price is $157.32 as of August 26, 2024, 10:00 AM EST.",
        "What is the predicted stock price?": "Analysts predict the stock price to reach $180 by the end of Q4 2024.",
        "Are there any upcoming deals?": "A major acquisition is rumored to be announced in the coming weeks.",
        "What are the current management tenures?": "The current CEO's contract is set to expire in December 2024, with succession plans to be announced soon."
    }
    if question_slug:
        # Check if the slug is valid
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
    faq_data = {
        f"What is {company_name.replace('-', ' ').title()}?": f"{company_name.replace('-', ' ').title()} is a company that...",
        f"How can I invest in {company_name.replace('-', ' ').title()}?": f"To invest in {company_name.replace('-', ' ').title()}, you can...",
        "When is the Reliance Concall 2024?": "The Reliance Industries Concall for 2024 is scheduled for May 15, 2024, at 10:00 AM IST.",
        "How can I join the Reliance Concall 2024?": "You can join the Reliance Concall 2024 by visiting the official Reliance website and following the instructions provided under the 'Concall' section."
    }
    
    if question_slug:
        # Check if the slug is valid
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