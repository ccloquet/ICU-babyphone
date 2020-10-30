# ICU babyphone
Modern babyphone to transmit monitoring alarms in ICU units

Features

 1. broadcasts the sounds of the alamrs inside the ICU room to any device outside (eg: a smartphone, a computer, ...)
   - this uses 2 raspberry pi (1 as a mike in the room, 1 as a server outside the room), and, eg, 1 smartphone.
   - technology: RTSP
   - software: FFMPEG, VLC, RTSP-SERVER
 
 2. notifies the user that an alarm is sounding from inside the room
   - using the same raspberry pis
   - technology: Bluetooth Low Energy beacon frames
   
 The combination of 1 & 2 is designed for the reliability (should one fail, the other is expected to work)

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
  - using it, install the Raspbian lite distro (~400 Mb) on each micro SD card
  - on each card
    - create a ssh folder at the root
    - connect the ethernet cable
    - using you preferred SSH client (eg: Putty), connect to raspberrypi.local (login: pi, password:raspberry)
    - change the default SSH password using the passwd command
    - sudo raspi-config
      - enter hostname
        - for the servers, eg, babyserver000 (babyserver000)
        - for the microphones, eg, babymike000 (babymike000, babymike001, ...)
      - wireless lan (not needed if your compute shares its internet connection through the ethernet cable)
        - the local wifi router should be in 2.4 Ghz
        - enter the SSID & password of your local wifi router
      - reboot
    - connect again through ethernet cable
      - from now on, they can be accessed through the ethernet cable using {hostname}.local instead of raspberrypi.local
      - sudo apt-get update
      - sudo apt-get upgrade
      - sudo apt-get install vim vlc ffmpeg

3. share the internet connection of your computer through the etehernet cable (in network configuration, properties of the wifi, sharing, over Ethernet)

4. on the babyserver configure an accesspoint 
 https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
 (skip the routing section)
  - in the 192.168.4.* range (potential conflicts with home router ?)
  - provides adresses trough DHCP between 192.168.4.2 and 192.168.4.20
  (-> can presumably accept fixed ips outside this range)
  
  ssid=babynet
  
  on the babymike, configure the ssid for the network access
  https://raspberrypihq.com/how-to-connect-your-raspberry-pi-to-wifi/
  
5. basic streaming from babymike to babyserver
   https://blog.mutsuda.com/raspberry-pi-into-an-audio-spying-device-7a56e7a9090e#.fr4l82xek
   connect the usb microphone to the babymike
   on the babymike: arecord -D plughw:1,0 -f dat | ssh -C pi@192.168.4.1 aplay -f dat
   enter the password of the babyserver
   listen on the babyserver (through HDMI or through headphones)
   
   le mini micro usb n'est pas génial...
   
6. more advanced streaming (with compression & server)
    
   some tests 
    - listening to the radio (works also in VLC)
      cvlc -A alsa,none --alsa-audio-device default http://icecast.omroep.nl/radio2-bb-mp3.m3u
    
    - streaming on the babymike itself
       ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtp rtp://localhost:1234
       cvlc -A alsa,none --alsa-audio-device default rtp://localhost:1234
    
    does this work?
      on the mike: ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtp rtp://192.168.4.1:1234
      on the server: cvlc -A alsa,none --alsa-audio-device default rtp://192.168.4.1:1234
  
    setting up a streaming server using https://github.com/revmischa/rtsp-server
      
      to install, on the babyserver:
      ~~~
      sudo apt-get install git libmoose-perl liburi-perl libmoosex-getopt-perl libsocket6-perl libanyevent-perl
      sudo cpan AnyEvent::MPRPC::Client
      cd
      git clone https://github.com/revmischa/rtsp-server
      cd rtsp-server
      perl Makefile.PL
      sudo make
      sudo make test
      sudo make install
      ~~~   
     
      to run, on the babyserver:
      ~~~   
      sudo -b /home/pi/rtsp-server/rtsp-server.pl
      ~~~   
  
      to run, on the babymike: 
      ~~~
      sudo -b ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtsp rtsp://192.168.4.1:5545/babymike000
      ~~~

    then, on any device connected on the network
    use, eg, VLC/VLC for Android/... to read the stream 
    eg: cvlc -A alsa,none --alsa-audio-device default rtsp://192.168.4.1/babymike000
    
    **from now on, you can listen on any device (rpi, smartphone, ...) the sounds heard by the babymikes**
    
7. send BLE frames from the babymike
    **goal: to send alarms to the server, as a back up if the ffmpeg stream does not work**
    sudo hciconfig hci0 up
    sudo hciconfig hci0 leadv 3
    sudo hcitool -i hci0 cmd 0x08 0x0008 1c 02 01 06 03 03 aa fe 14 16 aa fe 10 00 02 63 69 72 63 75 69 74 64 69 67 65 73 74 07 00 00 00
    
8. receive BLE frames on the server
      **goal: on receiving a particular UUID, sound an alarm (may be a gentle music)/show something on the screen**
      uses https://github.com/singaCapital/BLE-Beacon-Scanner
      ~~~
      sudo apt-get install python3-pip python3-dev ipython3 bluetooth libbluetooth-dev
      sudo pip3 install pybluez
      cd
      git clone https://github.com/singaCapital/BLE-Beacon-Scanner.git

      sudo python3 /home/pi/BLE-Beacon-Scanner/BeaconScanner.py


9. send BLE frames when the sound meet some criteria
   - volume
   - frequency

10. play/display the alarms
  - on the server
  - on a smartphone



References
FFMPEG streaming : https://trac.ffmpeg.org/wiki/StreamingGuide
VLC : https://www.videolan.org/streaming-features.html
