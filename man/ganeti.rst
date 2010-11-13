ganeti(7) Ganeti | Version @GANETI_VERSION@
===========================================

Name
----

ganeti - cluster-based virtualization management

Synopsis
--------

::

    # gnt-cluster init cluster1.example.com
    # gnt-node add node2.example.com
    # gnt-instance add -n node2.example.com \
    > -o debootstrap --disk 0:size=30g \
    > -t plain instance1.example.com


DESCRIPTION
-----------

The Ganeti software manages physical nodes and virtual instances of a
cluster based on a virtualization software. The current version (2.3)
supports Xen 3.x and KVM (72 or above) as hypervisors, and LXC as an
experimental hypervisor.

Quick start
-----------

First you must install the software on all the cluster nodes, either
from sources or (if available) from a package. The next step is to
create the initial cluster configuration, using **gnt-cluster init**.

Then you can add other nodes, or start creating instances.

Cluster architecture
--------------------

In Ganeti 2.0, the architecture of the cluster is a little more
complicated than in 1.2. The cluster is coordinated by a master daemon
(**ganeti-masterd**(8)), running on the master node. Each node runs
(as before) a node daemon, and the master has the RAPI daemon running
too.

Node roles
~~~~~~~~~~

Each node can be in one of the following states:

master
    Only one node per cluster can be in this role, and this node is the
    one holding the authoritative copy of the cluster configuration and
    the one that can actually execute commands on the cluster and
    modify the cluster state. See more details under
    *Cluster configuration*.

master_candidate
    The node receives the full cluster configuration (configuration
    file and jobs) and can become a master via the
    **gnt-cluster master-failover** command. Nodes that are not in this
    state cannot transition into the master role due to missing state.

regular
    This the normal state of a node.

drained
    Nodes in this state are functioning normally but cannot receive
    new instances, because the intention is to set them to *offline*
    or remove them from the cluster.

offline
    These nodes are still recorded in the Ganeti configuration, but
    except for the master daemon startup voting procedure, they are not
    actually contacted by the master. This state was added in order to
    allow broken machines (that are being repaired) to remain in the
    cluster but without creating problems.


Node flags
~~~~~~~~~~

Nodes have two flags which govern which roles they can take:

master_capable
    The node can become a master candidate, and furthermore the master
    node. When this flag is disabled, the node cannot become a
    candidate; this can be useful for special networking cases, or less
    reliable hardware.

vm_capable
    The node can host instances. When enabled (the default state), the
    node will participate in instance allocation, capacity calculation,
    etc. When disabled, the node will be skipped in many cluster checks
    and operations.


Cluster configuration
~~~~~~~~~~~~~~~~~~~~~

The master node keeps and is responsible for the cluster
configuration. On the filesystem, this is stored under the
``@LOCALSTATEDIR@/ganeti/lib`` directory, and if the master daemon is
stopped it can be backed up normally.

The master daemon will replicate the configuration database called
``config.data`` and the job files to all the nodes in the master
candidate role. It will also distribute a copy of some configuration
values via the *ssconf* files, which are stored in the same directory
and start with a ``ssconf_`` prefix, to all nodes.

Jobs
~~~~

All cluster modification are done via jobs. A job consists of one
or more opcodes, and the list of opcodes is processed serially. If
an opcode fails, the entire job is failed and later opcodes are no
longer processed. A job can be in one of the following states:

queued
    The job has been submitted but not yet processed by the master
    daemon.

waiting
    The job is waiting for for locks before the first of its opcodes.

canceling
    The job is waiting for locks, but is has been marked for
    cancellation. It will not transition to *running*, but to
    *canceled*.

running
    The job is currently being executed.

canceled
    The job has been canceled before starting execution.

success
    The job has finished successfully.

error
    The job has failed during runtime, or the master daemon has been
    stopped during the job execution.


Common options
--------------

Many Ganeti commands provide the following options. The
availability for a certain command can be checked by calling the
command using the ``--help`` option.

**gnt-...** *command* [--dry-run] [--priority {low | normal | high}]

The ``--dry-run`` option can be used to check whether an operation
would succeed.

The option ``--priority`` sets the priority for opcodes submitted
by the command.