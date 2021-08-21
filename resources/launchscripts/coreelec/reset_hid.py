import os

base = '/sys/bus/usb/devices/'
devices = os.listdir(base)
for a in devices:
    ifacePath = base + a + '/bInterfaceClass'
    try:
        if os.path.isfile(ifacePath):
            with open(ifacePath, 'r') as f:
                interface = int(f.read())
            if interface == 3 and os.path.isfile(base + a + '/authorized'):
                os.system('echo 0 > ' + base + a + '/authorized')
                os.system('echo 1 > ' + base + a + '/authorized')
    except:
        continue