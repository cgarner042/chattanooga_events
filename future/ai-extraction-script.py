import os
import time
import json
import pandas as pd
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import logging

# Setup directories
LOG_FOLDER = 'logs'
DATA_FOLDER = 'data'

for folder in [LOG_FOLDER, DATA_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOG_FOLDER, 'ai_extraction.log'),
    filemode='w'
)

# Configuration - same sites as in the original script
SITES = {
    "Visit Chattanooga": {
        "url": "https://www.visitchattanooga.com/events/",
        "description": "Events page from Visit Chattanooga website."
    },
    "CHA Guide Events": {
        "url": "https://www.cha.guide/events",
        "description": "Events listing from CHA Guide."
    },
    "Chattanooga Pulse": {
        "url": "https://www.chattanoogapulse.com/search/event/the-pulse-event-search/#page=1",
        "description": "Event search page from Chattanooga Pulse."
    },
    "Chatt Library": {
        "url": "https://chattlibrary.org/events/",
        "description": "Events page from Chattanooga Library."
    }
}

class OllamaClient:
    """Client for interacting with local Ollama API"""
    
    def __init__(self, model="llava:latest"):
        """Initialize with a multimodal model for processing HTML and screenshots"""
        self.base_url = "http://localhost:11434/api"
        self.model = model
        self.check_model_availability()
    
    def check_model_availability(self):
        """Check if the specified model is available, if not suggest downloading"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            
            if self.model not in available_models:
                logging.warning(f"Model {self.model} not found. Available models: {available_models}")
                logging.info(f"You can download {self.model} with: ollama pull {self.model}")
                # Fall back to a text model if a multimodal one isn't available
                for model in ["mistral:latest", "llama3:latest", "phi3:latest"]:
                    if model in available_models:
                        logging.info(f"Falling back to {model}")
                        self.model = model
                        return
        except requests.RequestException as e:
            logging.error(f"Error connecting to Ollama: {e}")
            logging.error("Is Ollama running? Start with 'ollama serve'")
    
    def generate(self, prompt, image=None):
        """Generate a response from Ollama with an optional image"""
        endpoint = f"{self.base_url}/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        # Add image if provided and using a multimodal model
        if image and "llava" in self.model:
            payload["images"] = [image]
        
        try:
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                logging.error(f"Error from Ollama API: {response.text}")
                return None
        except requests.RequestException as e:
            logging.error(f"Failed to communicate with Ollama: {e}")
            return None

class AIWebExtractor:
    """Extract events from websites using AI"""
    
    def __init__(self):
        """Initialize the extractor with an Ollama client"""
        self.ollama = OllamaClient()
        self.setup_browser()
    
    def setup_browser(self):
        """Set up the browser for fetching web pages"""
        chromedriver_autoinstaller.install()
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
    
    def fetch_page(self, url):
        """Fetch a web page and return its HTML content"""
        try:
            self.driver.get(url)
            time.sleep(5)  # Wait for JavaScript content to load
            
            # Scroll to load all content
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            html_content = self.driver.page_source
            
            # Take a screenshot for visual context if using a multimodal model
            screenshot = None
            if "llava" in self.ollama.model:
                self.driver.save_screenshot("temp_screenshot.png")
                with open("temp_screenshot.png", "rb") as img_file:
                    import base64
                    screenshot = base64.b64encode(img_file.read()).decode('utf-8')
                os.remove("temp_screenshot.png")
            
            return html_content, screenshot
        except Exception as e:
            logging.error(f"Error fetching the page: {e}")
            return None, None
    
    def extract_events(self, html_content, screenshot, site_name, site_url):
        """Extract events from HTML content using AI"""
        # Clean up HTML for easier processing
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles to reduce token count
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get the main content area (most relevant part)
        main_content = soup.find('main') or soup.find('div', {'id': 'main'}) or soup.find('div', {'class': 'main'})
        clean_html = main_content.prettify() if main_content else soup.prettify()
        
        # Create chunks if the HTML is too large
        html_chunks = self.chunk_html(clean_html, max_size=12000)  # Adjust size based on model context window
        
        # Combine all events from different chunks
        all_events = []
        
        for i, chunk in enumerate(html_chunks):
            logging.info(f"Processing chunk {i+1}/{len(html_chunks)} for {site_name}")
            
            prompt = f"""
You are an expert web scraper tasked with extracting event information from the HTML of {site_name}.
URL: {site_url}

Extract ALL events found in the HTML, focusing on these fields:
1. title: The event title
2. date: The event date in MM-DD format
3. time: The event time in HH:MM AM/PM format
4. location: Where the event is taking place
5. url: The URL to the event details page
6. image_url: URL to the event image

Return the results as a JSON array with each event as an object containing these fields.
If a field is not found, use "N/A" as the value.

Example format:
```json
[
  {{
    "title": "Event Title",
    "date": "04-24",
    "time": "7:00 PM",
    "location": "Event Location",
    "url": "https://example.com/event",
    "image_url": "https://example.com/image.jpg"
  }},
  ...
]
```

Here's the HTML content:
{chunk}
"""
            
            # If we have a screenshot and using a multimodal model, add context
            if screenshot and i == 0 and "llava" in self.ollama.model:
                response = self.ollama.generate(prompt, screenshot)
            else:
                response = self.ollama.generate(prompt)
            
            if response:
                try:
                    # Extract the JSON part from the response
                    json_content = self.extract_json_from_text(response)
                    chunk_events = json.loads(json_content)
                    all_events.extend(chunk_events)
                    logging.info(f"Extracted {len(chunk_events)} events from chunk {i+1}")
                except Exception as e:
                    logging.error(f"Error parsing events from chunk {i+1}: {e}")
                    logging.error(f"Response: {response}")
        
        # Post-process events for consistency
        processed_events = self.post_process_events(all_events)
        return processed_events
    
    def chunk_html(self, html, max_size=12000):
        """Break HTML into chunks if it's too large"""
        if len(html) <= max_size:
            return [html]
        
        soup = BeautifulSoup(html, 'html.parser')
        chunks = []
        current_chunk = ""
        
        # Look for natural breaking points like div elements
        for element in soup.find_all(['div', 'section', 'article']):
            element_html = str(element)
            if len(current_chunk) + len(element_html) > max_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = element_html
            else:
                current_chunk += element_html
        
        if current_chunk:
            chunks.append(current_chunk)
        
        # If we couldn't chunk naturally, do it by size
        if not chunks:
            chunks = [html[i:i+max_size] for i in range(0, len(html), max_size)]
        
        return chunks
    
    def extract_json_from_text(self, text):
        """Extract JSON content from the text response"""
        # Find content between triple backticks
        import re
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            return json_match.group(1).strip()
        
        # If no json code block, try to find array directly
        json_match = re.search(r'\[\s*{\s*".*?}\s*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If all fails, return the full text
        return text
    
    def post_process_events(self, events):
        """Clean and standardize event data"""
        processed = []
        seen_titles = set()
        
        for event in events:
            # Skip duplicates
            if event.get('title', 'N/A') in seen_titles:
                continue
            
            seen_titles.add(event.get('title', 'N/A'))
            
            # Ensure all required fields exist
            clean_event = {
                'title': event.get('title', 'N/A'),
                'date': event.get('date', 'N/A'),
                'time': event.get('time', 'N/A'),
                'location': event.get('location', 'N/A'),
                'url': event.get('url', 'N/A'),
                'image_url': event.get('image_url', 'N/A')
            }
            
            # Clean up date format if possible
            if clean_event['date'] != 'N/A':
                try:
                    # Handle various date formats
                    for fmt in ['%m-%d', '%m/%d', '%B %d', '%b %d']:
                        try:
                            date_obj = datetime.strptime(clean_event['date'], fmt)
                            clean_event['date'] = date_obj.strftime('%m-%d')
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass  # Keep the original if parsing fails
            
            processed.append(clean_event)
        
        return processed
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def create_all_events_dataframe(all_events):
    """Create a dataframe with all events"""
    all_df = pd.DataFrame()
    for site_name, events in all_events.items():
        df = pd.DataFrame(events)
        df['source'] = site_name
        all_df = pd.concat([all_df, df], ignore_index=True)
    return all_df

def save_all_events_to_csv(all_df, filename="all_events.csv"):
    """Save all events to a CSV file"""
    filepath = os.path.join(DATA_FOLDER, filename)
    all_df.to_csv(filepath, index=False)
    logging.info(f"Saved all events to {filepath}")
    return filepath

def save_site_events_to_csv(events, site_name):
    """Save events from a specific site to a CSV file"""
    file_name = os.path.join(DATA_FOLDER, f"{site_name.lower().replace(' ', '_')}_events.csv")
    df = pd.DataFrame(events)
    df.to_csv(file_name, index=False)
    logging.info(f"Saved {len(events)} events from {site_name} to {file_name}")

def main():
    """Main function to extract events from all sites"""
    logging.info("Starting AI-powered event extraction")
    extractor = AIWebExtractor()
    all_events = {}
    
    try:
        for site_name, site_info in SITES.items():
            url = site_info["url"]
            logging.info(f"Processing {site_name} ({url})")
            
            html_content, screenshot = extractor.fetch_page(url)
            if html_content:
                # Save the HTML for debugging if needed
                with open(os.path.join(LOG_FOLDER, f"{site_name.lower().replace(' ', '_')}.html"), 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                events = extractor.extract_events(html_content, screenshot, site_name, url)
                all_events[site_name] = events
                
                # Save individual site events
                save_site_events_to_csv(events, site_name)
                
                logging.info(f"Extracted {len(events)} events from {site_name}")
            else:
                logging.error(f"Failed to fetch content from {site_name}")
        
        # Create and save all events
        if all_events:
            all_events_df = create_all_events_dataframe(all_events)
            csv_path = save_all_events_to_csv(all_events_df)
            print(f"All events saved to {csv_path}")
        else:
            logging.error("No events were extracted")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
