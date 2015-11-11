import unittest

import pandas as pd
import numpy as np

from progressivis import *
from progressivis.core.changemanager import ChangeManager, NIL

class TestChangeManager(unittest.TestCase):
    def test_changemanager(self):
        cm = ChangeManager()
        self.assertEqual(cm.last_run, 0)
        self.assertEqual(cm.created_length(), 0)
        self.assertEqual(cm.updated_length(), 0)
        self.assertEqual(cm.deleted_length(), 0)

        df = pd.DataFrame({'a': [ 1, 2, 3],
                           Module.UPDATE_COLUMN: [ 1, 1, 1 ]})
        now = 1
        cm.update(now, df)
        self.assertEqual(cm.last_run, now)
        self.assertEqual(cm.next_created(),slice(0, 3))
        self.assertEqual(cm.updated_length(), 0)
        self.assertEqual(cm.deleted_length(), 0)

        now = 2
        df = df.append(pd.DataFrame({'a': [ 4], Module.UPDATE_COLUMN: [ now ]}),
                       ignore_index=True)
        cm.update(now, df)
        self.assertEqual(cm.last_run, now)
        self.assertEqual(cm.next_created(), slice(3,4))
        self.assertEqual(cm.updated_length(), 0)
        self.assertEqual(cm.deleted_length(), 0)
        
        now = 3
        df = df.append(pd.DataFrame({'a': [ 5], Module.UPDATE_COLUMN: [ now ]}),
                       ignore_index=True)
        cm.update(now, df)
        self.assertEqual(cm.last_run, now)
        self.assertEqual(cm.next_created(),slice(4, 5))
        self.assertEqual(cm.updated_length(), 0)
        self.assertEqual(cm.deleted_length(), 0)
        
        now = 4
        df2 = df[df.index != 2] # remove index==2 
        cm.update(now, df2)
        self.assertEqual(cm.last_run, now)
        self.assertEqual(cm.created_length(), 0)
        self.assertEqual(cm.updated_length(), 0)
        self.assertEqual(cm.next_deleted(),slice(2,3))


if __name__ == '__main__':
    unittest.main()
