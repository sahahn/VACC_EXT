# VACC_EXT

This library is designed as a specialized extension to the ABCD_ML library (https://github.com/sahahn/ABCD_ML). Make sure you have the latest version of ABCD_ML installed!

The purpose is to allow users at the University of Vermont with VACC accounts an easy way to integrate ABCD_ML expiriments within a local notebook to the VACC.

## Install

Navigate to the directory you would like to install this package and type:
(More details for each step below)

<pre>
git clone https://github.com/sahahn/VACC_EXT.git
cd VACC_EXT
nano VACC_EXT/config.py
pip install .
</pre>

1.  git clone https://github.com/sahahn/VACC_EXT.git
Creates a copy of this code repository.

2.  cd VACC_EXT
Navigate within the cloned copy of this code

3.  nano (or whatever text editor you are comfortable with) VACC_EXT/config.py

Within config.py, you will at the very least need to change config['username'] to your VACC username. 
It is further reccomended to look through the other params and change any that you may wish to change.
While all params can be changed at the time of submitting a job, the only way to update any changes to
congig.py requires re-installing VACC_EXT, as seen in the next step.

4. pip install . 
Make sure this command is run in the top level VACC_EXT directory, and only after config.py has been
changed to your desired settings. If you wish to change config.py in the future, just re-run pip install .
afterwards to update those changes.


## Usage

VACC_EXT is designed to work within a jupyter-notebook environment, and will therefore
only work in this type of environment with ABCD_ML code. 

### Connect

At the start of your jupyter notebook / Ipython session, you must import the library and setup a connection.
```python
from VACC_EXT import connect
VE = connect()
```

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output1.png" />
</p>

Enter your VACC account password in the prompt, and an ssh session will be established for this run!
Note: The above code only needs to be run once at the start of an expiriment, and saves the connection
within an object called VE (you can set this to whatever you wish, but within the example VE will refer to
this connection object).

Once a connection has been established, you can now easily run a cell of code containing an
ABCD_ML expiriment on the VACC! There are few restrictions,
but it will be hopefully straightforeward what you can and can't do with a few examples.

### Submit a job with v_run

One common use case is to run your expiriment locally all the way through data loading, and defining CV strategy ect...
up until the Modeling phase. In this example it is further assumed that the main
ABCD_ML object is called ML, and that ML.Set_Default_ML_Params have already been set. This example
then shows a case where everything has been set up expect actually running usually compute intensive
Evaluate calls, a perfect place to run on the VACC instead! 
To run a cell of code on the VACC, one just has to place the following on the first line of
a jupyter noteboook cell:
'%%v_run Name_Of_ABCD_ML_Object' for example:

```python
%%v_run ML

ML.Evaluate(model='dt')
```

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output2.png" />
</p>

In this case, a job is sumbitted to the VACC, and will run ML.Evaluate as if run in this place within the notebook (i.e., taking into account any previously defined default ML params, and whatever data is loaded ect...). Notice from the output the run_name, which is 'v_run0', and the second message which tells us the job submitted correctly.

There are a few other things to know about the %%v_run command. The first argument after %%v_run and seperated by a space is always required to be the name of whatever ABCD_ML object is used in the rest of the cell, but beyond that, you can also specify 
a differing value for any of the config.py values (except username, and host as you've already established a connection)! These params can be specified following the name of the ABCD_ML object as 'param=value' pairs each seperated by a space (any order is okay). For example, we could specify some values as:

```python
%%v_run ML ppn=8 mem=30gb walltime=30:00:00

ML.Evaluate(model='dt')
```

Be careful though! Any passed params here define new default params for the rest of this session! For example
if you set ppn=1 and submitted a v_run, and then below it submitted another v_run with no value set for ppn, the
new default for the rest of this session is 1, so it will also be submitted with 1 processor. This behavior can be both useful and potentially misleading, so just beware.

Another large caveat to submitting jobs with v_run is that variables beyond the ABCD_ML object will not be
passed to the job. In other words, if you have a python list defined earlier, say:

```python
runs = ['dti', 'mid', 'sst']
```

You **cannot** run the code below for two reasons!

```python
%%v_run ML

results = []
for run in runs
    result = ML.Evaluate(model='dt'
                         feats_to_use=run)
    results.append(results)
```

First, the variable run will not be passed to the VACC job, so the loop will not
run. To get around this you have to either define run within the cell, e.g.,

```python
%%v_run ML

runs = ['dti', 'mid', 'sst']

results = []
for run in runs
    result = ML.Evaluate(model='dt'
                         feats_to_use=run)
    results.append(results)
```

or as a class value, e.g.,

```python
ML.runs = ['dti', 'mid', 'sst']
```

and then in the main cell:

```python
%%v_run ML

results = []
for run in ML.runs
    result = ML.Evaluate(model='dt'
                         feats_to_use=run)
    results.append(results)
```

The second reason all of the above code might not work exactly as desired as while
appending the results to the locally defined results list will run, and will not give errors,
there is no way to recover the values of results from the VACC - as atleast for right now,
what you can get back as output from v_run jobs is fairly specific (but hopefully not limiting!).
Which leads us into the second main functionality of VACC_EXT, namely getting the output from a job run with v_run.


### Get the output from a job

An important point of running code externally is obviously being able to access the outcome of the externally run code. 
This functionally is implemented with the class method 'collect'. Specifically, you access this method through the
connection object, which we named VE in this example, obtained from the initial 'VE = connect()'.

At a bare minimum one needs to know the name of the submitted job they want to collect, e.g., in our case v_run0.
```python
results = VE.collect('v_run0')
```

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output3.png" />
</p>

In this case, we can see that the job has not yet finished, but we can see that it is running (Status = 'R'), and are given a measure of how long it has run (though in CPU time, so with 8-cores this easily outpaces clock time). Lastly, the job id is given, so if you want to log on to the VACC and check the job manually, you can refer to that job number. 

Let's see a case where the job has actually finished.
```python
results = VE.collect('v_run0')
```

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output4.png" />
</p>

In this case, the output which is normally printed as in a local call to Evaluate, is also printed here. One thing is this output is by default just printed, if you would like it to be saved in the local expiriments logs, you can optionally pass the following instead:

```python
results = VE.collect('v_run0', _print=ML._print)
```

This command just uses the ABCD_ML ML object's print instead of pythons default print, so will store logs if that is the behavior you have setup. 

The next thing to note is if in config, as passed special params to v_run, you specified both
```python
config['keep_run_logs'] = True
*and*
config['save_results'] = True
```
then results will return to you a dictionary containing the outputs to all calls to Evaluate or Test within thr cell that was run. So typically, when running ABCD_ML locally, when you call Evaluate or Test, it returns a dictionary with various outputs including summary score, raw scores, raw predictions, feature importances, ect... The only different here is that the output is a dictionary of these typical dictionaries (as this allows you to run more then one call to Evaluate per v_run!).

For example we can look in results:

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output5.png" />
</p>

We see from above that our run_name was saved as 'dt', so within results we can access the specific results via 'dt.eval' (or if it was a call to Test, 'dt.test' - or when in doubt just interactively view the keys in results!)

The last parameter to note is an optional call to boolean 'delete'. For example if you run:

```python
results = VE.collect('v_run0', delete=True)
```

You will get the same output as before, but after returning it to you all of the saved data on the VACC from the run will be deleted. This can be useful just a shortcut to clean up space. To make sure everything was deleted you can either manually check the directory on the VACC yourself, or just call the collect command again and get output:

<p align="center">
  <img src="https://raw.githubusercontent.com/sahahn/VACC_EXT/master/example_output/Output6.png" />
</p>

Which is what you'll get if the job you are looking for doesn't exist, due to either never been run or in this case deleted.


### Final thoughts

Well thats mostly it. If you discover any bugs, or have any ideas for extra functionality that you would like to see please let me know!






