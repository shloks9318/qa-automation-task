#imports 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
from deep_translator import GoogleTranslator
import re
from collections import Counter

#config
BASE_URL = "https://elpais.com/"
OPINION_URL = "https://elpais.com/opinion/"
IMAGE_FOLDER = "article_images"
MAX_ARTICLES = 5

# Create folder for images if not made already
os.makedirs(IMAGE_FOLDER, exist_ok=True)

#function for browser setup with automatic drivers
def setup_browser(browser="chrome"):

    if browser.lower() == "chrome":
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    elif browser.lower() == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    elif browser.lower() == "edge":
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        driver = webdriver.Edge(service=EdgeService(r"C:\Users\JANKI\Downloads\edgedriver_win64\msedgedriver.exe"))
    else:
        raise ValueError("Unsupported browser. Choose: chrome, firefox, or edge.")

    wait = WebDriverWait(driver, 30)
    return driver, wait

#function to open the given URL
def open_website(driver, url):
    driver.get(url)
    time.sleep(3)

#function to check the language
def check_language(driver):
    lang = driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
    print(f"Page language: {lang}")
    return lang.startswith("es")

#func to reach given section by clicking else via URL
def go_to_opinion(driver, wait):
    try:
        opinion_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(translate(text(), 'OPINION', 'opinion'), 'opin')]")
        ))
        opinion_link.click()
        print("Clicked 'Opinión' link successfully")
    except :
        print("Falling back to direct URL")
        driver.get(OPINION_URL)
    time.sleep(4)

#function to collect the article URLs
def get_article_urls(driver, wait):
    urls = []
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
    article_links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .c_t a, a.title-link")[:MAX_ARTICLES]

    for link in article_links:
        url = link.get_attribute("href")
        if url and url.startswith("https://elpais.com/opinion/"):
            urls.append(url)
    print(f"Collected {len(urls)} article URLs from list page")
    return urls

#scraping function
def scrape_single_article(driver, wait, url, idx):
    article_info = {"number": idx, "url": url}
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 300);")
    time.sleep(1)

    try:   
        try:
            title = driver.find_element(
                By.XPATH, "//meta[@property='og:title']"
            ).get_attribute("content")
        except:
            try:
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                title = "Title not found"
        article_info["title"] = title 

        #translate title to english
        try:
            translated_title = GoogleTranslator(source='auto', target='en').translate(title)
            article_info["translated_title"] = translated_title
        except:
            article_info["translated_title"] = "Translation failed"
    
        try:
            author = driver.find_element(
                By.XPATH, "//meta[@name='author']"
            ).get_attribute("content")

            if not author:
               author = driver.find_element(
                   By.XPATH, "//meta[@property='article:author']"
            ).get_attribute("content")

            article_info["author"] = author.strip()
        except:
            article_info["author"] = "No author"

        try:
            date = driver.find_element(By.CSS_SELECTOR, "time, .a_d-date").get_attribute("datetime") or \
                   driver.find_element(By.CSS_SELECTOR, "time").text.strip()
            article_info["date"] = date
        except:
            article_info["date"] = "No date"

        try:
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p, .a_c p")[:3]
            preview = " ".join(p.text.strip() for p in paragraphs if p.text.strip())[:500] + "..."
            article_info["preview"] = preview or "No preview found"
        except:
            article_info["preview"] = "No preview found"

        try:
            img_selectors = ["figure img", ".a_m-img img", ".lead_art img", "img.main-media"]
            img_url = None
            for sel in img_selectors:
                try:
                    img = driver.find_element(By.CSS_SELECTOR, sel)
                    img_url = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("data-lazy-src")
                    if img_url:
                        break
                except:
                    continue

            if img_url:
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    img_url = BASE_URL + img_url

                filename = f"{IMAGE_FOLDER}/article_{idx}_{title[:30].replace(' ', '_') if title else 'unknown'}.jpg"
                response = requests.get(img_url, stream=True, timeout=10)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    article_info["image_saved"] = filename
                else:
                    article_info["image_saved"] = "Download failed"
            else:
                article_info["image_saved"] = "No image found"
        except:
            article_info["image_saved"] = "No image"

    except:
        print(f"Error scraping article{idx}")

    return article_info

#main function
driver, wait = setup_browser("firefox")   # change to "firefox" or "edge" or "chrome" to test
open_website(driver, BASE_URL)
check_language(driver)
go_to_opinion(driver, wait)
article_urls = get_article_urls(driver, wait)
articles = []

for idx, url in enumerate(article_urls, 1):
    article = scrape_single_article(driver, wait, url, idx)
    articles.append(article)
    print(f"Article {idx} scraped")

print("\nFinal Scraped Articles:")
for art in articles:
    print(f"\nArticle {art['number']}:")
    print(f"Title (ES): {art.get('title', 'N/A')}")
    print(f"Title (EN): {art.get('translated_title', 'N/A')}")
    print(f"URL: {art['url']}")
    print(f"Author/Date: {art.get('author', 'N/A')} / {art.get('date', 'N/A')}")
    print(f"Preview: {art.get('preview', 'N/A')[:150]}...")
    print(f"Image: {art.get('image_saved', 'No image')}")

#translation
all_translated_titles = [art.get("translated_title", "") for art in articles]

#combine all titles into one string
combined_text = " ".join(all_translated_titles).lower()

#remove punctuation and keep only words
words = re.findall(r"\b[a-zA-Z]+\b", combined_text)

#count word frequency
word_counts = Counter(words)
print("\nRepeated Words more than twice in translated articles combined:")

found = False
for word, count in word_counts.items():
    if count > 2:
        print(f"{word} → {count} times")
        found = True
if not found:
    print("No words repeated more than twice.")

#driver.execute_script(
    'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed","reason": "All articles scraped successfully"}}'
#)
driver.quit()
print("Done!")
