config = {}

# Your username/netid that you use to login to the VACC
config['username'] = 'sahahn'

# Hostname of VACC,
# for example you could change this to 'bluemoon-user2.uvm.edu'
config['host'] = 'bluemoon-user1.uvm.edu'

# The directory in which to store runs on the VACC.
# You can specify an absolute path, or a relative path from
# your home dr, a relative path is listed below.
config['host_dr'] = 'ABCD_ML_Runs'

# A temporary local directory in which to store intermediary files.
# Leave as '' to use whatever directory the code is being run from.
# Note: No files will be left in this directory with the expection of if
# an error occurs or VACC_EXT is interrupted during a run for some reason.
config['temp_local_dr'] = ''

# If False, don't keep run logs,
# If True, will keep logs as base key name
config['keep_run_logs'] = True

# Keep run logs must True for save_results to work!
# Save results will allow the user to retrieve the full
# results dict from each Evaluate or Test call
config['save_results'] = True

# If for some reason you want to save the ABCD_ML object
# after the block of code has been run, I guess e.g., you
# save some values in a class param, and want to recover it.
# Or maybe you do all your data loading on the VACC then want to
# recover that object, I don't know.
# In those cases, you can set save_obj to True, and after the v_run
# the saved copy of the ML object on the VACC will be overriden
# with the object object whatever block of code was run.
config['save_obj'] = False

# Unless you have an up to date version of ABCD_ML installed
# on your VACC account, leave this option as True,
# as it will source sages ABCD_ML install before running.
config['source_sage'] = True

# Default VACC params when submitting jobs, basically dictates
# what the default v_run job should look like.

# The number of processors to run your job with,
# so you should set n_jobs within an Evaluate or Test call
# to this number.
config['ppn'] = '8'
config['mem'] = '20gb'
config['vmem'] = '30gb'
config['walltime'] = '20:00:00'

# This param will likely always be kept as True
# unless the job you are running needs only a very small
# amount of memory, it dictates if a pooled memory job should be run.
config['pool_mem'] = True
