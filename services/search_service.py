import requests
import os

class SearchService:
    def __init__(self):
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")

    def search(self, query):
        # We use the Google Custom Search JSON API as the robust programmatic alternative 
        # to the client-side JavaScript snippet which cannot be executed by the bot.
        url = f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.cse_id}&q={query}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('items', [])
            if not results:
                return "No search results found."
            
            output = ""
            for item in results[:3]:
                output += f"**{item['title']}**\n{item['link']}\n\n"
            return output
        except Exception as e:
            return f"Search failed: {str(e)}"
