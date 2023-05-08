#!/bin/bash

# A directory to hold everything
echo "Making directory... 'testing/'"
mkdir -p testing

# Build the executable
echo "Creating reference executable... 'testing/correct'"
make --silent --directory=ag/solution ship
cp ag/solution/galaxy testing/correct

# Run the tests found in project.ini with ag correct executable
# and store outputs in test-output/ as '-out.txt' files
echo "Running integration tests from project.ini, storing outputs in 'testing/'"
python3 << EOF
import configparser as cp
import subprocess

config = cp.RawConfigParser()
config.optionxform = lambda option: option
config.read('project.ini')

print('Decompressing test case inputs... ', end='', flush=True)
with subprocess.Popen(f"xz --decompress {config['integration-info']['test-dir']}/*.xz",
shell=True,
stderr=subprocess.PIPE) as p:
    p.wait()
print('done!')

for key in config['integration-tests'].keys():
    with open('testing/' + key + '-out.txt', 'wb') as cout:
        args = config['integration-tests'][key].split(' ')
        infile = 'ag/tests/' + args[0]
        subprocess.run(['echo', f"  {key}: correct < ag/tests/{config['integration-tests'][key]} > {key}-out.txt"])
        args[0] = 'testing/correct'
        with open(infile) as cin:
            p = subprocess.run(args, stdin=cin, stdout=cout)

[config.remove_section(s) for s in config.sections() if s != 'integration-tests']

with open('testing/integration-tests.ini', 'w') as itini:
    config.write(itini)

subprocess.run(['tree', 'testing'])
EOF
