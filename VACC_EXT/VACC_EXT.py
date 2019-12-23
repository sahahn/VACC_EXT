from __future__ import print_function
import paramiko
import getpass
from .config import config
import os
import shutil
import pickle as pkl
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic, needs_local_scope)
from .VACC import VACC


@magics_class
class VACC_EXT(Magics):

    def __init__(self, shell):

        # Call parent init
        super(VACC_EXT, self).__init__(shell)

        # Make SSH session
        self.make_ssh_session()

        # Init local dr
        self.init_drs()

    def make_ssh_session(self):

        self.ssh = paramiko.SSHClient()

        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(config['host'], 22,
                         username=config['username'],
                         password=getpass.getpass(
                            prompt='VACC Password:'))

    def init_drs(self):

        self.exts = ['.ML', '.py', '.script']

        if config['temp_local_dr'] == '':
            self.local_dr = os.getcwd()
        else:
            self.local_dr = config['temp_local_dr']

        # Make local dr
        os.makedirs(self.local_dr, exist_ok=True)

        # Make host dr
        stdin, stdout, stderr =\
            self.ssh.exec_command('mkdir ' + config['host_dr'])

    def get_current_host_files(self):

        stdin, stdout, stderr =\
            self.ssh.exec_command('cd ' + config['host_dr'] +
                                  " && for n in *; do printf '%s\n' \"$n\";" +
                                  "done")

        host_files = stdout.readlines()
        host_files = [f.rstrip() for f in host_files]

        return host_files

    def get_free_save_name(self):

        save = 'v_run'
        cnt = 0

        host_files = self.get_current_host_files()
        for ext in self.exts:

            while os.path.exists(os.path.join(
             self.local_dr, save + str(cnt) + ext)):
                cnt += 1

            while save + str(cnt) + ext in host_files:
                cnt += 1

        return save + str(cnt)

    def get_script_contents(self, save_name, cell, save_key, ML_name):

        c = []
        c.append('from ABCD_ML import Load')

        load_line = ML_name + ' = Load(loc="' + save_name + '", exp_name='

        if config['keep_run_logs']:
            load_line += '"' + save_key + '",'
        else:
            load_line += 'None,'

        load_line += ' log_dr="", verbose=True, notebook=False)'
        c.append(load_line)
        c.append('')

        verbose_line = ML_name + '.Set_Default_ML_Verbosity('
        if config['save_results']:
            verbose_line += 'save_results=True, '
        verbose_line += 'progress_bar=False)'
        c.append(verbose_line)

        # Add the user passed cell content
        c += cell.split('\n')
        c.append('')

        if config['save_obj']:
            c.append(ML_name + '.Save(loc="' + save_name + '")')
            c.append('')
        return c

    @cell_magic
    @needs_local_scope
    def v_run(self, line, cell, local_ns=None):
        # Get name of object + object itself
        split_line = line.split(' ')

        ML_name = split_line[0].strip()
        ML = local_ns[ML_name]

        # Proc rest of params
        params = {}
        for p in split_line[1:]:
            param, value = p.split('=')
            params[param] = value.replace('"', '').replace("'", "")

        config.update(params)
        self._run(ML, ML_name, cell)


    def run(self, ML, ML_name, cell, **kwargs):

       config.update(kwargs)
       self._run(ML, ML_name, cell)


    def _run(self, ML, ML_name, cell):

        # Get a valid save name
        save_key = self.get_free_save_name()
        save_name = save_key + '.ML'
        print('Run Name: ', save_key)

        local_save_loc = os.path.join(self.local_dr, save_name)
        host_save_loc = os.path.join(config['host_dr'], save_name)

        # Save the current ML object
        ML.Save(local_save_loc)

        # Get the script contents
        script_contents = self.get_script_contents(save_name, cell,
                                                   save_key, ML_name)

        # Generate the VACC scripts
        VACC(script_contents, key=save_key, local_dr=self.local_dr,
             host_dr=config['host_dr'], pool_mem=config['pool_mem'],
             ppn=config['ppn'], mem=config['mem'], vmem=config['vmem'],
             walltime=config['walltime'], source_sage=config['source_sage'])

        # Put the objects on the server
        ftp = self.ssh.open_sftp()

        for ext in self.exts:

            local_save_loc = os.path.join(self.local_dr, save_key + ext)
            host_save_loc = os.path.join(config['host_dr'], save_key + ext)
            ftp.put(local_save_loc, host_save_loc)

            # Remove the local copy, after moving
            os.remove(local_save_loc)

        ftp.close()

        # Run the job
        job_script = save_key + '.script'
        stdin, stdout, stderr =\
            self.ssh.exec_command('cd ' + config['host_dr'] + ' && ' +
                                  'qsub ' + job_script)

        stderr_lines = stderr.readlines()
        stderr_lines = [o.strip() for o in stderr_lines]
        stderr_lines = [o for o in stderr_lines if len(o) > 0]

        if len(stderr_lines) > 0:
            print('Job submitted with error message: ', end='')

            for line in stderr_lines:
                print(line)

            # Delete all
            self.delete(save_key)

        else:

            output_lines = stdout.readlines()
            output_lines = [o.strip() for o in output_lines]
            output_lines = [o for o in output_lines if len(o) > 0]

            print('Job submitted with message: ', end='')
            for line in output_lines:
                print(line)

            # Can delete the job script right away
            job_script_loc = os.path.join(config['host_dr'],
                                          save_key + '.script')
            stdin, stdout, stderr =\
                self.ssh.exec_command('rm ' + job_script_loc)

        return

    def delete(self, name):

        to_delete = ['', '.py', '.ML', '.script']
        for end in to_delete:
            to_del = os.path.join(config['host_dr'], name + end)
            _ = self.ssh.exec_command('rm -r ' + to_del)

    def collect(self, name, delete=False, _print=print):

        self._print = _print

        host_files = self.get_current_host_files()
        relevant = [h for h in host_files if name + '.o' in h]

        if name + '.ML' not in host_files:
            print('Job does not exist!')

        elif len(relevant) == 0:
            self.job_not_done(name)
        else:
            output_file = relevant[0]
            results = self.job_done(name, output_file, host_files,
                                    delete)

            return results

    def job_not_done(self, name):
        '''Regular print here as couldn't imagine
        wanting to keep this type of info in logs.'''

        print(name, 'not finished!')

        # Set a flag to see if the job was found in qstat
        found = False

        lines = self.get_qstat_lines()
        for line in lines:
            status = [l for l in line.split(' ') if len(l.rstrip()) > 0]

            if status[1] == name:
                found = True

                job_id = status[0]
                time = status[3]
                stat = status[4]

                if stat == 'C':
                    print('Something appears to have gone wrong,'
                          ' as status is completed, but no VACC',
                          ' output file was found!')
                    print('Deleting job files! Please resubmit.')
                    self.delete(name)

                else:
                    print('Status:', stat)
                    print('CPU Time Used:', time)
                    print('Job Id:', job_id)

        if not found:
            print('Something appears to have gone wrong,'
                  ' as this job does not appear in qstat',
                  ' and no output file was found!')
            print('Deleting job files! Please resubmit.')
            self.delete(name)

    def job_done(self, name, output_file, host_files, delete):

        results = {}
        output_loc = os.path.join(config['host_dr'], output_file)

        stdin, stdout, stderr =\
            self.ssh.exec_command('cat ' + output_loc)

        for line in stdout:
            self._print(line, end='')

        if delete:
            _ = self.ssh.exec_command('rm ' + output_loc)

        # If the key name is in host_files, then it is the
        # ABCD_ML generated dr
        if name in host_files:

            ftp = self.ssh.open_sftp()

            ML_loc = os.path.join(config['host_dr'], name)
            files = ftp.listdir(ML_loc)

            if 'results' in files:
                results_loc = os.path.join(ML_loc, 'results')
                results_files = files = ftp.listdir(results_loc)

                local_results_dr = os.path.join(self.local_dr,
                                                name + '_results')
                os.makedirs(local_results_dr, exist_ok=True)

                # Collect and load results
                for rf in results_files:

                    host_loc = os.path.join(results_loc, rf)
                    local_loc = os.path.join(local_results_dr, rf)

                    ftp.get(host_loc, local_loc)

                    # Load in the results pickle
                    with open(local_loc, 'rb') as f:
                        results[rf] = pkl.load(f)

                ftp.close()

                # Now remove local copy of files
                shutil.rmtree(local_results_dr)

            elif config['save_results']:
                print('Warning, no saved results found.')

            else:
                pass

        # If delete passed, delete VACC copy of things
        if delete:
            self.delete(name)

        return results

    def get_qstat_lines(self):

        # Get all jobs that are running or in queue
        stdin, stdout, stderr =\
            self.ssh.exec_command('qstat')
        lines = stdout.readlines()

        return lines

    def check_all(self):

        # Get all finished jobs
        host_files = self.get_current_host_files()
        done = [h for h in host_files if '.o' in h and 'v_run' in h]

        # Get all jobs in queue or running
        running = []
        queue = []
        other = []

        lines = self.get_qstat_lines()
        for line in lines:
            status = [l for l in line.split(' ') if len(l.rstrip()) > 0]
            name = status[1]

            if 'v_run' in name:
                stat = status[4]

                if stat == 'R':
                    running.append([name, status[3]])
                elif stat == 'Q':
                    queue.append(name)
                elif stat != 'C':
                    other.append([name, stat])

        if len(done) > 0:
            print('The following jobs are finished:')
            for d in done:
                print(d.split('.o')[0])
            print()

        if len(running) > 0:
            print('The following jobs are running:')
            for r in running:
                print(r[0], 'Cpu Time:', r[1])
            print()

        if len(queue) > 0:
            print('The following jobs are in queue:')
            for q in queue:
                print(q)
            print()

        if len(other) > 0:
            print('The following jobs have an unknown status')
            for o in other:
                print(o[0], 'Status:', o[1])
            print()


def connect():

    ip = get_ipython()
    magics = VACC_EXT(ip)
    ip.register_magics(magics)

    return magics
