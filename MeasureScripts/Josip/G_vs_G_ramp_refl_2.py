scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')
num_ramps  =1
# Number of adjacent points to average in the read data
num_aver_pts = 20
num_points_vertical = scope_segment_length//num_aver_pts
ramp = np.linspace(-num_ramps*ramp_amp, num_ramps*ramp_amp, num_ramps*num_points_vertical)  # Defining the ramp segment

num_samples, wave = UHFLI_lib.get_scope_record(daq = daq, scopeModule= scopeModule)   

# Organizing a scope shot, which is in this case the whole measurement, into individual rows of a matrix
refl_mag = wave[0].reshape(-1, scope_segment_length)   
refl_phase = wave[1].reshape(-1, scope_segment_length) 

# Average every num_ramps rows of the whole matrix 
#General formula for taking the average of r rows for a 2D array a with c columns:
#a.transpose().reshape(-1,r).mean(1).reshape(c,-1).transpose()
refl_mag = refl_mag.transpose().reshape(-1,num_ramps).mean(1).reshape(scope_segment_length,-1).transpose()
refl_phase = refl_phase.transpose().reshape(-1,num_ramps).mean(1).reshape(scope_segment_length,-1).transpose()

# Kick out the last elements from each trace, which do not fit in num_points_vertical*num_aver_pts
refl_mag = refl_mag[:,:num_points_vertical*num_aver_pts]
refl_phase = refl_phase[:,:num_points_vertical*num_aver_pts]


# Average amongst defined number (num_aver_pts) of adjacent samples
refl_mag = refl_mag.reshape(-1, num_aver_pts).mean(1).reshape(-1, num_points_vertical)
refl_phase = refl_phase.reshape(-1, num_aver_pts).mean(1).reshape(-1, num_points_vertical)
