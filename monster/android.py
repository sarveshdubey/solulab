import datetime
import math
import re
import datetime as dt
import sys
import time
from time import sleep
from selenium import webdriver

import requests as requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import urllib.request

from packaging.requirements import URL
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as foptions
options = foptions()
options.add_argument('--headless')

# profile = webdriver.FirefoxProfile("/Users/apple/Library/Application Support/Firefox/Profiles/0ur7nimh.default-release-11")
# gecko_path="/Users/apple/doc/Git/geckodriver/geckodriver"
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
driver.maximize_window()


def location_res(result):
    '''Function to extract location from Indeed search result'''

    tag = result.find(name='p', attrs={'class': 'job-cardstyle__JobCardDetails-sc-1mbmxes-5 kPCMPL'})  # find appropriate tag
    try:
        tag2 = tag.select('span')
        if tag2:
            location = tag2[0].text
        else:
            location = tag.text
        return location
    except:
        return 'NaN'


def company_res(result):
    '''Function to extract company name from Indeed search result'''

    tag = result.find(name='h3', attrs={'class': 'job-cardstyle__JobCardCompany-sc-1mbmxes-3 GPHLl'})  # find appropriate tag
    try:  # Second try statement accounts for whether there any nested tags
        Name = tag.text
        return Name
    except:
        return 'NaN'



def job_res(result):
    '''Function to extract job title'''

    try:  # Accounts for missing job title
        tag = result.find(name='a', attrs={'class': 'job-cardstyle__JobCardTitle-sc-1mbmxes-2 iQztVR'})
        job = tag.text
        return job
    except:
        return 'NaN'

def job_description(result):
    try:
        Lists = []
        Today = datetime.datetime.today()
        tag = result.find(name='a',attrs={'class':'job-cardstyle__JobCardTitle-sc-1mbmxes-2 iQztVR'})['href']
        url = "https:"+ tag
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
        response = requests.get(url,headers=headers)
        html = response.text
        soup_ = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
        # Job Description
        tag2 = soup_.find(name='div', attrs={'class': 'descriptionstyles__DescriptionContainer-sc-13ve12b-0 bOxUQy'})
        if tag2:
            job_desc = tag2.text
        else:
            job_desc = 'NaN'

        # Posted on
        Date_tag = soup_.find(name='div',attrs={'class':'detailsstyles__DetailsTableDetailPostedBody-sc-1deoovj-6 gmYLjn'})
        if Date_tag:
            date_ = re.findall(r'\d+', Date_tag.text)
            d = datetime.timedelta(days=int(date_[0]))
            a = Today - d
            Published_Date = a.strftime('%Y-%m-%d')
        else:
            Published_Date = 'NaN'

        # Company URL
        URL_tag = soup_.find(name='div',attrs={'class':'detailsstyles__CompanyUrl-sc-1deoovj-3 dAGmjp'})
        if URL_tag:
            Company_URL =  URL_tag.text
        else:
            Company_URL = 'NaN'

        # Company Size
        Size_tag = soup_.find(name='div',attrs={'data-test-id':'svx-jobview-companysize-div'})
        if Size_tag:
            Company_Size = Size_tag.text
            Company_Size = Company_Size.removeprefix("COMPANY SIZE")
        else:
            Company_Size = 'NaN'

        # Industry Type
        Industry_tag = soup_.find(name='div',attrs={'data-test-id':'svx-jobview-industry'})
        if Industry_tag:
            Industry_type = Industry_tag.text

        else:
            Industry_type = 'NaN'

        Lists.append(job_desc)
        Lists.append(Published_Date)
        Lists.append(Company_URL)
        Lists.append(Company_Size)
        Lists.append(Industry_type)
        return Lists
    except:
        return 'NaN'


def all_funcs(search):
    '''
    This function iterates through each result on a single Indeed.com results
    page then applies the four functions above to extract the relevant
    information. It takes a search argument in order to also keep track of the
    search term used, since location can give a different value than the actual
    city or location searched.'''

    entries = []
    for result in search.find_all(name='div',attrs={'class':'job-cardstyle__JobCardHeader-sc-1mbmxes-8 eKuJQp'}):
        result_data = []
        result_data.append(job_res(result))
        result_data.append(company_res(result))
        result_data.append(location_res(result))
        JD_List = job_description(result)
        if JD_List != 'NaN':
            for attribute in JD_List:
                result_data.append(attribute)
        else:
            Null = 'NaN'
            for i in range(4):
                result_data.append(Null)

        # result_data.append(search)
        entries.append(result_data)
    return entries


def scrape(cities_list,job_list, max=200):
    max_results_per_city = max
    page_no = math.ceil(max/9)
    results = []  # Empty list that will contain all results
    a = dt.datetime.now()  # Start time of process
    print(a)

    for job in job_list:
        for city in cities_list:  # Iterate through cities
            for start in range(page_no):  # Iterate through results pages
                url = "https://www.monster.com/jobs/search?q="+job+"&where="+city+"&page="+str(start)+""
                driver.get(url)
                time.sleep(15)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
                data = all_funcs(soup)  # use functions from before to extract all job listing info
                for i in range(len(data)):  # add info to results list
                    results.append(data[i])
                sleep(1)
            print(city + " DONE")
            print("Elapsed time: " + str(dt.datetime.now() - a))  # Update user on progress

        b = dt.datetime.now()
        c = b - a
        print(c)

        print(job + "Done")
        print("Elapsed time: " + str(dt.datetime.now() - a))
    d= dt.datetime.now()
    time_taken = d-a
    print(time_taken)

    # Turn results list into dataframe
    df = pd.DataFrame(results, columns=['Job Title', 'Company', 'Location', 'Job Description', 'Publishing Date','Company URL','Company Size','Industry Type'])

    df.to_csv(f'csvs/Monster_android.csv')  # Save data


cities = ['Alabama',
'Alaska',
'Arizona',
'Arkansas',
'California',
'Colorado',
'Connecticut',
'Delaware',
'Florida',
'Georgia',
'Hawaii',
'Idaho',
'Illinois',
'Indiana',
'Iowa',
'Kansas',
'Kentucky',
'Louisiana',
'Maine',
'Maryland',
'Massachusetts',
'Michigan',
'Minnesota',
'Mississippi',
'Missouri',
'Montana',
'Nebraska',
'Nevada',
'New+Hampshire',
'New+Jersey',
'New+Mexico',
'New+York',
'North+Carolina',
'North+Dakota',
'Ohio',
'Oklahoma',
'Oregon',
'Pennsylvania',
'Rhode+Island',
'South+Carolina',
'South+Dakota',
'Tennessee',
'Texas',
'Utah',
'Vermont',
'Virginia',
'Washington',
'West+Virginia',
'Wisconsin',
'Wyoming']

jobs = ['Android%20Developer', 'Android%20iOS%20App%20Developer', 'Software%20Engineer%20-%20Android', 'Native%20Android%20Developer', 
'Android%20+ROS%20Developer', 'Android%20Developer%20-%20Java/sdk/c/c++', 'React%20Native%20Developer%20-%20Android/iOS%20Platform', 
'Android%20Developer%20-%20Java/Kotlin/SDK', 'Full%20Stack%20Android%20App%20Developer%20(JAVA+Laravel)']

scrape(cities,jobs)
driver.close()
