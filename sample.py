from datetime import datetime
from simple_sm import state_machine as sm

class Market:
    def __init__(self):
        pass

    def _start_market(self, event, *args, **kwargs):
        'stopped - k_start -> started'
        pass

    def _stop_market(self, event, *args, **kwargs):
        'started - k_stop -> stopped'
        pass


    def _suspend_market(self, event):
        'started -- k_suspend -> suspend'
        pass

    def _resume_market(self):
        'suspend -> k_resume -> started'
        pass

    def _other_event_market(self, event):
        'started ---> k_event_* -> started'
        pass


market = sm.StateMachine('MarketSM', Market(), start='stopped', debug=True)

market.handle_event('k_start')

market.handle_event('k_stop', datetime.now())

market.handle_event('k_suspend')

market.handle_event('k_start', datetime.now(), 'restart')

market.handle_event('k_suspend')

market.handle_event('k_event_tick', [1,2,3])

market.handle_event('k_resume')

market.handle_event('k_event_bars',[4,5,6])

