import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import smtplib
from email.mime.text import MIMEText

KASPI_URL = "https://kaspi.kz/shop/p/ehrmann-puding-vanil-bezlaktoznyi-1-5-200-g-102110634/?c=750000000"
CHECK_INTERVAL = 5 * 60  # проверка каждые 5 минут

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # app password for gmail

def send_email(subject, body):
    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:
        print("Email settings not configured.")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    server.quit()

def check_availability():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(KASPI_URL)

    try:
        availability_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class,"product-availability__text")]')
            )
        )
        availability_text = availability_elem.text.lower()
        driver.quit()
        return "в наличии" in availability_text
    except Exception as e:
        print("Ошибка поиска наличия:", e)
        driver.quit()
        return False

if __name__ == "__main__":
    last_status = None  # None, True или False

    while True:
        in_stock = check_availability()
        print(f"Текущее наличие: {'в наличии' if in_stock else 'нет в наличии'}")

        # Отправляем email только если статус изменился
        if last_status is None or in_stock != last_status:
            if in_stock:
                subject = "Товар появился на Kaspi!"
                body = f"🎉 Товар появился в наличии!\n{KASPI_URL}"
                send_email(subject, body)
            last_status = in_stock

        time.sleep(CHECK_INTERVAL)
