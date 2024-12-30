import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from bs4 import BeautifulSoup
import random
import time
import csv
import re

def get_crew_data(imdb_id, driver):

    """
    Fetches the crew data including directors, writers, and cast for a given IMDb ID.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get crew data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing lists of directors, writers, and cast members. Each key maps
              to a list of names, or 'N/A' if data is unavailable.
    """
    
    crew_link = f'https://www.imdb.com/title/{imdb_id}/fullcredits'
    crew = {
        "director": 'N/A',
        "writer": 'N/A',
        "cast": 'N/A'
    }

    if driver:
        # Use Selenium
        driver.get(crew_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(crew_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return crew
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')
    
    director_data = []
    writer_data = []
    cast_data=[]
    
    director_header = soup.find('h4', id='director', class_='dataHeaderWithBorder')
    if director_header:
        director_table = director_header.find_next_sibling('table', class_='simpleTable simpleCreditsTable')
        if director_table:
            for row in director_table.find_all('tr'):
                name_tag = row.find('td', class_='name')
                if name_tag:
                    director_name = name_tag.text.strip()
                    director_data.append(director_name)

    writer_header = soup.find('h4', id='writer', class_='dataHeaderWithBorder')
    if writer_header:
        writer_table = writer_header.find_next_sibling('table', class_='simpleTable simpleCreditsTable')
        if writer_table:
            for row in writer_table.find_all('tr'):
                name_tag = row.find('td', class_='name')
                if name_tag:
                    writer_name = name_tag.text.strip()
                    writer_data.append(writer_name)

    cast_table = soup.find('table', class_='cast_list')
    if cast_table:
        for row in cast_table.find_all('tr', class_=['odd', 'even']):
            cells = row.find_all('td')
            if len(cells) > 1:
                name_cell = cells[1]
                name_tag = name_cell.find('a')
                if name_tag:
                    cast_name = name_tag.get_text(strip=True)
                    cast_data.append(cast_name)

    crew["director"] = director_data if director_data else 'N/A'
    crew["writer"] = writer_data if writer_data else 'N/A'
    crew["cast"] = cast_data if cast_data else 'N/A'

    return crew

def get_technical_data(imdb_id, driver):

    """
    Fetches the technical data for a given IMDb ID, including runtime, sound mix, and color.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get technical data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the technical data with keys 'runtime', 'sound_mix', and 'color'.
              Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    technical_link = f'https://www.imdb.com/title/{imdb_id}/technical'
    technical_data = {
        "runtime": 'N/A',
        "sound_mix": 'N/A',
        "color": 'N/A'
    }

    if driver:
        # Use Selenium
        driver.get(technical_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(technical_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return technical_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')
    
    runtime_tag = soup.find('li', class_='ipc-metadata-list__item', id = 'runtime')
    if runtime_tag:
        runtime_spec = runtime_tag.find('li', class_= 'ipc-inline-list__item')
        runtime = runtime_spec.find('span', class_='ipc-metadata-list-item__list-content-item').get_text(strip=True) if runtime_tag else 'N/A' 
        technical_data["runtime"] = runtime
        

    sound_mix = []
    sound_mix_tag = soup.find('li', class_='ipc-metadata-list__item', id = 'soundmixes')
    if sound_mix_tag:
        sound_mix_spec = sound_mix_tag.find_all('li', class_= 'ipc-inline-list__item')
        for spec in sound_mix_spec:
            sound_mix_name = spec.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            for name in sound_mix_name:
                sound_mix.append(name.get_text(strip=True))
        technical_data["sound_mix"] = sound_mix

    color_tag = soup.find('li', class_='ipc-metadata-list__item', id = 'colorations')
    if color_tag:
        color_spec = color_tag.find('li', class_= 'ipc-inline-list__item')
        color = color_spec.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').get_text(strip=True) if color_tag else 'N/A'
        technical_data["color"] = color
    
    return technical_data

def get_parent_guide_data(imdb_id, driver):

    """
    Fetches the parental guide data for a given IMDb ID, including severity ratings and vote counts for
    Sex & Nudity, Violence & Gore, Profanity, Alcohol, Drugs & Smoking, and Frightening & Intense Scenes.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get parental guide data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the parental guide data, where each key is a category and the
              value is a dictionary with keys 'Severity', 'Number of vote:', and 'Total votes:'.
              Each of these keys maps to its respective data or 'N/A' if data is unavailable.
    """
    
    parent_guide_link = f'https://www.imdb.com/title/{imdb_id}/parentalguide'
    parent_guide_data = {
        "Sex & Nudity": {
            "Severity": "N/A",
            "Number of vote:": "N/A",
            "Total votes:": "N/A",
        },
        "Violence & Gore": {
            "Severity": "N/A",
            "Number of vote:": "N/A",
            "Total votes": "N/A",
        },
        "Profanity": {
            "Severity": "N/A",
            "Number of vote:": "N/A",
            "Total votes": "N/A",
        },
        "Alcohol, Drugs & Smoking": {
            "Severity": "N/A",
            "Number of vote:": "N/A",
            "Total votes": "N/A",
        },
        "Frightening & Intense Scenes": {
            "Severity": "N/A",
            "Number of vote:": "N/A",
            "Total votes": "N/A",
        }
    }

    if driver:
        # Use Selenium
        driver.get(parent_guide_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(parent_guide_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return parent_guide_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')

    sections = soup.find_all('section', class_='ipc-page-section ipc-page-section--base')
    if sections:
        for section in sections:
            feature_title_tag = section.find('h3', class_='ipc-title__text')
            if feature_title_tag:
                feature_name = feature_title_tag.text.strip()

                if feature_name in parent_guide_data:
                    # Extract severity
                    severity_tag = section.find('div', class_='ipc-signpost__text')
                    severity = severity_tag.text.strip() if severity_tag else 'N/A'
                    parent_guide_data[feature_name]["Severity"] = severity if severity else 'N/A'

                    # Extract vote counts
                    vote_text_tag = section.find('span', {'data-testid': 'severity-summary'})
                    if vote_text_tag:
                        vote_text = vote_text_tag.text.strip()
                        vote_split = vote_text.split(' of ')
                        if len(vote_split) == 2:
                            number_of_votes = int(vote_split[0].replace(",", ""))
                            total_votes = int(vote_split[1].split()[0].replace(",", ""))
                        else:
                            number_of_votes = 'N/A'
                            total_votes = 'N/A'
                    else:
                        number_of_votes = 'N/A'
                        total_votes = 'N/A'

                    parent_guide_data[feature_name]["Number of vote:"] = number_of_votes if number_of_votes else 'N/A'
                    parent_guide_data[feature_name]["Total votes:"] = total_votes if total_votes else 'N/A'

    return parent_guide_data


def get_basic_data(imdb_id, driver): 

    """
    Fetches the basic data for a given IMDb ID, including type, year, certificate, duration, and genre.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get basic data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the basic data with keys 'type', 'year', 'certificate', 'duration', and 'genre'.
              Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    basic_data_link = f'https://www.imdb.com/title/{imdb_id}/'
    basic_data = {
        "Type": "N/A",
        "Year": "N/A",
        "Certificate": "N/A",
        "Duration": "N/A",
        "Genre": []
    }

    if driver:
        # Use Selenium
        driver.get(basic_data_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(basic_data_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return basic_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')

    IMDB_TYPES = {
    "Movie", "TV Series", "Short", "TV Episode", "TV Mini Series",
    "TV Movie", "TV Special", "TV Short", "Video Game", "Video",
    "Music Video", "Podcast Series", "Podcast Episode"
    }

    basic_data_tag = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt')

    if basic_data_tag:
        items = basic_data_tag.find_all('li', class_='ipc-inline-list__item')
        for item in items:
            text = item.get_text(strip=True)

            if text in IMDB_TYPES:
                basic_data["Type"] = text
            elif re.search(r"\d{4}(–\d{4})?", text):
                basic_data["Year"] = text
            elif "TV-" in text or text in ["PG", "R", "G", "PG-13"]:
                basic_data["Certificate"] = text
            elif re.search(r"\d+h\s*\d*m|\d+m", text):
                basic_data["Duration"] = text

    genre_tags = soup.find_all('div', class_='ipc-chip-list--baseAlt ipc-chip-list ipc-chip-list--nowrap sc-3ac15c8d-4 eFIDNe')
    genres = []
    if genre_tags:
        for genre_tag in genre_tags:  # Iterate through each tag in the list
            genre_as = genre_tag.find_all('a', class_='ipc-chip ipc-chip--on-baseAlt')  
            for genre_a in genre_as:
                genre_span = genre_a.find('span', class_='ipc-chip__text')  
                if genre_span:
                    genres.append(genre_span.get_text(strip=True)) 

    basic_data["Genre"] = genres if genres else "N/A"

    return basic_data

def get_detail(imdb_id, driver):

    """
    Fetches the details data including release date, country of origin, languages, production companies, filming locations, watchlist count, and critic reviews for a given IMDb ID.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get details data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the details data with keys 'Release Date', 'Country of Origin', 'Languages', 'Production Companies', 'Filming Locations', 'Watchlist Count', and 'Critic Reviews'. Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    detail_link = f'https://www.imdb.com/title/{imdb_id}/'
    details = {
        "Release Date": "N/A",
        "Country of Origin": "N/A",
        "Languages": "N/A",
        "Production Companies": "N/A",
        "Filming Locations": "N/A"
    }

    if driver:
        # Use Selenium
        driver.get(detail_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(detail_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return details
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')

    details_section_tag = soup.find('section', {'data-testid': 'Details'})

    if details_section_tag:
        release_date_tag = details_section_tag.find('li', {'data-testid': 'title-details-releasedate'})
        if release_date_tag:
            release_date_tag_li = release_date_tag.find_all('a', class_= 'ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            if release_date_tag_li:
                details["Release Date"] = release_date_tag_li[0].get_text(strip=True)

        # Country
        country_tag = details_section_tag.find_all('li', {'data-testid': 'title-details-origin'})
        country = []
        if country_tag:
            for country_tag in country_tag:
                country_a_tag = country_tag.find_all('a', class_= 'ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            for ca_tag in country_a_tag:
                country.append(ca_tag.get_text(strip=True))
            details["Country of Origin"] = country

        # Language
        language_tags = details_section_tag.find_all('li', {'data-testid': 'title-details-languages'})
        languages = []
        if language_tags:
            for language_tag in language_tags:
                language_a_tag = language_tag.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            for la_tag in language_a_tag:
                languages.append(la_tag.get_text(strip=True))
            details["Languages"] = languages

        # Production Companies
        production_tags = details_section_tag.find_all('li', {'data-testid': 'title-details-companies'})
        production_companies = []
        if production_tags:
            for production_tag in production_tags:
                production_a_tag = production_tag.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            for pa_tag in production_a_tag:
                production_companies.append(pa_tag.get_text(strip=True))
            details["Production Companies"] = production_companies

        # Filming Locations
        filming_location_tags = details_section_tag.find_all('li', {'data-testid': 'title-details-filminglocations'})
        filming_locations = []
        if filming_location_tags:
            for location_tag in filming_location_tags:
                location_a_tag = location_tag.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
            for la_tag in location_a_tag:
                filming_locations.append(la_tag.get_text(strip=True))
            details["Filming Locations"] = filming_locations

    return details

def get_box_office_data(imdb_id, driver):

    """
    Fetches the box office data for a given IMDb ID, including budget and worldwide gross.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get box office data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the box office data with keys 'Budget' and 'Gross Worldwide'.
              Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    box_office_link = f'https://www.imdb.com/title/{imdb_id}/'
    box_office_data = {
        "Budget": "N/A",
        "Gross Worldwide": "N/A"
    }

    if driver:
        # Use Selenium
        driver.get(box_office_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(box_office_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return box_office_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')
    
    box_office_section = soup.find('section', {'data-testid': 'BoxOffice'})

    if box_office_section:
        budget_tag = box_office_section.find('li', {'data-testid': 'title-boxoffice-budget'})
        if budget_tag:
            budget_tag_li = budget_tag.find('li', class_= 'ipc-inline-list__item')
            if budget_tag_li:
                budget_tag_span = budget_tag_li.find('span', class_= 'ipc-metadata-list-item__list-content-item')
                if budget_tag_span:
                    budget_value = budget_tag_span.get_text(strip=True)
                    box_office_data["Budget"] = budget_value

        
        gross_tag = box_office_section.find('li', {'data-testid': 'title-boxoffice-cumulativeworldwidegross'})
        if gross_tag:
            gross_tag_li = gross_tag.find('li', class_= 'ipc-inline-list__item')
            if gross_tag_li:
                gross_tag_span = gross_tag_li.find('span', class_= 'ipc-metadata-list-item__list-content-item')
                if gross_tag_span:
                    gross_value = gross_tag_span.get_text(strip=True)
                    box_office_data["Gross Worldwide"] = gross_value

    return box_office_data

def get_scores(imdb_id, driver):

    """
    Fetches the scores data for a given IMDb ID, including watchlist count, critic reviews, and Metascore.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get scores data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the scores data with keys 'Watchlist Count', 'Critic Reviews', and 'Metascore'.
              Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    scores_link = f'https://www.imdb.com/title/{imdb_id}/'
    scores_data = {
        "Watchlist Count": "N/A",
        "Critic Reviews": "N/A",
        "Metascore": "N/A"
    }

    if driver:
        # Use Selenium
        driver.get(scores_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(scores_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return scores_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')

    title_watchlist_tag = soup.find('div', class_='sc-11817e04-1 bTLZoL')
    if title_watchlist_tag:
        watchlist_tag = title_watchlist_tag.find('div', {'data-testid': 'tm-box-wl-count'})
        if watchlist_tag:
            watchlist_count_str = watchlist_tag.get_text(strip=True)
            if "Added by" in watchlist_count_str:
                watchlist_count_str_num = watchlist_count_str.split(" ")[2]

                if watchlist_count_str_num.endswith("K"):
                    watchlist_count = int(float(watchlist_count_str_num[:-1]) * 1_000)
                elif watchlist_count_str_num.endswith("M"):
                    watchlist_count = int(float(watchlist_count_str_num[:-1]) * 1_000_000)
                else:
                    watchlist_count = int(watchlist_count_str_num)
                scores_data["Watchlist Count"] = watchlist_count
                
    reviews_tag = soup.find('li', class_='ipc-inline-list__item sc-b782214c-1 flXrcD')
    if reviews_tag:
        score_tag = reviews_tag.find('span', class_='score')
        if score_tag:
            critic_reviews_score_str = score_tag.get_text(strip=True)

            if critic_reviews_score_str.endswith("K"):
                critic_reviews_score = int(float(critic_reviews_score_str[:-1]) * 1_000)
            elif critic_reviews_score_str.endswith("M"):
                critic_reviews_score = int(float(critic_reviews_score_str[:-1]) * 1_000_000)
            elif critic_reviews_score_str.isdigit():
                critic_reviews_score = int(critic_reviews_score_str)

            scores_data["Critic Reviews"] = critic_reviews_score

    metascore_tag = soup.find('span', class_='sc-b0901df4-0 bXIOoL metacritic-score-box')
    if metascore_tag:
        metascore = metascore_tag.get_text(strip=True) 
        if metascore.isdigit():
            metascore = int(metascore)

        scores_data["Metascore"] = metascore

    return scores_data

def get_rating_and_popularity(imdb_id, driver):

    """
    Fetches the rating, number of votes, popularity score, and popularity delta for a given IMDb ID.

    Args:
        imdb_id (str): The IMDb ID of the title for which to get rating and popularity data.
        driver (webdriver): Selenium WebDriver instance for browser automation. If provided, Selenium
                            is used to fetch the page source. Otherwise, 'requests' is used.

    Returns:
        dict: A dictionary containing the rating and popularity data with keys 'Rating', 'Number of votes',
              'Popularity', and 'Popularity Delta'. Each key maps to its respective data or 'N/A' if data is unavailable.
    """
    
    rating_and_popularity_link = f'https://www.imdb.com/title/{imdb_id}/'
    rating_and_popularity_data = {
        "Rating": "N/A",
        "Number of votes": "N/A",
        "Popularity": "N/A",
        "Popularity Delta": "N/A"
    }

    if driver:
        # Use Selenium
        driver.get(rating_and_popularity_link)
        time.sleep(3)
        page_source = driver.page_source
    else:
        # Use requests
        headers = {
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(rating_and_popularity_link, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page for IMDb ID {imdb_id} with requests. Status code: {response.status_code}")
            return rating_and_popularity_data
        page_source = response.text

    soup = BeautifulSoup(page_source, 'html.parser')

    imdb_rating = None
    number_of_votes_str = None
    popularity_score = None
    popularity_delta = None

    # Rating extraction
    rating_div = soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
    if rating_div:
        rating_span = rating_div.find('span', class_='sc-d541859f-1')
        if rating_span:
            imdb_rating = rating_span.get_text(strip=True)

    # Number of votes extraction
    number_of_votes_div = soup.find('div', class_='sc-d541859f-3 dwhNqC')
    if number_of_votes_div:
        number_of_votes_str = number_of_votes_div.get_text(strip=True)
    if number_of_votes_str:
        if number_of_votes_str.endswith("K"):
            number_of_votes = int(float(number_of_votes_str[:-1]) * 1_000)
        elif number_of_votes_str.endswith("M"):
            number_of_votes = int(float(number_of_votes_str[:-1]) * 1_000_000)
        else:
            number_of_votes = int(number_of_votes_str)
    else:
        number_of_votes = "N/A"

    # Popularity score extraction
    popularity_score_div = soup.find('div', {'data-testid': 'hero-rating-bar__popularity__score'})
    if popularity_score_div:
        popularity_score = popularity_score_div.get_text(strip=True)

    # Popularity delta extraction
    popularity_delta_div = soup.find('div', {'data-testid': 'hero-rating-bar__popularity__delta'})
    if popularity_delta_div:
        popularity_delta = popularity_delta_div.get_text(strip=True)

    # Update dictionary with extracted data
    rating_and_popularity_data["Rating"] = imdb_rating if imdb_rating else "N/A"
    rating_and_popularity_data["Number of votes"] = number_of_votes if number_of_votes else "N/A"
    rating_and_popularity_data["Popularity"] = popularity_score if popularity_score else "N/A"
    rating_and_popularity_data["Popularity Delta"] = popularity_delta if popularity_delta else "N/A"

    return rating_and_popularity_data

def crawl_data_and_save(imdb_id, driver, output_file):
    
    
    """
    Crawls and saves detailed IMDb data for a specific IMDb ID to a CSV file.

    Args:
        imdb_id (str): The IMDb ID of the title for which to crawl data.
        driver (webdriver): Selenium WebDriver instance for browser automation.
        output_file (str): Path to the CSV file where crawled data will be saved.

    Notes:
        This function collects various types of data, including crew, technical
        specifications, parental guide, basic information, detailed information,
        scores, box office, and rating and popularity data. The collected data
        is then flattened and saved to the specified CSV file. If the file exists,
        data is appended; otherwise, a new file is created with headers.
    """
    # Crawl the data for the given IMDb ID
    crew_data = get_crew_data(imdb_id, driver)
    technical_data = get_technical_data(imdb_id, driver)
    parent_guide_data = get_parent_guide_data(imdb_id, driver)
    basic_data = get_basic_data(imdb_id, driver)
    detail_data = get_detail(imdb_id, driver)
    score_data = get_scores(imdb_id, driver)
    box_office_data = get_box_office_data(imdb_id, driver)
    rating_and_popularity_data = get_rating_and_popularity(imdb_id, driver)

    # Flatten data for CSV output
    flattened_data = {
        "IMDb ID": imdb_id,
        "Director": "|".join(crew_data["director"]) if isinstance(crew_data["director"], list) else crew_data["director"],
        "Writer": "|".join(crew_data["writer"]) if isinstance(crew_data["writer"], list) else crew_data["writer"],
        "Cast": "|".join(crew_data["cast"]) if isinstance(crew_data["cast"], list) else crew_data["cast"],
        "Runtime": technical_data["runtime"],
        "Sound Mix": "|".join(technical_data["sound_mix"]),
        "Color": technical_data["color"],
        "Parental Guide": str(parent_guide_data),
        "Type": basic_data["Type"],
        "Year": basic_data["Year"],
        "Certificate": basic_data["Certificate"],
        "Duration": basic_data["Duration"],
        "Genre": "|".join(basic_data["Genre"]),
        "Release Date": detail_data["Release Date"],
        "Country of Origin": "|".join(detail_data["Country of Origin"]) if isinstance(detail_data["Country of Origin"], list) else detail_data["Country of Origin"],
        "Languages": "|".join(detail_data["Languages"]) if isinstance(detail_data["Languages"], list) else detail_data["Languages"],
        "Production Companies": "|".join(detail_data["Production Companies"]) if isinstance(detail_data["Production Companies"], list) else detail_data["Production Companies"],
        "Filming Locations": "|".join(detail_data["Filming Locations"]) if isinstance(detail_data["Filming Locations"], list) else detail_data["Filming Locations"],
        "Watchlist Count": score_data["Watchlist Count"],
        "Critic Reviews": score_data["Critic Reviews"],
        "Metascore": score_data["Metascore"],
        "Budget": box_office_data["Budget"],
        "Gross Worldwide": box_office_data["Gross Worldwide"],
        "Rating" : rating_and_popularity_data["Rating"],
        "Number of votes": rating_and_popularity_data["Number of votes"],
        "Popularity": rating_and_popularity_data["Popularity"],
        "Popularity Delta" : rating_and_popularity_data["Popularity Delta"]
    }
    
    # Convert to DataFrame for CSV export
    df = pd.DataFrame([flattened_data])

    # Append data to the output file
    try:
        # If file exists, append without writing the header
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            df.to_csv(f, index=False, header=f.tell() == 0, encoding='utf-8')
    except FileNotFoundError:
        # If file doesn't exist, write the header
        df.to_csv(output_file, index=False, header=True, encoding='utf-8')

    print(f"Data for IMDb ID {imdb_id} saved to {output_file}")

def extract_all_imdb_ids_for_selenium(imdb_url, driver, crawling_amount, existing_ids_file):
    # Load existing IMDb IDs from the file
    """
    Extracts IMDb IDs from the given IMDb URL using Selenium.

    Args:
    -----------
    imdb_url : str
        The URL of the IMDb page to extract IDs from.
    driver : webdriver
        A Selenium WebDriver instance for browser automation.
    crawling_amount : int
        The number of IMDb IDs to extract.
    existing_ids_file : str
        The file path to save the extracted IMDb IDs.

    Returns:
    -------
    list
        A list of extracted IMDb IDs.
    """
    existing_ids = set()
    try:
        with open(existing_ids_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                existing_ids.add(row[0])
    except FileNotFoundError:
        print(f"No existing file found. Starting fresh.")

    imdb_ids = []
    ids_since_last_save = 0  # Counter for incremental saving
    retries = 5  # Retry limit for transient errors
    crawled_web = 0  # Track pages processed

    # Navigate to the IMDb URL
    driver.get(imdb_url)
    driver.set_script_timeout(30)
    time.sleep(3)  # Allow initial load

    while crawled_web < crawling_amount:
        try:
            try:
                # Find the "50 more" button using XPath
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ipc-see-more__text') and text()='50 more']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                time.sleep(random.uniform(3, 6))
                driver.execute_script("arguments[0].click();", show_more_button)
                time.sleep(random.uniform(3, 6))  # Wait for new content to load
            except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException):
                print("No more '50 more' button found or timeout occurred.")
                break

            # Parse the current page content
            for attempt in range(retries):
                try:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    break
                except WebDriverException as e:
                    print(f"Retry {attempt + 1}/{retries} after WebDriverException: {e}")
                    time.sleep(random.uniform(3, 6))
            else:
                print("Failed to fetch page source after retries. Exiting loop.")
                break

            movie_links = soup.select('a[href^="/title/tt"]')
            for link in movie_links:
                href = link.get('href')
                imdb_id = href.split('/')[2]
                if imdb_id not in existing_ids and imdb_id not in imdb_ids:
                    imdb_ids.append(imdb_id)
                    ids_since_last_save += 1

            # Incremental saving every 50 IDs
            if ids_since_last_save >= 50:
                with open(existing_ids_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for imdb_id in imdb_ids[-ids_since_last_save:]:  # Save only new IDs
                        writer.writerow([imdb_id])
                print(f"Saved 50 new IDs. Total saved: {len(existing_ids) + len(imdb_ids)}")
                ids_since_last_save = 0  # Reset counter
                crawled_web += 1

            # Clear the BeautifulSoup object to release memory
            soup.decompose()
            
        except WebDriverException as e:
            print(f"WebDriverException encountered: {e}. Retrying...")
            time.sleep(random.uniform(3, 6))
            continue

        except Exception as e:
            print(f"Unexpected error: {e}. Stopping crawl.")
            break

    # Final save for any remaining IDs
    if ids_since_last_save > 0:
        with open(existing_ids_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for imdb_id in imdb_ids[-ids_since_last_save:]:
                writer.writerow([imdb_id])
        print(f"Final save: {ids_since_last_save} IDs.")

    print(f"Total new IDs added: {len(imdb_ids)}")
    return imdb_ids


def get_imdb_ids(output_file_ids, number_of_movies):
    """
    Extracts IMDb IDs from the IMDb search page and saves them to a CSV file.

    Args:
        output_file_ids (str): The file path to save the IMDb IDs to.
        number_of_movies (int): The number of movies to extract IDs for.

    Notes:
        Uses Selenium to load the page and extract IDs.
        The number of '50 more' button clicks is determined by the number of movies to extract IDs for.
        The extracted IMDb IDs are saved to the specified output file in a CSV format with a single column 'IMDb ID'.
    """
    movie_url = "https://www.imdb.com/search/title/?title_type=feature"

    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disk-cache-dir=/tmp/cache-dir")
    options.add_argument("--disk-cache-size=1073741824")
    options.add_argument("--renderer-process-limit=10")
    options.add_argument("--max-active-webgl-contexts=16")

    try:
        # Initialize Selenium WebDriver
        driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(60)

        # Calculate the number of times to load more movies
        crawling_amount_int = number_of_movies // 50 
        crawling_amount_float = number_of_movies % 50
        crawling_amount = crawling_amount_int + 1 if crawling_amount_float > 0 else crawling_amount_int

        # Extract IMDb IDs using the updated function
        new_imdb_ids = extract_all_imdb_ids_for_selenium(movie_url, driver, crawling_amount, output_file_ids)

        # Print results
        print(f"New IMDb IDs added: {len(new_imdb_ids)}")
        print(f"Saved IMDb IDs to {output_file_ids}")

    finally:
        # Ensure the WebDriver is closed
        if driver:
            driver.quit()


def run_crawling(number_of_movies, imdb_ids_file, output_file_data, method, driver=None, start_time=None, max_seconds=None):
    
    """
    Crawls data for each IMDb ID from the specified file and saves it to the output file.

    Args:
        number_of_movies (int): The number of movies to crawl data for.
        imdb_ids_file (str): The file path containing IMDb IDs to crawl.
        output_file_data (str): The file path to save the crawled data.
        method (str): The method to use for web crawling, either 'selenium' or 'requests'.
        driver (webdriver, optional): Selenium WebDriver instance for browser automation. Required if method is 'selenium'.
        start_time (float, optional): The start time of the crawling process.
        max_seconds (float, optional): The maximum number of seconds to run the crawling process.

    Notes:
        The function will crawl data up to the specified number of movies or until the time limit is reached.
        If using 'selenium', the WebDriver instance is closed at the end.
    """
    # Crawl data for each IMDb ID
    imdb_ids = pd.read_csv(imdb_ids_file)['IMDb ID'].astype(str).tolist()
    number_now = 0
    for imdb_id in imdb_ids:
        elapsed_time = time.time() - start_time
        print(f"Elapsed time for run_crawling: {elapsed_time:.2f} seconds")
        print(f"Max time: {max_seconds:.2f} seconds")
        if max_seconds and elapsed_time >= max_seconds:
            print("Time limit reached inside web_crawling.")
            break
        if number_now >= number_of_movies:
            break
        number_now += 1
        print(f"Processing IMDb ID {imdb_id} ({number_now}/{number_of_movies})")
        crawl_data_and_save(imdb_id, driver, output_file_data)
        time.sleep(3)

    if method == 'selenium' and driver:
        driver.quit()

def get_remaining_imdb_ids(imdb_ids_file, crawled_data_file):

    """
    Returns a list of IMDb IDs that have not yet been crawled.

    Args:
        imdb_ids_file (str): The file path containing IMDb IDs to crawl.
        crawled_data_file (str): The file path containing crawled IMDb data.

    Returns:
        list: A list of IMDb IDs that have not yet been crawled.

    Notes:
        The function reads both input files and finds the difference between the two (IDs not yet crawled).
        The function prints the total number of IMDb IDs, the number of crawled IMDb IDs, and the number of remaining IMDb IDs to crawl.
    """
    imdb_ids_df = pd.read_csv(imdb_ids_file)
    crawled_data_df = pd.read_csv(crawled_data_file, encoding='ISO-8859-1')

    if imdb_ids_df.empty:
        print("No IMDb IDs found in the input file.")
        return []

    if crawled_data_df.empty:
        print("No crawled IMDb data found in the input file.")
        return []
    
    all_imdb_ids = set(imdb_ids_df['IMDb ID'].astype(str))
    crawled_imdb_ids = set(crawled_data_df['IMDb ID'].astype(str))

    # Find the difference (IDs not yet crawled)
    remaining_imdb_ids = list(all_imdb_ids - crawled_imdb_ids)

    print(f"Total IMDb IDs: {len(all_imdb_ids)}")
    print(f"Crawled IMDb IDs: {len(crawled_imdb_ids)}")
    print(f"Remaining IMDb IDs to crawl: {len(remaining_imdb_ids)}")

    return remaining_imdb_ids 

def continue_crawling(imdb_ids_file, crawled_data_file, driver, start_time=None, max_seconds=None):

    """
    Continue crawling IMDb data for the remaining IMDb IDs.

    Parameters:
    ------------
    imdb_ids_file : str
        The file path containing IMDb IDs to crawl.
    crawled_data_file : str
        The file path containing crawled IMDb data.
    driver : webdriver
        Selenium WebDriver instance for browser automation.
    start_time : float, optional
        The start time of the crawling process.
    max_seconds : float, optional
        The maximum number of seconds to run the crawling process.

    Returns:
    -------
    list
        A list of IMDb IDs that failed to be crawled.

    Notes:
    ------
    The function will continue to run the web_crawling function until the time limit is reached.
    If an error occurs during crawling, the function will append the IMDb ID to the error list and continue.
    The function will also print the elapsed time and the maximum time allowed.
    If the time limit is reached, the function will break and return the error list.
    """
    remaining_ids = get_remaining_imdb_ids(imdb_ids_file, crawled_data_file)
    error_id = []
    count = 0
    first_time = True
    for imdb_id in remaining_ids:
        elapsed_time = time.time() - start_time
        print(f"Elapsed time for continue_crawling: {elapsed_time:.2f} seconds")
        print(f"Max time: {max_seconds:.2f} seconds")
        if max_seconds and elapsed_time >= max_seconds:
            print("Time limit reached inside web_crawling.")
            break

        if first_time:
            first_time = False
            error_id.append(imdb_id)
        else:
            try:
                print(f"Remaining IMDb IDs to crawl: {len(remaining_ids) - count}")
                print(f"Processing IMDb ID {imdb_id}")
                crawl_data_and_save(imdb_id, driver, crawled_data_file)
            except Exception as e:
                error_id.append(imdb_id)
                print(f"Error processing IMDb ID {imdb_id}: {e}")
            count += 1
            time.sleep(3)
    if driver:
        driver.quit()
    return error_id

def web_crawling(number_of_movies=1000, method='selenium', start_time=None, max_seconds=None):

    """
    Crawls IMDb data for a specified number of movies, extracting IMDb IDs and saving detailed data.

    Parameters:
    -----------
    number_of_movies : int, optional
        The total number of movies to crawl data for (default: 1000).
    method : str, optional
        The method to use for web crawling, either 'selenium' or 'requests' (default: 'selenium').

    Returns:
    -------
    list
        A list of IMDb IDs that failed to be crawled.

    Notes:
    ------
    The function writes the IMDb IDs to 'imdb_ids_request.csv' and crawled data to 'crawled_web_data_request.csv'.
    If using 'selenium', a WebDriver instance is created and closed at the end.
    """

    list_of_error_imdb_ids = []
    imdb_ids_file = "imdb_ids_request.csv"
    crawled_data_file = "crawled_web_data_request.csv"
    bias = 0
    success = False
    column_data = [
        "IMDb ID", "Director", "Writer", "Cast", "Runtime", "Sound Mix", "Color",
        "Parental Guide", "Type", "Year", "Certificate", "Duration", "Genre",
        "Release Date", "Country of Origin", "Languages", "Production Companies",
        "Filming Locations", "Watchlist Count", "Critic Reviews", "Metascore", "Budget",
        "Gross Worldwide", "Rating", "Number of votes", "Popularity", "Popularity Delta"
    ]

    column_id = ["IMDb ID"]
    # Initialize crawled_data_file
    try:
        crawled_data_df = pd.read_csv(crawled_data_file, encoding='ISO-8859-1')
        print(f"Loaded existing crawled data from {crawled_data_file}.")
    except FileNotFoundError:
        print(f"{crawled_data_file} not found. Initializing new file with columns.")
        crawled_data_df = pd.DataFrame(columns=column_data)
        crawled_data_df.to_csv(crawled_data_file, index=False)

    # Initialize imdb_ids_file
    try:
        imdb_ids_df = pd.read_csv(imdb_ids_file)
        print(f"Loaded existing IMDb IDs from {imdb_ids_file}.")
    except FileNotFoundError:
        print(f"{imdb_ids_file} not found. Initializing new file.")
        imdb_ids_df = pd.DataFrame(columns=column_id)
        imdb_ids_df.to_csv(imdb_ids_file, index=False)

    if method == 'selenium':
        driver = webdriver.Chrome()
    elif method == 'requests':
        driver = None
    
    try:
        print(f"Starting crawling process for {number_of_movies} movies.")
        print("Crawled DataFrame columns:", crawled_data_df.columns)
        print("IMDb IDs DataFrame columns:", imdb_ids_df.columns)
        number_of_crawled_movie = len(crawled_data_df)
        while number_of_crawled_movie < number_of_movies and bias < 50:
            elapsed_time = time.time() - start_time
            print(f"Elapsed time for web_crawling: {elapsed_time:.2f} seconds")
            print(f"Max time: {max_seconds:.2f} seconds")
            if max_seconds and elapsed_time >= max_seconds:
                print("Time limit reached inside web_crawling.")
                break
            try:
                if crawled_data_df.empty and imdb_ids_df.empty:
                    get_imdb_ids(imdb_ids_file, number_of_movies)
                    run_crawling(number_of_movies, imdb_ids_file, crawled_data_df, method, driver, start_time, max_seconds)
                elif crawled_data_df.empty and not imdb_ids_df.empty:
                    remain_imdb_ids = get_remaining_imdb_ids(imdb_ids_file, crawled_data_file)
                    if len(remain_imdb_ids) == 0:
                        print("No remaining IMDb IDs to crawl. Running new crawling process.")
                        run_crawling(number_of_movies, imdb_ids_file, crawled_data_file, method, driver, start_time, max_seconds)
                    else:
                        print("Running continue_crawling with remaining IMDb IDs.")
                        continue_crawling(imdb_ids_file, crawled_data_file, driver, start_time, max_seconds)
                elif not crawled_data_df.empty and imdb_ids_df.empty:
                    get_imdb_ids(imdb_ids_file, number_of_movies)
                    remain_imdb_ids = get_remaining_imdb_ids(imdb_ids_file, crawled_data_file)
                    if len(remain_imdb_ids) == 0:
                        print("No remaining IMDb IDs to crawl. Running new crawling process.")
                        run_crawling(number_of_movies, imdb_ids_file, crawled_data_file, method, driver, start_time, max_seconds)
                    else:
                        print("Running continue_crawling with remaining IMDb IDs.")
                        continue_crawling(imdb_ids_file, crawled_data_file, driver, start_time, max_seconds)
                else:
                    remain_imdb_ids = get_remaining_imdb_ids(imdb_ids_file, crawled_data_file)
                    if len(remain_imdb_ids) == 0:
                        print("No remaining IMDb IDs to crawl. Running new crawling process.")
                        run_crawling(number_of_movies, imdb_ids_file, crawled_data_file, method, driver, start_time, max_seconds)
                    else:
                        print("Running continue_crawling with remaining IMDb IDs.")
                        continue_crawling(imdb_ids_file, crawled_data_file, driver, start_time, max_seconds)
                if len(crawled_data_df) >= number_of_movies:
                    success = True  
                    break
            except Exception as e:
                print(f"Error during crawling: {e}")
                error_id = continue_crawling(imdb_ids_file, crawled_data_file, driver)
                list_of_error_imdb_ids.extend(error_id)
                bias += 1

            crawled_data_df = pd.read_csv(crawled_data_file, encoding='ISO-8859-1')
            imdb_ids_df = pd.read_csv(imdb_ids_file)    
            number_of_crawled_movie = len(crawled_data_df)
    finally:
        if driver:
            driver.quit()

    print("Crawling process completed.")
    return list_of_error_imdb_ids, success

def crawling_with_time_limit(max_hours, number_of_movies, method):

    """
    Run the web_crawling function with a time limit.

    Parameters:
    -----------
    max_hours : int
        The maximum number of hours to run the crawling process.
    number_of_movies : int
        The number of movies to attempt to crawl.
    method : str
        The method to use for web crawling, either 'selenium' or 'requests'.

    Notes:
    ------
    The function will continue to run the web_crawling function until the time limit is reached.
    If an error occurs during crawling, the function will wait 10 seconds and attempt to continue.
    """
    
    start_time = time.time() 
    max_seconds = max_hours * 3600  

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_seconds:
            print("Time limit reached. Stopping the crawling process.")
            break
        
        try:
            error_ids, success = web_crawling(number_of_movies, method, start_time, max_seconds)
            if success:
                print("Crawling process completed successfully.")
                break
        except Exception as e:
            print(f"Error occurred: {e}. Retrying after 10 seconds.")
            time.sleep(10)

    print("Crawling process completed or time limit reached.")
    return error_ids

method='requests'
time_limit = 0.5 # Hours
number_of_movies = 100
crawling_with_time_limit(time_limit, number_of_movies, method)