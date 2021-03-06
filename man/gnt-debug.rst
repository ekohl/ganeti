gnt-debug(8) Ganeti | Version @GANETI_VERSION@
==============================================

Name
----

gnt-debug - Debug commands

Synopsis
--------

**gnt-debug** {command} [arguments...]

DESCRIPTION
-----------

The **gnt-debug** is used for debugging the Ganeti system.

COMMANDS
--------

IALLOCATOR
~~~~~~~~~~

**iallocator** [--debug] [--dir *DIRECTION*] {--algorithm
*ALLOCATOR* } [--mode *MODE*] [--mem *MEMORY*] [--disks *DISKS*]
[--disk-template *TEMPLATE*] [--nics *NICS*] [--os-type *OS*]
[--vcpus *VCPUS*] [--tags *TAGS*] {*instance*}

Executes a test run of the *iallocator* framework.

The command will build input for a given iallocator script (named
with the ``--algorithm`` option), and either show this input data
(if *DIRECTION* is ``in``) or run the iallocator script and show its
output (if *DIRECTION* is ``out``).

If the *MODE* is ``allocate``, then an instance definition is built
from the other arguments and sent to the script, otherwise (*MODE* is
``relocate``) an existing instance name must be passed as the first
argument.

This build of Ganeti will look for iallocator scripts in the following
directories: @CUSTOM_IALLOCATOR_SEARCH_PATH@; for more details about
this framework, see the HTML or PDF documentation.

DELAY
~~~~~

**delay** [--debug] [--no-master] [-n *NODE*...] {*duration*}

Run a test opcode (a sleep) on the master and on selected nodes
(via an RPC call). This serves no other purpose but to execute a
test operation.

The ``-n`` option can be given multiple times to select the nodes
for the RPC call. By default, the delay will also be executed on
the master, unless the ``--no-master`` option is passed.

The *delay* argument will be interpreted as a floating point
number.

SUBMIT-JOB
~~~~~~~~~~

**submit-job** [--verbose] [--timing-stats] [--job-repeat ``N``]
[--op-repeat ``N``] {opcodes_file...}

This command builds a list of opcodes from files in JSON format and
submits a job per file to the master daemon. It can be used to test
options that are not available via command line.

The ``verbose`` option will additionally display the corresponding
job IDs and the progress in waiting for the jobs; the
``timing-stats`` option will show some overall statistics inluding
the number of total opcodes, jobs submitted and time spent in each
stage (submit, exec, total).

The ``job-repeat`` and ``op-repeat`` options allow to submit
multiple copies of the passed arguments; job-repeat will cause N
copies of each job (input file) to be submitted (equivalent to
passing the arguments N times) while op-repeat will cause N copies
of each of the opcodes in the file to be executed (equivalent to
each file containing N copies of the opcodes).

TEST-JOBQUEUE
~~~~~~~~~~~~~

**test-jobqueue**

Executes a few tests on the job queue. This command might generate
failed jobs deliberately.

LOCKS
~~~~~

| **locks** [--no-headers] [--separator=*SEPARATOR*] [-v]
| [-o *[+]FIELD,...*] [--interval=*SECONDS*]

Shows a list of locks in the master daemon.

The ``--no-headers`` option will skip the initial header line. The
``--separator`` option takes an argument which denotes what will be
used between the output fields. Both these options are to help
scripting.

The ``-v`` option activates verbose mode, which changes the display of
special field states (see **ganeti(7)**).

The ``-o`` option takes a comma-separated list of output fields.
The available fields and their meaning are:

@QUERY_FIELDS_LOCK@

If the value of the option starts with the character ``+``, the new
fields will be added to the default list. This allows to quickly
see the default list plus a few other fields, instead of retyping
the entire list of fields.

Use ``--interval`` to repeat the listing. A delay specified by the
option value in seconds is inserted.

.. vim: set textwidth=72 :
.. Local Variables:
.. mode: rst
.. fill-column: 72
.. End:
