from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

app = Flask(__name__)

def get_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def read_urls_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = [line.strip() for line in file]
    return urls

def get_all_urls(url, search_term, depth=1, file_path="output.txt"):
    if depth <= 0:
        return

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a', href=True)

            with open(file_path, 'w', encoding='utf-8') as file:  # Open in write mode
                for link in all_links:
                    full_url = urljoin(url, link['href'])
                    print('keyword:'+ search_term, 'ip:'+ full_url, 'found:false')
                    content = get_url_content(full_url)
                    
                    if content and search_term in content:
                        print('keyword:'+ search_term, 'ip:'+ full_url, 'found:true')
                        file.write(full_url + '\n')
                       
                    get_all_urls(full_url, search_term, depth - 1, file_path)

        else:
            print(f"Failed to retrieve the page for {url}. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"An error occurred while processing {url}: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {url}: {str(e)}")

@app.route('/api/search')
def search():
    search_term = request.args.get('term', '')
    if search_term:
        # Define a list of starting URLs related to programming
        starting_urls = [
            'https://en.wikipedia.org',
            'https://www.geeksforgeeks.org',
            'https://stackoverflow.com',
            'https://quora.com',
            'https://youtube.com',
            'https://facebook.com'
        ]

        output_file = 'output.txt'

        # Initiate search from each starting URL
        for url in starting_urls:
            get_all_urls(url, search_term, depth=10, file_path=output_file)

        urls = read_urls_from_file(output_file)
        return jsonify({'urls': urls})
    else:
        return jsonify({'error': 'No search term provided'})

if __name__ == '__main__':
    app.run(debug=True)
