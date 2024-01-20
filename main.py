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
from moviepy.editor import *
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

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
        logs = driver.get_log('performance')

        # The first pattern we search for is 'playlist.m3u8'
        # The second pattern we search for starts with 'https' and finished with "V001"
        pattern = re.compile(r'playlist\.m3u8')
        pattern2 = re.compile(r'https://\S+(?=V001)')

        # We loop into the log of the driver searching for the two patterns above
        for log in logs:

            # Every element in the list is a nested dictionary. we only look in the values associated with the key 'message'
            message = log['message']

            # Check if the string matches the first pattern
            # When we match the 2nd pattern we store the link and then break from the code
            if pattern.search(message):
                main_m3u8_link = pattern2.findall(message)[0]
                break

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
    AudioList = []

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
    exit_loop = False
    while tries < 3 and exit_loop is False:
        try:
            chosen_res_num = int(input("what resolution you want? (Enter the associated number) "))
            if index > chosen_res_num >= 0:

                # Return the filename of the chosen resolution
                ResChose = ResolutionsList[chosen_res_num][0]
                exit_loop = True

            else:
                print("Invalid input. Please enter a valid integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

        tries += 1

    # If we reach the maximum number of tries the script exits
    if tries == 3:
        print(f"Maximum attempts reached. Exiting the program.")
        exit()

    # We display every possible audio, if there is any
    if len(m3u8_master.data['media']) != 0:
        index = 0
        print("\nAudio:")
        for media in m3u8_master.data['media']:
            if media['default'] == "YES":
                print(f"{media['name']} ({index}) Default: {media['default']}")
            else:
                print(f"{media['name']} ({index})")
            AudioList.append([media['uri'], media['name']])

            index += 1
        # The user chooses a resolution and the script checks if the input is correct
        tries = 0
        exit_loop = False
        while tries < 3 and exit_loop is False:
            try:
                chosen_audio_num = int(input("what resolution you want? (Enter the associated number) "))
                if index > chosen_audio_num >= 0:

                    # Return the filename of the chosen resolution
                    AudioChose = AudioList[chosen_audio_num][0]
                    exit_loop = True

                else:
                    print("Invalid input. Please enter a valid integer.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

            tries += 1

    else:
        AudioChose = None

    # If we reach the maximum number of tries the script exits
    if tries == 3:
        print(f"Maximum attempts reached. Exiting the program.")
        exit()

    return ResChose, AudioChose


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


def merge_vid_n_audio(video, audio, merged_video):
    videoclip = VideoFileClip(video)
    audioclip = AudioFileClip(audio)

    # Concatenate the video clip with the audio clip
    final_clip = videoclip.set_audio(audioclip)

    # Export the final video with audio
    final_clip.write_videofile(merged_video)

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
        StoringPath = f"{file_path}\\..\\..\\VideoDownloads\\{FileName}"
        VideoPath = f"{StoringPath}.ts"
        AudioPath = f"{StoringPath}.mp3"
        VidAndAudio = f"{StoringPath}.mp4"

        main_m3u8_link = find_master_m3u8_link(Url, VideoPlayer_Full_XPATH, ChromeUser_Dir, user_agent)

        # Reads the m3m8 master file and retrieves the resolution
        m3u8_name, m3u8_audio = get_master_m3u8(main_m3u8_link)

        # This is the "folder" in witch all the files we work with are stored on the site
        splitted_url = url_splitter(main_m3u8_link)

        # Reads the m3m8 file we have chosen and downloads the file/files in the path chosen
        # If we have just one audio the work is done
        print("Video")
        get_chosen_m3u8(splitted_url, m3u8_name, VideoPath)

        # If we also have the audio we have to put it with the video in one singular file
        if m3u8_audio is not None:
            print("Audio")
            get_chosen_m3u8(splitted_url, m3u8_audio, AudioPath)
            merge_vid_n_audio(VideoPath, AudioPath, VidAndAudio)

            # We delete the two files we just merged
            if os.path.exists(VideoPath) and os.path.exists(AudioPath):
                os.remove(VideoPath)
                os.remove(AudioPath)
            else:
                print("There is some issue when locating the audio and video file. It seems they does not exist.")

        print("The video is READY!!!")

    except ValueError as e:
        print(f"Error: {e}")
        exit()


# SCRIPT STARTS
if __name__ == "__main__":
    main()
