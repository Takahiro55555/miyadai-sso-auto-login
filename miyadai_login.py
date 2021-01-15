"""
selenium自動ログイン
"""
import datetime
import socket
import platform

from selenium import webdriver
import keyring
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def login(mid):
    # 外部との疎通が確認できた場合は何もしない
    address01 = "8.8.8.8"
    if check_internet("8.8.8.8"):
        print("[%s] 外部(%s)との疎通を確認しました" % (datetime.datetime.now(), address01))
        return
    address02 = "1.1.1.1"
    if check_internet("1.1.1.1"):
        print("[%s] 外部(%s)との疎通を確認しました" % (datetime.datetime.now(), address02))
        return

    if keyring.get_password('keyring_selenium', mid) is None:
        print("Please store your login info!",)
        print("Run script in terminal: pipenv python save_pass.py")
        return

    # WebDriverのパスを指定してChromeを起動
    os_name = platform.system()
    if os_name == "Darwin":
        driver_path = "bin/chromedriver_mac_v2_41"
    elif os_name == "Linux":
        driver_path = "bin/chromedriver_linux_v2_41"
    elif os_name == "Windows":
        driver_path = "bin/chromedriver_win32_v2_41.exe"
    else:
        print("Unknown System. Please send Issue.")
        return
    driver = webdriver.Chrome(driver_path)

    # 宮崎大学公式ホームページをブラウザで開きます
    miyadai_url = "https://www.miyazaki-u.ac.jp/"
    driver.get(miyadai_url)
    print(driver.current_url)
    try:
        WebDriverWait(driver, 10).until(lambda driver: driver.current_url != miyadai_url)
        login_url = driver.current_url
        print(login_url)
        input_mid = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
        print(driver.current_url)
    except TimeoutException:
        print("Already login or don't connecting.")
        driver.quit()
        return

    input_mid.send_keys(mid)
    input_pass = driver.find_element_by_id("login-password")
    input_pass.send_keys(keyring.get_password('keyring_selenium', mid))

    # 検索ボタン要素の取得
    button_login = driver.find_element_by_id("btn-login")

    # 検索ボタンをクリックする
    button_login.click()

    try:
        WebDriverWait(driver, 10).until(lambda driver: driver.current_url != login_url)
        print(driver.current_url)
    except TimeoutException:
        print("Failed login. Please check MID or password.")
    driver.quit()
    return

def check_internet(Host="8.8.8.8", port=53, timeout_s=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout_s)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((Host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def read_user_file():
    path = 'user.txt'
    with open(path, mode='r') as f:
        name = f.readline()
    return name


if __name__ == '__main__':
    mid = read_user_file()
    login(mid)
