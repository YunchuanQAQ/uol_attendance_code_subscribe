import os
import urllib
import http.cookiejar
import json
import datetime


def simulate_login(username, password, year, month, day):
    year_str = str(year)
    if month < 10:
        month_str = '0' + str(month)
    else:
        month_str = str(month)
    if day < 10:
        day_str = '0' + str(day)
    else:
        day_str = str(day)

    url = 'https://timetables.liverpool.ac.uk/services/get-events?start=' + year_str + '-' + month_str + '-' + day_str + '&end=' + year_str + '-' + month_str + '-' + day_str

    data = {'Username': username,
            'Password': password}
    post_data = urllib.parse.urlencode(data).encode('utf-8')

    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    login_url = 'https://timetables.liverpool.ac.uk/account?returnUrl=%2F'

    req = urllib.request.Request(login_url, headers=headers, data=post_data)

    cookie = http.cookiejar.CookieJar()

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))

    try:
        resp = opener.open(req)
    except Exception:
        print('There might be some problem with your network.')
        print('Check you network setting and rerun the program.')
        quit()

    req = urllib.request.Request(url, headers=headers)

    resp = opener.open(req)

    result = resp.read().decode('utf-8')
    if 'Username:' in result:
        result = 'password error'

    return result


def force_number_two_digits(number):
    if number < 10:
        result = '0' + str(number)
    else:
        result = str(number)

    return result


def reformat_date_time(year, month, day, hour, minute):
    year_str = str(year)
    month_str = force_number_two_digits(month)
    day_str = force_number_two_digits(day)
    hour_str = force_number_two_digits(hour)
    minute_str = force_number_two_digits(minute)

    result = year_str + '-' + month_str + '-' + day_str + 'T' + hour_str + ':' + minute_str
    return result


def get_class_info(html, date_time):
    html_json_load = (json.loads(html))
    result_list = []
    for one_class in html_json_load:
        if one_class['start'] == date_time:
            result_list.append(one_class['start'])
            result_list.append(one_class['activitydesc'])
            result_list.append(one_class['attendancecode'])
        else:
            continue
    return result_list


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")


sender_email = os.environ['send']
sender_password = os.environ['sender_password']
recipient = os.environ['recipient']
username = os.environ['username']
password = os.environ['password']

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour

html = simulate_login(username, password, year, month, day)
formatted_date_time = reformat_date_time(year, month, day, hour, 0)

class_info = get_class_info(html, formatted_date_time)
start_time = class_info[0]
class_name = class_info[1]
attendance_code = class_info[2]

if attendance_code != '':
    send_email(sender_email, sender_password, recipient, 'Attendance code found', attendance_code)
else:
    print('no found')
