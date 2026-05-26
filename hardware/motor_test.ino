#define PUL_PIN D5
#define DIR_PIN D6

void setup() {
    pinMode(PUL_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);

    digitalWrite(DIR_PIN, HIGH);
}

void loop() {
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(500);

    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(500);
}