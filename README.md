# batvis
Batvis is a tool to assist in the generation of a variety of plots from data produced by our modified version of the batsim program. This tool is intended to be run from the command line, and can be scripted through the use of bash scripts. This tool pulls information from the config files of a batsim experiment run, then charts the jobs based on the information in the out_jobs.csv file. As the program traverses the expected directory structure of our batsim outputs, there is no need to specifically pull these files out; instead just point batvis at the directory for the "run" of batsim. 
## Installation
Note: Installation assumes that you are already using the batsim4 repo from [here]() configured with the batsched4 repo from [here]().

1. Clone this repo and the evalys repo from [here](https://gitlab.newmexicoconsortium.org/lanl-ccu/evalys). 
2. Change to the macOS branch of this repo by running `cd batsimGantt && git checkout macOS && cd ..`
3. Change to the dev branch of the evalys repo by running `cd evalys && git checkout dev && cd ..`
4. Run `pip install ./evalys && pip install ./batsimGantt` to install both the modified evalys library and this program

## Usage
Execute this program by running `python3 -m batvis [options]`. You can also call the modules batvis.main, batvis.gantt, batvis.plots, and batvis.utils separately from within a python script. This is the format for running this program:

``` python3 -m batvis -i <inputpath> [-o <outputfile>] [-r <y/N>] [-s <y/N>] [-w <y/N>] ```

in practice, this looks like this:

``` python3 -m batvis -i/home/vivi/experiments/110822/Steve_reservations_90k_tests/12_half_100exp/experiment_1/id_100 -o/tmp/testing -ry -wy -sy```

you can run it with as many or as few options as you want. For example, to only generate window plots:

``` python3 -m batvis -i/home/vivi/experiments/110822/Steve_reservations_90k_tests/12_half_100exp/experiment_1/id_100 -o/tmp/testing -wy```

The options are detailed below:

| Option | Description                                                   |
|--------|---------------------------------------------------------------|
| -r     | Gantt charts for each reservation                             |
| -s     | Bubble plots for each reservation                             |
| -b     | Binned plot for each reservation                              |
| -w     | Gantt charts generated for a window containing 4 reservations |
| -t     | Timeline plot                                                 |