config = {}

# hostname of Vacc
config['host'] = 'bluemoon-user1.uvm.edu'

# your username on the VACC
config['username'] = 'sahahn'

# dr in which to temp store runs on the VACC
config['host_dr'] = '/users/s/a/sahahn/ABCD_ML_Runs'

# a temp local dr to store intermediary files, leave as '' for whatever
# the current directory is
config['temp_local_dr'] = ''

# If False, don't keep run logs,
# If True, will keep logs as base key name
config['keep_run_logs'] = True

# Keep run logs must True for save_results to work!
# Save results will allow the user to retrieve the full
# results dict from each Evaluate or Test call
config['save_results'] = True

# Unless you have an up to date version of ABCD_ML installed
# on your VACC account, leave this option as True,
# as it will source sages ABCD_ML install before running.
config['source_sage'] = True

# Default VACC run params
config['pool_mem'] = True
config['ppn'] = '8'
config['mem'] = '20gb'
config['vmem'] = '30gb'
config['walltime'] = '20:00:00'
