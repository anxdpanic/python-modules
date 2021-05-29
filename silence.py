"""
    Mute replacement
        - Set volume to 1 instead Muting (no onscreen 'Muted' indicator)
        - Saves volume before setting volume to 1
        - On consecutive run volume will be reset to saved volume

    Place this file in the Kodi userdata folder (https://kodi.wiki/view/Userdata#Location)
    Create a key bind in Kodi to run this script (https://kodi.wiki/view/Keymap)

    - Keymap action: RunScript("special://userdata/silence.py")
    - example keymap:
        '''
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <keymap>
            <global>
                <keyboard>
                    <f1 mod="ctrl,alt">RunScript("special://userdata/silence.py")</f1>
                </keyboard>
            </global>
        </keymap>
        '''

"""


import json

import xbmc
import xbmcgui

WINDOW = xbmcgui.Window(10000)
WINDOW_PROPERTY = 'silence_script-volume'


def json_request(payload):
    return json.loads(xbmc.executeJSONRPC(json.dumps(payload)))


def set_volume(volume):
    request_payload = {
        "jsonrpc": "2.0",
        "method": "Application.SetVolume",
        "id": 1,
        "params": {
            "volume": int(volume)
        }
    }

    response_payload = json_request(request_payload)
    return 'error' not in response_payload


def get_volume():
    request_payload = {
        "jsonrpc": "2.0",
        "method": "Application.GetProperties",
        "id": 1,
        "params": {
            "properties": ["volume"]
        }
    }

    response_payload = json_request(request_payload)
    return response_payload.get('result', {}).get('volume', 75)


if __name__ == '__main__':
    property_volume = WINDOW.getProperty(WINDOW_PROPERTY)
    try:
        property_volume = int(property_volume)
    except ValueError:
        property_volume = None

    print('Saved volume: %s' % property_volume)

    if isinstance(property_volume, int):
        print('Setting volume: %s' % property_volume)
        set_volume(property_volume)
        WINDOW.clearProperty(WINDOW_PROPERTY)
    else:
        current_volume = get_volume()
        WINDOW.setProperty(WINDOW_PROPERTY, str(current_volume))
        print('Setting volume: 1 | Saved volume: %s' % current_volume)
        set_volume(1)
