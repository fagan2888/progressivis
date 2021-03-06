from __future__ import absolute_import, division, print_function

from progressivis.core.utils import indices_len, fix_loc
from progressivis.table.module import TableModule
from progressivis.table.table import Table
from progressivis.core.slot import SlotDescriptor
from progressivis.core.synchronized import synchronized
import time
import numpy as np
import pandas as pd

import logging
logger = logging.getLogger(__name__)


class Counter(TableModule):
    def __init__(self, **kwds):
        self._add_slots(kwds,'input_descriptors',
                        [SlotDescriptor('table', type=Table, required=True)])
        super(Counter, self).__init__(**kwds)
        self.default_step_size = 10000

    def is_ready(self):
        if self.get_input_slot('table').created.any():
            return True
        return super(Counter, self).is_ready()

    @synchronized
    def run_step(self,run_number,step_size,howlong):
        dfslot = self.get_input_slot('table')
        dfslot.update(run_number)
        if dfslot.updated.any() or dfslot.deleted.any():
            dfslot.reset()
            if self._table is not None:
                self._table.resize(0)
            dfslot.update(run_number)
        indices = dfslot.created.next(step_size) # returns a slice
        steps = indices_len(indices)
        if steps==0:
            return self._return_run_step(self.state_blocked, steps_run=0)
        input_df = dfslot.data()
        data = pd.DataFrame(dict(counter=steps), index=[0])
        if self._table is None:
            self._table = Table(self.generate_table_name('counter'),
                                data=data,
#                                scheduler=self.scheduler(),
                                create=True)
        elif len(self._table)==0: # has been resetted
            self._table.append(data)
        else:
            self._table['counter'].loc[0] += steps
        return self._return_run_step(self.next_state(dfslot), steps_run=steps)
