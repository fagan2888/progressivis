
from abc import ABCMeta, abstractmethod


class Tracer(metaclass=ABCMeta):
    default = None

    @abstractmethod
    def start_run(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def end_run(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def run_stopped(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def before_run_step(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def after_run_step(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def exception(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def terminated(self, ts, run_number, **kwds):
        pass

    @abstractmethod
    def trace_stats(self, max_runs=None):
        _ = max_runs  # keeps pylint mute
        return []
