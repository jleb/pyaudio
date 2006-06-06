"""
PyAudio Example: Low Level C Module test.

Display detected Host APIs and Devices.
"""

import _portaudio as p

p.initialize()
max_apis = p.get_host_api_count()
max_devs = p.get_device_count()

print "\nPortAudio System Info:\n======================"
print "Version: %d" % p.get_version()
print "Version Text: %s" % p.get_version_text()
print "Number of Host APIs: %d" % max_apis
print "Number of Devices  : %d" % max_devs

print "\nHost APIs:\n=========="

for i in range(max_apis):
    apiinfo = p.get_host_api_info(i)
    print "Number              : ", i
    print "Name                : ", apiinfo.name
    print "Type                : ", apiinfo.type
    print "Devices             : ", apiinfo.deviceCount
    print "defaultInputDevice  : ", apiinfo.defaultInputDevice
    print "defaultOutputDevice : ", apiinfo.defaultOutputDevice
    print "--------------------------"

print "\nDevices:\n========"

for i in range(max_devs):
    devinfo = p.get_device_info(i)
    print "Number                   : ", i
    print "Name                     : ", devinfo.name
    print "hostApi Index            : ",  devinfo.hostApi
    print "maxInputChannels         : ", devinfo.maxInputChannels
    print "maxOutputChannels        : ", devinfo.maxOutputChannels
    print "defaultLowInputLatency   : ", devinfo.defaultLowInputLatency
    print "defaultLowOutputLatency  : ", devinfo.defaultLowOutputLatency
    print "defaultHighInputLatency  : ", devinfo.defaultHighInputLatency
    print "defaultHighOutputLatency : ", devinfo.defaultHighOutputLatency
    print "defaultSampleRate        : ", devinfo.defaultSampleRate
    print "--------------------------------"

print "\nDefault Devices:\n================"
try:
    print "Input  :", p.get_default_input_device()
except IOError, e:
    print "No Input devices."

try:
    print "Output :", p.get_default_output_device()
except IOError, e:
    print "No Output devices."

p.terminate()

    
