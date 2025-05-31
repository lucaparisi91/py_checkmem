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