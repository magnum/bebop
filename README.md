# Parrot Bebop Drone Hacking

## Shell Access

Connect to the Bebop's WiFi network, then:

    $ telnet 192.168.42.1

## FTP

There's an FTP server running on the normal port with no username or password, which provides access to everything under `/data/ftp`, which includes media (JPEGs, DNGs, videos), PUDs, logs, black box recordings and more.

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
    
## PUD files (flight recordings)

The drone records every flight as a single file in `/data/ftp/internal_000/Bebop_Drone/academy`.

The file format is self-describing. Each file begins with a null-terminated JSON string listing the columns present in each data packet. For example (pretty-printed here for clarity):

    {
      "version": "1.0",
      "date": "2014-11-30T160423+0000",
      "product_id": 2305,
      "serial_number": "PI...",
      "uuid": "EB...",
      "controller_model": "manta",
      "controller_application": "Nexus 10",
      "run_origin": 0,
      "details_headers": [
        {
          "name": "time",
          "type": "integer",
          "size": 4
        },
        {
          "name": "battery_level",
          "type": "integer",
          "size": 4
        },
        {
          "name": "controller_gps_longitude",
          "type": "double",
          "size": 8
        },
        {
          "name": "controller_gps_latitude",
          "type": "double",
          "size": 8
        }, ...
      ]
    }

This JSON header is followed by fixed-size binary packets, through to the end of the file. There are roughly 30 packets per second.

The fields currently present in the log packets are:

|Name|Type|Size|Description|
|:---|:---|:---|---|
|time|integer|4|Timestamp of the log entry, in milliseconds|
|battery_level|integer|4|Battery level, in percent|
|controller_gps_longitude|double|8|Controller GPS longitude, in degrees|
|controller_gps_latitude|double|8|Controller GPS latitude, in degrees|
|flying_state|integer|1|Flying state: 1 = landed, 2 = in the air, 3 = in the air|
|alert_state|integer|1|Alert state: 0 = normal|
|wifi_signal|integer|1|WiFi signal strength, always 0 right now|
|product_gps_available|boolean|1|Bebop GPS availability, always 0 right now|
|product_gps_longitude|double|8|BeBop GPS longitude, in degrees|
|product_gps_latitude|double|8|BeBop GPS latitude, in degrees|
|product_gps_position_error|integer|4|BeBop GPS position error, always 0 right now|
|speed_vx|float|4|Horizontal speed, unknown units|
|speed_vy|float|4|Horizontal speed, unknown units|
|speed_vz|float|4|Vertical speed, unknown units|
|angle_phi|float|4|Euler angle phi, likely in radians|
|angle_theta|float|4|Euler angle theta, likely in radians|
|angle_psi|float|4|Euler angle psi, likely in radians|
|altitude|integer|4|Altitude, likely in centimeters|
|flip_type|integer|1|Flip type, 0 = no flip|

A quick way to dump the data as a table from the shell is to run:

    hexdump -s 1379 -e ' "%07_ad|" 2/4 "%8d" 2/8 "%13.7f" 4/1 "%2d" 2/8 "%13.7f " 1/4 "%4d" 6/4 "%12.5f" 1/4 "%6d" 1/1 "%3d" "\n" ' *.pud | more

This repository contains a Python script to convert .pud files into .csv and .kml files (for Google Earth). For .kml support, you'll need the `simplekml` package, which can be installed trivially using `easy_install simplekml`. To convert a single .pud file:

    ./pud_to_csv_kml.py 0901_2014-12-01T162824+0000_F88751.pud

To convert all the .pud files in a directory:

    ./pud_to_csv_kml.py /path/to/directory

## Debug Mode

Run `/usr/bin/DragonDebug.sh` to enable debug mode.
