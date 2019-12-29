import os
from dotenv import load_dotenv

from balaland import balaland_game


def play():
    load_dotenv()
    BalalandGame = balaland_game.BalalandGame()
    while True:
        BalalandGame.update()
        BalalandGame.clock.tick(int(os.environ.get('BL_CLOCK_TICK')))


if __name__ == '__main__':
    play()
