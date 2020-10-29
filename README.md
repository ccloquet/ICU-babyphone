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
      - wireless lan
        - the local wifi router should be in 2.4 Ghz
        - enter the SSID & password of your local wifi router
      - reboot
    - connect again through ethernet cable
      - from now on, they can be accessed through the ethernet cable using {hostname}.local instead of raspberrypi.local
      - sudo apt-get update
      - sudo apt-get upgrade
      - sudo apt-get install vim
    
3. configure an accesspoint 
 https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
 (skip the routing section)
  - in the 192.168.4.* range (potential conflicts with home router ?)
  - provides adresses trough DHCP between 192.168.4.2 and 192.168.4.20
  (-> can presumably accept fixed ips outside this range)
  
  ssid=babynet
  
~~~
 sudo cp /etc/network/interfaces /etc/network/interfaces-orig
 
 sudo vim /etc/network/interfaces
 
    source-directory /etc/network/interfaces.d

    auto lo
    iface lo inet loopback

    iface eth0 inet dhcp

    auto wlan0
    iface wlan0 inet static
    address 172.16.0.200
    netmask 255.255.255.0
    wireless-channel 7
    wireless-essid babynet
    wireless-mode ad-hoc

 sudo systemctl stop dhcpcd.service    
  ~~~
  
