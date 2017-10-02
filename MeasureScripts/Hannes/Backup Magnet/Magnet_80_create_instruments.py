print "Create Keithley1"
keithley1 = qt.instruments.create('keithley1','Keithley_2000', address='GPIB0::16')

print "Create Keithley2"
keithley2 = qt.instruments.create('keithley2','Keithley_2000', address='GPIB0::17')

print "Create IV rack."
#ivvi = qt.instruments.create('ivvi', 'OPTO', address='ASRL1', numdacs=8)
ivvi = qt.instruments.create('ivvi', 'IVVI', address='ASRL1', numdacs=16)

print "Create SRS830"
lockin1 = qt.instruments.create('lockin1','SR830', address='GPIB0::8')

print "Create AMI430 Magnet Supply"
magnet = qt.instruments.create('magnet', 'AMI430', address='169.254.65.236') #237 is Bx, 236 is Bz192.168.0.1  '169.254.65.236'

print "Create AMI430 MagnetX Supply"
magnetX = qt.instruments.create('magnetX', 'AMI430_Bx', address='169.254.65.237') #237 is Bx, 236 is Bz


#print "Create mw generator"
#mw = qt.instruments.create('mw','SMB100A', address='GPIB0::28')

#print "Create Lakeshore controller"
#Lakeshore = qt.instruments.create('Lakeshore','Lakeshore_325', address='GPIB0::12')








#print "Create SRS830"
#lockin1 = qt.instruments.create('lockin1','SR830', address='GPIB0::8')

#print "Create AMI_magnet"
#magnet = qt.instruments.create('magnet', 'AMI_magnet', address='ASRL7')

#print "Create Cryomagnetics_CS4_magnet"
#magnet = qt.instruments.create('magnet', 'Cryomagnetics_CS4_magnet', address='GPIB0::9')

#print "Create Cryogenic SMC120C Magnet Supply"
#magnet = qt.instruments.create('magnet', 'Cryogenic_SMS120C_USB_magnet', address='ASRL4')



#print "Create Keithley1"
#keithley1 = qt.instruments.create('keithley1','Keithley_2000', address='GPIB0::17')

#print "Create Keithley2"
#keithley2 = qt.instruments.create('keithley2','Keithley_2000', address='GPIB2::17')


#print "Create Wiltron generator"
#mw = qt.instruments.create('mw','wiltron_mw', address='GPIB0::5')

#print "Create SRS830"
#lockin1 = qt.instruments.create('lockin1','SR830', address='GPIB0::8')

#print "Create Cryogenic SMC120C Magnet Supply"
#magnet = qt.instruments.create('magnet', 'Cryogenic_SMS120C_USB_magnet', address='ASRL4')

#print "Create Cryogenic SMC120C MagnetX Supply"
#magnetX = qt.instruments.create('magnetX', 'Cryogenic_SMS120C_USB_magnetX', address='ASRL6')

#print "Create Cryomagnetics_CS4_magnet"
#magnet = qt.instruments.create('magnet', 'Cryomagnetics_CS4_magnet', address='GPIB0::21')

#print "Create Cryomagnetics_CS4_magnetX"
#magnetX = qt.instruments.create('magnetX', 'Cryomagnetics_CS4_magnetX', address='GPIB0::9')

#print "Create Cryogenic SMC120C Magnet_X Supply"
#magnetX = qt.instruments.create('magnetX', 'Cryogenic_SMS120C_USB_magnetX', address='ASRL4')

#print "Create Cryogenic SMC120C Magnet_Z Supply"
#magnetZ = qt.instruments.create('magnetZ', 'Cryogenic_SMS120C_USB_magnetZ', address='ASRL5')