
import os
import time
from flask import Request

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def selenium_handler(request: Request):
    chrome_bin = "/tmp/headless-chromium"
    driver_path = "/tmp/chromedriver"

    if not os.path.exists(chrome_bin):
        os.system("cp files/headless-chromium /tmp/headless-chromium")
        os.system("cp files/chromedriver /tmp/chromedriver")
        os.system("chmod +x /tmp/headless-chromium /tmp/chromedriver")

    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    try:
        driver.get("https://www.google.com")
        time.sleep(2)
        return f"Título da página: {driver.title}"
    except Exception as e:
        return f"Erro ao rodar Selenium: {str(e)}"
    finally:
        driver.quit()
