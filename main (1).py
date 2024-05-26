import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up the WebDriver
driver = webdriver.Chrome()

# URL to scrape
url = 'https://www.fred-forest-archives.com/fr/p/11/archives'

# Open the webpage
driver.get(url)

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pagination-button')))

# Close the tab using the close button
close_button = driver.find_element(By.CSS_SELECTOR, 'button.mfp-close')
close_button.click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'pagination-button'))
)

# Initialize dataframe
df = pd.DataFrame(columns=['Name', 'Path'])


while True:

    # Find all the links

    # Loop through all the links
    for i in range(18):

        # media_block = action.find_element(By.CLASS_NAME, 'block-media')
        actions = driver.find_elements(By.CLASS_NAME, "action-block-content")

        action = actions[i]

        text_block = action.find_element(By.CLASS_NAME, 'block-text')

        temp = text_block.find_element(By.TAG_NAME, 'h3')

        title = temp.find_element(By.TAG_NAME, 'a')

        driver.execute_script("arguments[0].scrollIntoView();", action)
        WebDriverWait(driver, 2)

        # Click the link
        name = title.get_attribute('href').split('/')[-1]

        t = True
        while(t):
            try:
                title.click()
                t=False
            except:
                t=True
        

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

        # Scrape the information
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text()

        # Save the information into a .txt file
        path = os.path.join('actions', f'{name}.txt')
        with open(path, 'w') as f:
            f.write(text)

        # Save the name and path of the .txt file into a dataframe
        # df = df.update({'Name': name, 'Path': path}, ignore_index=True)
        

        # Go back to the previous page
        driver.back()

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pagination-button')))


    try:
        # Click the next page button
        try:
            next_button = driver.find_element(By.ID, 'pagination-button')
            next_button.click()
        except:
            raise Exception('Not found')

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/fr/actions/"]')))

        

    except Exception as e:
        print(f'Error: {e}')
        break

# Close the WebDriver
driver.quit()

# Save the dataframe
df.to_csv('dataframe.csv', index=False)