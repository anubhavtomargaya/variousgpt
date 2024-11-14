import re
from dirs import APP_DIR
from pathlib import Path
import requests
from xml.etree.ElementTree import Element, SubElement, ElementTree
from gpt_app.common.supabase_handler import get_content_top_questions,get_distinct_transcript_files
# Function to fetch filenames from the API
def fetch_filenames():
    try:
        print("trying")
        # response = requests.get('http://localhost:5000/view/docs/list')
        response = requests.get('https://stockrabit.com/view/docs/list')
        response.raise_for_status()
        filenames = response.json()  # Assuming the API returns a JSON list of filenames
        return filenames
    except requests.RequestException as e:
        print(e)
        # print(f"Error fetching filenames: e")
        return []
def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def fetch_questions():
    files = get_distinct_transcript_files()
    questions_all = []
    for f in files:
        qa = get_content_top_questions(f)
        questions = list(qa.keys())
        print(questions)
        questions_all.extend(questions)
    return questions_all

def generate_sitemap():
    filenames = fetch_filenames()
    print('filenames', filenames)
    
    if not filenames:
        print("No filenames available to generate sitemap.")
        return

    # Create the root element
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Define base domain with HTTPS
    BASE_URL = "https://stockrabit.com"  # Changed to https

    # Create URL entries for each filename
    for company_name, files in filenames.items():
        for file_info in files:
            file_name = file_info['file_name']
            
            # Base URLs - using f-strings with BASE_URL
            base_urls = [
                f"{BASE_URL}/company/{company_name}",
        
                # f"{BASE_URL}/view/chat/{file_name}",
                # f"{BASE_URL}/view/document/{file_name}",
                # f"{BASE_URL}/view/document/section/qa/{file_name}",
                # f"{BASE_URL}/view/document/section/management/{file_name}",
                # f"{BASE_URL}/view/content/top_questions/{file_name}",
                f"{BASE_URL}/view/concall/{file_name}?section=top_questions",
                f"{BASE_URL}/view/concall/{file_name}?section=qa_section",
                f"{BASE_URL}/view/concall/{file_name}?section=management_guidance",
                f"{BASE_URL}/view/concall/{file_name}?section=transcript"
                f"{BASE_URL}/view/concall/{file_name}?section=structured_summary"
            ]

            # Add base URLs to sitemap
            for url in base_urls:
                url_elem = SubElement(urlset, 'url')
                loc = SubElement(url_elem, 'loc')
                loc.text = url

            # Add question URLs
            try:
                questions = get_content_top_questions(file_name)
                for question in questions.keys():
                    question_slug = slugify(question)
                    question_url = f"{BASE_URL}/view/concall/{file_name}/questions/{question_slug}"
                    
                    url_elem = SubElement(urlset, 'url')
                    loc = SubElement(url_elem, 'loc')
                    loc.text = question_url
            except Exception as e:
                print(f"Error processing questions for {file_name}: {e}")
                continue

    # Create and save the XML file
    tree = ElementTree(urlset)
    with open(Path(APP_DIR, 'sitemap.xml'), 'wb') as file:
        tree.write(file)
    print("Sitemap generated successfully!")
def count_sitemap_urls():
    try:
        tree = ElementTree.parse(Path(APP_DIR, 'sitemap.xml'))
        root = tree.getroot()
        urls = root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        return len(urls)
    except Exception as e:
        print(f"Error counting URLs: {e}")
        return 0

if __name__ == "__main__":
    # fetch_questions()
    generate_sitemap()

    # Add after generating sitemap
    actual_urls = count_sitemap_urls()
    print(f"\nVerification: Found {actual_urls} URLs in sitemap.xml")
