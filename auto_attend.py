import os
import http.cookiejar
import urllib
import time
import json
import pytz
import datetime


def submit_attendance_code(username, password, year, month, day, attCode, uniqueId, actId):
    attStart = reformat_date_time_for_post(year, month, day, hour, minute)
    attEnd = reformat_date_time_for_post(year, month, day, hour + 1, minute)

    url = 'https://timetables.liverpool.ac.uk/services/register-attendance-student'

    data = {'Username': username,
            'Password': password,
            'attCode': attCode,
            'attCodeInput': attCode,
            'uniqueId': uniqueId,
            'actId': actId,
            'attStart': attStart,
            'attEnd': attEnd,
            'location': ''
            }
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

    req = urllib.request.Request(url, headers=headers, data=post_data)

    resp = opener.open(req)

    result = resp.read().decode('utf-8')
    if 'Username:' in result:
        result = 'password error'

    return result


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


def reformat_date_time_for_cookies(year, month, day, hour, minute):
    year_str = str(year)
    month_str = force_number_two_digits(month)
    day_str = force_number_two_digits(day)
    hour_str = force_number_two_digits(hour)
    minute_str = force_number_two_digits(minute)

    result = year_str + '-' + month_str + '-' + day_str + 'T' + hour_str + ':' + minute_str
    return result


def reformat_date_time_for_post(year, month, day, hour, minute):
    year_str = str(year)
    month_str = force_number_two_digits(month)
    day_str = force_number_two_digits(day)
    hour_str = force_number_two_digits(hour)
    minute_str = force_number_two_digits(minute)

    result = day_str + '/' + month_str + '/' + year_str + ' ' + hour_str + ':' + minute_str
    return result


def extract_info_from_html(html, date_time, attribute):
    html_json_load = json.loads(html)
    result = ''
    for one_class in html_json_load:
        if one_class['start'] == date_time:
            result = one_class[attribute]
        else:
            continue

    return result


def main_program():
    username = os.environ['username']
    password = os.environ['password']
    start_perf = time.perf_counter()

    time_zone = pytz.timezone('Europe/London')
    now = datetime.datetime.now(tz=time_zone)
    print(now)
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    while hour < 18:
        if minute < 50:
            time.sleep(300)
        else:
            # Get information
            html = simulate_login(username, password, year, month, day)
            formatted_date_time = reformat_date_time_for_cookies(year, month, day, hour, 0)
            attendance_code = extract_info_from_html(html, formatted_date_time, 'attendancecode')
            uniqueId = extract_info_from_html(html, formatted_date_time, 'uniqueid')
            actId = extract_info_from_html(html, formatted_date_time, 'activityid')
            activitydesc = extract_info_from_html(html, formatted_date_time, 'activitydesc')
            start = extract_info_from_html(html, formatted_date_time, 'start')

            print(html)
            print('formatted_date_time = ' + formatted_date_time)
            print('attendance_code = ' + attendance_code)
            print('uniqueId = ' + uniqueId)
            print('activitydesc = ' + activitydesc)
            print('start = ' + start)

            if attendance_code != '':
                print('***************************************************************')

                print(submit_attendance_code(username, password, year, month, day, attendance_code, uniqueId, actId))
                print('***************************************************************')
                print('The attendance code of ' + activitydesc + ' on ' + start + 'has been successfully submitted.')

            time.sleep(1800)

        now = datetime.datetime.now(tz=time_zone)
        print(now)
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute

        now_perf = time.perf_counter()
        running_time = now_perf - start_perf
        print('running time = ' + str(running_time))
        if running_time > 18000:
            break


def main():
    main_program()

if __name__ == '__main__':
    main()
