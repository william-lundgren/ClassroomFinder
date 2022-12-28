import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import smtplib
import ssl
from keep_alive import keep_alive
from os import getenv
import schedule
import time


def send_mail(receiver_email, content, day):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender_email = getenv("sender")
    password = getenv("password")
    message = f"""\
Subject: Dagens bra klassrum ({day}). Ha en fin dag.

{content}"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def add(key, dic, count):
    # Add to dictionary depending on if key already exists
    if " " in key:
        key = key.split()[0]
    if key in dic:
        dic[key] += count
    else:
        dic[key] = count


def scrape(url, day):  # Make day preset to current date
    # Setup html and get response
    response = requests.get(url)
    html = response.content
    soup = bs(html, "html.parser")
    bookings = soup.find_all("div", "bookingDiv")

    # take the interesting info from bookings and divide by category
    bookings = [booking.get("title").split(",") for booking in bookings]

    # Bookings on current day
    relevant_bookings = []

    # Get the relevant bookings
    for booking in bookings:
        # check if correct date and add
        if booking[0].split()[0] == day:
            relevant_bookings.append(booking)

    # Hours that the classroom is busy
    times_booked = {}

    # Number of bookings per classroom
    no_of_bookings = {}

    # All possible classrooms
    classrooms = ["MH:227",
                  "MH:228",
                  "MH:229",
                  "MH:309A",
                  "MH:309B",
                  "MH:309C",
                  "MH:331",
                  "MH:332A",
                  "MH:332B",
                  "MH:333",
                  "MH:362A",
                  "MH:362B",
                  "MH:362C",
                  "MH:362D"]

    # Set all possible values, maybe make it customizable for more classrooms
    for classroom in classrooms:
        add(classroom, no_of_bookings, 0)

    # Find all occurrences of the classroom
    for booking in relevant_bookings:
        for info in booking:
            if "MH:" in info:
                add("MH:" + info.split("MH:")[1], no_of_bookings, 1)
                add("MH:" + info.split("MH:")[1], times_booked, " " + " ".join(booking[0].split()[1:4]))

    # Get rid of first whitespace
    for ele in times_booked:
        if times_booked[ele][0] == " ":
            times_booked[ele] = times_booked[ele][1:]

    print(f"Current day: {day}")
#    for i in times_booked:
#        print(i, times_booked.get(i))
    sorted_list = sorted(no_of_bookings.items(), key=lambda x: x[1])

    sorted_string = ""
    for i in sorted_list:
        sorted_string += f"{i[1]} {i[0]} {times_booked.get(i[0])}\n"

    # Find all the lowest values
    min_val = min(no_of_bookings.values())
    #res = [key for key, value in no_of_bookings.items() if value == min_val]

    return sorted_string


'''
use dictionary with keys for every room to be searched
go through the day and use findall(bookingDiv) and loop through their classrooms
add to the dictionary and present all 0 then 1 etc
use find(bookingDiv) (class) on every day from classrooms 
'''


def setup():
    # LP 2
    url = "https://cloud.timeedit.net/lu/web/lth1/ri16W65057506XQQ55ZZ767005yYW64856Y05506Q65116X65262902465144XY70016755X0Y5Y247X1052252X5176456060X49Y54457Y6557104X670Y5822Y1450862X46Y47X6095X72551501Y40Y014XX562424027Y546165X36743997162730X504YY5X4625676047QY.html"
    # Level 3 and 2
    # url = "https://cloud.timeedit.net/lu/web/lth1/ri16666565000YQQ65Z652500Xy7Y4810g75g0X6Y65ZW6465X2Q10X126004Y745502461Y5767X54Y055X06XY5042952511Y6476X8647455205XY245761X09075522XY82971Y4545Y4X6615507257904YY63X1141X04632025YX64516406674X5Y702746YX30Q20456Y794756.html"
    # For all level 3
    # url = "https://cloud.timeedit.net/lu/web/lth1/ri16666565000YQQ65Z652500Xy7Y4810g75g0X6Y65ZW6465X2Q10X126004Y745502461Y5767X54Y055X06XY5042952511Y6476X8647455205XY245761X09075522XY82971Y4545Y4X66155072Y70445Y6251160X7Q7.html"
    ''
#    day = datetime.today().strftime('%Y-%m-%d')
    day = "2022-12-13"
    res = scrape(url, day)

    for mail in getenv("password").split(","):
        send_mail(mail, res, day)


def main():
    keep_alive()

    #schedule.every(3).minutes.do(setup)
    schedule.every().day.at("07:30").do(setup)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
