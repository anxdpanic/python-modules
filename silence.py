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
