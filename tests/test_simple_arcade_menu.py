import os
import unittest
from simple_arcade_menu import *

path = os.path.dirname(os.path.abspath(__file__))
dummy = arcade.Window  # required to pass arcade.Window instance to some methods and class constructors


class TestSimpleArcadeMenu(unittest.TestCase):
    """"""


if __name__ == '__main__':
    dummy()
    unittest.main()
