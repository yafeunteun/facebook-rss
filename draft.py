#!/usr/bin/env python
# coding: utf-8


URL = "https://m.facebook.com/groups/DeepNetGroup/"


import re
import datetime
import selenium
import requests
from bs4 import BeautifulSoup

import time
from tqdm import tqdm
import dateparser
from email.utils import formatdate

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

"""
  Returns the first element found that has an attribute containing given pattern 
  params:
    - elements: an iterable containing the Webdriver elements
    - attribute: The attribute of the html element where to check for pattern
    - pattern: a string to verify if it is in attribute
  returns:
    - html element if its attribute contains the pattern
    - None else
""" 

def get_element_with_pattern_in_attribute(elements, attribute, pattern):
    els = []
    for element in elements:
        try:
            if pattern in element.get_attribute(attribute):
                els.append(element)
        except:
            pass
    return els



MAX_PAGE_FETCH = 5

fp = webdriver.FirefoxProfile()
browser = webdriver.Firefox(firefox_profile=fp)
browser.get(URL)
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

posts = []

root = browser.find_element_by_id("m_group_stories_container")
els = get_element_with_pattern_in_attribute(root.find_elements_by_tag_name("a"), "text", "Full Story")

for el in els: 
    posts.append(el.get_attribute("href"))

print(len(posts))

for i in range(MAX_PAGE_FETCH):
    wait = WebDriverWait(browser, 10)
    timeline = wait.until(EC.presence_of_element_located((By.ID, 'm_group_stories_container')))
  
    print(f"Page {i}") 
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    for span in browser.find_elements_by_tag_name("span"):
        if "See More Posts" in span.text:
            break
    span.click()

    root = browser.find_element_by_id("m_group_stories_container")
    els = get_element_with_pattern_in_attribute(root.find_elements_by_tag_name("a"), "text", "Full Story")
   
    for el in els: 
        posts.append(el.get_attribute("href"))
    print(len(posts))


articles = []
for post in tqdm(posts):
    browser.get(post)
    wait = WebDriverWait(browser, 10)
    timeline = wait.until(EC.presence_of_element_located((By.ID, 'm_story_permalink_view')))
    roi = browser.find_element_by_id('m_story_permalink_view')
    
    articles.append(roi.get_attribute("innerHTML"))
    browser.execute_script("document.getElementById('m_story_permalink_view').remove();")


## @todo replace unallowed characters in xml from title and description 

print(f"""
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
  
  <title>Facebook</title>
    <description>RSS for a Facebook group</description>
    <lastBuildDate>{formatdate(float(datetime.datetime.now().strftime('%s')))}</lastBuildDate>
    <link>https://facebook.com</link>
""")

p = re.compile("groups\/(\d+)\?view=permalink&id=(\d+)")

for idx, a in enumerate(articles):
    print("<item>")
    soup = BeautifulSoup(a)
    user_text = soup.find_all('div', {'data-ft':'{"tn":"*s"}'})[0].text
    date = soup.find_all('div', {'data-ft':'{"tn":"*W"}'})[0].text
    
    if len(user_text) > 100:
        print(f"<title>{user_text[:100]}</title>")
    else:
        print(f"<title>{user_text}</title>")
    
    print(f"<description>{user_text}</description>")
    post_url = posts[idx].split("&refid")[0][23:] # 23 to remove https://m.facebook.com/ (will be added in xml with <link> tag)
    #post_url = urllib.parse.quote(post_url)
    
    m = p.match(post_url)
    group_id, post_id = m.group(1), m.group(2)
    clean_url = f'groups/{group_id}?id={post_id}'
    print(f"<link>{clean_url}</link>")
    
    date = date.split("·")[0]
    date = dateparser.parse(date)
    date = formatdate(float(date.strftime('%s')))
    print(f"<pubDate>{date}</pubDate>")
    print("</item>")
    print()
print("""
</channel>
</rss>
""")

browser.quit()
