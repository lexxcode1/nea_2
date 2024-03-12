import unittest

import numpy as np

from helper import table_exists, row_exists, valid_variable, validate_types


class TestNormalGoodnessOfFitTest(unittest.TestCase):
   def __init_distribute(self):
       self.distribute = np.random.normal(0, 1, 1000)