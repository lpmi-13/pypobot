from unittest import TestCase
from util.text_utils import an_finder

class Text_Block_Tests(TestCase):
    def test_for_an_an(self):
        test_text = 'we have discussed an an outside perspective'
        found_pattern = an_finder(test_text)
        self.assertEqual(found_pattern, ' an an ')
