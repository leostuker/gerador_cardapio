import os
import urllib.request

fonts = {
    'Martel-Bold.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/martel/Martel-Bold.ttf',
    'Assistant-Regular.ttf': 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf',
    'Assistant-Bold.ttf': 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf',
    'Balmy.ttf': 'https://raw.githubusercontent.com/google/fonts/main/apache/permanentmarker/PermanentMarker-Regular.ttf'
}

os.makedirs('static/fonts', exist_ok=True)
for name, url in fonts.items():
    path = os.path.join('static/fonts', name)
    if not os.path.exists(path):
        try:
            print(f"Downloading {name}...")
            urllib.request.urlretrieve(url, path)
        except Exception as e:
            print(f"Failed to download {name}: {e}")
