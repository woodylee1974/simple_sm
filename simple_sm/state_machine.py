__author__ = 'woody'

import logging
import re
import fnmatch

log = logging.getLogger("StateMachine")

class StateMachine(object):
    def __init__(self, name, handler, **kwargs):
        self.transit_map_ = {}
        self.name_ = name
        self.current_state_ = None
        self.handler_ = handler
        self.__dict__.update(kwargs)
        if 'start' in kwargs:
            self.current_state_ = kwargs['start']
        self.parser_ = re.compile(r'^(\S*)[\s]*[\-]+[>]?[\s]*(\S*)[\s]*[\-]+>[\s]*(\S*)$')
        for k, v in handler.__dict__.items():
            if hasattr(v, '__call__'):
                self._add_transit_by(v, v.__doc__)

    def _add_transit_by(self, v, trans):
        trans_line = self.parser_.match(trans)
        if trans_line:
            self.add_transit(trans_line.group(1), trans_line.group(2), \
                             trans_line.group(3), v)
            if self.current_state_ is None:
                self.current_state_ = trans_line.group(1)


    def add_transit(self, s0, e, s1, func=None):
        if s0 in self.transit_map_:
            handles = self.transit_map_[s0]
            handles[e] = {'func': func, 'state': s1}
        else:
            self.transit_map_[s0] = {e: {'func': func, 'state': s1}}

    def start_state(self, s):
        self.current_state_ = s

    def handle_event(self, e, *args, **kwargs):
        if self.current_state_ in self.transit_map_:
            handles = self.transit_map_[self.current_state_]
            for k, func in handles.items():
                if fnmatch.fnmatch(e, k):
                    func(self.handler_, *(e + args), **kwargs)
                    if self.debug_:
                        log.debug("[%s][%s -- %s --> %s]" % (self.name_,
                                                             self.current_state_,
                                                             e,
                                                             handles[k]['state']))
                    self.current_state_= handles[k]['state']

    def get_state(self):
        return self.current_state_

    def dump(self):
        for (s, v) in self.transit_map_.items():
            print(s, v)

    
