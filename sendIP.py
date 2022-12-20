#!/usr/bin/env python3
# Copyright (c) 2022. 楊鵬. All Rights Reserved.
import os
import socket

import requests
from dotenv import load_dotenv

load_dotenv()
URL = "https://notify-api.line.me/api/notify"


def sendIP(ip: str):
    headers = {"Authorization": "Bearer " + os.environ["TOKEN"]}
    params = {"message": ip}
    r = requests.post(URL, headers=headers, params=params)
    print(r.text)


if __name__ == "__main__":
    connect_interface = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connect_interface.connect(("8.8.8.8", 80))
    ip_addr = connect_interface.getsockname()[0]
    connect_interface.close()
    message = f"IP Address: {ip_addr}"
    sendIP(message)
