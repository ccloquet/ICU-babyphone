# ICU babyphone network

_A modern babyphone solution to transmit ICU units monitoring alarms -- through Wifi and/or Ethernet network -- to a display, a smartphone, a DECT, or any other computer._

**Motivation**: during the Covid-19 crisis, temporary intensive care units (ICU) with isolated rooms have been created and equipped with biomedical equipment (monitoring, ECMOs, ...). These devices sound alarms, but the sound cannot be heard outside the room. Because of the temporary nature of the rooms, the devices are not linked to a central desk like in established ICU. When there is a central desk, no nurse is available to check it. 

Sometimes, babyphones are used to transmit the alarms from the room, but they cannot be carried by several people at a time, they are too far to be heard and their alarms are not specific: it is often difficult to distinguish which device is triggering the alarm, which causes either losses of time and energy for the staff (false positives), or degraded care to the patients (false negatives).

There is therefore a need for a versatile and robust solution that can relay the alarms of any biomedical device and specify which device is sounding. The following solution is based on a set of Raspberry Pi devices.


**Proposed solution** (work in progress)


![Schema of Babyphone Network](icu_babyphone.png)


_0. Features_

 1. broadcasts the sounds of the alarms inside the ICU room to any device outside (eg: a smartphone, a computer, ...)
    - this uses 2 Raspberry Pi (1 as a mike in the room, 1 as a server outside the room), and, eg, 1 smartphone.
    - technology: RTSP
    - software: FFMPEG, VLC, RTSP-SERVER
 
 2. notifies the user that an alarm is sounding from inside the room
    - using the same Raspberry Pis or not
    - technology: Bluetooth Low Energy beacon frames
   
 The combination of 1 & 2 is designed for the reliability (should one fail, the other is expected to work)
 
 Note: in this tutorial, a network is created netween the Pi's. Any sufficienty robust/secured network could be used.

_1. Material_

  - let n<sub>d</sub> be the number of detectors, n<sub>s</sub> be the number of servers and n<sub>tot</sub> = n<sub>d</sub> + n<sub>s</sub>
  - then you need n<sub>tot</sub> of the following:
    - 1 raspberry pi 4
    - 1 official raspberry pi alim (3A)
    - 1 Kingston 32 Gb class-10 micro SD card
    - 1 raspberry pi case
  - you also need n<sub>d</sub> of the following:
    - 1 USB microphone (this ones works but is of low quality: https://www.amazon.fr/gp/product/B086PH9ZZX -- try to buy from your local shop)
  - and finally
    - 1 computer with Ethernet port
    - 1 Ethernet cable (crossover or not)
    - optionally 1 dedicated smartphone per person that should receive the alarms
    
_2. Basic install_

  - install Raspberry Pi Imager on your computer
  - share the internet connection of your computer with its ethernet port (in network configuration > properties of the wifi > sharing > over Ethernet)
  - on each micro SD card
    - install the Raspbian lite distro (~400 Mb) 
    - create a folder named "ssh" (without quotes) at the root
  - on each Pi
    - connect the Ethernet cable
    - using you preferred SSH client (eg: Putty), connect to raspberrypi.local (login: pi, password:raspberry)
    - change the default SSH password using the passwd command
    - sudo raspi-config
      - enter hostname:
        - for the servers, eg, babyserver000 (babyserver000)
        - for the microphones, eg, babymike000 (babymike000, babymike001, ...)
      - optional: wireless lan (not needed if your compute shares its internet connection through the ethernet cable)
        - the local wifi router should be in 2.4 Ghz
        - enter the SSID & password of your local wifi router
      - reboot
    - connect again through ethernet cable
      - from now on, the Pi can be accessed through the ethernet cable using {hostname}.local instead of raspberrypi.local
      - ~~~
        sudo apt-get update
        sudo apt-get upgrade
        sudo apt-get install git vim vlc ffmpeg

3. Configure the _babyserverXXX_ as an accesspoint 
     - follow: https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
     - skip the routing section if you do not want to share the internet through the ethernet connection
     - in the 192.168.4.* range (potential conflicts with home router ?)
     - provides adresses trough DHCP between 192.168.4.2 and 192.168.4.20 (-> can presumably accept fixed ips outside this range)
     - ssid=babynet

4. Configure the _babymikeXXX_, to connect to the accesspoint
      - follow: https://raspberrypihq.com/how-to-connect-your-raspberry-pi-to-wifi/
      - any pi of the network can be accessed from any other pi
  
5. basic streaming from _babymikeXXX_ to _babyserverXXX_ (just for test, wont be used in prod)
    - source : https://blog.mutsuda.com/raspberry-pi-into-an-audio-spying-device-7a56e7a9090e#.fr4l82xek
    - connect the usb microphone to the babymike
    - on the babymikeXXX:  arecord -D plughw:1,0 -f dat | ssh -C pi@192.168.4.1 aplay -f dat
    - enter the password of the babyserverXXX
    - listen on the babyserver (through HDMI or through headphones)
   
6. more advanced streaming (with compression & server)
    
   a. some tests 
    - listening to the radio (works also in VLC)
      cvlc -A alsa,none --alsa-audio-device default http://icecast.omroep.nl/radio2-bb-mp3.m3u
    
    - streaming on the babymike itself
       ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtp rtp://localhost:1234
       cvlc -A alsa,none --alsa-audio-device default rtp://localhost:1234
    
    - does this work?
       on the mike: ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtp rtp://192.168.4.1:1234
       on the server: cvlc -A alsa,none --alsa-audio-device default rtp://192.168.4.1:1234
  
   b. setting up a streaming server using https://github.com/revmischa/rtsp-server
   
      
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
     
      **to run, on the babyserver:**
      ~~~   
      sudo -b /home/pi/rtsp-server/rtsp-server.pl
      ~~~   
  
      **to run, on the babymike:**
      ~~~
      sudo -b ffmpeg -re -f alsa -i plughw:1,0 -acodec mp3 -ab 128k -ac 2 -f rtsp rtsp://192.168.4.1:5545/babymike000
      ~~~

      then, read on on any device connected on the network, eg:
        - on a smartphone, using VLC/VLC for Android/... 
        - on a pi, using the command: cvlc -A alsa,none --alsa-audio-device default rtsp://192.168.4.1/babymike000
    
      **from now on, you can listen on any device (rpi, smartphone, ...) the sounds heard by the babymikes**
    
7. send BLE frames from the babymike
    **goal: to send alarms to the server, as a backup if the ffmpeg stream does not work**
    https://medium.com/@bhargavshah2011/converting-raspberry-pi-3-into-beacon-f01b3169e12f (explains with Eddystone)
    https://pimylifeup.com/raspberry-pi-ibeacon/ (explains with BLE + how to generate uuid)

    ~~~
    sudo hciconfig hci0 up
    sudo hciconfig hci0 leadv 3
    sudo hcitool -i hci0 cmd 0x08 0x0008 1c 02 01 06 03 03 aa fe 14 16 aa fe 10 00 02 63 69 72 63 75 69 74 64 69 67 65 73 74 07 00 00 00
    ~~~
    
    to stop: sudo hciconfig hci0 down
    
8. receive BLE frames on the babyserver
      **goal: on receiving a particular UUID, sound an alarm (may be a gentle music)/show something on the screen**
      uses https://github.com/singaCapital/BLE-Beacon-Scanner
      ~~~
      sudo apt-get install python3-pip python3-dev ipython3 bluetooth libbluetooth-dev
      sudo pip3 install pybluez
      cd
      git clone https://github.com/ccloquet/BLE-Beacon-Scanner.git
 
      this code should be adapted (eg: remove all the unneeded parts, sound an alarm on frame detection, etc)

      basic usage:
          sudo python3 /home/pi/BLE-Beacon-Scanner/BeaconScanner.py

9. detect when the when the sound meet some criteria
   - volume
     - https://moduliertersingvogel.de/2018/11/07/measure-loudness-with-a-usb-micro-on-a-raspberry-pi/
   - frequency
     - it seems that SoundAnalyze above can detect the pitch (https://github.com/ExCiteS/SLMPi/tree/master/SoundAnalyse-0.1.1)
     - but what if many frequencies? if they come rapidly on after another? -> to test
     - otherwise: filtering:
        - https://pypi.org/project/audiolazy/
        - https://stackoverflow.com/questions/35764018/python-microphone-input-and-low-pass-filter-effect-realtime


10. send the BLE frames whe the sound meet these criteria 

11. play/display the alarms
  - on the server
  - on a smartphone
    - VLC for Android
    - Tasker for the BLE frames: https://forum.frandroid.com/topic/69334-tasker-aideinfoscreation-de-profils/page/9/

  - play a gentle sound
   https://raspberrypi.stackexchange.com/questions/94098/reliable-way-to-play-sound-ogg-mp3-in-python-on-pi-zero-w
   https://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python

  - show the status as large color blocks

12. Autoload on boot

13. Keepalive

_Other references_

  - FFMPEG streaming: https://trac.ffmpeg.org/wiki/StreamingGuide, https://www.raspberrypi.org/forums/viewtopic.php?t=226843, http://sharonleal.me/, http://iltabiai.github.io/2018/03/17/rpi-stream.html, https://blog.tremplin.ens-lyon.fr/GerardVidal/faire-du-streaming-live-avec-une-raspberry-pi-et-les-ressources-de-lens-ife.html, https://raspberrypi.stackexchange.com/questions/32677/setup-microphone-stream-and-turn-your-raspberry-pi-into-a-baby-phone
  - VLC: https://www.videolan.org/streaming-features.html
  - BLE: https://www.argenox.com/library/bluetooth-low-energy/using-raspberry-pi-ble/
  - WebRTC Streaming: https://github.com/kclyu/rpi-webrtc-streamer
  - usb audio: https://www.seeedstudio.com/blog/2019/08/08/how-to-use-usb-mini-microphone-on-raspberry-pi-4/, https://iotbytes.wordpress.com/connect-configure-and-test-usb-microphone-and-speaker-with-raspberry-pi/, https://raspberrytips.com/add-microphone-raspberry-pi/
  
  
(note:it seems that the screen connected to the pi should not be hi-res otherwise risk of Radio Interference with Wifi?)

