import pandas as pd
import requests
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage

# Read CSV with URLs
df = pd.read_csv('/data/all_events.csv')

# Create a new Excel workbook
wb = Workbook()
ws = wb.active

# Write headers
ws.append(list(df.columns) + ['Embedded Image'])

# Function to download and resize image
def get_image(url, max_size=(200, 200)):
    try:
        response = requests.get(url, timeout=10)
        img_data = BytesIO(response.content)
        img = XLImage(img_data)
        
        # Resize if needed
        if img.width > max_size[0] or img.height > max_size[1]:
            img.width, img.height = max_size
        return img
    except:
        return None

# Process each row
for index, row in df.iterrows():
    # Write original data
    ws.append(list(row))
    
    # Add image if URL exists
    if pd.notna(row['image_url']):  # change 'image_url' to your column name
        img = get_image(row['image_url'])
        if img:
            cell_ref = f'L{index+2}'  # Column L, adjust as needed
            ws.add_image(img, cell_ref)

# Save the workbook
wb.save('/data/all_events.xlsx')
print("Excel file with embedded images created successfully!")