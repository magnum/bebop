# Parrot Bebop Drone Hacking

## Shell Access

Connect to the Bebop's WiFi network, then:

    $ telnet 192.168.42.1

## Networking

The drone and controller seem to interact via two ports:

    c2dport: 54321
    d2cport: 43210

### USB Networking

To active USB networking:

    / # /bin/usbnetwork.sh

The Bebop's IP address on the USB network is 192.168.43.1

Short pressing on the Bebop's button while USB connected might also activate USB networking (untested).

## Configuration

`/data/dragon.conf` contains a JSON dict with many settings, including blackbox_enable and navdata_enable.

`/etc/debug.conf`: contains debug settings, including enabling blackbox and navdata.

`/etc/gps_config.txt`: contains the GPS configuration:

    PERDAPI,FIRSTFIXFILTER,STRONG
    PERDAPI,FIXPERSEC,5
    PERDAPI,FIXMASK,SENSITIVITY
    PERDAPI,STATIC,0,0
    PERDAPI,LATPROP,-1
    PERDAPI,OUTPROP,0
    PERDAPI,CROUT,V
    PERDAPI,PIN,OFF
    PERDAPI,GNSS,AUTO,2,2,0,-1,-1
    PERDSYS,ANTSEL,FORCE1L

## GPS

To monitor GPS output (NMEA):

    / # cat `cat /etc/parrot/gps/tty`

You'll see one NMEA stanza per second, for example:

    $GNGST,000608.916,,,,,,,*57
    $GNGSA,A,1,,,,,,,,,,,,,,,,1*1D
    $GNZDA,000609.029,22,08,1999,,*4C
    $GPGSV,1,1,00,,,,,,,,,,,,,,,,,1*64
    $GLGSV,1,1,00,,,,,,,,,,,,,,,,,1*78
    $PERDCRV,0.00,0,0.00,0.00,0.00,44.0,13368000*49
    $GNRMC,000609.916,V,0000.0000,N,00000.0000,E,0.00,0.00,220899,,,N,V*1B
    $GNGNS,000609.916,0000.0000,N,00000.0000,E,NNN,00,,-18.0,18.0,,,V*6E

## Sensors

    /usr/bin # ./p7_sensors-test
    posix init start build on : Nov 13 2014 19:27:05
    Use ctrl+\ (SIGQUIT) to end the application
    
    Usage: ./p7_sensors-test [options]
    Options:
    -h | --help          Print this message
    -b | --bit-mask      Bitfield to activate sensors
                            > 00000001 : vertical camera................ mt9v117
                            > 00000010 : gyro/accelero.................. mpu6050
                            > 00000100 : pressure/temperature sensor.... ms5607
                            > 00001000 : magneto sensor................. ak8963
                            > 00010000 : us sensor...................... xxxxxxx
                            > 00100000 : gyro in fifo................... mpu6050
                            > 01000000 : accelero in fifo............... mpu6050
                            > 10000000 : fifo count..................... mpu6050
    -s | --samples       Number of acquisition (default = 5000)
    -d | --debug-print   Debug print
    -f | --file          Log file
    -p | --port          Network port to use-H                   Human friendly (print matrices on several lines)
    -M                   Machine friendly (all data on one line)
    -m                   if us is activated  > 1 : low_power mode > 0 : high_power mode
    

## Debug Mode

Run `/usr/bin/DragonDebug.sh` to enable debug mode.
