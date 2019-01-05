import pigpio
import time

pi = pigpio.pi()

gpio_out_lst = (10, 9, 6, 13, 19, 26)
input_list = 11

# only pins, no shift
gpio_pinout = (26, 19, 13, 6, 3, 2, 9, 10)
gpio_pinin = (22, 27, 17, 4, 5, 11, 21, 20)

LATCH_IN, CLOCK_IN, RESET_OUT, CLOCK_OUT, LATCH_OUT, DATA_OUT = gpio_out_lst
DATA_IN = input_list
    
for pin in gpio_out_lst:
    pi.set_mode(pin, pigpio.OUTPUT)
pi.set_mode(DATA_IN, pigpio.INPUT)

pi.write(LATCH_IN, 0)
pi.write(LATCH_OUT, 0)


def read_pins():
    board = []
    for out_pin in gpio_pinout:
        row = []
        pi.write(out_pin, 1)
        time.sleep(0.01)
        for in_pin in gpio_pinin:
            pin_input = pi.read(in_pin)
            row.append(pin_input)
        pi.write(out_pin, 0)
        board.append(row)
        time.sleep(0.01)
    return board


def shift():
    pi.write(LATCH_IN, 1)
    time.sleep(0.01)
    row = []
    for i in range(8):
        row.append(pi.read(DATA_IN))
        pulse(CLOCK_IN)
    pi.write(LATCH_IN, 0)
    time.sleep(0.01)
    return row
    
def next_row():
    pi.write(LATCH_OUT, 0)
    time.sleep(0.01)
    pulse(CLOCK_OUT)
    pi.write(LATCH_OUT, 1)
    time.sleep(0.01)

def first_row():
    pi.write(LATCH_OUT, 0)
    time.sleep(0.01)
    pulse_inverse(RESET_OUT)
    pi.write(DATA_OUT, 1)
    time.sleep(0.01)
    pulse(CLOCK_OUT)
    pi.write(DATA_OUT, 0)
    time.sleep(0.01)
    pi.write(LATCH_OUT, 1)
    time.sleep(0.01)
    
def read_with_shift():
    board = []
    for i in range(8):
        if i == 0:
            first_row()
        else:
            next_row()
        board.append(shift())
        time.sleep(0.01)
    return board

def shift_in():
    apnd_lst = []
    
    pulse_inverse(RESET)
    pi.write(LATCH_OUT, 0)
    pi.write(DATA_OUT, 1)
    
    pulse(CLOCK_OUT)
    pi.write(DATA_OUT, 0)
    
    for i in range(8):
        row = []
        pulse(LATCH_OUT)
        pi.write(LATCH_IN, 1)
        for j in range(8):
            pi.write(CLOCK_IN, 0)
            time.sleep(0.01)
            row.append(pi.read(DATA_IN))
            pi.write(CLOCK_IN, 1)
            time.sleep(0.01)
        pi.write(LATCH_IN, 0)
        pulse(CLOCK_OUT)
        row.reverse()
        apnd_lst.append(row)
        
    return apnd_lst

def pulse_inverse(pin):
    pi.write(pin, 0)
    time.sleep(0.01)
    pi.write(pin, 1)
    time.sleep(0.01)

def pulse(pin):
    pi.write(pin, 1)
    time.sleep(0.01)
    pi.write(pin, 0)
    time.sleep(0.01)

for pin in gpio_pinout:
    pi.write(pin, 0)
