import unittest

def suite():
    return unittest.TestLoader().discover("pypobot.tests", pattern="*.py")
