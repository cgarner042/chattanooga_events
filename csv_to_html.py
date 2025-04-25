import pandas as pd
from datetime import datetime
import os

def csv_to_html():
    # Get the script's directory and set file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "data", "all_events.csv")
    output_html_path = os.path.join(script_dir, "data", "events_table.html")
    
    # Read the CSV file and ensure date column is treated as string
    df = pd.read_csv(csv_path, dtype={'date': str})
    
    # Add a simple style to make the table more readable
    html_style = """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .event-image {
            width: 340px;
            height: 227px;
            object-fit: cover;
        }
        .date-header {
            background-color: #e6f7ff;
            font-weight: bold;
        }
    </style>
    """
    
    # Convert image URLs to actual images with consistent sizing
    def make_image_html(url):
        if pd.isna(url) or url == "N/A":
            return "N/A"
        return f'<img class="event-image" src="{url}" alt="Event image">'
    
    df['image_url'] = df['image_url'].apply(make_image_html)
    
    # Sort by date (handling "N/A" and NaN dates by putting them last)
    def parse_date(x):
        if pd.isna(x) or x == "N/A":
            return datetime.max
        try:
            return datetime.strptime(x, "%m-%d")
        except ValueError:
            return datetime.max
    
    df['sort_date'] = df['date'].apply(parse_date)
    df = df.sort_values('sort_date')
    df = df.drop('sort_date', axis=1)
    
    # Generate the HTML table
    html_table = df.to_html(classes='event-table', escape=False, index=False)
    
    # Create the complete HTML document
    current_date = datetime.now().strftime("%B %d, %Y")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chattanooga Events</title>
        {html_style}
    </head>
    <body>
        <h1>Chattanooga Events</h1>
        <p>Last updated: {current_date}</p>
        {html_table}
    </body>
    </html>
    """
    
    # Save to HTML file
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML file saved to {output_html_path}")

if __name__ == "__main__":
    csv_to_html()