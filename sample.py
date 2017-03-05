import logging
import sys
from datetime import datetime
from simple_sm import state_machine as sm

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Market(object):
    def __init__(self):
        self.pinpang = False
        pass

    def _start_market(self, event, *args, **kwargs):
        'stopped - k_start -> started'
        pass

    def _stop_market(self, event, *args, **kwargs):
        'started - k_stop -> stopped'
        pass


    def _suspend_market(self, event, *args, **kwargs):
        'started -- k_suspend -> suspend'
        if self.pinpang:
            self.pinpang = not self.pinpang
            return True
        self.pinpang = not self.pinpang
        return False

    def _resume_market(self, event, *args, **kwargs):
        'suspend -> k_resume -> started'
        print('hello world')

    def _other_event_market(self, event, *args, **kwargs):
        'started ---> k_event_* -> started'
        pass

market = sm.StateMachine('MarketSM', Market(), start='stopped', debug=True)

market.k_start()

market.handle_event('k_start')

market.handle_event('k_stop', datetime.now())

market.handle_event('k_suspend')

market.handle_event('k_start', datetime.now(), 'restart')

market.handle_event('k_suspend')
market.k_suspend()

market.handle_event('k_event_tick', [1,2,3])

market.handle_event('k_resume')

market.k_event_bars([4,5,6])
market.handle_event('k_event_bars',[4,5,6])

