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

2. installation
  - install Raspberry Pi Imager on your computer
  - using it, install the minimal Raspbian distro (~400 Mb) on each micro SD card
  - on each card
    - create a ssh folder at the root
    - connect the ethernet cable
    - using you preferred SSH client (eg: Putty), connect to raspberrypi.local (login: pi, password:raspberry)
    - change the default SSH password using the passwd command
      
