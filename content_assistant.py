import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from urllib.parse import quote_plus

# --- 1. THE HEADLINE ANALYSIS ENGINE (from a previous project) ---
POWER_WORDS = {
    'amazing', 'secret', 'powerful', 'proven', 'guaranteed', 'effortless', 'best', 'you',
    'free', 'new', 'discover', 'ultimate', 'simple', 'exclusive', 'instantly', 'shocks'
}

def analyze_headline_for_gui(headline):
    """A simplified analysis function for clean GUI output."""
    blob = TextBlob(headline)
    words = [word.lower() for word in blob.words]
    
    sentiment_score = blob.sentiment.polarity
    sentiment_label = "Neutral"
    if sentiment_score > 0.1: sentiment_label = "Positive"
    if sentiment_score < -0.1: sentiment_label = "Negative"
        
    found_power_words = POWER_WORDS.intersection(words)
    power_word_str = ', '.join(found_power_words) if found_power_words else 'None'
    
    return f"-> Sentiment: {sentiment_label} ({sentiment_score:.2f}), Power Words: {power_word_str}"

# --- 2. THE WEB SCRAPING ENGINE ---
def scrape_google_news(topic, num_headlines=5):
    """Scrapes Google News for a given topic and returns a list of headlines."""
    # Format the topic for a URL
    safe_topic = quote_plus(topic)
    url = f"https://news.google.com/search?q={safe_topic}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google News headlines are often in 'h3' tags with a specific class, this may change
        headlines = []
        # Find article links which contain the headline text
        for item in soup.find_all('a', class_='JtKRv', limit=num_headlines * 2): # get more to filter
            if len(headlines) < num_headlines:
                headlines.append(item.text)
        
        if not headlines:
            return None, "No headlines found. Google's structure may have changed, or the topic is too obscure."

        return headlines, "Success"

    except requests.exceptions.RequestException as e:
        return None, f"Network Error: {e}"

# --- 3. THE GUI APPLICATION ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Content Assistant v1.0")
        self.root.geometry("700x700")
        self.root.configure(bg="#34495e")

        # --- Widget Creation ---
        main_frame = tk.Frame(root, bg="#34495e", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Input
        input_label = tk.Label(main_frame, text="Enter a Topic to Research:", font=("Roboto", 14), bg="#34495e", fg="white")
        input_label.pack(pady=(0, 10))

        self.topic_entry = tk.Entry(main_frame, font=("Roboto", 14), width=60, relief=tk.FLAT, bd=5)
        self.topic_entry.pack(pady=(0, 20), ipady=10)
        
        # Button
        self.analyze_btn = tk.Button(main_frame, text="SEARCH & ANALYZE NOW", command=self.run_full_process, font=("Roboto", 14, "bold"), bg="#16a085", fg="white", relief=tk.FLAT, padx=20, pady=10)
        self.analyze_btn.pack()

        # Results
        results_label = tk.Label(main_frame, text="RESULTS:", font=("Roboto", 14), bg="#34495e", fg="white")
        results_label.pack(pady=(30, 10))

        self.results_text = scrolledtext.ScrolledText(main_frame, font=("Consolas", 12), height=20, width=80, relief=tk.FLAT, bd=5, bg="#2c3e50", fg="white", wrap=tk.WORD)
        self.results_text.pack()

    # --- Widget Functions ---
    def run_full_process(self):
        """Orchestrates the scraping and analysis process."""
        topic = self.topic_entry.get()
        if not topic.strip():
            messagebox.showwarning("Warning", "Please enter a topic.")
            return

        self.display_results("Searching for headlines...")
        self.root.update_idletasks() # Force GUI to update

        headlines, status = scrape_google_news(topic)
        
        if headlines:
            self.display_results(f"Found {len(headlines)} headlines. Analyzing now...\n\n")
            self.root.update_idletasks()
            
            final_output = ""
            for i, headline in enumerate(headlines):
                analysis = analyze_headline_for_gui(headline)
                final_output += f"{i+1}. {headline}\n   {analysis}\n\n"
            
            self.display_results(final_output)
        else:
            messagebox.showerror("Error", status)
            self.display_results(f"Failed. Reason: {status}")

    def display_results(self, text):
        """Helper to safely update the results text area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)

# --- 4. RUN THE APPLICATION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()