import pigpio
import time
import threading
import math

pi = pigpio.pi()

gpio_pin_lst = (14, 15, 18, 23, 24, 25, 8, 16, 20)
DIR_PIN1, STEP_PIN1, DIR_PIN2, STEP_PIN2, M2, M1, M0, GRAB_SERVO, MAG_SERVO  = gpio_pin_lst

for pin in gpio_pin_lst:
    pi.set_mode(pin, pigpio.OUTPUT)


pi.write(M0, 1)                                                                                                                                                                                                                                                                      
pi.write(M1, 0)
pi.write(M2, 0)

home_distance = 950
side_distance = 120
square_side = 374

magnet_up = 1100
magnet_down = 810
grabber_up = 1650
grabber_down_normal = 1025
grabber_down_king = 1115


class Stepper:
    def __init__(self, step_pin, dir_pin):
        self.coord = 0
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.velocity = 0
        
    def move(self, coord):
        travel = coord - self.coord
        if travel != 0:
            accel_travel = int((travel/abs(travel)))*100
            decel_travel = int((travel/abs(travel)))*70
            linear_travel = travel - accel_travel - decel_travel
            direction = self.coord < coord
            
            if (linear_travel < 0) == (travel < 0):
                self.accelerate(accel_travel)
                for i in range(abs(linear_travel)):
                    self.step(direction)
                self.decelerate(decel_travel)
            else:
                small_acceleration = int(travel/2)
                small_decel = travel - small_acceleration
                self.accelerate(small_acceleration)
                self.decelerate(small_decel)
            
            
    def step(self, dir_positive):
        if dir_positive:
            pi.write(self.dir_pin, 1)
            self.coord += 1
        else:
            pi.write(self.dir_pin, 0)
            self.coord -= 1
        pi.write(self.step_pin, 1)
        time.sleep(0.001)
        pi.write(self.step_pin, 0)
    
    def accelerate(self, steps):
        current_steps = abs(steps)
        steps_amount = abs(steps)
        interval = 0.001
        while current_steps > 0:
            time.sleep((current_steps/steps_amount)**(1/4)*interval)
            self.step(steps > 0)
            current_steps -= 1
        
    def decelerate(self, steps):
        current_steps = 0
        interval = 0.001
        while current_steps < abs(steps):
            time.sleep(math.sqrt(current_steps/abs(steps))*interval)
            self.step(steps > 0)
            current_steps += 1
        

tst_stepper1 = Stepper(STEP_PIN1, DIR_PIN1)
tst_stepper2 = Stepper(STEP_PIN2, DIR_PIN2)

def move_to(x, y):
    t1 = threading.Thread(target=tst_stepper1.move, args=(side_distance+square_side*(x-1),))
    t2 = threading.Thread(target=tst_stepper2.move, args=(home_distance+square_side*(y-1),))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
def move_home():
    t1 = threading.Thread(target=tst_stepper1.move, args=(0,))
    t2 = threading.Thread(target=tst_stepper2.move, args=(0,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
def grabber_lower(king=False):
    if king:
        pi.set_servo_pulsewidth(GRAB_SERVO, grabber_down_king)
    else:
        pi.set_servo_pulsewidth(GRAB_SERVO, grabber_down_normal)
    time.sleep(0.3)
    pi.set_servo_pulsewidth(GRAB_SERVO, 0)

def grabber_lower_with_height(pieces):
    piece_height = 80
    pi.set_servo_pulsewidth(GRAB_SERVO, grabber_down_normal + piece_height*(pieces-1))
    time.sleep(0.3)
    pi.set_servo_pulsewidth(GRAB_SERVO, 0)
        
def grabber_elevate():
    pi.set_servo_pulsewidth(GRAB_SERVO, grabber_up)
    time.sleep(0.3)
    pi.set_servo_pulsewidth(GRAB_SERVO, 0)

def magnet_lower():
    pi.set_servo_pulsewidth(MAG_SERVO, magnet_down)
    time.sleep(0.2)
    pi.set_servo_pulsewidth(MAG_SERVO, 0)
    
def magnet_elevate():
    pi.set_servo_pulsewidth(MAG_SERVO, magnet_up)
    time.sleep(0.2)
    pi.set_servo_pulsewidth(MAG_SERVO, 0)

def grabber_grab(king=False):
    grabber_lower(king)
    magnet_lower()
    grabber_elevate()
    
def grabber_drop(king=False):
    grabber_lower(king)
    magnet_elevate()
    grabber_elevate()
    

grabber_elevate()
magnet_elevate()

