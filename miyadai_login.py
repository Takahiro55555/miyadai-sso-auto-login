"""
selenium自動ログイン
"""
import datetime
import platform
import time

import pings
from selenium import webdriver
import keyring
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def login(mid):
    # 外部との疎通が確認できた場合は何もしない
    p = pings.Ping()
    address00 = "35.196.128.215"  # MyServer
    if p.ping(address00).is_reached():
        print("[%s] 外部(%s)との疎通を確認しました" % (datetime.datetime.now(), address00))
        return
    address01 = "8.8.8.8"
    if p.ping(address01).is_reached():
        print("[%s] 外部(%s)との疎通を確認しました" % (datetime.datetime.now(), address01))
        return
    address02 = "1.1.1.1"
    if p.ping(address02).is_reached():
        print("[%s] 外部(%s)との疎通を確認しました" % (datetime.datetime.now(), address02))
        return
    print("[%s] 外部との疎通を確認することができませんでした" % (datetime.datetime.now()))
    
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
    print("[%s] 自動ログインを終了します" % (datetime.datetime.now()))
    return


def read_user_file():
    path = 'user.txt'
    with open(path, mode='r') as f:
        name = f.readline()
    return name


if __name__ == '__main__':
    interval_s = 3
    mid = read_user_file()
    while True:
        t = time.time()
        try:
            login(mid)
        except Error as e:
            print(e)
        wait_t = interval_s - (time.time() - t)
        if wait_t > 0:
            time.sleep(wait_t)
