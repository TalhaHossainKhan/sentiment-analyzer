# Introduction

This project scrapes user reviews for the game Brawlhalla from Steam, processes the data, and generates a word cloud to visualize review sentiment.

## Project Overview
The project consists of three main components:

1. Web scraping using NodeJS and PuppeteerJS
2. Data cleaning with Python
3. Text analysis and visualization using NLTK and WordCloud
   
### Web Scraping
I used NodeJS with PuppeteerJS to scrape Brawlhalla reviews from Steam. Here's a brief overview of the process:

1. Set up a NodeJS project and installed PuppeteerJS
2. Created a script to navigate to the Brawlhalla Steam page
3. Implemented logic to scroll through review pages and extract data
4. Saved the scraped reviews as a JSON file
   
### Data Cleaning
After scraping, I used Python to clean and prepare the data:

1. Loaded the JSON file into a pandas DataFrame
2. Removed unnecessary columns and handled missing values
3. Cleaned text data by removing special characters and formatting
4. Exported the cleaned data as a CSV file
   
### Text Analysis and Visualization
Finally, I used NLTK and WordCloud to analyze the review sentiment:

1. Tokenized and processed the review text using NLTK
2. Performed sentiment analysis to categorize reviews as positive or negative
3. Generated a word cloud to visualize the most common terms in polarized reviews
   
## Results
The resulting word cloud provides a visual representation of the most frequently used words in Brawlhalla reviews, highlighting the polarized opinions of players. This visualization helps quickly identify common themes and sentiments expressed by the game's community.

![World cloud picture](https://github.com/TalhaHossainKhan/sentiment-analyzer/blob/main/wordcloud.png)

## Future Improvements

+ Implement more advanced sentiment analysis techniques
+ Create separate word clouds for positive and negative reviews
+ Analyze review trends over time
