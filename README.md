# HiFiberry Buttons

A short script that starts internet radio on a raspberry pi running [HiFiberryOS](https://github.com/hifiberry/hifiberry-os) at the touch of a button. Also, it adds two buttons for volume control. No additional hardware needed, just a raspberry pi, some buttons and cables.

## APIs
[HiFiberryOS](https://github.com/hifiberry/hifiberry-os) comes with the possibility to configure _interactions_ through [Beocreate2](https://github.com/bang-olufsen/create) which it uses as a web interface. However, these interactions are limited to serial communication or REST API calls. In order to use hardware buttons, additional hardware is required in both cases. Furthermore, it is currently not possible to start internet radio though _interactions_.

HiFiberryOS also exposes the [audiocontrol2 REST API](https://github.com/hifiberry/audiocontrol2/blob/master/doc/api.md) that can be used to play / pause a audio source or to switch sources. Again, starting a specific radio stream is not possible through the audiocontrol2 API.

Starting a radio stream can however easily be done in the Beocreate2 web interface. The web app uses a very talkative websocket to communicate with the server. A undocumented subprotocol called _beocreate_ is used on the websocket, which we can however easily have a look at with Firefox dev tools. Thus, we can setup our own websocket connection to start a internet radio stream.

## Implementation
The main script initializes three buttons with `gpiozero.Button` and than sets up appropriate callbacks for when each of the buttons is pressed.

Since _websockets_ uses asyncio, the radio button must first create an event loop in which the websocket connection can than be run. We ask through the websocket, whether any (main) source is currently playing. If so, we pause the source. Otherwise (if the hifiberry was silent), we start a [Deutschlandfunk radio stream](https://www.deutschlandfunk.de/unsere-live-streams.2396.de.html).

Since it takes some time for the radio stream to buffer, a sound is played to give feedback that the stream is now buffering, after the radio button is pressed. Such sounds can be found e.g. on [freesound](https://freesound.org/).

The volume control is performed through the audiocontrol2 REST API, since it support increasing / decreasing volume in percentage points and is more reliable than the beocreate2 service.

## Installation
First, setup a custom root password through the beocreate web interface. Then you can access your raspberry running HiFiberryOS through `ssh root@hifiberry.local` (or a different local name, if you have given it one).

Some additional python packages are needed for the script to run. Namely:
- [gpiozero]()
- [websockets]()

While you can't install them directly, they can be downloaded with curl from [pypi](https://pypi.org/) and than installed locally with pip.

The python script can be started on boot with a simple systemd service. This repo includes an example (`buttons.service`) that can be placed in `/usr/lib/systemd/system/` and than be activated and enabled.

Note that HiFiberryOS [uses Buildroot](https://github.com/hifiberry/hifiberry-os#adding-packages), so installation is not persistant and must be performed after each system upgrade. Or you could setup your own Buildroot build that includes a button control script.