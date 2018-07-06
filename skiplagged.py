# -*- coding: utf-8 -*-
# @Author: Shen Huang
# @Date:   2018-06-15 16:18:55
# @Last Modified by:   Shen Huang
# @Last Modified time: 2018-07-02 10:50:11
import base64
import json
import time as tt
import traceback
import requests
import logging
import logging.config
import IPython
import datetime, pytz, time


logger = logging.getLogger('main.Skiplagged')


class DateTime:
    def __init__(self, timezone, epoch):
        self.timezone = timezone
        self.epoch = epoch
        timezoneobject = pytz.timezone(timezone)
        datetimeobject = datetime.datetime.fromtimestamp(self.epoch)
        self.datetime = timezoneobject.localize(datetimeobject)

    def hour(self):
        return self.datetime.hour


class Skiplagged():
    SKIPLAGGED_API = 'https://skiplagged.com/api/'
    SPECIFIC_API = None
    PROFILE = None
    PROFILE_RAW = None

    def __init__(self):
        self.interval = 60  # 60 s one calll
        self.request_id = 1530553743443  # request id will be add one by one
        self.place_from = 'SEA'
        self.place_to = 'SJC'
        self.date_depart = '2018-08-24'
        self.date_return = ''
        self.depart_flight = 'AS328'
        self.depart_flights_numbers = [328, 348, 7009, 6785, 5717, 322]
        self.return_flight = 'DL5728'
        self.return_flights_numbers = [5728, 368]

    def get_history_url(self, flight_type, date):
        self.request_id += 1
        url = self.SKIPLAGGED_API + 'price_history.php?'
        if flight_type == 'depart':
            url += 'from={}&to={}&depart={}&return={}&flights={}&_={}'.format(self.place_from, self.place_to, date, self.date_return, self.depart_flight, self.request_id)  # noqa
        else:
            url += 'from={}&to={}&depart={}&return={}&flights={}&_={}'.format(self.place_to, self.place_from, date, self.date_return, self.return_flight, self.request_id)  # noqa
        return url

    def get_search_url(self, flight_type, date):
        self.request_id += 1
        url = self.SKIPLAGGED_API + 'search.php?'
        if flight_type == 'depart':
            url += 'from={}&to={}&depart={}&return={}&poll=true&format=v2&_={}'.format(self.place_from, self.place_to, date, self.date_return, self.request_id)  # noqa
        else:
            url += 'from={}&to={}&depart={}&return={}&poll=true&format=v2&_={}'.format(self.place_to, self.place_from, date, self.date_return, self.request_id)  # noqa
        return url

    def find_price(self, flight_numbers, resp):
        data = json.loads(resp.text)
        flight_data = data['flights']
        price_data = data['itineraries']['outbound']
        min_price = 100000000
        min_flight_num = None
        for flight_number in flight_numbers:
            key_val = None
            for key in flight_data:
                if flight_data[key]['segments'][0]['flight_number'] == flight_number:
                    # print(key, flight_data[key])
                    key_val = key
                    break
            for x in price_data:
                if x['flight'] == key_val:
                    # print(x['one_way_price'] / 100)
                    if min_price > x['one_way_price'] / 100:
                        min_price = min(min_price, x['one_way_price'] / 100)
                        min_flight_num = flight_number
        return min_price, min_flight_num

    def _test(self):
        depart_day = datetime.datetime(2018, 7, 6)
        return_day = datetime.datetime(2018, 7, 9)
        min_tot = 100000000
        min_depart_date = None
        for i in range(19):
            try:
                date_depart = '{}-{:02}-{:02}'.format(depart_day.year, depart_day.month, depart_day.day)
                date_return = '{}-{:02}-{:02}'.format(return_day.year, return_day.month, return_day.day)
                resp = requests.get(self.get_search_url('depart', date_depart))
                depart_price, depart_flight_num = self.find_price(self.depart_flights_numbers, resp)
                resp = requests.get(self.get_search_url('return', date_return))
                # IPython.embed()
                return_price, return_flight_num = self.find_price(self.return_flights_numbers, resp)
                if min_tot > depart_price + return_price:
                    min_depart_date = date_depart
                    min_tot = min(min_tot, depart_price + return_price)
                print("{}:{},{},{}".format(date_depart, depart_price, return_price, depart_price + return_price))
                print(depart_flight_num, return_flight_num)
                depart_day += datetime.timedelta(days=7)
                return_day += datetime.timedelta(days=7)
                tt.sleep(1)

            except Exception:
                print("post exception {}".format(traceback.format_exc()))
                print(date_depart, date_return)
                # IPython.embed()
                break
                tt.sleep(1)
        print(min_tot, min_depart_date)
        print(self.request_id)

    # Calls
    def _call(self):
        depart_day = datetime.datetime(2018, 7, 6)
        return_day = datetime.datetime(2018, 7, 9)
        for i in range(19):
            try:
                date_depart = '{}-{:02}-{:02}'.format(depart_day.year, depart_day.month, depart_day.day)
                date_return = '{}-{:02}-{:02}'.format(return_day.year, return_day.month, return_day.day)
                resp = requests.get(self.get_history_url('depart', date_depart))
                depart_price = json.loads(resp.text)['history'][0]['price'] / 100
                resp = requests.get(self.get_history_url('return', date_return))
                return_price = json.loads(resp.text)['history'][0]['price'] / 100
                print("{}:{},{},{}".format(date_depart, depart_price, return_price, depart_price + return_price))
                depart_day += datetime.timedelta(days=7)
                return_day += datetime.timedelta(days=7)
                tt.sleep(1)

            except Exception:
                print("post exception {}".format(traceback.format_exc()))
                print(date_depart, date_return)
                IPython.embed()
                break
                tt.sleep(1)
        print(self.request_id)
