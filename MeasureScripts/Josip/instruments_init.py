IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM1', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')
dmm2 = qt.instruments.create('dmm2','a34410a', address = 'USB0::0x2A8D::0x0101::MY54506631::INSTR')

magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.150')
magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.175')