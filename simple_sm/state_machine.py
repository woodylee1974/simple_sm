__author__ = 'woody'

import sys
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
        self.events_ = []
        self.event = None
        self.__dict__.update(kwargs)
        self.next_state = None
        if 'start' in kwargs:
            self.current_state_ = kwargs['start']
        self.parser_ = re.compile(r'^(\S*)[\s]*[\-]+[>]?[\s]*(\S*)[\s]*[\-]+>[\s]*(\S*)$')
        cls = handler.__class__
        for k, v in cls.__dict__.items():
            if hasattr(v, '__call__') and v.__doc__ is not None:
                self._add_transit_by(v, v.__doc__)
    
    def _event_func(self, *args, **kwargs):
        self.handle_event(self.event, *args, **kwargs)

    def _add_transit_by(self, v, trans):
        trans_line = self.parser_.match(trans)
        if trans_line:
            self.add_transit(trans_line.group(1), trans_line.group(2), \
                             trans_line.group(3), v)
            if self.current_state_ is None:
                self.current_state_ = trans_line.group(1)
            self.events_.append(trans_line.group(2))

    def __getattr__(self, item):
        for event in self.events_:
            if fnmatch.fnmatch(item, event):
                self.event = item
                return self._event_func

    def add_transit(self, s0, e, s1, func=None):
        if s0 in self.transit_map_:
            handles = self.transit_map_[s0]
            handles[e] = {'func': func, 'state': s1}
        else:
            self.transit_map_[s0] = {e: {'func': func, 'state': s1}}

    def start_state(self, s):
        self.current_state_ = s

    def handle_event(self, e, *args, **kwargs):
        handled = False
        if self.current_state_ in self.transit_map_:
            handles = self.transit_map_[self.current_state_]
            for k, trans in handles.items():
                if fnmatch.fnmatch(e, k):
                    func = trans['func']
                    self.next_state = handles[k]['state']
                    ret = func(self.handler_, e, *args, **kwargs)
                    current_state = self.current_state_
                    transit_done = True
                    if ret is None:
                        self.current_state_= self.next_state
                    elif ret == True:
                        self.current_state_= self.next_state
                    else:
                        transit_done = False
                    handled = True
                    if self.debug:
                        if transit_done:
                            log.debug("[%s][%s -- %s --> %s]" % (self.name_,
                                                                 current_state,
                                                                 e,
                                                                 self.current_state_))
                        else:
                            log.debug("[%s][%s -- %s --> %s[%s]][Transition is refused]" % (self.name_,
                                                                 current_state,
                                                                 e,
                                                                 self.current_state_,
                                                                 self.next_state))

                        for a in args:                                
                            log.debug(a)
                        for k, v in kwargs.items():
                            log.debug('%s=%o' %(k,v))
        if not handled:
            if self.debug:
                   log.debug("[%s][%s -- %s <-- %s]" % (self.name_,
                                                        self.current_state_,
                                                        e,
                                                        'not handled'))

    def get_state(self):
        return self.current_state_
        
    def set_next_state(self, next_state):
        self.next_state = next_state

    def dump(self):
        for (s, v) in self.transit_map_.items():
            print(s, v)

    
