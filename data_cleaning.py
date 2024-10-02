import pandas as pd
import re
import json

# Load the JSON data
with open('steam_reviews.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

# Create DataFrame
df = pd.DataFrame(reviews)

# Rename columns to match the expected format
df = df.rename(columns={
    'early_access_review': 'EarlyAccess',
    'review_content': 'ReviewText',
    'thumb_text': 'Review',
    'review_length': 'ReviewLength',
    'play_hours': 'PlayHours',
    'date_posted': 'DatePosted'
})

# Clean PlayHours
df['PlayHours'] = df['PlayHours'].str.extract('([\d.]+)').astype(float)

# Clean DatePosted
df['DatePosted'] = df['DatePosted'].str.replace('Posted: ', '')

# Define month mapping
month_mapping = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}

# Extract day and month
df[['Day', 'Month']] = df['DatePosted'].str.extract(r'(\d+) (\w+)', expand=True)
df['Month'] = df['Month'].map(month_mapping)

# Create new DatePosted format
df['DatePosted'] = df['Day'] + '/' + df['Month'] + '/2024'
df['DatePosted'] = pd.to_datetime(df['DatePosted'], format='%d/%m/%Y').dt.strftime('%d-%m-%Y')

# Drop temporary columns
df = df.drop(['Day', 'Month'], axis=1)

# Save to CSV
df.to_csv('steam_reviews.csv', encoding='utf-8', sep=';', index=False)

print("Data cleaned and saved to game_reviews.csv")