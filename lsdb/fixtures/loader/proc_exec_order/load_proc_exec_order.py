# load_proc_exec_order.py initial_id
# Generates procedureexecutionorder objects to build Test Sequence Definitions
# from Procedure Results
# John Watts, PVEL
# john.watts@pvel.com
#
# Arguments:
# initial_id - the first primary key of the record series


import sys
import csv
import json
import os

# Create JSON template
executiongroup = json.loads("""{
    "model": "lsdb.procedureexecutionorder",
    "pk": 162,
    "fields": {
        "execution_group_name": "Isc EL Image",
        "test_sequence": 7,
        "procedure_definition": 12,
        "execution_group_number": 24,
        "allow_skip": true
    }
}""")

# Set initial id value from argument
pk = int(sys.argv[1])

# load_proc_exec_order(pk, egfilepath, outputfilepath)
# Generates procedureexecutionorder objects to build Test Sequence Definitions
# Arguments:
# pk - the first primary key of the record series
# egfilepath - path to a CSV containing the procedureexecutionorder definitions
# with a header containing the following names:
# execution_group_number,execution_group_name,allow_skip,
# test_sequence,procedure_definition (other columns are ignored)
# outputfilepath - path where a JSON file will be written
# with procedureexecutionorder objects
# Returns the next pk value
def load_proc_exec_order(pk, egfilepath, outputfilepath):
    # Open files
    with open(egfilepath, newline='') as csvfile, \
        open(outputfilepath, 'a+') as outputfile:
        # This uses the first row as field names and reads next rows as dicts
        egreader = csv.DictReader(csvfile)
        for row in egreader:
            # Populate the procedureexecutionorder dict,
            # leaving previous values if no new value given
            executiongroup['pk'] = pk
            for key in executiongroup['fields']:
                # Integers
                if key in {'test_sequence', 'procedure_definition', 'execution_group_number'}:
                    if row[key]: executiongroup['fields'][key] = int(row[key])
                # Booleans
                elif key in {'allow_skip'}:
                    if row[key]: executiongroup['fields'][key] = (row[key].lower() == 'true')
                # Strings
                elif key in {'execution_group_name'}:
                    if row[key]: executiongroup['fields'][key] = row[key]
                # If we don't know it, don't load it!

            # Dump to JSON and write to output file
            outputfile.write(json.dumps(executiongroup, indent=4) + ',\n')
            # Increment the pk (id) for the next go-round
            pk += 1
    return pk
            

# Get all files in working directory
filelist = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]
for f in filelist:
    # Use this to generate separate files for each Test Sequence Definition
    # pk = load_proc_exec_order(pk, f, (os.path.splitext(f)[0] + '.json'))
    # Use this to create one file for all Test Sequence Definitions
    pk = load_proc_exec_order(pk, f, 'proc_exec_order.json')
    