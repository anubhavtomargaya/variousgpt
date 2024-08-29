from gpt_app.common.supabase_handler import get_company_content_all

# data = get_company_content_all()
d = { 
        'company_name':'',
        'upcoming': { 'questions' : {
                                        'When is the reliance earning call?': 'Reliance Industries earning call for Q1 FY25 is on 29th August 2024.',
                                        'What are the expectations from upcoming Escorts Kubota concall?': 'Escorts Kubota are expected to show improvements in EBITDA margins.',
                                    }          
                    },
        'faq': {'questions': 
                        { 'What are the sectors Reliance operates in?': 'Reliance operates in all sectors from oil to retail to tech.',
                        'Who are the top management in Reliance?': 'The Ambanis',      
                        },
                },
        'links': ['www','wwhtml','dotcom.com']
        }

def get_upcoming_content(company_name):
    #data = query_company_content
    data = d
    return data['upcoming']['questions']

def get_faq_content(company_name):
    #data = query_company_content
    data = d
    return data['faq']['questions']
