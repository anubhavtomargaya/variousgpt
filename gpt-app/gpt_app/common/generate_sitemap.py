from dirs import APP_DIR
from pathlib import Path
import requests
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Function to fetch filenames from the API
def fetch_filenames():
    try:
        print("trying")
        response = requests.get('http://localhost:5000/view/docs/list')
        response.raise_for_status()
        filenames = response.json()  # Assuming the API returns a JSON list of filenames
        return filenames
    except requests.RequestException as e:
        print(e)
        # print(f"Error fetching filenames: e")
        return []

# Function to generate the sitemap XML
def generate_sitemap():
    filenames = fetch_filenames()
    
    print(filenames)
    if not filenames:
        print("No filenames available to generate sitemap.")
        return

    # Create the root element
    urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Create URL entries for each filename
    for filename in filenames:
        print(filename)
        print(filenames[filename][0]['file_name'])
        urls = [
            f"http://wallartlabs.tech/view/document/{filenames[filename][0]['file_name']}",
            f"http://wallartlabs.tech/view/document/section/qa/{filenames[filename][0]['file_name']}",
            f"http://wallartlabs.tech/view/document/section/management/{filenames[filename][0]['file_name']}",
            f"http://wallartlabs.tech/view/content/top_questions/{filenames[filename][0]['file_name']}"
        ]
        
        for url in urls:
            url_elem = SubElement(urlset, 'url')
            loc = SubElement(url_elem, 'loc')
            loc.text = url

    # Create and save the XML file
    tree = ElementTree(urlset)
    with open(Path(APP_DIR,'sitemap.xml'), 'wb') as file:
        tree.write(file)
    print("Sitemap generated successfully!")

if __name__ == "__main__":
    generate_sitemap()
