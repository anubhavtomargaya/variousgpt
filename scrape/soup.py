
from bs4 import BeautifulSoup
import requests
import pandas as pd 
def fetch_html_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def extract_span_content(html):
    # soup = BeautifulSoup(html, 'html.parser')
    soup = BeautifulSoup(html, 'lxml')
    span_elements = soup.find_all('span')
    
    span_dict = {}
    for span in span_elements:
        class_name = span.get('class')
        if class_name:
            class_name = ' '.join(class_name)  # Handle multiple class names
            text_content = span.get_text(strip=True)
            if class_name in span_dict:
                span_dict[class_name].append(text_content)
            else:
                span_dict[class_name] = [text_content]
    
    return span_dict


def parse_react_table(html):
    soup = BeautifulSoup(html, 'lxml')
    table_div = soup.find('div', class_='swReactTable-scrollable')
    
    if not table_div:
        raise ValueError("React table not found in the HTML content.")
    
    row_data = pd.DataFrame()
    # Iterate through each row in the table
    a = []
    b= [ ]
    c = [ ]
    for row_div in table_div.find_all('div', class_='swReactTableCell'):
        
        # print(row_div.get_text(strip=True))
        
        # Extract data from each cell in the row
        for cell_div in row_div.find_all('div'):
            keyword_span = cell_div.find('span', class_='search-keyword')
            if keyword_span:
                keyword = keyword_span.get_text(strip=True)
                a.append(keyword)
            
            
   
            traffic_share_span = cell_div.find('span', class_='min-value')
            if traffic_share_span:
                traffic_share_value = traffic_share_span.get_text(strip=True)
                b.append(traffic_share_value)

        
            total_visits = cell_div.find('div', class_='TotalVisitsContainer-fdcRnX')
            if total_visits:
                total_visits_ = total_visits.get_text(strip=True)
                c.append(total_visits_)
        
       
    row_data['search-keyword'] = [a] 
    row_data['min-value'] = [b] 
    row_data['total-visits'] = [c]

    print(len(a))
    print(len(c))
    print(len(c ))

    df = pd.DataFrame(columns=['search-keyword','min-value','total-visits'],data={'a':[a],'v':[b],'c': [c]} )
    
    return df

from pathlib import Path

def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

html_path = Path('scrape')
table_file = 'similar_web_table.html'
# with open('scrape/div_sample.html','r') as f:
# print(all_span)
    
html_content = read_html_file(Path(html_path,table_file))
df = parse_react_table(html_content)
print(df)
# all_span = extract_span_content(html_content)
# print([ {k: len(set(v))} for k,v in all_span.items()] )
# required_class = 'search-keyword' #gpt will figure this out from the samples
# keyword_for_alphastreet = all_span[required_class]
# print(keyword_for_alphastreet)