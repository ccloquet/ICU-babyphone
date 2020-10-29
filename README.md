# icu_babyphone
modern babyphone to transmit monitoring alarms in ICU units

1. material

  - let n_d be the number of detectors and n_s be the number of servers and n_tot = n_d + n_s
  - then you need n_tot of the following
    - 1 raspberry pi 4
    - 1 officiel raspberry pi alim
    - 1 Kingston 32 Gb class-10 micro SD card
    - 1 raspberry pi case
  - you also need n_d times
    - 1 USB microphone
  - and finally
    - 1 computer
    - 1 ethernet cable (crossover or not)

2. basic install 
  - install Raspberry Pi Imager on your computer
  - using it, install the minimal Raspbian distro (~400 Mb) on each micro SD card
  - on each card
    - create a ssh folder at the root
    - connect the ethernet cable
    - using you preferred SSH client (eg: Putty), connect to raspberrypi.local (login: pi, password:raspberry)
    - change the default SSH password using the passwd command
    - sudo raspi-config
      - enter hostname
        - for the servers, eg, babyserver000 (babyserver000)
        - for the microphones, eg, babymike000 (babymike000, babymike001)
        - from now on, they can be accessed through the ethernet cable using {hostname}.local instead of raspberrypi.local
      - wireless lan
        - the local wifi router should be in 2.4 Ghz
        - enter the SSID & password of your local wifi router
      - reboot
      - sudo apt-get upgrade
      - sudo apt-get update
    
3. configure one pi as a wifi access point
https://thepi.io/how-to-use-your-raspberry-pi-as-a-wireless-access-point/
  - in the 172.16.0.0/12 range (to avoid potential conflicts with home router)
  - can accept fixed ips between 172.16.0.200 and 172.16.0.254
  - and provide adresses trough DHCP between 172.16.0.11 and 172.16.0.199
  
  ``
  sudo apt-get install hostapd
  sudo apt-get install dnsmasq
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq
  sudo vim /etc/dhcpcd.conf
    interface wlan0
    static ip_address=192.168.0.10/24
    denyinterfaces eth0
    denyinterfaces wlan0

  sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
  sudo vim /etc/dnsmasq.conf
    interface=wlan0
    dhcp-range=172.16.0.11,172.16.0.199,255.255.255.0,24h
  
  sudo vim /etc/hostapd/hostapd.conf
    interface=wlan0
    bridge=br0
    hw_mode=g
    channel=7
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    ssid=NETWORK
    wpa_passphrase=PASSWORD

  sudo vim /etc/default/hostapd
    DAEMON_CONF="/etc/hostapd/hostapd.conf"
  
  sudo reboot now´´
