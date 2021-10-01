arduino-cli compile --fqbn arduino:avr:uno arduino/three-ds/three-ds.ino
arduino-cli upload -p /dev/ttyACM$1 --fqbn arduino:avr:uno arduino/three-ds/three-ds.ino