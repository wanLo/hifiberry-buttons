#!/usr/bin/env python

import asyncio
import websockets
import json
from gpiozero import Button
from signal import pause
import requests
import os

async def playPauseDLF():
    ws = await websockets.connect("ws://localhost", subprotocols=["beocreate"])
    print("ws initialized")
    await ws.send("{\"target\":\"sources\",\"header\":\"getSources\"}")
    answer = await ws.recv()
    sources = json.loads(answer)["content"]["sources"]

    playing = False
    for source in sources:
        if (source != "radio" and source != "music" and sources[source]["playerState"] == "playing"):
            playing = True
    if (not playing):
        print("starting DLF ...")
       	os.system("aplay /opt/buttons/ping.wav")
        await ws.send("{\"header\":\"play\",\"content\":{\"URL\":\"https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac\",\"stationName\":\"Deutschlandfunk\"},\"target\":\"radio\"}")
    else:
       	print("stopping source ...")
       	await ws.send("{\"target\":\"now-playing\",\"header\":\"transport\",\"content\":{\"action\":\"playPause\"}}")
    await ws.close()

def dlf_handler():          
    loop = asyncio.new_event_loop()   
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.ensure_future(playPauseDLF()))
    loop.close()

def volume_handler(value):
    vol_string = "%+d" % value
    data = "{\"percent\":\"" + vol_string + "\"}" 
    response = requests.post("http://localhost:81/api/volume", headers={"Content-Type":"application/json"}, data=data)
    print(response.json())

dlf_button = Button(22, bounce_time=0.005)
up_button = Button(17, bounce_time=0.005)
down_button = Button(27, bounce_time=0.005)

dlf_button.when_pressed = dlf_handler
up_button.when_pressed = lambda: volume_handler(5)
down_button.when_pressed = lambda: volume_handler(-5)

pause()

