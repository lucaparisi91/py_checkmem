# py_checkmem

A python script that polls memory usage from the os.

## Installation

You can build with pip.  

```bash
pip install .
```

## Testing

Use

```bash

pytest  -vvv --capture=tee-sys checkmem/tests
flake8  --max-line-length=120   src/checkmem 

```

## Usage

The quickest way to get started is to run:

```
checkem
```

See `checkmem -h ` for a list of options.

To run on multiple nodes you will need to launch checkmem on each node in the background and then send a SIGINT signal to checkmem to ensure its clean termination.

```bash
srun --hint=nomultithread --distribution=block:block --ntasks=32 --nodes=32 --ntasks-per-node=1 --overlap checkmem --recorder_type process &
sleep 30 # Make sure checkmem started
srun --hint=nomultithread --distribution=block:block my_app # Launch you application as usual
scancel --signal=INT $SLURM_JOB_ID.0 # Stop monitoring memory and close safely
wait
```
