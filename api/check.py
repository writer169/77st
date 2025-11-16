import os
import json
from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

def send_email(product_url, status_text):
    """Отправляет email уведомление о появлении товара"""
    EMAIL_FROM = os.environ.get("EMAIL_FROM")
    EMAIL_TO = os.environ.get("EMAIL_TO")
    EMAIL_PASS = os.environ.get("EMAIL_PASS")

    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASS:
        print("Email переменные окружения не заданы!")
        return

    msg = MIMEText(f"Товар появился на Kaspi!\n\nСтатус: {status_text}\n\nСсылка: {product_url}")
    msg["Subject"] = "🔔 Kaspi: Товар в наличии!"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Email отправлен!")
    except Exception as e:
        print(f"❌ Ошибка при отправке email: {e}")

def check_availability():
    """Проверяет наличие товара на Kaspi через ScraperAPI"""
    product_url = "https://kaspi.kz/shop/p/ehrmann-puding-vanil-bezlaktoznyi-1-5-200-g-102110634/?c=750000000"
    SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
    SEND_EMAIL_ALWAYS = os.environ.get("SEND_EMAIL_ALWAYS", "false").lower() == "true"

    if not SCRAPER_API_KEY:
        return {"error": "SCRAPER_API_KEY не задан!"}

    scraper_url = f"https://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={product_url}"

    try:
        r = requests.get(scraper_url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        return {"error": f"Ошибка при запросе: {e}"}

    # Парсим наличие товара через meta теги и JSON-LD
    availability_text = ""
    available = False
    
    # Способ 1: Проверяем meta тег product:availability (самый надёжный)
    meta_availability = soup.find("meta", property="product:availability")
    if meta_availability:
        content = meta_availability.get("content", "").lower()
        availability_text = content
        available = content == "in stock"
    
    # Способ 2: Парсим JSON-LD данные
    if not availability_text:
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    offers = data.get("offers", [])
                    for offer in offers:
                        if isinstance(offer, dict):
                            avail = offer.get("availability", "")
                            if "InStock" in avail or "in stock" in avail.lower():
                                available = True
                                availability_text = "in stock"
                            elif "OutOfStock" in avail or "out of stock" in avail.lower():
                                available = False
                                availability_text = "out of stock"
                            break
            except:
                continue
    
    # Способ 3: Ищем в digitalData (window.digitalData)
    if not availability_text:
        for script in soup.find_all("script"):
            if script.string and "window.digitalData" in script.string:
                if '"stock":0' in script.string or '"stock": 0' in script.string:
                    available = False
                    availability_text = "stock: 0"
                elif '"stock":' in script.string:
                    available = True
                    availability_text = "stock > 0"
                break

    # Отправляем email если товар появился в наличии
    if available or SEND_EMAIL_ALWAYS:
        send_email(product_url, availability_text)

    return {
        "available": available,
        "statusText": availability_text,
        "productUrl": product_url
    }

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_GET(self):
        try:
            result = check_availability()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            response_body = json.dumps(result, ensure_ascii=False)
            self.wfile.write(response_body.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            error_response = json.dumps({"error": str(e)}, ensure_ascii=False)
            self.wfile.write(error_response.encode('utf-8'))
