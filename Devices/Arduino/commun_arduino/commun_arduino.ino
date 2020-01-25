const int motor1pins[4] = {50, 51, 52, 53};
const int relais1pin = 31;
const int relais2pin = 33;
const int relais3pin = 35;
const int relais4pin = 37;
const int warmWhitepin = 11;
const int coldWhitepin = 12;
const byte numChars = 8;
char receivedChars[numChars]; // an array to store the received data
boolean newData = false;

int val = -1024;
char *answer = (char *)malloc(16u);

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  Serial.begin(9600);
  for (int i = 0; i < 4; ++i) {
    pinMode(motor1pins[i], OUTPUT);
    digitalWrite(31, LOW);
  }
  //relais
  pinMode(relais1pin, OUTPUT);
  digitalWrite(relais1pin, HIGH);
  pinMode(relais2pin, OUTPUT);
  digitalWrite(relais2pin, HIGH);
  pinMode(relais3pin, OUTPUT);
  digitalWrite(relais3pin, HIGH);
  pinMode(relais4pin, OUTPUT);
  digitalWrite(relais4pin, HIGH);
  //pwms
  pinMode(warmWhitepin, OUTPUT);
  analogWrite(warmWhitepin, 0);
  pinMode(coldWhitepin, OUTPUT);
  analogWrite(coldWhitepin, 0);
}

// the loop function runs over and over again forever
void loop() {
  if (Serial.available() > 0) {
    recvWithEndMarker();
    process();
    showNewData();
  }
}

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = ';';
  char rc;

  // if (Serial.available() > 0) {
  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

void showNewData() {
  if (newData == true) {
    Serial.print("Incoming Command: ");
    Serial.print(receivedChars);
    Serial.println(";");
    Serial.print("Outgoing Answer: ");
    Serial.print(answer);
    if (val != -1024) {
      Serial.print(val);
    }
    Serial.println(";");
    newData = false;
  }
}

void process() {
  int hundreds;
  int tens;
  int ones;
  if (newData == true) {
    switch (receivedChars[0]) {
      case 'M':
        if (receivedChars[1] == 49) {
          for (int i = 0; i < 4; ++i) {
            if (receivedChars[2 + i] == 49) {
              digitalWrite(motor1pins[i], HIGH);
            } else {
              digitalWrite(motor1pins[i], LOW);
            }
          }
          answer = (char *)" moved";
        } else {
          answer = (char *)"no such motor";
        }
        break;
      case 'R':
        val = -1024;
        switch (receivedChars[1]) {
          case 49:
            if (receivedChars[2] == 49) {
              digitalWrite(relais1pin, LOW);
              answer = (char *)"R1 switched on";
            } else {
              digitalWrite(relais1pin, HIGH);
              answer = (char *)"R1 switched off";
            }

            break;
          case 50:
            if (receivedChars[2] == 49) {
              digitalWrite(relais2pin, LOW);
              answer = (char *)"R2 switched on";
            } else {
              digitalWrite(relais2pin, HIGH);
              answer = (char *)"R2 switched off";
            }
            break;
          case 51:
            if (receivedChars[2] == 49) {
              digitalWrite(relais3pin, LOW);
              answer = (char *)"R3 switched on";
            } else {
              digitalWrite(relais3pin, HIGH);
              answer = (char *)"R3 switched off";
            }
            break;
          case 52:
            if (receivedChars[2] == 49) {
              digitalWrite(relais4pin, LOW);
              answer = (char *)"R4 switched on";
            } else {
              digitalWrite(relais4pin, HIGH);
              answer = (char *)"R4 switched off";
            }
            break;
          default:
            answer = (char *)"no such relais";
            break;
        }
        break;
      case 'W':
        analogWrite(A0, 1023);
        delay(500);
        val = analogRead(A1);
        answer = (char *)"Value: ";
        analogWrite(A0, 0);
        break;
      case 'P':
        hundreds = (receivedChars[2] - 48) * 100;
        tens = (receivedChars[3] - 48) * 10;
        ones = (receivedChars[4] - 48);
        val = hundreds + tens + ones;
        switch (receivedChars[1]) {
          case 49:
            analogWrite(warmWhitepin, val);
            answer = (char *)"L1 adjusted to ";
            break;
          case 50:
            analogWrite(coldWhitepin, val);
            answer = (char *)"L2 adjusted to ";
            break;
          default:
            answer = (char *)"no such light";
            break;
        }
        break;
      default:
        break;
    }
  }
}
