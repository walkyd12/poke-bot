#include <Servo.h>

class ThreeDsServo {
	private:
		int _pin_num;

	public:
		Servo _srvo;
		int _start_pos;
		int _end_pos;

		bool _is_reverse;

		ThreeDsServo(int pin, int start, int end, bool reverse) {
			_is_reverse = reverse;

			if(_is_reverse) {
				_end_pos= start;
				_start_pos = end;
			} else {
				_start_pos = start;
				_end_pos = end;
			}
			_pin_num = pin;
			
		}

		void setup() {
			_srvo.attach(_pin_num);
			_srvo.write(_start_pos);
		}

		void move_servo(int from_pos, int to_pos, int delay_sec) {
			int pos = 0;
			if(from_pos < to_pos) {
				for (pos = from_pos; pos <= to_pos; pos += 1) {
					// in steps of 1 degree ( += 1 )
					_srvo.write(pos);                                 // tell servo to go to position in variable 'pos'
					delay(delay_sec);                                   // waits x ms for the servo to reach the position
				}
			} else {
				for (pos = from_pos; pos >= to_pos; pos -= 1) {
					// in steps of 1 degree ( += 1 )
					_srvo.write(pos);                                 // tell servo to go to position in variable 'pos'
					delay(delay_sec);                                   // waits x ms for the servo to reach the position
				}
			}
		}

		void tap_button_servo(int delay_sec=5) {
			move_servo(_start_pos, _end_pos, delay_sec);
			delay(1);
			move_servo(_end_pos, _start_pos, delay_sec);
		}

		int get_start_pos() {
			return _start_pos;
		}

		int get_end_pos() {
			return _end_pos;
		}
};

void led_on_off(bool on, int pin_num){
	int out = LOW;
	if(on){
		out = HIGH;
	}
	digitalWrite(pin_num, out);
}

void flash_led(int pin_num, int num_flashes, int blink_time){
	for(int i=0;i<num_flashes;i++){
		digitalWrite(pin_num,HIGH);
		delay(blink_time/2);
		digitalWrite(pin_num,LOW);
		delay(blink_time/2);
	}
}

String recieve_serial_message() {
	if (Serial.available() > 0) {
		String data = Serial.readStringUntil('\n');
		Serial.flush();
		return data;
	}
	return "";
}

void send_serial_message(String msg) {
	Serial.flush();
	Serial.println(msg);
	delay(1);
}

ThreeDsServo servo_a(8, 50, 75, false);
ThreeDsServo servo_l(10, 50, 90, true);
ThreeDsServo servo_r(9, 0, 30, false);
ThreeDsServo servo_select(17, 125, 180, true);
ThreeDsServo servo_up(12, 40, 90, true);
ThreeDsServo servo_down(13, 90, 90, true);
ThreeDsServo servo_d_left(11, 90, 90, true);

// init on off switch pin
const int switch_pin = 3;

const int baud = 31250;

void setup() {
	servo_a.setup();
	servo_l.setup();
	servo_r.setup();
	servo_select.setup();
	servo_up.setup();

	pinMode(LED_BUILTIN, OUTPUT);		

	pinMode(switch_pin, INPUT);

	Serial.begin(baud);
	Serial.flush();
}

void soft_reset() {
	servo_r.move_servo(servo_r._start_pos, servo_r._end_pos, 1);
	servo_l.move_servo(servo_l._start_pos, servo_l._end_pos, 1);
	servo_select.move_servo(servo_select._start_pos, servo_select._end_pos, 1);
	delay(1200);
	servo_select.move_servo(servo_select._end_pos, servo_select._start_pos, 1);
	servo_l.move_servo(servo_l._end_pos, servo_l._start_pos, 1);
	servo_r.move_servo(servo_r._end_pos, servo_r._start_pos, 1);
}

void loop() {
	// Only check serial comm if switch is on
	if(digitalRead(switch_pin) == HIGH) {
		// Check serial comms
		String msg = recieve_serial_message();
		if(msg=="PRESS_A") {
			servo_a.tap_button_servo(5);
			send_serial_message("PRESS_A_SUCC");
		} else if(msg=="PRESS_R") {
			servo_r.tap_button_servo();
			send_serial_message("PRESS_R_SUCC");
		} else if(msg=="PRESS_L") {
			servo_l.tap_button_servo();
			send_serial_message("PRESS_L_SUCC");
		} else if(msg=="PRESS_SEL") {
			servo_select.tap_button_servo();
			send_serial_message("PRESS_SEL_SUCC");
		} else if(msg=="STICK_UP") {
			servo_up.move_servo(servo_up._start_pos, servo_up._end_pos, 1);
			delay(1200);
			servo_up.move_servo(servo_up._end_pos, servo_up._start_pos, 1);
			send_serial_message("STICK_UP_SUCC");
		} else if(msg=="STICK_DOWN") {
			servo_up.move_servo(servo_down._start_pos, servo_down._end_pos, 1);
			delay(1200);
			servo_up.move_servo(servo_down._end_pos, servo_down._start_pos, 1);
			send_serial_message("STICK_DOWN_SUCC");
		} else if(msg=="PRESS_D_LEFT") {
			servo_d_left.tap_button_servo();
			send_serial_message("PRESS_D_LEFT_SUCC");
		} else if(msg=="SOFT_RESET") {
			soft_reset();
			send_serial_message("SOFT_RESET_SUCC");
		} else if(msg=="FLUSH_SER") {
			Serial.flush();
			send_serial_message("FLUSH_SER_SUCC");
		}
	} else {
		Serial.flush();
	}
}