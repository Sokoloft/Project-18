# BSD 2-Clause License
# Copyright (c) 2023, Sokoloft

# import
import os, wifi, socketpool, ssl, alarm, board, simpleio, time
import adafruit_requests as requests

# Get user set time values
b_time = [int(value) for value in os.getenv('beeper_time').split(',')]
n_time = [int(value) for value in os.getenv('ntfy_time').split(',')]


# add seconds, minutes, hours, and days together
def add_val(s, m, h, d):
    return s + m + h + d


# multiplication to determine minutes, hours and days
bval = add_val(b_time[0], b_time[1] * 60, b_time[2] * 3600, b_time[3] * 86400)
nval = add_val(n_time[0], n_time[1] * 60, n_time[2] * 3600, n_time[3] * 86400)
ntfy = nval + bval

print("Last alarm state =", alarm.wake_alarm)  # prints last alarm state
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + bval)

if alarm.wake_alarm is None:
    # power on tone

    # simpleio
    print("Power on tone")
    simpleio.tone(board.GP18, 1000, duration=0.5)

    # wait for timer
    print("Sleeping for", bval, "seconds...")
    # start deep sleep
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

else:
    print("Push NTFY in", nval, "seconds...")
    while True:
        print("Beeping...")
        simpleio.tone(board.GP18, 1000, duration=1)
        time.sleep(1)
        bval += 1
        print(bval, "out of", ntfy)
        while bval == ntfy:
            # connect to your SSID
            wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
            pool = socketpool.SocketPool(wifi.radio)
            requests = requests.Session(pool, ssl.create_default_context())

            bval += 1
            requests.post(os.getenv('ntfy_url') + os.getenv('ntfy_key'),
                          data=os.getenv('ntfy_message'),
                          headers={
                              "Title": os.getenv('ntfy_title'),
                              "Priority": os.getenv('ntfy_prio'),
                              "Tags": os.getenv('ntfy_tag'),
                          })
            print("NTFY Notification sent")
            wifi.radio.stop_station()
