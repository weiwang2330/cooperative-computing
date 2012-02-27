#!/usr/bin/env python

# Enumerates parameter combinations
# Replaces regex's in protomol config file with values

import glob
import itertools
import os
import random
import shutil
import sys

fs = 1.0
ps = 1000.0 * fs
ns = 1000.0 * ps

def get_run_params(run):
    values                     = dict()
    dt                         =  2 * fs
    values['REGEX_NUMSTEPS']   =  1 * ps / dt
    values['REGEX_OUTPUTFREQ'] = 1000 * fs / dt
    values['REGEX_SEEDME']     = random.randint(0, 1000000)
    values['REGEX_TIMESTEP']   = dt
    return values

def copy_replace(infilename, outfilename, values):
    """
    Copies file from infile to outfile line by line, replacing strings as it goes.
    Values is a dict mapping regexs to values.
    """
    infile = open(infilename)
    outfile = open(outfilename, "w")
    for ln in infile:
        for regex, value in values.iteritems():
            ln = ln.replace(regex, str(value))
        outfile.write(ln)
    infile.close()
    outfile.close()

home   = sys.argv[1]
gendir = sys.argv[2]
run    = int(sys.argv[3])
clone  = int(sys.argv[4])

me = sys.argv[0]

print "[%s] %s %s %s %s " % (me, home, gendir, run, clone)

if not os.path.exists(gendir):
    os.makedirs(gendir)

common_init_files = glob.glob(os.path.join(home, 'datafiles-init-all', '*'))
startpdb          = os.path.join(home, 'startpdbs', 'state%d.pdb' % run)
starttpr          = os.path.join(home, 'topol.tpr')
startweight       = os.path.join(home, 'startpdbs', 'weight%d.txt' % run)
startcolor        = os.path.join(home, 'startpdbs', 'color%d.txt' % run)

shutil.copy(startpdb, os.path.join(gendir, 'start.pdb'))
shutil.copy(startweight, os.path.join(gendir, 'weight.txt'))
shutil.copy(starttpr, os.path.join(gendir, 'topol.tpr'))
shutil.copy(startcolor, os.path.join(gendir, 'color.txt'))

for path in common_init_files:
    shutil.copy(path, gendir)


input_config  = os.path.join(home, "template-protomol.conf")
output_config = os.path.join(gendir, "protomol.conf")

run_params = get_run_params(run)
copy_replace(input_config, output_config, run_params)

### mapping file is the list of parameters for the RUNs
mappings_file = os.path.join(home, "CONFIGS.mapping")
if run == 0 and os.path.exists(mappings_file):
    os.remove(mappings_file)

params_str = " ".join([str(k) + " " + str(v) for k, v in run_params.iteritems()])
message = "RUN %s %s" % (run, params_str)
print "[%s] Prepared: %s" % (me, message)
with open(mappings_file, 'a') as fd:
    fd.write("%s\n" % message)