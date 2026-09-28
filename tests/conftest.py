import os

# Headless: kein Fenster, kein Audio – nötig für CI und Container.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
