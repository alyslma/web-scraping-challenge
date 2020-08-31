#!/usr/bin/env python
# coding: utf-8

# Dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import time

# Path to driver
def init_browser():
    # Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # **NASA Mars News Site - Scrape latest news title and paragraph text**
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(1)
    site_html = browser.html
    soup = bs(site_html, 'lxml')
    news_title = soup.find_all('div', class_='content_title')[1].text
    news_p = soup.find('div', class_='article_teaser_body').text

    # **JPL Mars Space Images - Featured Image**
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(1)
    # Click on "FULL IMAGE" button
    browser.links.find_by_partial_text('FULL IMAGE').first.click()
    # "More info" button
    browser.links.find_by_partial_text('more info').first.click()
    image_html = browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(image_html, 'html.parser')
    # Find the partial url to the full size '.jpg' image
    image_url_part = soup.find('img', class_='main_image')['src']
    # Save complete url string for this image
    featured_image_url = 'https://www.jpl.nasa.gov' + image_url_part

    # **Mars Facts webpage - Planet facts**
    mars_facts_df = pd.read_html('https://space-facts.com/mars/')[0]
    mars_facts_df.columns=["Description", "Values"]
    facts_html = mars_facts_df.to_html(index=False)

    # **USGS Astrogeology site - Mars Hemispheres**
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)
    hemi_html = browser.html
    soup = bs(hemi_html, 'html.parser')
    # Create a list to hold dictionary with image url string and title for each hemisphere
    hemisphere_image_urls = []
    # Parse info for each hemisphere
    results = soup.find('div', class_='result-list')
    hemis = results.find_all('div', class_='item')
    # For loop to form and save links to each full resolution image
    for hemi in hemis:
        hemi_title = hemi.find('h3').text
        hemi_title = hemi_title.replace(' Enhanced',"") # Remove "Enhanced" from name
        link_part = hemi.find('a')['href']
        small_hemi_url = 'https://astrogeology.usgs.gov/' + link_part
        browser.visit(small_hemi_url) # Visit newly formed url
        full_reso_html = browser.html 
        hemi_soup = bs(full_reso_html, 'html.parser') 
        hemi_url_div = hemi_soup.find('div', class_='downloads')
        hemi_url = hemi_url_div.find('a')['href']
        hemisphere_image_urls.append({'title': hemi_title, 'img_url': hemi_url}) # Add dictionary to list
    
    # Store in 'mars_data' dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "facts_html": facts_html,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser
    browser.quit()

    # Return dictionary
    return mars_data