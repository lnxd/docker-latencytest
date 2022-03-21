import os
import argparse

import json
import re

import requests as rq
import pandas as pd


class StratumPing:
    def __init__(self, filename='pools.json'):
        self.file_read(filename)

    def file_read(self, filename):
        try:
            self.pools = json.loads(' '.join(open(filename, 'r').readlines()))
            return True
        except:
            self.pools = None
        return False

    def val_converter(self, value):
        try:
            number = re.findall(r'[0-9.]+', value)[0]
            string = value.replace(number, '').strip().lower()
            number = float(number)

            if string == 'ms':
                number /= 1000
            elif string == 'μs':
                number /= 1000000

            return number
        except:
            return None

    def get_ip(self, link, timeout=30):
        try:
            command = f'''timeout {timeout} ./stratum-ping -c 1 {link} | grep PING | sed -e "s/).*//" | sed -e "s/.*(//"'''

            return os.popen(command).read().strip()
        except:
            return None

    def get_location(self, ip_address):
        try:
            link = f'http://ip-api.com/json/{ip_address}?fields=country'
            if res := rq.get(link):
                return res.json()['country']
            return None
        except:
            return None

    def get_latency(self, link, count=10, timeout=30):
        try:
            command = f'''timeout {timeout} ./stratum-ping -c {count} {link} | tail -1 | awk 4'''

            return os.popen(command).read(
            ).strip().split()[-2].replace(',', '')
        except:
            return None

    def pipeline(self, count=10, timeout=30):
        self.all_data = []
        for pool, j in self.pools.items():
            per_pool = []
            for k in j.values():
                ip_address = self.get_ip(k, timeout)
                location = self.get_location(ip_address)
                latency = self.get_latency(k, count, timeout)

                temp = [pool, location, latency, ip_address, k]
                per_pool.append(temp)

            per_pool = sorted(per_pool, key=lambda x: self.val_converter(x[2]))
            self.all_data += per_pool

    def generate_result(self, output='output.csv'):
        columns = ['Pool', 'Geo', 'Latency', 'IP', 'Address']
        df = pd.DataFrame(self.all_data, columns=columns)
        df.to_csv(output,index=False)
        return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default='pools.json',
                        required=False, help='File path')
    parser.add_argument('--timeout', type=int, default=30,
                        required=False, help='Timeout for late response')
    parser.add_argument('--count', type=int, default=10,
                        required=False, help='Latency count of average')
    parser.add_argument('--output', type=str, default='output.csv',
                        required=False, help='Output csv filename')

    args = parser.parse_args()

    filename = args.file
    timeout = args.timeout
    count = args.count
    output = args.output

    my_obj = StratumPing(filename=filename)
    my_obj.pipeline(count=count, timeout=timeout)
    my_obj.generate_result(output)