from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

game_id = 291550
url_template = "https://steamcommunity.com/app/{}/reviews/?p=1&browsefilter=mostrecent&filterLanguage=english"
url = url_template.format(game_id)

print(f"Scraping reviews from: {url}")

# Specify the path to msedgedriver.exe
edge_driver_path = "./msedgedriver.exe"

# Create a Service object
service = Service(edge_driver_path)

# Create Options object
options = Options()
options.add_argument("--lang=en-US")

# Create the Edge WebDriver instance
driver = webdriver.Edge(service=service, options=options)

def get_current_scroll_position(driver):
    return driver.execute_script("return window.pageYOffset;")

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

def get_steam_id(card):
    profile_url = card.find_element(By.XPATH, './/div[@class="apphub_friend_block"]/div/a[2]').get_attribute('href')
    steam_id = profile_url.split('/')[-2]
    return steam_id

def scrape_review_data(card):
    date_posted_element = card.find_element(By.XPATH, './/div[@class="apphub_CardTextContent"]/div[@class="date_posted"]')
    date_posted = date_posted_element.text.strip()
    
    try:
        early_access_review_element = card.find_element(By.XPATH, './/div[@class="apphub_CardTextContent"]/div[@class="early_access_review"]')
        early_access_review = early_access_review_element.text.strip()
    except NoSuchElementException:
        early_access_review = ""

    try:
        received_compensation_element = card.find_element(By.CLASS_NAME, "received_compensation").text
    except NoSuchElementException:
        received_compensation_element = ""

    card_text_content_element = card.find_element(By.CLASS_NAME, "apphub_CardTextContent")
    review_content = card_text_content_element.text.strip()
    excluded_elements = [date_posted, early_access_review, received_compensation_element]

    for excluded_element in excluded_elements:
        review_content = review_content.replace(excluded_element, "")
    review_content = review_content.replace("\n", " ").strip()

    review_length = len(review_content.replace(" ", ""))

    thumb_text = card.find_element(By.XPATH, './/div[@class="reviewInfo"]/div[contains(@class, "thumb")]').text
    play_hours = card.find_element(By.XPATH, './/div[@class="reviewInfo"]/div[contains(@class, "hours")]').text

    return {
        "date_posted": date_posted,
        "early_access_review": early_access_review,
        "received_compensation": bool(received_compensation_element),
        "review_content": review_content,
        "thumb_text": thumb_text,
        "review_length": review_length,
        "play_hours": play_hours
    }

reviews = []
steam_ids_set = set()
max_scroll_attempts = 5

try:
    driver.get(url)
    driver.maximize_window()
    last_position = get_current_scroll_position(driver)
    running = True
    while running:
        cards = driver.find_elements(By.CLASS_NAME, 'apphub_Card')

        for card in cards[-20:]:
            try:
                steam_id = get_steam_id(card)
                if steam_id not in steam_ids_set:
                    steam_ids_set.add(steam_id)
                    review = scrape_review_data(card)
                    reviews.append(review)
                    print(f"Reviews scraped: {len(reviews)}")
            except Exception as e:
                print(f"Error processing card: {e}")

        scroll_attempt = 0
        while scroll_attempt < max_scroll_attempts:
            scroll_to_bottom(driver)
            curr_position = get_current_scroll_position(driver)

            if curr_position == last_position:
                scroll_attempt += 1
                time.sleep(3)

                if scroll_attempt >= 3:
                    running = False
                    break
            else:
                last_position = curr_position
                break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print(f"Total reviews scraped: {len(reviews)}")

# You can now process or save the reviews as needed
# For example, you could save them to a JSON file:
import json
with open('steam_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, ensure_ascii=False, indent=4)
print("Reviews saved to steam_reviews.json")