import copy
import json
import os
import logging

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MySchemeScraper:
    def __init__(self):
        self.myscheme_url = 'https://rules.myscheme.in/'
        self.driver = webdriver.Firefox()

    def get_scheme_links(self):
        self.driver.get(self.myscheme_url)
        scheme_links = []

        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "__next")))
            result_elements = self.driver.find_element(By.ID, '__next').find_element(By.TAG_NAME,
                                                                                     'tbody').find_elements(By.TAG_NAME,
                                                                                                            'tr')

            for result_element in result_elements:
                table_rows = result_element.find_elements(By.TAG_NAME, 'td')
                result_details_dict = {
                    'sr_no': table_rows[0].text,
                    'scheme_name': table_rows[1].text.replace('\nCheck Eligibility', ''),
                    'scheme_link': table_rows[2].find_element(By.TAG_NAME, 'a').get_attribute('href')
                }
                scheme_links.append(result_details_dict)

        except TimeoutException:
            logging.error("Timeout while waiting for page to load")
        except NoSuchElementException as e:
            logging.error(f"Element not found: {e}")

        return scheme_links

    def get_scheme_details(self, scheme_links):
        for scheme in scheme_links:
            self.driver.get(scheme['scheme_link'])
            try:
                WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "__next")))

                # Extract tags with exception handling
                try:
                    tags_elements = self.driver.find_elements(By.XPATH, '//div[@id="tags"]/div')
                    scheme['tags'] = [i.text for i in tags_elements]
                except NoSuchElementException:
                    scheme['tags'] = []

                # Extract details with exception handling
                try:
                    scheme['details'] = self.driver.find_element(By.ID, 'details').text
                except NoSuchElementException:
                    scheme['details'] = 'Not Available'

                # Extract benefits with exception handling
                try:
                    scheme['benefits'] = self.driver.find_element(By.ID, 'benefits').text
                except NoSuchElementException:
                    scheme['benefits'] = 'Not Available'

                # Extract eligibility with exception handling
                try:
                    scheme['eligibility'] = self.driver.find_element(By.ID, 'eligibility').text
                except NoSuchElementException:
                    scheme['eligibility'] = 'Not Available'

                # Extract application process with exception handling
                try:
                    scheme['application_process'] = self.driver.find_element(By.ID, 'application-process').text
                except NoSuchElementException:
                    scheme['application_process'] = 'Not Available'

                # Extract documents required with exception handling
                try:
                    scheme['documents_required'] = self.driver.find_element(By.ID, 'documents-required').text
                except NoSuchElementException:
                    scheme['documents_required'] = 'Not Available'

            except TimeoutException:
                logging.error(f"Timeout while waiting for scheme page to load: {scheme['scheme_link']}")
            except Exception as e:
                logging.error(f"An error occurred for scheme page {scheme['scheme_link']}: {e}")

    def download(self):
        scheme_links = self.get_scheme_links()
        self.get_scheme_details(scheme_links)
        self.driver.quit()
        return scheme_links

    def combine_myscheme_provided_and_scraped_data(self, scraped_scheme_details):
        with open('myScheme-data.json') as file:
            myscheme_structured_data = json.load(file)['hits']['hits']

        individual_beneficiary_types = ['Individual', 'Family', 'Sportsperson', 'Journalist']
        myscheme_structured_data = [scheme for scheme in myscheme_structured_data if any(
            i in individual_beneficiary_types for i in scheme['_source']['targetBeneficiaries'])]

        required_fields_from_structured_data = ['schemeShortTitle', 'schemeCategory', 'schemeSubCategory', 'gender',
                                                'minority',
                                                'beneficiaryState', 'residence', 'caste', 'disability', 'occupation',
                                                'maritalStatus', 'education', 'age', 'isStudent', 'isBpl']

        myscheme_structured_data_dict = {i['_source']['schemeName'].lower().strip(): i['_source'] for i in
                                         myscheme_structured_data}

        combined_schemes_data = []
        for scheme in scraped_scheme_details:
            structured_info = myscheme_structured_data_dict.get(scheme['scheme_name'].lower().strip())
            if structured_info is not None:
                structured_info = {k: v for k, v in structured_info.items() if
                                   k in required_fields_from_structured_data}
                scheme.update(structured_info)
            combined_schemes_data.append(copy.deepcopy(scheme))

        return combined_schemes_data


if __name__ == '__main__':
    download_path = os.path.join(os.path.dirname(__file__), 'myschemes_scraped_9feb.json')
    scraper = MySchemeScraper()
    scraped_scheme_details = scraper.download()
    with open(download_path, 'w') as file:
        json.dump(scraped_scheme_details, file)

    combined_schemes_data = scraper.combine_myscheme_provided_and_scraped_data(scraped_scheme_details)
    output_path = os.path.join(os.path.dirname(__file__), 'myschemes_scraped_combined_9feb.json')
    with open(output_path, 'w') as file:
        json.dump(combined_schemes_data, file)
