# A script from Peter Hinch.
# https://forum.micropython.org/viewtopic.php?p=62674#p62683
#
# This script returns the period between pulses and also the pulse duration (mark) and duty ratio (mark/period)

from machine import Pin, PWM
from rp2 import PIO, StateMachine, asm_pio
import time

onboardled = Pin(25, Pin.OUT)
onboardled.value(1)
time.sleep(0.5)
onboardled.value(0)
time.sleep(0.5)
onboardled.value(1)
time.sleep(0.5)
onboardled.value(0)



@rp2.asm_pio(set_init=rp2.PIO.IN_LOW, autopush=True, push_thresh=32)
def period():
    wrap_target()
    set(x, 0)
    wait(0, pin, 0)  # Wait for pin to go low
    wait(1, pin, 0)  # Low to high transition
    label('low_high')
    jmp(x_dec, 'next') [5]  # unconditional
    label('next')
    jmp(pin, 'low_high')  # while pin is high
    label('low')  # pin is low
    jmp(x_dec, 'nxt')
    label('nxt')
    jmp(pin, 'done')  # pin has gone high: all done
    jmp('low')
    label('done')
    in_(x, 32)
     # Auto push: SM stalls if FIFO full
    wrap()

@rp2.asm_pio(set_init=rp2.PIO.IN_LOW, autopush=True, push_thresh=32)
def mark():
    wrap_target()
    set(x, 0)
    wait(0, pin, 0)  # Wait for pin to go low
    wait(1, pin, 0)  # Low to high transition
    label('low_high')
    jmp(x_dec, 'next') [1]  # unconditional
    label('next')
    jmp(pin, 'low_high')  # while pin is high
    in_(x, 32)  # Auto push: SM stalls if FIFO full
    wrap()
    
#PIO --------------
pin22 = Pin(28, Pin.IN, Pin.PULL_UP)
sm0 = rp2.StateMachine(0, period, in_base=pin22, jmp_pin=pin22)
sm0.active(1)
sm1 = rp2.StateMachine(1, mark, in_base=pin22, jmp_pin=pin22)
sm1.active(1)

#MOSFET ------------
mos = Pin(3, Pin.OUT)

# Clock is 125MHz. 3 cycles per iteration, so unit is 24.0ns
def scale(v):
    return (1 + (v ^ 0xffffffff)) * 24e-6  # Scale to ms


c = 0

while True:
    
    period = scale(sm0.get())
    pulse = scale(sm1.get())
    
    print(period, pulse)
    time.sleep(0.01)
    
   
    if 10.5 < period < 10.6  and 5.9 < pulse < 6:
        print ('true', c)
        c += 1
        
    elif c > 10:
        print ('DETONATION DETONATION DETONATION DETONATION DETONATION', c )
        mos.value(1)
        time.sleep(5)
        mos.value(0)
        c=0
        break
        
        
    
    else:
        sm0.restart()
        sm1.restart()
        print('exit')
        c = 0
        