"""
Dataflow Graph maintaining a graph of modules and implementing
commit/rollback semantics.
"""
from __future__ import absolute_import, division, print_function

import logging

from uuid import uuid4
import six
from collections import namedtuple

from .utils import ProgressiveError
from .scheduler import Scheduler
from .toposort import toposort

logger = logging.getLogger(__name__)

Slot = namedtuple('Slot', ['module', 'name'])

class Dataflow(object):
    """Class managing a Dataflow, a configuration of modules and slots
    constructed by the user to be run by a Scheduler.

    The contents of a Dataflow can be changed at any time without
    interfering with the Scheduler. To update the Scheduler, it should
    be validated and committed first.
    """
    default = None
    """
    Dataflow graph maintaining modules connected with slots.
    """
    def __init__(self, scheduler=None):
        if scheduler is None:
            scheduler = Scheduler.default
        assert scheduler is not None
        self.scheduler = scheduler
        self._modules = {}
        self._inputs = {}
        self._outputs = {}

    def generate_name(self, prefix):
        "Generate a name for a module given its class prefix."
        for i in range(1, 10):
            mid = '%s_%d' % (prefix, i)
            if mid not in self._modules:
                return mid
        return '%s_%s' % (prefix, uuid4())

    def __getitem__(self, name):
        return self._modules[name]

    def __contains__(self, name):
        return name in self._modules

    def add_module(self, module):
        "Add a module to this Dataflow."
        assert module.is_created()
        assert module.name not in self._inputs
        self._modules[module.name] = module
        self._inputs[module.name] = {}
        self._outputs[module.name] = {}

    def remove_module(self, module):
        "Remove the specified module"
        if isinstance(module, six.string_types):
            module = self._modules[module]
        module.terminate()
        del self._modules[module.name]
        self._remove_module_inputs(module.name)
        self._remove_module_outputs(module.name)

    def add_connection(self, output_module, output_name,
                       input_module, input_name):
        "Declare a connection between two module slots"
        assert input_name not in self._inputs[input_module.name]
        self._inputs[input_module.name][input_name] = Slot(output_module.name, output_name)
        oslot = Slot(input_module.name, input_name)
        if output_module.name not in self._outputs:
            self._outputs[output_module.name] = {output_name: [oslot]}
        elif output_name not in self._outputs[output_module.name]:
            self._outputs[output_module.name][output_name] = [oslot]
        else:
            self._outputs[output_module.name].append(oslot)

    def _remove_module_inputs(self, name):
        module_slots = self._inputs[name]
        for slot in module_slots.values():
            slots = self._outputs[slot.module][slot.name]
            nslots = [s for s in slots if s.module != name]
            if nslots:
                self._outputs[slot.module][slot.name] = nslots
            else:
                del self._outputs[slot.module][slot.name]
        del self._inputs[name]

    def _remove_module_outputs(self, name):
        module_slots = self._outputs[name]
        for sname in list(module_slots.keys()):
            slots = module_slots[sname]
            nslots = [s for s in slots if s.module != name]
            assert nslots != slots
            if nslots:
                module_slots[sname] = nslots
            else:
                del module_slots[sname]
        del self._outputs[name]

    def collect_dependencies(self):
        "Return the dependecies of the modules"
        dependencies = {}
        for (module, slots) in six.iteritems(self._inputs):
            outs = [m[0] for m in slots.values()]
            dependencies[module] = set(outs)
        return dependencies

    def order_modules(self):
        """Compute a topological order for the modules.
        """
        dependencies = self.collect_dependencies()
        runorder = toposort(dependencies)
        return runorder

    def validate(self):
        "Validate the Dataflow, returning [] if it is valid or the invalid modules otherwise."
        invalid = []
        for module in self._modules.values():
            if not self.validate_module(module):
                logger.error('Cannot validate module %s', 
                             module.name)
                invalid.append(module)
        return invalid

    def validate_module(self, module):
        inputs = self._inputs[module.name]
        valid = True
        for sd in module.input_descriptors.values():
            slot = inputs.get(sd.name)
            if sd.required and slot is None:
                logger.error('Missing inputs slot %s in %s',
                             sd.name, module.name)
                valid = False
                break
        return valid

    def __len__(self):
        return len(self._modules)

Dataflow.default = Dataflow()
