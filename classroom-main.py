import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime


def add(key, dic, count):
    if " " in key:
        key = key.split()[0]
    if key in dic:
        dic[key] += count
    else:
        dic[key] = count


def scrape(url, day=datetime.today().strftime('%Y-%m-%d')):  # Make day preset to current date
    # Setup html and get response
    response = requests.get(url)
    html = response.content
    soup = bs(html, "lxml")
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

    # for i in relevant_bookings:
    #     print(i)

    # Find all occurrences of the classroom
    for booking in relevant_bookings:
        for info in booking:
            if "MH:" in info:
                add("MH:" + info.split("MH:")[1], no_of_bookings, 1)
                add("MH:" + info.split("MH:")[1], times_booked, " " + " ".join(booking[0].split()[1:4]))

    # Get rid of first whitespace
    times_booked["MH:362A"] = times_booked["MH:362A"][1:]

    print(f"Current day: {day}")
    print(no_of_bookings)
    print(times_booked)
    print(sorted(no_of_bookings.items(), key=lambda x: x[1]))

    # Find all the lowest values
    min_val = min(no_of_bookings.values())
    res = [key for key, value in no_of_bookings.items() if value == min_val]
    print(res)


'''
use dictionary with keys for every room to be searched
go through the day and use findall(bookingDiv) and loop through their classrooms
add to the dictionary and present all 0 then 1 etc
use find(bookingDiv) (class) on every day from classrooms 
'''


def main():
    # Level 3 and 2
    url = "https://cloud.timeedit.net/lu/web/lth1/ri16666565000YQQ65Z652500Xy7Y4810g75g0X6Y65ZW6465X2Q10X126004Y745502461Y5767X54Y055X06XY5042952511Y6476X8647455205XY245761X09075522XY82971Y4545Y4X6615507257904YY63X1141X04632025YX64516406674X5Y702746YX30Q20456Y794756.html"
    # For all level 3
    #   url = "https://cloud.timeedit.net/lu/web/lth1/ri16666565000YQQ65Z652500Xy7Y4810g75g0X6Y65ZW6465X2Q10X126004Y745502461Y5767X54Y055X06XY5042952511Y6476X8647455205XY245761X09075522XY82971Y4545Y4X66155072Y70445Y6251160X7Q7.html"
    # initial test
    #    url = "https://cloud.timeedit.net/lu/web/lth1/ri16666565000YQQ65Z652500Xy7Y4810g75g0X6Y65ZW6465X2Q15976047QY.html"
    scrape(url)


if __name__ == "__main__":
    main()
