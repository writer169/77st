{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "935c6bcc-50f9-4202-8100-fb37ebec9885",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "import os\n",
    "import json\n",
    "import smtplib\n",
    "from email.mime.text import MIMEText\n",
    "\n",
    "KASPI_URL = \"https://kaspi.kz/shop/p/ehrmann-puding-vanil-bezlaktoznyi-1-5-200-g-102110634/?c=750000000\"\n",
    "\n",
    "EMAIL_FROM = os.getenv(\"kolyan77st@gmail.com\")\n",
    "EMAIL_TO = os.getenv(\"olesya.u95@gmail.com\")\n",
    "EMAIL_PASSWORD = os.getenv(\"EMAIL_PASSWORD\")  # app password for gmail\n",
    "\n",
    "def send_email(subject, body):\n",
    "    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:\n",
    "        print(\"Email settings not configured.\")\n",
    "        return\n",
    "\n",
    "    msg = MIMEText(body, \"plain\", \"utf-8\")\n",
    "    msg[\"Subject\"] = subject\n",
    "    msg[\"From\"] = EMAIL_FROM\n",
    "    msg[\"To\"] = EMAIL_TO\n",
    "\n",
    "    server = smtplib.SMTP_SSL(\"smtp.gmail.com\", 465)\n",
    "    server.login(EMAIL_FROM, EMAIL_PASSWORD)\n",
    "    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())\n",
    "    server.quit()\n",
    "\n",
    "def check_availability():\n",
    "    headers = {\n",
    "        \"User-Agent\": \"Mozilla/5.0\"\n",
    "    }\n",
    "    \n",
    "    r = requests.get(KASPI_URL, headers=headers)\n",
    "    soup = BeautifulSoup(r.text, \"html.parser\")\n",
    "\n",
    "    data_block = soup.find(\"script\", {\"type\": \"application/ld+json\"})\n",
    "    if not data_block:\n",
    "        return False\n",
    "\n",
    "    data = json.loads(data_block.text)\n",
    "    availability = data.get(\"offers\", {}).get(\"availability\", \"\")\n",
    "\n",
    "    return \"InStock\" in availability\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    in_stock = check_availability()\n",
    "\n",
    "    if in_stock:\n",
    "        subject = \"Товар появился на Kaspi!\"\n",
    "        body = f\"🎉 Товар появился в наличии!\\n{KASPI_URL}\"\n",
    "        print(body)\n",
    "        send_email(subject, body)\n",
    "    else:\n",
    "        print(\"Товара нет в наличии.\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
