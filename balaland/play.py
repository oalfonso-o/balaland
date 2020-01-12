import os
from dotenv import load_dotenv
load_dotenv()

from balaland import balaland_game  # noqa E402


def play():
    BalalandGame = balaland_game.BalalandGame()
    while True:
        BalalandGame.update()
        BalalandGame.clock.tick(int(os.environ.get('BL_CLOCK_TICK')))


if __name__ == '__main__':
    play()
