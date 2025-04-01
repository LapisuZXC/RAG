from selenium import webdriver
from selenium.webdriver.common.by import By
from util.selenium_workflow import await_of_load, driver_context_manager
from util.datetime_util import last_three_months

URL = 'https://www.hltv.org/news/archive/'
output_file = "Data/news_links.txt"

TABLE_SELECTOR = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol"
# Селектор общей таблицы данных



def extract_links(driver: webdriver) -> list[str]:
    parent_selector = "body > div.bgPadding > div.widthControl > div:nth-child(2) > div.contentCol > div.index > div.standard-box.standard-list"
    links = []

    try:
        link_elements = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} > a")
        for link_element in link_elements:
            link = link_element.get_attribute('href')
            if link:
                links.append(link)
    except Exception as e:
        print(f"Error extracting links: {e}")
    
    return links


def write_links(output_file: str, data: {str}):
    with open(output_file, 'w') as file:
        for month in data:
            for link in month:
                file.write(link + '\n')
    print(f"Data written to {output_file}")



def main():
    required_monthes = last_three_months() # TODO переделать функцию покрасивее и оптимальнее
    links = []

    for cur_url in required_monthes:
        with driver_context_manager() as driver_manager:
            driver = driver_manager.driver
            print("Parsing news list from:", str(URL + cur_url))

            driver.get(str(URL + cur_url))
            isValid = await_of_load(driver, TABLE_SELECTOR)

            if isValid:
                print("Found data")
                links.append(extract_links(driver))
            else:
                print("Cant find data")

    write_links(output_file, links)



if __name__ == "__main__":
    main()