# This script polls BME280 sensor data and pushes it to local influxDB

TODO
sudo cat << EOF >> /etc/modules
i2c-bcm2708
i2c-dev
EOF
sudo echo "dtparam=i2c_arm=on" >> /boot/config.txt
sudo reboot

sudo i2cdetect -y 1
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
