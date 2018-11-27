Simple State Machine (Python) Version 1.0.00

Copyright (C) 2017 Woody.Lee All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
The name of the Woody Lee may not be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

# Introduction
This state machine is a compact table-driven state machine on Python. In general, a state machine contains a set of states, a set of possible input events and the actions should be performed when an event is recevied on a specified state. A state is changed to another state by performing specified actions when a specified event is received. State diagram or state table is used to describe state transitions, and the later is more formally, and easier to be implemented correspondingly. Although simply state machine can be implemented by nested switch/case or if/else, considering the requirement of re-usability or maintainable, table-driven state machine pattern is recommended to use for more complex cases.

Where we should use state machine:

* simple parser, lexers, ... or any filter-pattern stuffs
* UI logic, which represents enable, disable, checked, unchecked and so on.
* device control, typical sample is like the control of recorder, player, or something like that

When you find you have to do with a group of complex rule and conditions, you should consider to use state machine pattern. A simple example is like:

* A device has 2 states, plugged, unplugged
* This device driver received 'tick_event' for each 1 second
* An event 'do_plug' to change state from 'unplugged' to 'plugged'
* An event 'unplug' to change state from 'plugged' to 'unplugged'
* On plugged state, when it received 'tick_event', it read data from device
* On unplugged state, when it received 'tick_event', it do nothing

We describe this rule by state diagram:
![Image](./state_diagram.png) 

Also, we may discribe this state transitions by a table:

|  	| unplugged 	| plugged 	|
|------------	|--------------------------	|----------------------------	|
| do_plug 	| transit to plugged state 	| no op 	|
| unplug 	| no op 	| transit to unplugged state 	|
| tick_event 	| no op 	| read data 	|

x-axis represents a set of possible states: plugged, unplugged

y-axis represents a set of possible events: tick_event, do_plug, unplug

The each cell represents the action that should be performed when received the event under the state.

When you have to handle a complex rule, such as an action should only be performed under a set of specified states, or a group of specific events should be handled differentially for different states, it is better to use a table to describe them and use a table-driven state machine to implement them. For example, using simple state machine, you simply implement above example:
```
import sys
import logging
from simple_sm import state_machine as sm
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
class DeviceCore:
    def read_data(self):
        print('read_data()')

    def handle_tick_event(self, *args, **kwargs):
        'plugged -- tick_event --> plugged'
        self.read_data()

    def do_plug(self, *args, **kwargs):
        'unplugged -- do_plug --> plugged'

    def unplug(self, *args, **kwargs):
        'plugged --> unplug --> unplugged'

device = sm.StateMachine('Device', DeviceCore(), start='unplugged', debug=True)

device.tick_event()
device.do_plug()
device.tick_event()
device.unplug()
```

The log looks like:
```
DEBUG:StateMachine:[Device][unplugged -- tick_event <-- not handled]
DEBUG:StateMachine:[Device][unplugged -- do_plug --> plugged]
read_data()
DEBUG:StateMachine:[Device][plugged -- tick_event --> plugged]
DEBUG:StateMachine:[Device][plugged -- unplug --> unplugged]
```
Notice that, the log of performing function appears before the log of state transition.

# How to use
## Define state table
You define state table by 2 methods:

1) by __doc__ of functions.
Please check the following example:
```
	def unplug(self, *args, **kwargs):
		'plugged --> unplug --> unplugged'

```
In the example, the function name unplug() do not matter, you may name this function to any name. And the __doc__ of this function defines a transition, which the first segment: `plugged` is start state, the third segment `unplugged` represents the end state, it means this transition will transit from `plugged` state to `unplugged` state. The middle segment `unplug` represents the event that causes this transition.

You have to define all transitions for a state diagram. Thus, you provide enough information for state machine, such as a group of states, a group of events and the bound actions.

2) by add_transit() function.
You also can write the code like the following to define a transition:
```
	sm.add_transit(start, event, end, func)
```
## Define start state
A state machine must start from a specified state. You may specify the start state by 2 methods:

1) By parameters of constructor
```
device = sm.StateMachine('Device', DeviceCore(), start='unplugged', debug=True)
```
Here, `start='unplugged'` is to define the start state.

2) By method of state machine
```
sm.start_state('unplugged')
```
Also, you define the start state to `unplugged`.


## Define event handler by wildcard
You may define multiple events by wildcard, which share same event handler, like:
```
    def _other_event(self, event):
        'started ---> k_event_* -> started'
        pass
```

Thus, any event like `k_event_tick`, `k_event_bars`, will be handled by this function.

only the following wildcard characters are supported:
```
*  multiple characters
?  single characters
```

## Multiple event transitions are mapping to one handler
It is possible to map multiple event transitions to one handler, as the following:
```
	def process_count(self, input_line):
		'start --> accept_count --> start'
		'upper_line --> accept_count --> start'
		do_handle_accept()
```

## Default Handler
Set default handler is also possible, when no handler is assigned to a event-transition,
default handler is called:
```
	def process_count(self, input_line):
		'default_handle'
		do_handle_accept()
```

## send event to state machine
You have 2 methods to send event to state machine object:

1) call the method with the name same as event
For example,
```
	def nothing_unplug(self, *args, **kwargs):
		'plugged --> unplug --> unplugged'
```
when you defines this transition, the state machine will create a method named `unplug`, thus, you
may send event to this state machine by calling this function directly, like:
```
	device.unplug()
```

2) Due to the wildcard event definition, you have to send event to state machine by calling the function `handle_event`:
```
	device.handle_event('k_event_tick')
```

###Change default end state
You may change default end state when you handle an event. Normally, you need not to care about it. So the destinate state will be as you set in your transition table. But sometimes, you need to change the destinate state according to your logic:
```
	def nothing_unplug(self, *args, **kwargs):
		'plugged --> unplug --> unplugged'
		if something_error:
			return False #This code will refuse to change state to unplugged.
```
In this state machine, `no return` or `return True` means the state transition is done successfully, while `return False` means the state transition is refused.

If you want to state machine transit to a specified state(of course, it is not recommended), you may do like that:
```
	def nothing_unplug(self, *args, **kwargs):
		'plugged --> unplug --> unplugged'
		if some_condition_satisifed:
			self.next_state = `specified_state`
```
Thus, you changed the default destinate state to what you specified.

# Bug reports

Hope this small piece of code does your help, if it can make your code more simple, more maintainability, I shall feel happy. If you find any problems, or you have any improvement advice, please contact with me by the following e-mail address:

-- By woody(li.woodyli@gmail.com)




