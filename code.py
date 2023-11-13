# BSD 2-Clause License
# Copyright (c) 2023, Sokoloft

# import
import os, wifi, socketpool, ssl, alarm, board, simpleio, time
import adafruit_requests as requests

#  connect to your SSID
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))

# for wifi
pool = socketpool.SocketPool(wifi.radio)
requests = requests.Session(pool, ssl.create_default_context())

# prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

# Get user set values & conversions
push_ntfy_url = os.getenv('push_ntfy_url')
push_ntfy_key = os.getenv('push_ntfy_key')
push_ntfy_title = os.getenv('push_ntfy_title')
push_ntfy_message = os.getenv('push_ntfy_message')
push_ntfy_prio = os.getenv('push_ntfy_prio')
push_ntfy_tag = os.getenv('push_ntfy_tag')
seconds = os.getenv('seconds')
minute = os.getenv('minutes') * 60
hour = os.getenv('hours') * 3600
day = os.getenv('days') * 86400
val = seconds + minute + hour + day
push_ntfy = os.getenv('push_ntfy') + val

print(alarm.wake_alarm)
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + val)

if alarm.wake_alarm == None:
    # power on tone

    # simpleio
    print("Power on tone")
    simpleio.tone(board.GP18, 1000, duration=0.5)

    # wait for timer
    print("Sleeping for", val, "seconds...")
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

else:
    while True:
        print("Beeping...")
        simpleio.tone(board.GP18, 1000, duration=1)
        time.sleep(1)
        val += 1
        print(val)
        while val == push_ntfy:
            val += 1
            requests.post(push_ntfy_url + push_ntfy_key,
                          data=push_ntfy_message,
                          headers={
                              "Title": push_ntfy_title,
                              "Priority": push_ntfy_prio,
                              "Tags": push_ntfy_tag,
                          })
            print("NTFY Notification sent")
