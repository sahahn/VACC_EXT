import os
import random
import shutil


class VACC():

    def __init__(self, contents, key, local_dr, host_dr, pool_mem=True,
                 ppn='8', mem='20gb', vmem='30gb', walltime='20:00:00',
                 name='ABCD_ML', source_sage=True):

        self.key = key
        self.contents = contents
        self.local_dr = local_dr
        self.host_dr = host_dr
        self.pool_mem = pool_mem
        self.ppn = ppn
        self.mem = mem
        self.vmem = vmem
        self.walltime = walltime
        self.name = name
        self.source_sage = source_sage

        self.make_base_script()
        self.make_vacc_script()

    def make_base_script(self):

        py_loc = os.path.join(self.local_dr, self.key + '.py')

        with open(py_loc, 'w') as f:
            for line in self.contents:
                f.write(line)
                f.write('\n')

    def make_vacc_script(self):

        script_loc = os.path.join(self.local_dr, self.key + '.script')

        with open(script_loc, 'w') as f:

            if self.pool_mem:
                f.write('#PBS -qpoolmemq')
                f.write('\n')

            f.write('#PBS -l nodes=1:ppn=' + str(self.ppn))
            f.write(',mem=' + str(self.mem) + ',vmem=' + str(self.vmem))
            f.write('\n')

            f.write('#PBS -l walltime=' + str(self.walltime))
            f.write('\n')

            f.write('#PBS -N ' + str(self.key))
            f.write('\n')

            f.write('#PBS -j oe\n')

            if self.source_sage:
                f.write('source /users/s/a/sahahn/.bashrc')
                f.write('\n')

            f.write('cd ')
            f.write(self.host_dr)
            f.write('\n')

            f.write('python ' + self.key + '.py')

            f.write('\n')
