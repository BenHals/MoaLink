import sys, os
import shlex
import glob
import argparse
import random
import pickle

import moaLink
import config
import subprocess


import numpy as np

from time import process_time






def start_run(options):
    if not os.path.exists(options.experiment_directory):
        print('No Directory')
        return
    name = '-'.join([options.moa_learner, str(options.concept_limit)])
    datastream_filename = None
    datastream_pickle_filename = None
    fns = glob.glob(os.sep.join([options.experiment_directory, "*.ARFF"]))
    print(fns)
    for fn in fns:
        if fn.split('.')[-1] == 'ARFF':
            actual_fn = fn.split(os.sep)[-1]
            fn_path = os.sep.join(fn.split(os.sep)[:-1])
            print(actual_fn)
            print(fn_path)
            pickle_fn = f"{actual_fn.split('.')[0]}_concept_chain.pickle"
            pickle_full_fn = os.sep.join([fn_path, pickle_fn])
            csv_fn = f"{name}.csv"
            csv_full_fn = os.sep.join([fn_path, csv_fn])
            if os.path.exists(pickle_full_fn):
                skip_file = False
                if os.path.exists(csv_full_fn):
                    if os.path.getsize(csv_full_fn) > 2000:
                        skip_file = True
                if not skip_file:
                    datastream_filename = fn
                    datastream_pickle_filename = pickle_full_fn
                    break
                else:
                    print('csv exists')
    if datastream_filename == None:
        print('Not datastream file')
        return
    print(datastream_filename)

    
    bat_filename = f"{options.experiment_directory}{os.sep}{name}.{'bat' if not options.using_linux else 'sh'}"
    if not os.path.exists(bat_filename) or True:
        with open(f'{datastream_pickle_filename}', 'rb') as f:
            concept_chain = pickle.load(f)
        print(concept_chain)
        concepts = sorted(list(concept_chain.keys()))
        num_examples = concepts[-1] + (concepts[-1] - concepts[-2])
        stream_string = moaLink.get_moa_stream_from_filename(os.sep.join(datastream_filename.split(os.sep)[:-1]), datastream_filename.split(os.sep)[-1])
        moa_string = moaLink.make_moa_command(
            stream_string,
            options.moa_learner,
            options.concept_limit,
            'int',
            num_examples,
            config.report_window_length,
            options.experiment_directory,
            is_bat= not options.using_linux
        )
        moaLink.save_moa_bat(moa_string, bat_filename, not options.using_linux)
        # datastream = None
    t_start = process_time()
    command = f"{bat_filename} {options.moa_location}"
    print(command)
    if options.using_linux:
        
        subprocess.run(['chmod' ,'+x', bat_filename])
        subprocess.run([bat_filename, options.moa_location])
    else:
        subprocess.run(command)
    #fsm, system_stats, concept_chain, ds, stream_examples =  fsmsys.run_fsm(datastream, options, suppress = True, name = name, save_checkpoint=True)
    t_stop = process_time()
    print("")
    print("Elapsed time during the whole program in seconds:", 
                                         t_stop-t_start)
    # with open(f"{options.experiment_directory}{os.sep}{name}_timer.txt", "w") as f:
    #     f.write(f"Elapsed time during the whole program in seconds: {t_stop-t_start}")
    # display.results.stitch_csv(options.experiment_directory, name)

def subdir_run(options):
    base_directory = options.experiment_directory
    list_of_directories = []
    for (dirpath, dirnames, filenames) in os.walk(base_directory):
        for filename in filenames:
            if filename.endswith('.ARFF'): 
                list_of_directories.append(dirpath)
    list_of_directories.sort(reverse = True)
    for subdir in list_of_directories:
        options.experiment_directory = subdir
        start_run(options)

class MoaOptions:
    def __init__(self, concept_limit, moa_location, using_linux, directory, moa_learner):
        self.concept_limit = concept_limit
        self.moa_location = moa_location
        self.using_linux = using_linux
        self.experiment_directory = directory
        self.seed = None
        self.moa_learner = moa_learner

if __name__ == "__main__":
    # Set config params, get commandline params
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--seed", type=int,
        help="Random seed", default=None)
    ap.add_argument("-n", "--noise", type=float,
        help="Noise", default=0)
    ap.add_argument("-cl", "--conceptlimit", type=int,
        help="Concept limit", default=-1)
    ap.add_argument("-d", "--directory",
        help="tdata generator for stream", default="datastreams")
    ap.add_argument("-m", "--moa",
        help="Moa location", default=f"moa{os.sep}lib{os.sep}")
    ap.add_argument("-ml", "--moalearner",
        help="Moa location", default=f"rcd", choices = ['ht', 'rcd'])
    ap.add_argument("-l", "--linux", action="store_true",
        help="running on linux")
    args = vars(ap.parse_args())
    options = MoaOptions(args['conceptlimit'], args['moa'], args['linux'], args['directory'], args['moalearner'])

    seed = args['seed']
    if seed == None:
        seed = random.randint(0, 10000)
        args['seed'] = seed
    options.seed = seed

    subdir_run(options)

