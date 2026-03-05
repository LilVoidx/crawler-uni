#!/usr/bin/env python3
"""
Web Crawler
Downloads 100+ web pages from Wikipedia and creates index file.
"""

import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
from pathlib import Path


class WebCrawler:
    def __init__(self, output_dir="crawl_output", max_pages=100):
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.visited = set()
        self.downloaded = []

        # Create HTTP session for efficient requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(exist_ok=True)

    def is_valid_url(self, url):
        """Check if URL is valid and points to HTML content"""
        try:
            parsed = urlparse(url)
            # Skip non-HTML files (images, CSS, JS, etc.)
            skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip',
                             '.css', '.js', '.ico', '.svg', '.mp4', '.mp3']
            return (parsed.scheme in ['http', 'https'] and
                   not any(parsed.path.lower().endswith(ext) for ext in skip_extensions))
        except:
            return False

    def download_page(self, url):
        """Download a single page and save it as HTML file"""
        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=10, allow_redirects=True)

            # Check if it's actually HTML
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                print(f"  Skipped (not HTML): {content_type}")
                return False

            # Parse HTML and check if it has enough text
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(strip=True)

            if len(text_content) < 200:
                print(f"  Skipped (insufficient text)")
                return False

            # Save page with HTML markup
            page_num = len(self.downloaded) + 1
            filename = f"page_{page_num:04d}.html"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Track this download
            self.downloaded.append({
                'number': page_num,
                'url': url,
                'filename': filename
            })

            print(f"  Saved as: {filename}")
            return True

        except Exception as e:
            print(f"  Error downloading {url}: {str(e)}")
            return False

    def get_links(self, url, html_content):
        """Extract all links from a page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        # Find all <a> tags with href attribute
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)  # Convert relative to absolute URL
            if self.is_valid_url(full_url):
                links.append(full_url)

        return links

    def crawl_from_seed(self, seed_urls):
        """Main crawling loop - starts from seed URLs and follows links"""
        to_visit = seed_urls.copy()

        while to_visit and len(self.downloaded) < self.max_pages:
            url = to_visit.pop(0)

            # Skip if already visited or have enough pages
            if url in self.visited or len(self.downloaded) >= self.max_pages:
                continue

            self.visited.add(url)

            try:
                response = self.session.get(url, timeout=10)

                # Only process HTML pages
                if 'text/html' in response.headers.get('Content-Type', ''):
                    if self.download_page(url):
                        # Extract new links and add to queue
                        new_links = self.get_links(url, response.text)
                        for link in new_links:
                            if link not in self.visited and link not in to_visit:
                                to_visit.append(link)

                # wait between requests
                time.sleep(0.5)

            except Exception as e:
                print(f"Error visiting {url}: {str(e)}")
                continue

    def create_index(self):
        """Create index.txt with page numbers and URLs"""
        index_path = os.path.join(self.output_dir, 'index.txt')

        with open(index_path, 'w', encoding='utf-8') as f:
            for item in self.downloaded:
                f.write(f"{item['number']}\t{item['url']}\n")

        print(f"\nIndex file created: {index_path}")
        print(f"Total pages downloaded: {len(self.downloaded)}")

    def create_urls_list(self):
        """Create urls_list.txt with all downloaded URLs"""
        urls_path = os.path.join(self.output_dir, 'urls_list.txt')

        with open(urls_path, 'w', encoding='utf-8') as f:
            for item in self.downloaded:
                f.write(f"{item['url']}\n")

        print(f"URLs list created: {urls_path}")


def get_seed_urls():
    """Starting URLs for crawling"""
    seed_urls = [
        "https://en.wikipedia.org/wiki/Information_retrieval",
        "https://en.wikipedia.org/wiki/Web_crawler",
        "https://en.wikipedia.org/wiki/Search_engine",
        "https://en.wikipedia.org/wiki/Natural_language_processing",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Data_mining",
        "https://en.wikipedia.org/wiki/Computer_science",
        "https://en.wikipedia.org/wiki/Algorithm",
        "https://en.wikipedia.org/wiki/Data_structure",
    ]
    return seed_urls


def main():
    print("=" * 60)
    print("Task 1: Web Crawler")
    print("=" * 60)

    # Create crawler instance
    crawler = WebCrawler(output_dir="crawl_output", max_pages=100)

    # Start crawling
    print("\nStarting crawl from seed URLs...")
    seed_urls = get_seed_urls()
    crawler.crawl_from_seed(seed_urls)

    # Create output files
    print("\nCreating index file...")
    crawler.create_index()

    print("\nCreating URLs list...")
    crawler.create_urls_list()

    print("\n" + "=" * 60)
    print("Crawling complete!")
    print(f"Pages downloaded: {len(crawler.downloaded)}")
    print(f"Output directory: {crawler.output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
