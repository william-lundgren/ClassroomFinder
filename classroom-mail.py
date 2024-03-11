import requests
from bs4 import BeautifulSoup as bs
import smtplib
import ssl
import os
import schedule
import time
from datetime import datetime
from date import find_week_day


def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def send_mail(receiver_email, content, day):
    # Setup and send mail
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("sender_mail")
    password = os.getenv("mail_password")
    message = f"""\
Subject: Dagens bra klassrum ({day}). Ha en fin dag.

{content}"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        print("Logging in!", get_time())
        server.login(sender_email, password)

        print("Sending mail", get_time())
        server.sendmail(sender_email, receiver_email, message)

        print("Mail sent!", get_time())

def add(key, dic, count, allow_new):
    # Add to dictionary depending on if key already exists
    if " " in key:
        key = key.split()[0]
    if key in dic:
        dic[key] += count
    elif allow_new:
        dic[key] = count


def scrape(url, day):
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
    classrooms = [
        "MH:227", "MH:228", "MH:229", "MH:309A", "MH:309B", "MH:309C",
        "MH:331", "MH:332A", "MH:332B", "MH:333", "MH:362A", "MH:362B",
        "MH:362C", "MH:362D"
    ]

    # Set all possible values, maybe make it customizable for more classrooms
    for classroom in classrooms:
        add(classroom, no_of_bookings, 0, True)

    # Find all occurrences of the classroom
    for booking in relevant_bookings:
        for info in booking:
            if "MH:" in info:
                start_time = "".join(booking[0].split()[1:4])
                # Only add if start time is before 17
                if int(start_time[:2]) < 17:
                    add("MH:" + info.split("MH:")[1], no_of_bookings, 1, False)
                    add("MH:" + info.split("MH:")[1], times_booked,
                        " " + " ".join(booking[0].split()[1:4]), True)

    # Get rid of first whitespace
    for ele in times_booked:
        if times_booked[ele][0] == " ":
            times_booked[ele] = times_booked[ele][1:]

    print(f"Current day: {day}")
    sorted_list = sorted(no_of_bookings.items(), key=lambda x: x[1])

    # Large string of format {no of bookings} {classroom} {times it is booked} sorted by no of bookings
    sorted_string = ""
    for i in sorted_list:
        sorted_string += f"{i[1]} {i[0]} {times_booked.get(i[0])}\n"
        # print(i[0], times_booked.get(i[0]))

    # Get rid of final newline character
    sorted_string = sorted_string[:-1]

    # Find all the lowest values
    # min_val = min(no_of_bookings.values())
    # res = [key for key, value in no_of_bookings.items() if value == min_val]

    return sorted_string


'''
use dictionary with keys for every room to be searched
go through the day and use findall(bookingDiv) and loop through their classrooms
add to the dictionary and present all 0 then 1 etc
use find(bookingDiv) (class) on every day from classrooms 
'''


def empty(day):
    # Check for leading 0s, if all are then its empty
    for classroom in day.split("\n"):
        if classroom[0] != "0":
            return False
    return True


def setup(person, exclusions):
    # Schedule url for every classroom
    url = "https://cloud.timeedit.net/lu/web/lth1/ri17666530000YQQ85Z552500Xy7Y3810g76g5X6Y65ZW8465X2Q10X126004Y745502461Y5767X54Y055X06XY5042952511Y6476X8647455205XY245761X09075522XY82971Y4545Y4X6615507257904YY63X1141X04632025YX64516406674X5Y702746YX30Q20456Y794756.html"

    # day of format YYYY-MM-DD
    day = datetime.today().strftime('%Y-%m-%d')

    res = scrape(url, day)

    weekend = ["Saturday", "Sunday"]

    # Only send mail if there are things scheduled
    if not empty(res):
        if person == "normal_time":
            for mail in os.getenv("normalmails").split(","):
                # Check that they want mail on weekend
                if not (any(exclusion == main for exclusion in exclusions)
                        and find_week_day(day) not in weekend):
                    print("Sending email to:", mail)
                    send_mail(mail, res, day)
        else:
            for mail in os.getenv("specmails").split(","):
                if person in mail:
                    if not (any(exclusion == main for exclusion in exclusions)
                            and find_week_day(day) not in weekend):
                        print("Sending email to:", mail)
                        send_mail(mail, res, day)
    else:
        print("Empty day:", day)


def main():
    print("Starting server!")
    print(datetime.now())

    wanted_times = {"eric": "06:00", "normal_time": "14:50"}

    weekend_exclusion = ["ax", "em", "wille"]

    for key in wanted_times.keys():
        wanted_time = wanted_times[key]
        print(wanted_time)
        schedule.every().day.at(wanted_time).do(setup, key, weekend_exclusion)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
