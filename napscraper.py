import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
from itertools import islice
import time

def crawl_website(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract contact information based on common patterns
        address_patterns = [re.compile(r'\b\d{1,5}\s\w.*?\b'),
                            re.compile(r'\b\w+,\s\w{2}\s\d{5}\b')]
        phone_patterns = [re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')]

        addresses = []
        phones = []

        for pattern in address_patterns:
            matches = soup.find_all(string=pattern)
            addresses.extend(matches)

        for pattern in phone_patterns:
            matches = soup.find_all(string=pattern)
            phones.extend(matches)

        # If no structured address or phone number found, try the contact page
        if not addresses or not phones:
            contact_page_url = find_contact_page(url)
            if contact_page_url:
                contact_page_response = requests.get(contact_page_url)
                if contact_page_response.status_code == 200:
                    contact_page_soup = BeautifulSoup(contact_page_response.text, 'html.parser')
                    addresses.extend(contact_page_soup.find_all(string=address_patterns))
                    phones.extend(contact_page_soup.find_all(string=phone_patterns))

        # Search Google for email addresses associated with the domain
        domain = url.split('//')[1].split('/')[0]
        email_search_query = f'site:{domain} email'
        emails = list(islice(search(email_search_query), 5))

        return {
            'Addresses': addresses,
            'Phones': phones,
            'Emails': emails
        }
    else:
        return None

def find_contact_page(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for a link that contains "contact" in the href attribute
        contact_links = soup.find_all('a', href=lambda href: href and 'contact' in href.lower())
        
        if contact_links:
            # Use the first link found (you may need to improve this logic based on the website structure)
            contact_page_url = contact_links[0].get('href')
            
            # Ensure the URL is complete
            if not contact_page_url.startswith('http'):
                contact_page_url = url + contact_page_url

            return contact_page_url

    return None

def save_results(results):
    with open('contact_info.txt', 'w') as file:
        for key, value in results.items():
            file.write(f'{key}:\n')
            for item in value:
                file.write(f'  {item}\n')

if __name__ == "__main__":
    company_website = input("Enter the company's website (e.g., https://example.com): ").strip()

    results = crawl_website(company_website)

    if results:
        # Display results
        for key, value in results.items():
            print(f'{key}:')
            for item in value:
                print(f'  {item}')

        # Save results to a text file
        save_results(results)
        print('Results saved to contact_info.txt')
    else:
        print('Failed to retrieve information from the website.')
