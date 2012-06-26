#!/usr/bin/env python

import datetime
import time
import sys
import gpib
import optparse

class Hardware:
    def __init__(self):
        self.dev = None
        self.min_voltage_mV = 2900
        self.max_voltage_mV = 5000

    def setup(self):
        self.dev = gpib.find('keithley')
        #self.write('*RST')
        self.write('DISP:CHAN 1')
        self.write('SENS1:NPLC 1')
        self.write('SENS1:AVER 3')


    def write(self, cmd):
        gpib.write(self.dev, '%s\n' % (cmd,))


    def read(self):
        ret = gpib.read(self.dev, 256).strip()
        return ret


    def set_all_power(self, power_on):
        if power_on:
            self.write(':OUTP1 ON')
            self.write(':OUTP2 ON')
        else:
            self.write(':OUTP1 OFF')
            self.write(':OUTP2 OFF')

    def set_channel_power(self, ch, power_on):
	if ch == 1:
	        if power_on:
        	    self.write(':OUTP1 ON')
        	else:
        	    self.write(':OUTP1 OFF')
	elif ch == 2:
	        if power_on:
        	    self.write(':OUTP2 ON')
        	else:
        	    self.write(':OUTP2 OFF')
	else:
		print " This channel is not present !"
		
    def shutdown(self):
        time.sleep(1)
        self.set_power(False)
        gpib.clear(self.dev)
        gpib.close(self.dev)


    def set_voltage(self, ch, u_mV):
	if ch == 1:
	        if u_mV < self.min_voltage_mV or u_mV > self.max_voltage_mV:
		    print "Raised exception"
        	    raise Exception('Illegal voltage: %d' % (u_mV,))
        	self.write(':SOUR1:VOLT %1.3f' % (float(u_mV) / 1000.0,))
	elif ch == 2:
	        if u_mV < self.min_voltage_mV or u_mV  > 5001:
        	    raise Exception('Illegal voltage: %d' % (u_mV,))
        	self.write(':SOUR2:VOLT %1.3f' % (float(u_mV) / 1000.0,))
	else:
		print " This channel is not present !"

    def set_current(self, ch, u_mA):
	if ch == 1:
	        if u_mA < 0 or u_mA > 1001:
        	    raise Exception('Illegal value for Current: %d' % (u_mA,))
        	self.write(':SOUR1:CURR %1.3f' % (float(u_mA) / 1000.0,))
	elif ch == 2:
	        if u_mA < 0 or u_mA > 1201:
        	    raise Exception('Illegal value for Current: %d' % (u_mA,))
        	self.write(':SOUR2:CURR %1.3f' % (float(u_mA) / 1000.0,))
	else:
		raise Exception(' This channel is not present !')

    def set_current_lim(self, i_mA):
        if i_mA <= 0 or i_mA > 1250:
            raise Exception('Illegal current: %d' % (i_mA,))
        self.write(':SOUR1:CURR:TYPE LIM')
        self.write(':SOUR1:CURR %1.3f' % (float(i_mA) / 1000.0,))


    def read_voltage(self, ch):
	if ch == 1:
        	self.write('SENS1:FUNC "VOLT"')
        	self.write('READ1?')
        	u_mV = int(float(self.read()) * 1000.0)
	elif ch == 2:
        	self.write('SENS2:FUNC "VOLT"')
        	self.write('READ2?')
        	u_mV = int(float(self.read()) * 1000.0)
	else:
		u_mv = -1

       	return u_mV


    def read_current(self, ch):
	if ch == 1:
        	self.write('SENS1:FUNC "CURR"')
        	self.write('READ1?')
        	i_mA = int(float(self.read()) * 1000.0)
	elif ch == 2: 
        	self.write('SENS2:FUNC "CURR"')
        	self.write('READ2?')
        	i_mA = int(float(self.read()) * 1000.0)
	else:
		i_mA = -1
	
        return i_mA


if __name__ == '__main__' :
    parser = optparse.OptionParser()
    parser.add_option("--charger-voltage", type="int", dest="charger_voltage",
                      default=5000,
                      help="Max charger voltage, either 5000 (default) or 6000")
    parser.add_option("--charger-current", type="int", dest="charger_current",
                      default=1200,
                      help="Max charger current is 1000")
    parser.add_option("--battery-voltage", type="int", dest="battery_voltage",
                      default=4200,
                      help="Max battery voltage 4200")
    parser.add_option("--battery-current", type="int", dest="battery_current",
                      default=900,
                      help="Max Battery current is 900")
    parser.add_option("--poweron", type="int", dest="poweron",
                      default=1,
                      help="Set poweron=0 to switch off")
    parser.add_option("--charger-enable", type="int", dest="charger_enable",
                      default=0,
                      help="Set charger-enable=0 to disable charging channel")
    parser.add_option("--battery-enable", type="int", dest="battery_enable",
                      default=0,
                      help="Set battery-enable=0 to disable battery channel")

    parser.add_option("-r", "--read-values", action="store_true", dest="read_values", default=False,
                      help="reads current values of V/I in battery and charger channel")

    (opts, args) = parser.parse_args()

    try:
    	hw = Hardware()
    	hw.setup()

	if opts.read_values:
		time.sleep(1)
		print "Battery Channel voltage: "+ str(hw.read_voltage(1))
		print "Battery Channel current: "+ str(hw.read_current(1))
		print "Charging Channel voltage: "+ str(hw.read_voltage(2))
		print "Charging Channel current: "+ str(hw.read_current(2))
        	hw.write('DISP:CHAN 1')
		sys.exit(0)

	if opts.poweron == 0:
		hw.set_all_power(False)
        	hw.shutdown()
		sys.exit(1)
	
	if opts.charger_enable == 1:
		hw.set_voltage(2, opts.charger_voltage)
		hw.set_current(2, opts.charger_current)
		hw.set_channel_power(2, True)

	if opts.battery_enable == 1:
		hw.set_voltage(1, opts.battery_voltage)
		hw.set_current(1, opts.battery_current)
		hw.set_channel_power(1, True)

	if opts.battery_enable == 0:
		hw.set_channel_power(1, False)

	if opts.charger_enable == 0:
		hw.set_channel_power(2, False)

    except:
	#print "Please check the connection !"
	pass
