import urllib.request
from time import sleep
from random import randint
import re
import math
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import sys


def to_title(str):
    str = str.replace("-", " ").capitalize().replace("Iphone", "iPhone").replace("gb", "GB")


def send_email(p, best_price, better, prev_offers, password, model):
    sender_email = "mobilespricetracker823@gmail.com"
    receiver_email = "jack.parsons.uk@gmail.com"

    message = MIMEMultipart("alternative")
    if not better:
        message["Subject"] = "Price Update for {} at Mobiles.co.uk".format(to_title(model))
    else:
        message["Subject"] = "PRICE DROP for {} at Mobiles.co.uk".format(to_title(model))
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = u"Best price for at least 5GB: £{0} for {1}GB\n\nPrice\t\tData\n{2}"\
        .format(best_price[0], best_price[1], "\n".join("£%.2f\t%.1fGB"%(price, data) for price, data in p))
    html = "<html><head><style>th {{text-align: left;}}</style></head>"\
            "<body>Best price: £{0} for {1}GB <table style='width:100%'><th>Price</th><th>Data</th>{2}</table></body></html>"\
        .format(best_price[0], best_price[1],
         "\n".join("<tr%s><td>£%.2f</td><td>%.1fGB</td><tr>"%(" style='background-color:red'" if (price, data) not in prev_offers else "", price, data) for price, data in p))

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def main():
    password = sys.argv[1]
    model = sys.argv[2]

    old_raw = ""
    prices = []
    prev_offers = set()
    best_offer = (math.inf, 0)

    while True:
        fp = urllib.request.urlopen("https://www.mobiles.co.uk/{}?sort=total_cost_after_cashback_asc&filter_tariff_data%5B%5D=>%3D3000%2C-1".format(model))
        mybytes = fp.read()

        html_raw = mybytes.decode("utf8")
        fp.close()

        prices = []
        for price_str in re.findall('£.*total cost', html_raw):
            prices.append(float(price_str.replace(" total cost", "").replace("£", "")))
        data = []
        for data_str in re.findall('<strong>\d*GB</strong>', html_raw):
            data.append(float(re.findall("\d+", data_str)[0]))
        offers = list(zip(prices, data))
        print(*offers)

        if html_raw != old_raw:
            better = False
            for offer in offers:
                if offer[0] < best_offer[0]:
                    better = True
                    best_offer = offer
            send_email(offers, best_offer, better, prev_offers, password, model)

            print("Prices updated")
            
        old_raw = html_raw
        prev_offers.union(set(offers))
        print("Website checked...")
        sleep(randint(5, 10))


if __name__ == "__main__":
    main()