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

    ./pud_to_csv_kml.py -d /path/to/directory

## Debug Mode

Run `/usr/bin/DragonDebug.sh` to enable debug mode.

## Black Box Recordings

To turn on blackbox recordings, edit `/etc/debug.conf` and set the blackbox flag to `true`. The Bebop will then write one file per flight to `/data/ftp/internal_000/blackbox`. The files are named `light_run_*`. The format is as follows.

The files start with an ASCII header, which contains two sections. The first records the firmware version:

    -- Build infos
    product:  BebopDrone
    name:     BebopDrone-K...
    version:  1.32.0
    date:     2014-11-14
    time:     10h35m59s
    compiler: marjoriecoulin

The second lists the columns present in the recording:

    -- Navdata infos
    nentries: 129
    datasize: 8
    titles: index, time_s, sensor_acc_raw_x_m_s2, sensor_acc_raw_y_m_s2, sensor_acc_raw_z_m_s2, sensor_gyro_raw_x_rad_s, sensor_gyro_raw_y_rad_s, sensor_gyro_raw_z_rad_s, sensor_mag_raw_x_mG, sensor_mag_raw_y_mG, sensor_mag_raw_z_mG, phi_EST_rad, theta_EST_rad, psi_EST_rad, gyro_filt_x_rad_s, gyro_filt_y_rad_s, gyro_filt_z_rad_s, p_EST_rad_s, q_EST_rad_s, r_EST_rad_s, acc_x_EST_m_s2, acc_y_EST_m_s2, acc_z_EST_m_s2, speed_horiz_x_m_s, speed_horiz_y_m_s, speed_horiz_z_m_s, sensor_ultrasound_height_m, sensor_pressure_Pa, height_EST_m, height_vision_m, sensor_vision_speed_x_m_s, sensor_vision_speed_y_m_s, sensor_vision_speed_z_m_s, phi_REF_rad, theta_REF_rad, psi_REF_rad, p_REF_rad_s, q_REF_rad_s, r_REF_rad_s, r_wanted_rad_s, motor_cmd_pitch, motor_cmd_roll, motor_cmd_yaw, height_REF_m, height_REF_filt_m, speed_z_REF_m_s, motor_cmd_height, motor_cmd_ff, motor_cmd_1_rpm, motor_cmd_2_rpm, motor_cmd_3_rpm, motor_cmd_4_rpm, controler_state, acc_bias_x_m_s2, acc_bias_y_m_s2, acc_bias_z_m_s2, gyro_bias_x_rad_s, gyro_bias_y_rad_s, gyro_bias_z_rad_s, gyro_unbias_x_rad_s, gyro_unbias_y_rad_s, gyro_unbias_z_rad_s, speed_body_x_m_s, speed_body_y_m_s, speed_body_z_m_s, sensor_imu_ref_temperature_degC, sensor_imu_obs_temperature_degC, sensor_barometer_temperature_degC, battery_dV, motor1_obs_speed_rpm, motor2_obs_speed_rpm, motor3_obs_speed_rpm, motor4_obs_speed_rpm, BLDC_error, BLDC_motors_fault, BLDC_status, BLDC_temperature_degC, calage_x_rad, calage_y_rad, biais_pression_m, use_US, estimator_drone_position_m_x, estimator_drone_position_m_y, estimator_drone_position_m_z, estimator_psi_fused_rad, sensor_ultrasound_id, vision_indicator, sensor_ultrasound_mode, magneto_bias_x, magneto_bias_y, magneto_bias_z, magneto_radius, sensor_gps_flags, sensor_gps_latitude_deg, sensor_gps_longitude_deg, sensor_gps_altitude_m, sensor_gps_speed_m_s, sensor_gps_bearing_deg, sensor_gps_accuracy, sensor_gps_num_svs, sensor_gps_used_in_fix_mask, heading_magneto_rad, magneto_calibration_state, altitude_pression_m, altitude_pression_filt_m, dynamic_model_b, dynamic_model_f0, dynamic_model_Cz, dynamic_model_rpm_eq, psi_VIDEOREF_rad, airspeed_body_x_m_s, airspeed_body_y_m_s, airspeed_body_z_m_s, wind_body_x_m_s, wind_body_y_m_s, wind_body_z_m_s, stateFlightPlan, gpsDeviationPostionErrorLat_m, gpsDeviationPostionErrorLong_m, gpsDeviationPostionErrorAlt_m, gpsLatitudeRelative_m, gpsLongitudeRelative_m, gpsNorthSpeed_m_s, gpsEstSpeed_m_s, gpsDataOk, gpsNewValidData, battery_filt, magneticDeclination_rad, magneticDeclinationLocked

There are currently 129 columns in the recordings, everything from raw sensor data to attitude, position and wind estimates, to motor commands.

The data follows a data header:

    -- Data

Each packet contains `nentries` double floating point values, each `datasize` (8) bytes long.

The packets are logged at a rate of 200Hz.

This repository contains a Python script to convert blackbox files into .csv files. To convert a single blackbox file:

    ./blackbox_to_csv.py light_run_0

To convert all the .pud files in a directory:

    ./blackbox_to_csv.py -d /path/to/directory
