import requests
import m3u8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import os
import re


def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except:
        return False


def is_valid_filename(filename):
    # Define a regular expression for valid filename characters
    valid_chars_regex = r'^[a-zA-Z0-9_.-]+$'

    # Check if the filename matches the pattern
    return bool(re.match(valid_chars_regex, filename))


def url_splitter(url):
    # Find the last occurrence of '/'
    last_slash_index = url.rfind('/')

    # Extract the substring without the last part
    splitted_url = url[:last_slash_index + 1]

    return splitted_url


def find_master_m3u8_link(url, xpath, chromedir, user_agent):
    try:
        # Define the custom option
        options = webdriver.ChromeOptions()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_argument("user-data-dir=" + chromedir)
        options.add_argument('--headless=new')
        options.add_argument(f'user-agent={user_agent}') # Set the user agent cause in headless mode it blocks it otherwise

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Getting the url of the stream
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        perf = driver.get_log('performance')

        # The first pattern we search for is 'playlist.m3u8'
        pattern = re.compile(r'playlist\.m3u8')

        # The second pattern we search for starts with 'https' and finished with "V001"
        pattern2 = re.compile(r'https://\S+(?=V001)')


        # We loop into the log of the driver searching for the two patterns above
        for i in perf:

            # Every element in the list is a nested dictionary. we only look in the values associated with the key 'message'
            a = i['message']

            # Check if the string matches the first pattern
            if pattern.search(a):

                # After the previous check, we expect that there are matches in the following block of code.
                # We use the first match and then break from the code
                match = pattern2.findall(a)
                break

        main_m3u8_link = match[0]

        # Check if the variable is not empy
        if not main_m3u8_link:
            raise Exception

        # We work with the first match that contain the complete url
        print(f'Url of m3u8 master found! Url: {main_m3u8_link}')
        return main_m3u8_link

    except Exception as e:
        print(f"Error: {e}")
        exit()


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

    # If we reach the maximum number of tries the script exits
    print(f"Maximum attempts reached. Exiting the program.")
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


def main():
    # Declaring and checking variables
    try:
        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            Url = input("Enter the url: ")

            if is_valid_url(Url) and Url.startswith("https://www.raiplay.it/"):
                print(f"{Url} is a valid url.")
                break  # Exit the loop if a valid URL is entered
            else:
                print(f"The URL {Url} is not valid. Please try again.")
                attempts += 1

            if attempts == max_attempts:
                print(f"Maximum attempts reached. Exiting the program.")
                exit()

        attempts = 0
        while attempts < max_attempts:
            FileName = input("Enter the name you want your file to be: ")

            if is_valid_filename(FileName):
                print(f"The filename {FileName} is valid.")
                break  # Exit the loop if a valid filename is entered
            else:
                print(f"The filename {FileName} is not valid. Please try again.")
                attempts += 1

            if attempts == max_attempts:
                print(f"Maximum attempts reached. Exiting the program.")
                exit()

        VideoPlayer_Full_XPATH = "/html/body/main/section/div/div[2]/div/div/rai-player/div[2]/div[1]/button[1]"
        ChromeUser_Dir = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default') # This is an exmple, put your own Chrome User Profile
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        file_path = os.path.realpath(__file__)
        StoringPath = f"{file_path}\\..\\..\\VideoDownloads\\{FileName}.ts"

        main_m3u8_link = find_master_m3u8_link(Url, VideoPlayer_Full_XPATH, ChromeUser_Dir, user_agent)

        # Reads the m3m8 master file and retrieves the resolution
        m3u8_Name = get_master_m3u8(main_m3u8_link)

        # Reads the m3m8 file we have chosen and downloads the .ts file in the path chosen
        splitted_url = url_splitter(main_m3u8_link)  # This is the "folder" in witch all the files we work with are stored
        get_chosen_m3u8(splitted_url, m3u8_Name, StoringPath)
    except ValueError as e:
        print(f"Error: {e}")
        exit()


# SCRIPT STARTS
if __name__ == "__main__":
    main()
