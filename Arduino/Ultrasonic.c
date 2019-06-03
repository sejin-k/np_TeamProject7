int PIN_MOTER = 3;
int PIN_TRIG= 8;
int PIN_ECHO = 9;
int motor_speed = 255;
int motor_state = 1;

void setup() {
  Serial.begin(9600);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_MOTER, OUTPUT);
}
 
void loop() {
  digitalWrite(PIN_TRIG, LOW);
  digitalWrite(PIN_ECHO, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
 
  unsigned long duration = pulseIn(Echo, HIGH);
 
  float distance = duration / 29.0 / 2.0;
 
  if(distance < 10) {
   if (motor_state == 0){
      motor_state = 1;
      analogWrite(motor_pin, motor_speed);
      Serial.println(distance);
   }
  }
  else{
    if (motor_state == 1){
      motor_state = 0;
      analogWrite(motor_pin, LOW);
      Serial.println(distance);
   }
  }
 
  delay(500);
  
}