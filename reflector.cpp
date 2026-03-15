#include <RadioLib.h>

// Heltec V3 SX1262 pins
SX1262 radio = new Module(8, 14, 12, 13);

uint8_t buffer[256];

void setup() {

  Serial.begin(115200);
  delay(2000);

  Serial.println("Reflector node starting");

  int state = radio.begin(868.0, 125.0, 7, 5, 17);

  if (state != RADIOLIB_ERR_NONE) {
    Serial.print("Radio init failed: ");
    Serial.println(state);
    while(true);
  }

  Serial.println("Reflector ready");
}

void loop() {

  int state = radio.receive(buffer, 256);

  if(state == RADIOLIB_ERR_NONE){

    int len = radio.getPacketLength();

    // Immediate echo back
    radio.transmit(buffer, len);

  }

}