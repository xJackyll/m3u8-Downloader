import requests
import m3u8

# This function cut correctly the urls
def url_splitter(url):
    # Find the last occurrence of '/'
    last_slash_index = url.rfind('/')

    # Extract the substring without the last part
    splitted_url = url[:last_slash_index + 1]

    return splitted_url


def get_master_m3u8(url):
    ResolutionsList = []

    try:
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
    except:
        print("Something went wrong. Probably the Url is not valid")

    # If we reach the maximum number of tries the script exits
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
Url = input("Enter the url: ")  # This will be the link to the master m3u8 file
splitted_url = url_splitter(Url)  # This is the "folder" in witch all the files we work with are stored

FileName = input("Enter the name you want your file to be: ")
StoringPath = f"C:\\Users\\carus\\Desktop\\VideoDownloader\\{FileName}.ts"

# Reads the m3m8 master file and retrieves the resolution
m3u8_Name = get_master_m3u8(Url)

# Reads the m3m8 file we have chosen and downloads the .ts file
get_chosen_m3u8(splitted_url, m3u8_Name, StoringPath)
