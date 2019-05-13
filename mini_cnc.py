import RPi.GPIO as GPIO
import time


class Servo:
    
    def __init__(self, pin: int, freq: int, rot_per_s: float, name: str = "unknown"):
        self.name = name
        GPIO.setup(pin, GPIO.OUT)
        self.control_pin = GPIO.PWM(pin, freq)
        self.control_pin.start(10)
        self.rot_per_s = rot_per_s
        self.freq = freq # is this needed? cant i read the current freq from the pin itself?
        self.last_angle = -1
        
    def turn(self, angle: int):
        # limit turn angle to 0-180°
        if 0 <= angle <= 180:            
            duration_ms = 0.5 + (angle / 180)  * 2.5# 1ms -> 0° and 2ms -> 180°
            duration_rel = duration_ms / (10 / self.freq)
            self.control_pin.ChangeDutyCycle(duration_rel)
            print("setting cycle to {} ({}ms)".format(duration_rel, duration_ms))
            f_angle = 180 if self.last_angle == -1 else abs(self.last_angle - angle)
            time.sleep(f_angle / self.rot_per_s + 0.001)
            print("releasing... {}/{}".format(f_angle, self.last_angle))
            self.control_pin.ChangeDutyCycle(0)
            self.last_angle = angle
        else:
            raise Error("servo {} can only rotate between 0 and 180 degrees".format(self.name))
    
    def shutdown(self):
        self.control_pin.stop()


class MiniCnc:
    
    def __init__(self, name: str = "unknown", x_axis_pin_nr: int = 13, x_axis_freq: int = 50, x_rot_per_s: float = 600, y_axis_pin_nr: int = 17, y_axis_freq: int = 50, y_rot_per_s: float = 600, z_axis_pin_nr: int = 4, z_axis_freq: int = 50, z_rot_per_s: float = 600 ):
        self.name = name
        self.x_axis_pin_nr = x_axis_pin_nr
        self.x_axis_freq = x_axis_freq
        self.x_rot_per_s = x_rot_per_s
        
        self.y_axis_pin_nr = y_axis_pin_nr
        self.y_axis_freq = y_axis_freq
        self.y_rot_per_s = y_rot_per_s
        
        self.z_axis_pin_nr = z_axis_pin_nr
        self.z_axis_freq = z_axis_freq
        self.z_rot_per_s = z_rot_per_s
        
        self.setup_complete = False # isnt False the default for an not initialized field?
    
    def setup(self):
        # set pin numbering scheme
        GPIO.setmode(GPIO.BCM)
        
        # setup servo for x axis
        self.x_servo = Servo(self.x_axis_pin_nr, self.x_axis_freq, self.x_rot_per_s, "x axis")
        self.y_servo = Servo(self.y_axis_pin_nr, self.y_axis_freq, self.y_rot_per_s, "y axis")
        self.z_servo = Servo(self.z_axis_pin_nr, self.z_axis_freq, self.z_rot_per_s, "z axis")
        # mark setup as completed
        self.setup_complete = True
    
    def shutdown(self):
        # shutdown all pins if setup was called at least once.
        if self.setup_complete:
            # shutdown all previously initialized pins.
            self.x_servo.shutdown()
            self.y_servo.shutdown()
            self.z_servo.shutdown()
            # cleanup gpio in general.
            GPIO.cleanup()


if __name__ == "__main__":
    cnc = None
    try:
        print("mini cnc\n"+("=" * 8))
        
        configuration = {
            "name": "blue wonder",
            "x_axis_pin_nr": 26,
            "x_rot_per_s": 600
        }
        
        cnc = MiniCnc(**configuration)
        cnc.setup()
        while True:
            cnc.x_servo.turn(0)
            cnc.y_servo.turn(0)
            cnc.z_servo.turn(0)
            time.sleep(2)
            cnc.x_servo.turn(180)
            cnc.y_servo.turn(180)
            cnc.z_servo.turn(180)
            # cnc.x_servo.turn(90)
            #time.sleep(2)
            #  cnc.x_servo.turn(180)
            #for i in range(180, 0, -5):
            #    cnc.x_servo.turn(i)
            #    time.sleep(0.5)
            #for i in range(0, 180, 5):
            #    cnc.x_servo.turn(i)
            #    time.sleep(0.5)
            time.sleep(2)
        
    finally:
        if cnc is not None:
            cnc.shutdown()
        print("done!")
    
    
    
    