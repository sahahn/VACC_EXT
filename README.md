# VACC_EXT

This library is designed as a specialized extension to the ABCD_ML library (https://github.com/sahahn/ABCD_ML). Make sure you have the latest version of ABCD_ML installed!

The purpose is to allow users at the University of Vermont with VACC accounts an easy way to integrate ABCD_ML expiriments within a local notebook to the VACC.

Install
-------

Navigate to the directory you would like to install this package and type:
(Explaination of each step below)

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


Usage
-------

VACC_EXT is designed to work within a jupyter-notebook environment, and will therefore
only work in this type of environment with ABCD_ML code. 

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

One common use case is to run your expiriment through data loading, and defining CV strategy ect...
up until the Modeling phase before submitting any jobs. In this example it is further assumed that the main
ABCD_ML object is called ML, and that ML.Set_Default_ML_Params have already been set.
To run a cell of code externally on the VACC one then just has to put on the first line of a cell 
'%%v_run Name_Of_ABCD_ML_Object' for example:

```python
%%v_run ML

ML.Evaluate(model='linear')
```





