from machine import Pin, PWM, Timer
import time
import rp2
onboardled = Pin(25, Pin.OUT)
onboardled.value(1)
time.sleep(1)
onboardled.value(0)

@rp2.asm_pio(set_init = rp2.PIO.OUT_LOW)

def det_data():
    # sending 3 ones's and one zero, 1110 1110 1110 .... 
    wrap_target()
    set(pins , 1) [5]
    set(pins , 1) [5]
    set(pins, 0) [15]
    wrap()
    
@rp2.asm_pio(set_init = rp2.PIO.OUT_LOW)
def inert_data():
    wrap_target()
    set(pins, 1) [15]
    set(pins, 0) [20]
    wrap()
    
det_data = rp2.StateMachine(1, det_data, freq=2000, set_base=Pin(16))

inert_data = rp2.StateMachine(0, inert_data, freq=2000, set_base=Pin(16))
inert_data.active(1) # sending inert data



switch = False
running = False

button = Pin(15, Pin.IN, Pin.PULL_UP)

speaker = PWM(Pin(7, Pin.OUT))

meep = Timer()

def sendData_boolbutton(i):
    global running
    
    running = True
     
    
    
def alert(t):
    global speaker, switch
    
    dudt = int(65535 * 0.5)   
    if switch:
        speaker.freq(3000)
        speaker.duty_u16(dudt)
    else:
        speaker.freq(2000)
        speaker.duty_u16(dudt)
    switch = not switch 
    


button.irq(trigger=button.IRQ_RISING, handler = sendData_boolbutton)
    


while True:
    if running:
        
        meep.init(mode = Timer.PERIODIC, freq = 3.5, callback = alert)
        
        print ('ON')
    

        inert_data.active(0) #turn off inert data 
        det_data.active(1) #SENDING LAUNCH DATA
        time.sleep(5) # 5 seconds of launch data being send
        
        det_data.active(0)
        inert_data.active(1)
        
        meep.deinit()
        speaker.deinit()
        running = False
        
    
    
    





    
