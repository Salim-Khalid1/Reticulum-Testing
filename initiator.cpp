#include <RadioLib.h>

// Heltec V3 SX1262 pins
SX1262 radio = new Module(8, 14, 12, 13);

uint16_t seq = 0;

// Payload sizes for experiment
uint16_t payload_sizes[3] = {10, 64, 200};

// Packets per payload size
uint16_t packets_per_test = 1000;

uint8_t payload[256];
uint8_t rxbuf[256];

void setup() {

  Serial.begin(115200);
  delay(2000);

  Serial.println("# LoRa Baseline Experiment");
  Serial.println("# freq=868MHz bw=125kHz sf=7 cr=4/5 txp=17dBm");
  Serial.println("seq,payload_bytes,RTT_us,RSSI_return,SNR_return,status");

  int state = radio.begin(868.0, 125.0, 7, 5, 17);

  if (state != RADIOLIB_ERR_NONE) {
    Serial.print("Init failed ");
    Serial.println(state);
    while(true);
  }

}

void run_test(uint16_t size) {

  Serial.print("# Starting payload ");
  Serial.println(size);

  for(uint16_t i=0;i<packets_per_test;i++) {

    // Prepare payload
    payload[0] = seq >> 8;
    payload[1] = seq & 0xFF;

    for(int j=2;j<size;j++){
      payload[j] = random(0,255);
    }

    unsigned long start_us = micros();

    int state = radio.transmit(payload, size);

    if(state != RADIOLIB_ERR_NONE){

      Serial.print(seq); Serial.print(",");
      Serial.print(size); Serial.println(",---,---,---,TX_FAIL");

      seq++;
      delay(1000);
      continue;
    }

    // Manual timeout receive loop
    unsigned long rx_start = micros();
    bool received = false;

    while((micros() - rx_start) < 3000000) { // 3s timeout

      state = radio.receive(rxbuf,256);

      if(state == RADIOLIB_ERR_NONE){
        received = true;
        break;
      }

    }

    unsigned long end_us = micros();

    if(received){

      unsigned long rtt = end_us - start_us;

      int rssi = radio.getRSSI();
      float snr = radio.getSNR();

      uint16_t rxseq = (rxbuf[0] << 8) | rxbuf[1];

      if(rxseq == seq){

        Serial.print(seq); Serial.print(",");
        Serial.print(size); Serial.print(",");
        Serial.print(rtt); Serial.print(",");
        Serial.print(rssi); Serial.print(",");
        Serial.print(snr); Serial.println(",OK");

      } else {

        Serial.print(seq); Serial.print(",");
        Serial.print(size); Serial.println(",---,---,---,SEQ_ERROR");

      }

    } else {

      Serial.print(seq); Serial.print(",");
      Serial.print(size); Serial.println(",---,---,---,LOSS");

    }

    seq++;

    delay(1000); // channel clearing

  }

}

void loop() {

  for(int i=0;i<3;i++){

    run_test(payload_sizes[i]);

  }

  Serial.println("# EXPERIMENT COMPLETE");

  while(true);

}