import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from functools import lru_cache
import os
from tqdm import tqdm

URL = "https://w3.thetalesofdemonsandgods.com/manga/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
DOWNLOAD_DIR = r"C:\Users\reivson\Pictures\demonsandgods"

@lru_cache(maxsize=128)
def extract_chapter_info(url: str) -> tuple:
    """Extract chapter number and variation from URL with caching for performance."""
    match = re.search(r'chapter-(\d+(?:\.\d+)?)-?(\d+)?', url.lower())
    if match:
        chapter_num = float(match.group(1))
        variation = match.group(2) or '1'  # Default to '1' if no variation
        return chapter_num, variation
    return 0, '1'

def download_chapter(chapter_url: str, output_dir: str = None) -> None:
    """Download all images from a specific chapter."""
    try:
        # Create output directory based on chapter number if not specified
        if not output_dir:
            chapter_num, variation = extract_chapter_info(chapter_url)
            output_dir = os.path.join(DOWNLOAD_DIR, f'chapter_{chapter_num:.1f}_part_{variation}')
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nDownloading chapter to: {output_dir}")

        with requests.Session() as session:
            response = session.get(chapter_url, headers=HEADERS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different common selectors for manga sites
            image_selectors = [
                'div.reading-content img',  # Common manga reader
                'div#readerarea img',       # Alternative reader area
                'div.entry-content img',    # WordPress content
                'div.chapter-content img',  # Another common layout
                'div.reader-area img',      # Alternative reader
                '.chapter-content-inner img', # Inner content
                'article img',              # Generic article images
                'img.chapter-img',          # Direct chapter images
                'img[loading="lazy"]',      # Lazy-loaded images
            ]
            
            images = []
            for selector in image_selectors:
                print(f"\nTrying selector: {selector}")
                found_images = soup.select(selector)
                if found_images:
                    print(f"Found {len(found_images)} images with selector {selector}")
                    for img in found_images:
                        # Try different image source attributes
                        src = (img.get('data-src') or 
                               img.get('data-lazy-src') or 
                               img.get('data-original') or 
                               img.get('src'))
                        if src:
                            if not src.startswith(('http://', 'https://')):
                                src = urljoin(chapter_url, src)
                            images.append(src)
            
            # Remove duplicates while preserving order
            images = list(dict.fromkeys(images))
            
            if not images:
                print("\nDebug information:")
                print("Page content preview:")
                print(soup.prettify()[:1000])
                print("\nAll img tags found:")
                for img in soup.find_all('img'):
                    print(f"Image tag: {img}")
                return
            
            print(f"\nFound {len(images)} unique images. Starting download...")
            print("Image URLs:")
            for i, img_url in enumerate(images):
                print(f"{i+1}. {img_url}")
            
            # Download each image with progress bar
            for i, img_url in enumerate(tqdm(images, desc="Downloading images")):
                try:
                    img_response = session.get(img_url, stream=True)
                    img_response.raise_for_status()
                    
                    file_extension = os.path.splitext(urlparse(img_url).path)[1]
                    if not file_extension:
                        file_extension = '.jpg'
                    
                    filename = f'page_{i+1:03d}{file_extension}'
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                except Exception as e:
                    print(f"\nError downloading image {i+1}: {e}")
                    continue
            
            print(f"\nDownload complete! Images saved in '{output_dir}' directory")
            
    except requests.RequestException as e:
        print(f"Error downloading chapter: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_chapters(url: str, limit: int = 50) -> list:
    """Get the most recent manga chapters."""
    try:
        with requests.Session() as session:
            response = session.get(url, headers=HEADERS)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            chapters = []
            for link in soup.select('a[href*="chapter"]'):
                href = link.get('href', '')
                chapter_num, variation = extract_chapter_info(href)
                
                if chapter_num > 0:
                    chapters.append({
                        'number': chapter_num,
                        'variation': variation,
                        'url': href,
                        'title': link.text.strip()
                    })
            
            # Sort by chapter number (descending) and variation (ascending)
            return sorted(
                chapters,
                key=lambda x: (-x['number'], int(x['variation']))
            )[:limit]
            
    except requests.RequestException as e:
        print(f"Error fetching chapters: {e}")
        return []

def show_chapter_variations(chapters, chapter_num):
    """Show available variations for a specific chapter number."""
    variations = [c for c in chapters if c['number'] == chapter_num]
    if not variations:
        print("No chapters found!")
        return None
    
    print(f"\nFound {len(variations)} variations for Chapter {chapter_num}:")
    for i, var in enumerate(variations, 1):
        print(f"{i}. Part {var['variation']} - {var['url']}")
    
    while True:
        try:
            choice = input("\nSelect variation (1-{0}) or press Enter to cancel: ".format(len(variations)))
            if not choice.strip():
                return None
            choice = int(choice)
            if 1 <= choice <= len(variations):
                return variations[choice-1]
        except ValueError:
            print("Invalid choice! Please enter a number.")
    
    return None

def main():
    chapters = get_chapters(URL)
    
    if chapters:
        print(f"\nMost recent chapters (showing {len(chapters)} chapters):")
        prev_num = None
        for chapter in chapters:
            # Only print chapter number once if there are variations
            if chapter['number'] != prev_num:
                print(f"\nChapter {chapter['number']:.1f}:")
                prev_num = chapter['number']
            print(f"  Part {chapter['variation']} - {chapter['url']}")
        
        choice = input("\nEnter chapter number to download (or press Enter to exit): ")
        if choice.strip():
            try:
                chapter_num = float(choice)
                selected_chapter = show_chapter_variations(chapters, chapter_num)
                if selected_chapter:
                    download_chapter(selected_chapter['url'])
            except ValueError:
                print("Invalid chapter number!")
    else:
        print("No chapters found")

if __name__ == "__main__":
    main()
