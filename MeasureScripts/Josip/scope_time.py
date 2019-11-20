start = time()
for i in xrange(67):
    num_samples, wave = UHFLI_lib.get_scope_record(daq = daq, scopeModule=scopeModule)
stop = time()
print "Elapsed time:", stop-start
