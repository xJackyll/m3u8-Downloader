import requests
import m3u8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import re


def url_splitter(url):
    # Find the last occurrence of '/'
    last_slash_index = url.rfind('/')

    # Extract the substring without the last part
    splitted_url = url[:last_slash_index + 1]

    return splitted_url


def find_master_m3u8_link(url, xpath):
    try:
        # Define the custom option
        capa = DesiredCapabilities.CHROME
        capa['goog:loggingPrefs'] = {'performance': 'ALL'}
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + ChromeUser_Dir)
        options.add_argument('--headless=new')
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), desired_capabilities=capa, options=options)

        # Getting the url of the stream
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH)))
        perf = driver.get_log('performance')

        # The first pattern we search for is 'playlist.m3u8'
        pattern = re.compile(r'playlist\.m3u8')

        # The second pattern we search for starts with 'https' and finished with "V001"
        pattern2 = re.compile(r'https://.*?V001')

        # The list where we store the matches
        matches = []

        # We loop into the log of the driver searching for the two patterns above
        for i in perf:

            # Every element in the list is a nested dictionary. we only look in the values associated with the key 'message'
            a = i['message']

            # Check if the string matches the first pattern
            if pattern.search(a):

                # After the previous check, we expect that there are matches in the following block of code.
                # However, it is important to note that the first matches will not be used,
                # since they are incomplete or irrelevant strings. The match we are really interested in is the last one,
                # which represents the desired result after the filtering process.
                matches = pattern2.findall(a)
                # We store the first match in the string
                matches.append(matches[0])

        # We work with the last match that contain the complete url
        main_m3u8_link = matches[-1]
        print(f'Url of m3u8 master found! Url: {matches[-1]}')
        return main_m3u8_link

    except Exception as e:
        print(f"Error: {e}")


def get_master_m3u8(url):
    ResolutionsList = []

    # Reading the m3u8 master file
    r = requests.get(url)

    # With the m3u8 module we can efficiently parse the m3u8 file
    m3u8_master = m3u8.loads(r.text)

    # We display every possible resolution
    index = 0
    print("Resolutions:")

    for playlist in m3u8_master.data['playlists']:
        print(f"{playlist['stream_info']['resolution']} ({index})")
        ResolutionsList.append([playlist['uri'], playlist['stream_info']['resolution']])
        index += 1

    # The user chooses a resolution and the script checks if the input is correct
    tries = 0
    while tries < 3:
        try:
            chosen_res = int(input("what resolution you want? (Enter the associated number) "))
            if index > chosen_res >= 0:

                # Return the filename of the chosen resolution
                return ResolutionsList[chosen_res][0]

            else:
                print("Invalid input. Please enter a valid integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

        tries += 1

    # If the we reach the maximum number of tries the script exits
    exit()


def get_chosen_m3u8(url, name_chosen_m3u8, path_to_file):
    # Reading the m3u8 master file
    r = requests.get(url + name_chosen_m3u8)

    # With the m3u8 module we can efficiently parse the m3u8 file
    chosen_m3u8 = m3u8.loads(r.text)

    # Counting the total segments in order to do proper progress bar
    num_seg = len(chosen_m3u8.data['segments'])
    index = 0

    # We request and append each segment in a .ts file
    with open(path_to_file, "wb") as f:
        for segment in chosen_m3u8.data['segments']:
            r = requests.get(url + segment['uri'])
            f.write(r.content)
            index += 1
            print(f"Progress: {round(index / num_seg * 100, 1)} %")


# SCRIPT STARTS
Url = input("Enter the url: ")  # This will be the link to page
FileName = input("Enter the name you want your file to be: ")
ChromeUser_Dir = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default') # This is an exmple, put your own Chrome User Profile
VideoPlayer_Full_XPATH = "/html/body/main/section/div/div[2]/div/div/rai-player/div[2]/div[1]/button[1]"
StoringPath = f"C:\\Users\\carus\\Desktop\\CODING & PROJECTS\\VideoDownloader\\{FileName}.ts"

main_m3u8_link = find_master_m3u8_link(Url, VideoPlayer_Full_XPATH)

# Reads the m3m8 master file and retrieves the resolution
m3u8_Name = get_master_m3u8(main_m3u8_link)

# Reads the m3m8 file we have chosen and downloads the .ts file in the path chosen
splitted_url = url_splitter(main_m3u8_link)  # This is the "folder" in witch all the files we work with are stored
get_chosen_m3u8(splitted_url, m3u8_Name, StoringPath)
