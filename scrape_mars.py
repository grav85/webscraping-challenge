import pandas as pd 
import requests
import time
from bs4 import BeautifulSoup as bs 
from splinter import Browser 
from selenium import webdriver
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():

    browser = init_browser()
    mars_dict={}

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')

    title = soup.find_all('div', class_='content_title')[1].text
    paragraph = soup.find_all('div', class_='article_teaser_body')[1].text

    url='https://space-facts.com/mars/'
    tables=pd.read_html(url)
    
    mars_fact=tables[0]
    mars_fact=mars_fact.rename(columns={0:"Profile",1:"Value"},errors="raise")
    mars_fact.set_index("Profile",inplace=True)

    fact_table=mars_fact.to_html()
    fact_table.replace('\n','')

    usgs_url='https://astrogeology.usgs.gov'
    url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(5)
    html=browser.html
    soup=bs(html,'html.parser')

    mars_hems=soup.find('div',class_='collapsible results')
    mars_item=mars_hems.find_all('div',class_='item')
    hemisphere_image_urls=[]

    for item in mars_item:
    
        try:
        
            hem=item.find('div',class_='description')
            title=hem.h3.text
       
            hem_url=hem.a['href']
            browser.visit(usgs_url+hem_url)
            html=browser.html
            soup=bs(html,'html.parser')
            image_src=soup.find('li').a['href']

            if (title and image_src):
            
                print('-'*50)
                print(title)
                print(image_src)
                hem_dict={
                    'title':title,
                    'image_url':image_src
                }
                hemisphere_image_urls.append(hem_dict)
        except Exception as e:
            print(e)

    mars_dict={
        "title":title,
        "paragraph":paragraph,
        "fact_table":fact_table,
        "hemisphere_images":hemisphere_image_urls
    }

    browser.quit()

    return mars_dict


