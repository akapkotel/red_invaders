import os
import unittest
from simple_arcade_menu import *

path = os.path.dirname(os.path.abspath(__file__))
# required to pass arcade.Window instance to some methods and classes:
dummy = arcade.Window


class TestSimpleArcadeMenu(unittest.TestCase):
    """"""


if __name__ == '__main__':
    dummy()
    unittest.main()
