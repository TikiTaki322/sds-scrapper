import re
import requests

from time import sleep
from random import shuffle

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, StaleElementReferenceException

from core.keyboards.reply import get_try_again_sds_parser_or_menu

from aiogram.exceptions import TelegramBadRequest

EXEPTION_CUSTOM_GROUP = (NoSuchWindowException, NoSuchElementException,
                         StaleElementReferenceException, TelegramBadRequest, IndexError, AttributeError, Exception)


async def sigma_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        open_search = browser.find_element(By.ID, "header-search-search-wrapper-input")
        open_search.send_keys(item)
        sleep(1.5)
        # Checking if possible to retrieve quickly sds after insertion the catalog number into the search bar
        sds_div_quick_access = browser.find_element(By.ID, 'header-search-search-wrapper-menu')
        sds_quick_access = [tag for tag in sds_div_quick_access.find_elements(By.TAG_NAME, 'a') if
                            'SDS' in tag.get_attribute('href').upper()]
        if sds_quick_access != [] and sds_quick_access[0].is_enabled():
            result = sds_quick_access[0].get_attribute('href')
            print(f'Result from quick search - {result}')
            return result

        button = browser.find_element(By.ID, 'header-search-submit-search-wrapper')
        browser.execute_script("arguments[0].click();", button)
        sleep(2)

        try:
            sds_button = browser.find_element(By.CLASS_NAME, 'MuiTypography-colorSecondary')
            browser.execute_script("arguments[0].click();", sds_button)
            sleep(1.5)
        except NoSuchElementException:
            await message.answer(f'The search of the {source_name} yielded no results...',
                                 reply_markup=get_try_again_sds_parser_or_menu())
            return None

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        result = soup.find('a', {'id': 'sds-link-EN'})
        if result == []:
            result = soup.find('a', {'id': 'sds-link-DE'})
        result = source + result["href"]
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def cymitquimica_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_bar = browser.find_element(By.NAME, 'search') if 'text' == browser.find_element(By.NAME,
                                                                                               'search').get_attribute(
            'type') else None
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1)
        item_page = browser.find_element(By.CLASS_NAME, 'js-product-link')
        browser.execute_script("arguments[0].click();", item_page)
        sleep(1.5)
        sds_button = browser.find_element(By.CLASS_NAME, 'js-show-pdf-sds')
        result = sds_button.get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def usp_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(2.5)
        search_bar = browser.find_element(By.CLASS_NAME, 'search-query')
        search_bar.send_keys(item)
        sleep(1)
        try:
            collapsed_product = browser.find_element(By.CLASS_NAME, 'typeaheadProductName')
            browser.execute_script("arguments[0].click();", collapsed_product)
        except NoSuchElementException:
            await message.answer(f'The search of the {source_name} yielded no results...',
                                 reply_markup=get_try_again_sds_parser_or_menu())
            return None

        sleep(2.5)
        sds_page = browser.find_element(By.PARTIAL_LINK_TEXT, 'Safety data sheet.pdf')
        browser.execute_script("arguments[0].click();", sds_page)
        sleep(1.5)
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        result = browser.current_url
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def abcam_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_button = [elem for elem in browser.find_elements(By.TAG_NAME, 'button') if elem.get_attribute(
            'data-testid') == 'launch-search-overlay']

        search_field = search_button[0].find_element(By.TAG_NAME, 'span')
        browser.execute_script("arguments[0].click();", search_field)
        sleep(1)
        input_field = browser.find_element(By.ID, 'search-input')
        input_field.send_keys(item, Keys.RETURN)
        sleep(1.5)

        sds_page = [elem for elem in browser.find_elements(By.TAG_NAME, 'button') if
                    'support & downloads' in elem.text.lower()]
        sleep(1)
        if sds_page:
            browser.execute_script("arguments[0].click();", sds_page[0])
            sleep(1.3)

        result = browser.current_url
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def tci_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_bar = browser.find_element(By.ID, 'js-site-search-input')
        search_bar.send_keys(item)
        sleep(1.3)
        search_button = browser.find_element(By.CLASS_NAME, 'js_search_button')
        search_button.click()
        sleep(1.3)
        current_url = browser.current_url
        browser.close()
        sleep(0.3)
        # Re-entry to site
        browser = webdriver.Chrome()
        browser.get(current_url)
        sleep(1.5)

        item_page = browser.find_element(By.CLASS_NAME, 'text-concat')
        item_page.is_enabled() and item_page.tag_name == 'div'
        item_page_href = item_page.find_element(By.TAG_NAME, 'a')
        result = item_page_href.get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def trc_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        open_search = browser.find_element(By.CLASS_NAME, 'aa-DetachedSearchButton')
        browser.execute_script("arguments[0].click();", open_search)
        sleep(2)
        search_bar = browser.find_element(By.CLASS_NAME, 'aa-Input')
        search_bar.send_keys(item)
        sleep(1.5)
        # Checking if possible to get quickly sds after insertion the catalog number in search bar
        sds_quick_access = [elem for elem in browser.find_elements(By.CLASS_NAME, 'product-info') if
                            item.upper() in elem.get_attribute('href').upper() and 'SDS' in elem.get_attribute('href').upper()]
        if sds_quick_access != [] and sds_quick_access[0].is_enabled():
            result = sds_quick_access[0].get_attribute('href')
            print(f'Result from the if statement - {result}\nsource - {source_name}')
            return result

        search_button = browser.find_element(By.CLASS_NAME, 'aa-SubmitButton')
        browser.execute_script("arguments[0].click();", search_button)
        sleep(1.6)
        research_tools_checkmark = [i for i in browser.find_elements(By.CLASS_NAME, 'form-container') if
                                    i.text.split('\n')[0] == 'Research Tools']

        # if research_tools_checkmark != [] and research_tools_checkmark[0].is_enabled():
        browser.execute_script("arguments[0].click();", research_tools_checkmark[0])
        sleep(1.6)
        sds_checkmark = [i for i in browser.find_elements(By.CLASS_NAME, 'form-container') if
                         i.text.split('\n')[0] == 'SDS']

        if sds_checkmark == [] or sds_checkmark[0].text.split('\n')[1] == '0':
            await message.answer(f'The search of the {source_name} yielded no results...',
                                 reply_markup=get_try_again_sds_parser_or_menu())
            return None
        else:
            browser.execute_script("arguments[0].click();", sds_checkmark[0])
            sleep(1.5)

        soup = BeautifulSoup(browser.page_source, 'html.parser')
        all_tags = soup.find_all('a')
        sds_tags = [tag['href'] for tag in all_tags if 'SDS' in tag.get('href', '')]
        result = sds_tags[0]
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def progen_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_icon = browser.find_element(By.ID, 'scrollToBannerSearch')
        browser.execute_script("arguments[0].click();", search_icon)
        sleep(1.5)
        search_bar = browser.find_element(By.CLASS_NAME, 'dfd-searchbox-input')
        search_bar.send_keys(item)
        sleep(1.5)
        item_pages = [elem for elem in browser.find_elements(By.CLASS_NAME, 'dfd-card-type-product')
                      if item == elem.find_element(By.CLASS_NAME, 'dfd-card-id').text.split()[-1]]

        #if item_pages != [] and item_pages[0].is_enabled():
        item_page = item_pages[0].find_element(By.TAG_NAME, 'a')
        result = item_page.get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def honeywell_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        country_navigate_button = browser.find_element(By.ID, 'countryNavigate')
        browser.execute_script("arguments[0].click();", country_navigate_button)
        sleep(1)
        select_region = browser.find_element(By.LINK_TEXT, 'Europe')
        browser.execute_script("arguments[0].click();", select_region)
        sleep(1)
        select_country = browser.find_element(By.LINK_TEXT, 'SWITZERLAND')
        browser.execute_script("arguments[0].click();", select_country)
        sleep(1)
        search_bar = browser.find_element(By.CLASS_NAME, 'isc-button-wrap').find_element(By.TAG_NAME, 'input')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1)

        sds_page = browser.find_element(By.CLASS_NAME, 'sds-download')
        browser.execute_script("arguments[0].click();", sds_page)
        sleep(1.5)
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        result = browser.current_url
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def aniara_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_bar = browser.find_element(By.ID, 'l-Search')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(0.5)

        sds_page = browser.find_element(By.PARTIAL_LINK_TEXT, 'MSDS')
        result = sds_page.get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(
            f'The search of the {source_name} yielded no results...\nIf your catalog number looks like "HY-221402-500ML", you can try again with digits only, in format "221402"',
            reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def biorad_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(2)
        decline_button = browser.find_element(By.LINK_TEXT, 'Decline')
        browser.execute_script("arguments[0].click();", decline_button)
        sleep(1)
        search_bar = browser.find_element(By.ID, 'views-exposed-form-brc-acquia-search-brc-site-search').find_element(
            By.TAG_NAME, 'input')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1.5)

        pdf_button = browser.find_element(By.LINK_TEXT, 'Download PDF')
        browser.execute_script("arguments[0].click();", pdf_button)
        sleep(1)
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        result = browser.current_url
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(
            f'The search of the {source_name} yielded no results...',
            reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def edqm_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_option = browser.find_element(By.NAME, 'vSelectName')
        search_option.send_keys('Catalogue Code')
        search_type = browser.find_element(By.NAME, 'vContains')
        search_type.send_keys('is exactly')
        sleep(0.5)
        search_bar = browser.find_element(By.NAME, 'vtUserName')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(0.5)

        item_page = browser.find_element(By.LINK_TEXT, item)
        browser.execute_script("arguments[0].click();", item_page)
        sleep(0.5)
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        sleep(1)
        sds_list = [elem for elem in browser.find_elements(By.TAG_NAME, 'a') if
                    'click to download safety data sheet' in elem.text.lower()]
        browser.execute_script("arguments[0].click();", sds_list[0])
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        sleep(1)
        all_links = [elem for elem in browser.find_elements(By.TAG_NAME, 'a') if 'SDS_' in elem.text]
        english_link = [elem.get_attribute('href') for elem in all_links if elem.text.__contains__("EN")]
        result = english_link[0] if english_link else all_links[0].get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(
            f'The search of the {source_name} yielded no results...\n'
            f'In the case of {source_name} source, such a result may indicate that the item is most likely not hazardous.',
            reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def chemicalsafety_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_bar = browser.find_element(By.TAG_NAME, 'input') if browser.find_element(By.TAG_NAME, 'input').get_attribute(
            'type') == 'text' else None
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1)
        result_block = browser.find_element(By.ID, 'cs_divResults')
        if result_block.text == '':
            await message.answer(
                f'The search of the {source_name} yielded no results...',
                reply_markup=get_try_again_sds_parser_or_menu())
            return None

        all_tags = [elem for elem in browser.find_elements(By.TAG_NAME, 'td')]
        all_links, intermediate_results = list(), list()
        for tag in all_tags:
            try:
                elem = tag.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if elem and elem not in all_links:
                    all_links.append(elem)
            except NoSuchElementException:
                pass
        browser.close()

        length_all_links = len(all_links)
        flag = None
        if length_all_links > 5:
            flag = True
            shuffle(all_links)
            all_links = all_links[:5]

        for link in all_links:
            browser = webdriver.Chrome()
            browser.get(link)
            sleep(1.5)
            try:
                sds_button = browser.find_element(By.ID, 'sds_links').find_element(By.TAG_NAME, 'a')
                result = sds_button.get_attribute('href')
                intermediate_results.append(result)
                browser.close()
            except NoSuchElementException:
                pass

        if flag:
            results = f'The {source_name} source gives {length_all_links} sds-documents, ' \
                      f'but we took only {len(intermediate_results)} to avoid slowing down the program:\n\n'
        else:
            results = f'The {source_name} source gives {len(intermediate_results)} sds-documents:\n\n'

        counter = 1
        for result in intermediate_results:
            results += f'{counter}. {result}\n'
            counter += 1
        print(f'Main result in the end of program - {results}\nsource - {source_name}')
        return results
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def vwr_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_bar = browser.find_element(By.ID, 'msdsSearchPartNumber')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1.5)

        sds_button = [elem for elem in browser.find_elements(By.TAG_NAME, 'a') if 'View SDS' == elem.text]
        result = sds_button[0].get_attribute('href')
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def bdbiosciences_parse(message, source_name, source, item):
    try:
        browser = webdriver.Chrome()
        browser.get(source)
        sleep(1.5)
        search_icon = browser.find_element(By.CLASS_NAME, 'bdb-header__search-nav-link')
        search_icon.click()
        sleep(1)
        search_bar = browser.find_element(By.ID, 'searchModal').find_element(By.TAG_NAME, 'input')
        search_bar.send_keys(item, Keys.RETURN)
        sleep(1.5)

        item_page = browser.find_element(By.CLASS_NAME, 'card-title')
        browser.execute_script("arguments[0].click();", item_page)
        sleep(1.5)
        sds_button = browser.find_element(By.LINK_TEXT, 'Safety Data Sheet')
        browser.execute_script("arguments[0].click();", sds_button)
        sleep(1.5)
        lang_popup = browser.find_element(By.CLASS_NAME, 'data-sheets-container_multi-lang-popup').find_element(
            By.CLASS_NAME, 'btn')
        browser.execute_script("arguments[0].click();", lang_popup)
        sleep(1.5)
        all_open_tabs = browser.window_handles
        browser.switch_to.window(all_open_tabs[-1])
        result = browser.current_url
        print(f'Main result in the end of program - {result}\nsource - {source_name}')
        return result
    except EXEPTION_CUSTOM_GROUP as e:
        await message.answer(f'The search of the {source_name} yielded no results...',
                             reply_markup=get_try_again_sds_parser_or_menu())
        print(f'Error with exception "{e}" while program execution.\nSource: {source_name}\nLink: {source}')
        return None


async def source_checker(message):
    urls_db = {
        'sigma_parse': ['https://www.sigmaaldrich.com', 0],
        'cymitquimica_parse': ['https://cymitquimica.com', 1],
        'usp_parse': ['https://store.usp.org/', 2],
        'abcam_parse': ['https://www.abcam.com/', 3],
        'tci_parse': ['https://www.tcichemicals.com/US/en', 4],
        'trc_parse': ['https://www.lgcstandards.com/US/en/', 5],
        'progen_parse': ['https://www.progen.com', 6],
        'honeywell_parse': ['https://lab.honeywell.com/en/sds', 7],
        'aniara_parse': ['https://www.aniara.com/product-documentation.html', 8],
        'biorad_parse': ['https://www.bio-rad.com/', 9],
        'edqm_parse': ['https://crs.edqm.eu/', 10],
        'chemicalsafety_parse': ['https://chemicalsafety.com/sds-search', 11],
        'vwr_parse': ['https://uk.vwr.com/store/search/searchMSDS.jsp', 12],
        'bdbiosciences_parse': ['https://www.bdbiosciences.com', 13],
    }
    source_name = message.text.split()[0]
    source_data = [[source_name, *urls_db.get(key)] for key in [*urls_db.keys()] if source_name.lower() == key.split('_')[0]]

    if source_data == []:
        await message.answer(f'Selected source does not exist.\r\nPush the buttons!',
                             reply_markup=get_try_again_sds_parser_or_menu())
    else:
        source_name = source_data[0][0]
        index = source_data[0][2]
        link = source_data[0][1]
        return source_name, index, link


async def sds_search(message, source_name, func, link, catalog_number):
    return await func(message, source_name, link, catalog_number)

    # print(sigma_parse() # search by Sigma, Supelco, Merc etc.
    # print(cymitquimica_parse(urls_db['cymitquimica_parse'], item)) # search by TCI, TRC, TLC, USP, EDQM, Reagecon, Biosynth, Mikromol etc.
    # print(usp_parse(urls_db['usp_parse'], item))
    # print(abcam_parse(urls_db['abcam_parse'], item))
    # print(tci_parse(urls_db['tci_parse'], item))
    # print(trc_parse(urls_db['trc_parse'], item))
    # print(progen_parse(urls_db['progen_parse'], item))
    # print(honeywell_parse(urls_db['honeywell_parse'], item))
    # print(aniara_parse(urls_db['aniara_parse'], item)) # search by Biophen, Hyphen
    # print(biorad_parse(urls_db['biorad_parse'], item))
    # print(edqm_parse(urls_db['edqm_parse'], item))
    # print(chemicalsafety_parse(urls_db['chemicalsafety_parse'], item)) # Universal source, search by product name instead of catalog
    # print(vwr_parse(urls_db['vwr_parse'], item)) # search for Roshe, VWR
    # print(bdbiosciences_parse(urls_db['bdbiosciences_parse'], item)) # search for BD Biosciences
    pass

# Need to write termofisher source "https://www.thermofisher.com/"
