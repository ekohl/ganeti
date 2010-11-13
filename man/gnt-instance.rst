gnt-instance(8) Ganeti | Version @GANETI_VERSION@
=================================================

Name
----

gnt-instance - Ganeti instance administration

Synopsis
--------

**gnt-instance** {command} [arguments...]

DESCRIPTION
-----------

The **gnt-instance** command is used for instance administration in
the Ganeti system.

COMMANDS
--------

Creation/removal/querying
~~~~~~~~~~~~~~~~~~~~~~~~~

ADD
^^^

| **add**
| {-t {diskless | file \| plain \| drbd}}
| {--disk=*N*: {size=*VAL* \| adopt=*LV*},mode=*ro\|rw* \| -s *SIZE*}
| [--no-ip-check] [--no-name-check] [--no-start] [--no-install]
| [--net=*N* [:options...] \| --no-nics]
| [-B *BEPARAMS*]
| [-H *HYPERVISOR* [: option=*value*... ]]
| [--file-storage-dir *dir\_path*] [--file-driver {loop \| blktap}]
| {-n *node[:secondary-node]* \| --iallocator *name*}
| {-o *os-type*}
| [--submit]
| {*instance*}

Creates a new instance on the specified host. The *instance* argument
must be in DNS, but depending on the bridge/routing setup, need not be
in the same network as the nodes in the cluster.

The ``disk`` option specifies the parameters for the disks of the
instance. The numbering of disks starts at zero, and at least one disk
needs to be passed. For each disk, either the size or the adoption
source needs to be given, and optionally the access mode (read-only or
the default of read-write) can also be specified. The size is
interpreted (when no unit is given) in mebibytes. You can also use one
of the suffixes *m*, *g* or *t* to specify the exact the units used;
these suffixes map to mebibytes, gibibytes and tebibytes.

When using the ``adopt`` key in the disk definition, Ganeti will
reuse those volumes (instead of creating new ones) as the
instance's disks. Ganeti will rename these volumes to the standard
format, and (without installing the OS) will use them as-is for the
instance. This allows migrating instances from non-managed mode
(e.q. plain KVM with LVM) to being managed via Ganeti. Note that
this works only for the \`plain' disk template (see below for
template details).

Alternatively, a single-disk instance can be created via the ``-s``
option which takes a single argument, the size of the disk. This is
similar to the Ganeti 1.2 version (but will only create one disk).

The minimum disk specification is therefore ``--disk 0:size=20G`` (or
``-s 20G`` when using the ``-s`` option), and a three-disk instance
can be specified as ``--disk 0:size=20G --disk 1:size=4G --disk
2:size=100G``.

The ``--no-ip-check`` skips the checks that are done to see if the
instance's IP is not already alive (i.e. reachable from the master
node).

The ``--no-name-check`` skips the check for the instance name via
the resolver (e.g. in DNS or /etc/hosts, depending on your setup).
Since the name check is used to compute the IP address, if you pass
this option you must also pass the ``--no-ip-check`` option.

If you don't wat the instance to automatically start after
creation, this is possible via the ``--no-start`` option. This will
leave the instance down until a subsequent **gnt-instance start**
command.

The NICs of the instances can be specified via the ``--net``
option. By default, one NIC is created for the instance, with a
random MAC, and set up according the the cluster level nic
parameters. Each NIC can take these parameters (all optional):



mac
    either a value or 'generate' to generate a new unique MAC

ip
    specifies the IP address assigned to the instance from the Ganeti
    side (this is not necessarily what the instance will use, but what
    the node expects the instance to use)

mode
    specifies the connection mode for this nic: routed or bridged.

link
    in bridged mode specifies the bridge to attach this NIC to, in
    routed mode it's intended to differentiate between different
    routing tables/instance groups (but the meaning is dependent on the
    network script, see gnt-cluster(8) for more details)


Of these "mode" and "link" are nic parameters, and inherit their
default at cluster level.
Alternatively, if no network is desired for the instance, you can
prevent the default of one NIC with the ``--no-nics`` option.

The ``-o`` options specifies the operating system to be installed.
The available operating systems can be listed with **gnt-os list**.
Passing ``--no-install`` will however skip the OS installation,
allowing a manual import if so desired. Note that the
no-installation mode will automatically disable the start-up of the
instance (without an OS, it most likely won't be able to start-up
successfully).

The ``-B`` option specifies the backend parameters for the
instance. If no such parameters are specified, the values are
inherited from the cluster. Possible parameters are:



memory
    the memory size of the instance; as usual, suffixes can be used to
    denote the unit, otherwise the value is taken in mebibites

vcpus
    the number of VCPUs to assign to the instance (if this value makes
    sense for the hypervisor)

auto\_balance
    whether the instance is considered in the N+1 cluster checks
    (enough redundancy in the cluster to survive a node failure)


The ``-H`` option specified the hypervisor to use for the instance
(must be one of the enabled hypervisors on the cluster) and
optionally custom parameters for this instance. If not other
options are used (i.e. the invocation is just -H *NAME*) the
instance will inherit the cluster options. The defaults below show
the cluster defaults at cluster creation time.

The possible hypervisor options are as follows:



boot\_order
    Valid for the Xen HVM and KVM hypervisors.

    A string value denoting the boot order. This has different meaning
    for the Xen HVM hypervisor and for the KVM one.

    For Xen HVM, The boot order is a string of letters listing the boot
    devices, with valid device letters being:



    a
        floppy drive

    c
        hard disk

    d
        CDROM drive

    n
        network boot (PXE)


    The default is not to set an HVM boot order which is interpreted as
    'dc'.

    For KVM the boot order is either "cdrom", "disk" or "network".
    Please note that older versions of KVM couldn't netboot from virtio
    interfaces. This has been fixed in more recent versions and is
    confirmed to work at least with qemu-kvm 0.11.1.

cdrom\_image\_path
    Valid for the Xen HVM and KVM hypervisors.

    The path to a CDROM image to attach to the instance.

nic\_type
    Valid for the Xen HVM and KVM hypervisors.

    This parameter determines the way the network cards are presented
    to the instance. The possible options are:



    rtl8139 (default for Xen HVM) (HVM & KVM)
    ne2k\_isa (HVM & KVM)
    ne2k\_pci (HVM & KVM)
    i82551 (KVM)
    i82557b (KVM)
    i82559er (KVM)
    pcnet (KVM)
    e1000 (KVM)
    paravirtual (default for KVM) (HVM & KVM)


disk\_type
    Valid for the Xen HVM and KVM hypervisors.

    This parameter determines the way the disks are presented to the
    instance. The possible options are:



    ioemu (default for HVM & KVM) (HVM & KVM)
    ide (HVM & KVM)
    scsi (KVM)
    sd (KVM)
    mtd (KVM)
    pflash (KVM)


vnc\_bind\_address
    Valid for the Xen HVM and KVM hypervisors.

    Specifies the address that the VNC listener for this instance
    should bind to. Valid values are IPv4 addresses. Use the address
    0.0.0.0 to bind to all available interfaces (this is the default)
    or specify the address of one of the interfaces on the node to
    restrict listening to that interface.

vnc\_tls
    Valid for the KVM hypervisor.

    A boolean option that controls whether the VNC connection is
    secured with TLS.

vnc\_x509\_path
    Valid for the KVM hypervisor.

    If ``vnc_tls`` is enabled, this options specifies the path to the
    x509 certificate to use.

vnc\_x509\_verify
    Valid for the KVM hypervisor.

acpi
    Valid for the Xen HVM and KVM hypervisors.

    A boolean option that specifies if the hypervisor should enable
    ACPI support for this instance. By default, ACPI is disabled.

pae
    Valid for the Xen HVM and KVM hypervisors.

    A boolean option that specifies if the hypervisor should enabled
    PAE support for this instance. The default is false, disabling PAE
    support.

use\_localtime
    Valid for the Xen HVM and KVM hypervisors.

    A boolean option that specifies if the instance should be started
    with its clock set to the localtime of the machine (when true) or
    to the UTC (When false). The default is false, which is useful for
    Linux/Unix machines; for Windows OSes, it is recommended to enable
    this parameter.

kernel\_path
    Valid for the Xen PVM and KVM hypervisors.

    This option specifies the path (on the node) to the kernel to boot
    the instance with. Xen PVM instances always require this, while for
    KVM if this option is empty, it will cause the machine to load the
    kernel from its disks.

kernel\_args
    Valid for the Xen PVM and KVM hypervisors.

    This options specifies extra arguments to the kernel that will be
    loaded. device. This is always used for Xen PVM, while for KVM it
    is only used if the ``kernel_path`` option is also specified.

    The default setting for this value is simply ``"ro"``, which mounts
    the root disk (initially) in read-only one. For example, setting
    this to single will cause the instance to start in single-user
    mode.

initrd\_path
    Valid for the Xen PVM and KVM hypervisors.

    This option specifies the path (on the node) to the initrd to boot
    the instance with. Xen PVM instances can use this always, while for
    KVM if this option is only used if the ``kernel_path`` option is
    also specified. You can pass here either an absolute filename (the
    path to the initrd) if you want to use an initrd, or use the format
    no\_initrd\_path for no initrd.

root\_path
    Valid for the Xen PVM and KVM hypervisors.

    This options specifies the name of the root device. This is always
    needed for Xen PVM, while for KVM it is only used if the
    ``kernel_path`` option is also specified.

serial\_console
    Valid for the KVM hypervisor.

    This boolean option specifies whether to emulate a serial console
    for the instance.

disk\_cache
    Valid for the KVM hypervisor.

    The disk cache mode. It can be either default to not pass any cache
    option to KVM, or one of the KVM cache modes: none (for direct
    I/O), writethrough (to use the host cache but report completion to
    the guest only when the host has committed the changes to disk) or
    writeback (to use the host cache and report completion as soon as
    the data is in the host cache). Note that there are special
    considerations for the cache mode depending on version of KVM used
    and disk type (always raw file under Ganeti), please refer to the
    KVM documentation for more details.

security\_model
    Valid for the KVM hypervisor.

    The security model for kvm. Currently one of "none", "user" or
    "pool". Under "none", the default, nothing is done and instances
    are run as the Ganeti daemon user (normally root).

    Under "user" kvm will drop privileges and become the user specified
    by the security\_domain parameter.

    Under "pool" a global cluster pool of users will be used, making
    sure no two instances share the same user on the same node. (this
    mode is not implemented yet)

security\_domain
    Valid for the KVM hypervisor.

    Under security model "user" the username to run the instance under.
    It must be a valid username existing on the host.

    Cannot be set under security model "none" or "pool".

kvm\_flag
    Valid for the KVM hypervisor.

    If "enabled" the -enable-kvm flag is passed to kvm. If "disabled"
    -disable-kvm is passed. If unset no flag is passed, and the default
    running mode for your kvm binary will be used.

mem\_path
    Valid for the KVM hypervisor.

    This option passes the -mem-path argument to kvm with the path (on
    the node) to the mount point of the hugetlbfs file system, along
    with the -mem-prealloc argument too.

use\_chroot
    Valid for the KVM hypervisor.

    This boolean option determines wether to run the KVM instance in a
    chroot directory.

    If it is set to ``true``, an empty directory is created before
    starting the instance and its path is passed via the -chroot flag
    to kvm. The directory is removed when the instance is stopped.

    It is set to ``false`` by default.

migration\_downtime
    Valid for the KVM hypervisor.

    The maximum amount of time (in ms) a KVM instance is allowed to be
    frozen during a live migration, in order to copy dirty memory
    pages. Default value is 30ms, but you may need to increase this
    value for busy instances.

    This option is only effective with kvm versions >= 87 and qemu-kvm
    versions >= 0.11.0.

cpu\_mask
    Valid for the LXC hypervisor.

    The processes belonging to the given instance are only scheduled on
    the specified CPUs.

    The parameter format is a comma-separated list of CPU IDs or CPU ID
    ranges. The ranges are defined by a lower and higher boundary,
    separated by a dash. The boundaries are inclusive.

usb\_mouse
    Valid for the KVM hypervisor.

    This option specifies the usb mouse type to be used. It can be
    "mouse" or "tablet". When using VNC it's recommended to set it to
    "tablet".


The ``--iallocator`` option specifies the instance allocator plugin
to use. If you pass in this option the allocator will select nodes
for this instance automatically, so you don't need to pass them
with the ``-n`` option. For more information please refer to the
instance allocator documentation.

The ``-t`` options specifies the disk layout type for the instance.
The available choices are:



diskless
    This creates an instance with no disks. Its useful for testing only
    (or other special cases).

file
    Disk devices will be regular files.

plain
    Disk devices will be logical volumes.

drbd
    Disk devices will be drbd (version 8.x) on top of lvm volumes.


The optional second value of the ``--node`` is used for the drbd
template type and specifies the remote node.

If you do not want gnt-instance to wait for the disk mirror to be
synced, use the ``--no-wait-for-sync`` option.

The ``--file-storage-dir`` specifies the relative path under the
cluster-wide file storage directory to store file-based disks. It
is useful for having different subdirectories for different
instances. The full path of the directory where the disk files are
stored will consist of cluster-wide file storage directory +
optional subdirectory + instance name. Example:
/srv/ganeti/file-storage/mysubdir/instance1.example.com. This
option is only relevant for instances using the file storage
backend.

The ``--file-driver`` specifies the driver to use for file-based
disks. Note that currently these drivers work with the xen
hypervisor only. This option is only relevant for instances using
the file storage backend. The available choices are:



loop
    Kernel loopback driver. This driver uses loopback devices to access
    the filesystem within the file. However, running I/O intensive
    applications in your instance using the loop driver might result in
    slowdowns. Furthermore, if you use the loopback driver consider
    increasing the maximum amount of loopback devices (on most systems
    it's 8) using the max\_loop param.

blktap
    The blktap driver (for Xen hypervisors). In order to be able to use
    the blktap driver you should check if the 'blktapctrl' user space
    disk agent is running (usually automatically started via xend).
    This user-level disk I/O interface has the advantage of better
    performance. Especially if you use a network file system (e.g. NFS)
    to store your instances this is the recommended choice.


The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example::

    # gnt-instance add -t file --disk 0:size=30g -B memory=512 -o debian-etch \
      -n node1.example.com --file-storage-dir=mysubdir instance1.example.com
    # gnt-instance add -t plain --disk 0:size=30g -B memory=512 -o debian-etch \
      -n node1.example.com instance1.example.com
    # gnt-instance add -t drbd --disk 0:size=30g -B memory=512 -o debian-etch \
      -n node1.example.com:node2.example.com instance2.example.com


BATCH-CREATE
^^^^^^^^^^^^

**batch-create** {instances\_file.json}

This command (similar to the Ganeti 1.2 **batcher** tool) submits
multiple instance creation jobs based on a definition file. The
instance configurations do not encompass all the possible options
for the **add** command, but only a subset.

The instance file should be a valid-formed JSON file, containing a
dictionary with instance name and instance parameters. The accepted
parameters are:



disk\_size
    The size of the disks of the instance.

disk\_template
    The disk template to use for the instance, the same as in the
    **add** command.

backend
    A dictionary of backend parameters.

hypervisor
    A dictionary with a single key (the hypervisor name), and as value
    the hypervisor options. If not passed, the default hypervisor and
    hypervisor options will be inherited.

mac, ip, mode, link
    Specifications for the one NIC that will be created for the
    instance. 'bridge' is also accepted as a backwards compatibile
    key.

nics
    List of nics that will be created for the instance. Each entry
    should be a dict, with mac, ip, mode and link as possible keys.
    Please don't provide the "mac, ip, mode, link" parent keys if you
    use this method for specifying nics.

primary\_node, secondary\_node
    The primary and optionally the secondary node to use for the
    instance (in case an iallocator script is not used).

iallocator
    Instead of specifying the nodes, an iallocator script can be used
    to automatically compute them.

start
    whether to start the instance

ip\_check
    Skip the check for already-in-use instance; see the description in
    the **add** command for details.

name\_check
    Skip the name check for instances; see the description in the
    **add** command for details.

file\_storage\_dir, file\_driver
    Configuration for the file disk type, see the **add** command for
    details.


A simple definition for one instance can be (with most of the
parameters taken from the cluster defaults)::

    {
      "instance3": {
        "template": "drbd",
        "os": "debootstrap",
        "disk_size": ["25G"],
        "iallocator": "dumb"
      },
      "instance5": {
        "template": "drbd",
        "os": "debootstrap",
        "disk_size": ["25G"],
        "iallocator": "dumb",
        "hypervisor": "xen-hvm",
        "hvparams": {"acpi": true},
        "backend": {"memory": 512}
      }
    }

The command will display the job id for each submitted instance, as
follows::

    # gnt-instance batch-create instances.json
    instance3: 11224
    instance5: 11225

REMOVE
^^^^^^

**remove** [--ignore-failures] [--shutdown-timeout=*N*] [--submit]
{*instance*}

Remove an instance. This will remove all data from the instance and
there is *no way back*. If you are not sure if you use an instance
again, use **shutdown** first and leave it in the shutdown state
for a while.

The ``--ignore-failures`` option will cause the removal to proceed
even in the presence of errors during the removal of the instance
(e.g. during the shutdown or the disk removal). If this option is
not given, the command will stop at the first error.

The ``--shutdown-timeout`` is used to specify how much time to wait
before forcing the shutdown (e.g. ``xm destroy`` in Xen, killing the
kvm process for KVM, etc.). By default two minutes are given to each
instance to stop.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example::

    # gnt-instance remove instance1.example.com


LIST
^^^^

| **list**
| [--no-headers] [--separator=*SEPARATOR*] [--units=*UNITS*]
| [-o *[+]FIELD,...*] [--roman] [instance...]

Shows the currently configured instances with memory usage, disk
usage, the node they are running on, and their run status.

The ``--no-headers`` option will skip the initial header line. The
``--separator`` option takes an argument which denotes what will be
used between the output fields. Both these options are to help
scripting.

The units used to display the numeric values in the output varies,
depending on the options given. By default, the values will be
formatted in the most appropriate unit. If the ``--separator``
option is given, then the values are shown in mebibytes to allow
parsing by scripts. In both cases, the ``--units`` option can be
used to enforce a given output unit.

The ``--roman`` option allows latin people to better understand the
cluster instances' status.

The ``-o`` option takes a comma-separated list of output fields.
The available fields and their meaning are:



name
    the instance name

os
    the OS of the instance

pnode
    the primary node of the instance

snodes
    comma-separated list of secondary nodes for the instance; usually
    this will be just one node

admin\_state
    the desired state of the instance (either "yes" or "no" denoting
    the instance should run or not)

disk\_template
    the disk template of the instance

oper\_state
    the actual state of the instance; can be one of the values
    "running", "stopped", "(node down)"

status
    combined form of admin\_state and oper\_stat; this can be one of:
    ERROR\_nodedown if the node of the instance is down, ERROR\_down if
    the instance should run but is down, ERROR\_up if the instance
    should be stopped but is actually running, ADMIN\_down if the
    instance has been stopped (and is stopped) and running if the
    instance is set to be running (and is running)

oper\_ram
    the actual memory usage of the instance as seen by the hypervisor

oper\_vcpus
    the actual number of VCPUs the instance is using as seen by the
    hypervisor

ip
    the ip address Ganeti recognizes as associated with the first
    instance interface

mac
    the first instance interface MAC address

nic\_mode
    the mode of the first instance NIC (routed or bridged)

nic\_link
    the link of the first instance NIC

sda\_size
    the size of the instance's first disk

sdb\_size
    the size of the instance's second disk, if any

vcpus
    the number of VCPUs allocated to the instance

tags
    comma-separated list of the instances's tags

serial\_no
    the so called 'serial number' of the instance; this is a numeric
    field that is incremented each time the instance is modified, and
    it can be used to track modifications

ctime
    the creation time of the instance; note that this field contains
    spaces and as such it's harder to parse

    if this attribute is not present (e.g. when upgrading from older
    versions), then "N/A" will be shown instead

mtime
    the last modification time of the instance; note that this field
    contains spaces and as such it's harder to parse

    if this attribute is not present (e.g. when upgrading from older
    versions), then "N/A" will be shown instead

uuid
    Show the UUID of the instance (generated automatically by Ganeti)

network\_port
    If the instance has a network port assigned to it (e.g. for VNC
    connections), this will be shown, otherwise - will be displayed.

beparams
    A text format of the entire beparams for the instance. It's more
    useful to select individual fields from this dictionary, see
    below.

disk.count
    The number of instance disks.

disk.size/N
    The size of the instance's Nth disk. This is a more generic form of
    the sda\_size and sdb\_size fields.

disk.sizes
    A comma-separated list of the disk sizes for this instance.

disk\_usage
    The total disk space used by this instance on each of its nodes.
    This is not the instance-visible disk size, but the actual disk
    "cost" of the instance.

nic.mac/N
    The MAC of the Nth instance NIC.

nic.ip/N
    The IP address of the Nth instance NIC.

nic.mode/N
    The mode of the Nth instance NIC

nic.link/N
    The link of the Nth instance NIC

nic.macs
    A comma-separated list of all the MACs of the instance's NICs.

nic.ips
    A comma-separated list of all the IP addresses of the instance's
    NICs.

nic.modes
    A comma-separated list of all the modes of the instance's NICs.

nic.links
    A comma-separated list of all the link parameters of the instance's
    NICs.

nic.count
    The number of instance nics.

hv/*NAME*
    The value of the hypervisor parameter called *NAME*. For details of
    what hypervisor parameters exist and their meaning, see the **add**
    command.

be/memory
    The configured memory for the instance.

be/vcpus
    The configured number of VCPUs for the instance.

be/auto\_balance
    Whether the instance is considered in N+1 checks.


If the value of the option starts with the character ``+``, the new
field(s) will be added to the default list. This allows to quickly
see the default list plus a few other fields, instead of retyping
the entire list of fields.

There is a subtle grouping about the available output fields: all
fields except for ``oper_state``, ``oper_ram``, ``oper_vcpus`` and
``status`` are configuration value and not run-time values. So if
you don't select any of the these fields, the query will be
satisfied instantly from the cluster configuration, without having
to ask the remote nodes for the data. This can be helpful for big
clusters when you only want some data and it makes sense to specify
a reduced set of output fields.

The default output field list is: name, os, pnode, admin\_state,
oper\_state, oper\_ram.

INFO
^^^^

**info** [-s \| --static] [--roman] {--all \| *instance*}

Show detailed information about the given instance(s). This is
different from **list** as it shows detailed data about the
instance's disks (especially useful for the drbd disk template).

If the option ``-s`` is used, only information available in the
configuration file is returned, without querying nodes, making the
operation faster.

Use the ``--all`` to get info about all instances, rather than
explicitly passing the ones you're interested in.

The ``--roman`` option can be used to cause envy among people who
like ancient cultures, but are stuck with non-latin-friendly
cluster virtualization technologies.

MODIFY
^^^^^^

| **modify**
| [-H *HYPERVISOR\_PARAMETERS*]
| [-B *BACKEND\_PARAMETERS*]
| [--net add*[:options]* \| --net remove \| --net *N:options*]
| [--disk add:size=*SIZE* \| --disk remove \| --disk *N*:mode=*MODE*]
| [-t {plain \| drbd}]
| [--os-name=*OS* [--force-variant]]
| [--submit]
| {*instance*}

Modifies the memory size, number of vcpus, ip address, MAC address
and/or nic parameters for an instance. It can also add and remove
disks and NICs to/from the instance. Note that you need to give at
least one of the arguments, otherwise the command complains.

The ``-H`` option specifies hypervisor options in the form of
name=value[,...]. For details which options can be specified, see
the **add** command.

The ``-t`` option will change the disk template of the instance.
Currently only conversions between the plain and drbd disk
templates are supported, and the instance must be stopped before
attempting the conversion.

The ``--disk add:size=``*SIZE* option adds a disk to the instance. The
``--disk remove`` option will remove the last disk of the
instance. The ``--disk`` *N*``:mode=``*MODE* option will change the
mode of the Nth disk of the instance between read-only (``ro``) and
read-write (``rw``).

The ``--net add:``*options* option will add a new NIC to the
instance. The available options are the same as in the **add** command
(mac, ip, link, mode). The ``--net remove`` will remove the last NIC
of the instance, while the ``--net`` *N*:*options* option will
change the parameters of the Nth instance NIC.

The option ``--os-name`` will change the OS name for the instance
(without reinstallation). In case an OS variant is specified that
is not found, then by default the modification is refused, unless
``--force-variant`` is passed. An invalid OS will also be refused,
unless the ``--force`` option is given.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

All the changes take effect at the next restart. If the instance is
running, there is no effect on the instance.

REINSTALL
^^^^^^^^^

| **reinstall** [-o *os-type*] [--select-os] [-f *force*]
| [--force-multiple]
| [--instance \| --node \| --primary \| --secondary \| --all]
| [-O *OS\_PARAMETERS*] [--submit] {*instance*...}

Reinstalls the operating system on the given instance(s). The
instance(s) must be stopped when running this command. If the
``--os-type`` is specified, the operating system is changed.

The ``--select-os`` option switches to an interactive OS reinstall.
The user is prompted to select the OS template from the list of
available OS templates. OS parameters can be overridden using
``-O``.

Since this is a potentially dangerous command, the user will be
required to confirm this action, unless the ``-f`` flag is passed.
When multiple instances are selected (either by passing multiple
arguments or by using the ``--node``, ``--primary``,
``--secondary`` or ``--all`` options), the user must pass the
``--force-multiple`` options to skip the interactive confirmation.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

RENAME
^^^^^^

| **rename** [--no-ip-check] [--no-name-check] [--submit]
| {*instance*} {*new\_name*}

Renames the given instance. The instance must be stopped when
running this command. The requirements for the new name are the
same as for adding an instance: the new name must be resolvable and
the IP it resolves to must not be reachable (in order to prevent
duplicate IPs the next time the instance is started). The IP test
can be skipped if the ``--no-ip-check`` option is passed.

The ``--no-name-check`` skips the check for the new instance name
via the resolver (e.g. in DNS or /etc/hosts, depending on your
setup). Since the name check is used to compute the IP address, if
you pass this option you must also pass the ``--no-ip-check``
option.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Starting/stopping/connecting to console
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

STARTUP
^^^^^^^

| **startup**
| [--force] [--ignore-offline]
| [--force-multiple]
| [--instance \| --node \| --primary \| --secondary \| --all \|
| --tags \| --node-tags \| --pri-node-tags \| --sec-node-tags]
| [-H ``key=value...``] [-B ``key=value...``]
| [--submit]
| {*name*...}

Starts one or more instances, depending on the following options.
The four available modes are:


--instance
    will start the instances given as arguments (at least one argument
    required); this is the default selection

--node
    will start the instances who have the given node as either primary
    or secondary

--primary
    will start all instances whose primary node is in the list of nodes
    passed as arguments (at least one node required)

--secondary
    will start all instances whose secondary node is in the list of
    nodes passed as arguments (at least one node required)

--all
    will start all instances in the cluster (no arguments accepted)

--tags
    will start all instances in the cluster with the tags given as
    arguments

--node-tags
    will start all instances in the cluster on nodes with the tags
    given as arguments

--pri-node-tags
    will start all instances in the cluster on primary nodes with the
    tags given as arguments

--sec-node-tags
    will start all instances in the cluster on secondary nodes with the
    tags given as arguments


Note that although you can pass more than one selection option, the
last one wins, so in order to guarantee the desired result, don't
pass more than one such option.

Use ``--force`` to start even if secondary disks are failing.
``--ignore-offline`` can be used to ignore offline primary nodes
and mark the instance as started even if the primary is not
available.

The ``--force-multiple`` will skip the interactive confirmation in
the case the more than one instance will be affected.

The ``-H`` and ``-B`` options specify temporary hypervisor and
backend parameters that can be used to start an instance with
modified parameters. They can be useful for quick testing without
having to modify an instance back and forth, e.g.::

    # gnt-instance start -H root_args="single" instance1
    # gnt-instance start -B memory=2048 instance2


The first form will start the instance instance1 in single-user
mode, and the instance instance2 with 2GB of RAM (this time only,
unless that is the actual instance memory size already). Note that
the values override the instance parameters (and not extend them):
an instance with "root\_args=ro" when started with -H
root\_args=single will result in "single", not "ro single".
The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example::

    # gnt-instance start instance1.example.com
    # gnt-instance start --node node1.example.com node2.example.com
    # gnt-instance start --all


SHUTDOWN
^^^^^^^^

| **shutdown**
| [--timeout=*N*]
| [--force-multiple] [--ignore-offline]
| [--instance \| --node \| --primary \| --secondary \| --all \|
| --tags \| --node-tags \| --pri-node-tags \| --sec-node-tags]
| [--submit]
| {*name*...}

Stops one or more instances. If the instance cannot be cleanly
stopped during a hardcoded interval (currently 2 minutes), it will
forcibly stop the instance (equivalent to switching off the power
on a physical machine).

The ``--timeout`` is used to specify how much time to wait before
forcing the shutdown (e.g. ``xm destroy`` in Xen, killing the kvm
process for KVM, etc.). By default two minutes are given to each
instance to stop.

The ``--instance``, ``--node``, ``--primary``, ``--secondary``,
``--all``, ``--tags``, ``--node-tags``, ``--pri-node-tags`` and
``--sec-node-tags`` options are similar as for the **startup**
command and they influence the actual instances being shutdown.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

``--ignore-offline`` can be used to ignore offline primary nodes
and force the instance to be marked as stopped. This option should
be used with care as it can lead to an inconsistent cluster state.

Example::

    # gnt-instance shutdown instance1.example.com
    # gnt-instance shutdown --all


REBOOT
^^^^^^

| **reboot**
| [--type=*REBOOT-TYPE*]
| [--ignore-secondaries]
| [--shutdown-timeout=*N*]
| [--force-multiple]
| [--instance \| --node \| --primary \| --secondary \| --all \|
| --tags \| --node-tags \| --pri-node-tags \| --sec-node-tags]
| [--submit]
| [*name*...]

Reboots one or more instances. The type of reboot depends on the
value of ``--type``. A soft reboot does a hypervisor reboot, a hard
reboot does a instance stop, recreates the hypervisor config for
the instance and starts the instance. A full reboot does the
equivalent of **gnt-instance shutdown && gnt-instance startup**.
The default is hard reboot.

For the hard reboot the option ``--ignore-secondaries`` ignores
errors for the secondary node while re-assembling the instance
disks.

The ``--instance``, ``--node``, ``--primary``, ``--secondary``,
``--all``, ``--tags``, ``--node-tags``, ``--pri-node-tags`` and
``--sec-node-tags`` options are similar as for the **startup**
command and they influence the actual instances being rebooted.

The ``--shutdown-timeout`` is used to specify how much time to wait
before forcing the shutdown (xm destroy in xen, killing the kvm
process, for kvm). By default two minutes are given to each
instance to stop.

The ``--force-multiple`` will skip the interactive confirmation in
the case the more than one instance will be affected.

Example::

    # gnt-instance reboot instance1.example.com
    # gnt-instance reboot --type=full instance1.example.com


CONSOLE
^^^^^^^

**console** [--show-cmd] {*instance*}

Connects to the console of the given instance. If the instance is
not up, an error is returned. Use the ``--show-cmd`` option to
display the command instead of executing it.

For HVM instances, this will attempt to connect to the serial
console of the instance. To connect to the virtualized "physical"
console of a HVM instance, use a VNC client with the connection
info from the **info** command.

Example::

    # gnt-instance console instance1.example.com


Disk management
~~~~~~~~~~~~~~~

REPLACE-DISKS
^^^^^^^^^^^^^

**replace-disks** [--submit] [--early-release] {-p} [--disks *idx*]
{*instance*}

**replace-disks** [--submit] [--early-release] {-s} [--disks *idx*]
{*instance*}

**replace-disks** [--submit] [--early-release] {--iallocator *name*
\| --new-secondary *NODE*} {*instance*}

**replace-disks** [--submit] [--early-release] {--auto}
{*instance*}

This command is a generalized form for replacing disks. It is
currently only valid for the mirrored (DRBD) disk template.

The first form (when passing the ``-p`` option) will replace the
disks on the primary, while the second form (when passing the
``-s`` option will replace the disks on the secondary node. For
these two cases (as the node doesn't change), it is possible to
only run the replace for a subset of the disks, using the option
``--disks`` which takes a list of comma-delimited disk indices
(zero-based), e.g. 0,2 to replace only the first and third disks.

The third form (when passing either the ``--iallocator`` or the
``--new-secondary`` option) is designed to change secondary node of
the instance. Specifying ``--iallocator`` makes the new secondary
be selected automatically by the specified allocator plugin,
otherwise the new secondary node will be the one chosen manually
via the ``--new-secondary`` option.

The fourth form (when using ``--auto``) will automatically
determine which disks of an instance are faulty and replace them
within the same node. The ``--auto`` option works only when an
instance has only faulty disks on either the primary or secondary
node; it doesn't work when both sides have faulty disks.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

The ``--early-release`` changes the code so that the old storage on
secondary node(s) is removed early (before the resync is completed)
and the internal Ganeti locks for the current (and new, if any)
secondary node are also released, thus allowing more parallelism in
the cluster operation. This should be used only when recovering
from a disk failure on the current secondary (thus the old storage
is already broken) or when the storage on the primary node is known
to be fine (thus we won't need the old storage for potential
recovery).

Note that it is not possible to select an offline or drained node
as a new secondary.

ACTIVATE-DISKS
^^^^^^^^^^^^^^

**activate-disks** [--submit] [--ignore-size] {*instance*}

Activates the block devices of the given instance. If successful,
the command will show the location and name of the block devices::

    node1.example.com:disk/0:/dev/drbd0
    node1.example.com:disk/1:/dev/drbd1


In this example, *node1.example.com* is the name of the node on
which the devices have been activated. The *disk/0* and *disk/1*
are the Ganeti-names of the instance disks; how they are visible
inside the instance is hypervisor-specific. */dev/drbd0* and
*/dev/drbd1* are the actual block devices as visible on the node.
The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

The ``--ignore-size`` option can be used to activate disks ignoring
the currently configured size in Ganeti. This can be used in cases
where the configuration has gotten out of sync with the real-world
(e.g. after a partially-failed grow-disk operation or due to
rounding in LVM devices). This should not be used in normal cases,
but only when activate-disks fails without it.

Note that it is safe to run this command while the instance is
already running.

DEACTIVATE-DISKS
^^^^^^^^^^^^^^^^

**deactivate-disks** [--submit] {*instance*}

De-activates the block devices of the given instance. Note that if
you run this command for an instance with a drbd disk template,
while it is running, it will not be able to shutdown the block
devices on the primary node, but it will shutdown the block devices
on the secondary nodes, thus breaking the replication.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

GROW-DISK
^^^^^^^^^

**grow-disk** [--no-wait-for-sync] [--submit] {*instance*} {*disk*}
{*amount*}

Grows an instance's disk. This is only possible for instances
having a plain or drbd disk template.

Note that this command only change the block device size; it will
not grow the actual filesystems, partitions, etc. that live on that
disk. Usually, you will need to:




#. use **gnt-instance grow-disk**

#. reboot the instance (later, at a convenient time)

#. use a filesystem resizer, such as ext2online(8) or
   xfs\_growfs(8) to resize the filesystem, or use fdisk(8) to change
   the partition table on the disk


The *disk* argument is the index of the instance disk to grow. The
*amount* argument is given either as a number (and it represents
the amount to increase the disk with in mebibytes) or can be given
similar to the arguments in the create instance operation, with a
suffix denoting the unit.

Note that the disk grow operation might complete on one node but
fail on the other; this will leave the instance with
different-sized LVs on the two nodes, but this will not create
problems (except for unused space).

If you do not want gnt-instance to wait for the new disk region to
be synced, use the ``--no-wait-for-sync`` option.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example (increase the first disk for instance1 by 16GiB)::

    # gnt-instance grow-disk instance1.example.com 0 16g


Also note that disk shrinking is not supported; use
**gnt-backup export** and then **gnt-backup import** to reduce the
disk size of an instance.

RECREATE-DISKS
^^^^^^^^^^^^^^

**recreate-disks** [--submit] [--disks=``indices``] {*instance*}

Recreates the disks of the given instance, or only a subset of the
disks (if the option ``disks`` is passed, which must be a
comma-separated list of disk indices, starting from zero).

Note that this functionality should only be used for missing disks;
if any of the given disks already exists, the operation will fail.
While this is suboptimal, recreate-disks should hopefully not be
needed in normal operation and as such the impact of this is low.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Recovery
~~~~~~~~

FAILOVER
^^^^^^^^

**failover** [-f] [--ignore-consistency] [--shutdown-timeout=*N*]
[--submit] {*instance*}

Failover will fail the instance over its secondary node. This works
only for instances having a drbd disk template.

Normally the failover will check the consistency of the disks
before failing over the instance. If you are trying to migrate
instances off a dead node, this will fail. Use the
``--ignore-consistency`` option for this purpose. Note that this
option can be dangerous as errors in shutting down the instance
will be ignored, resulting in possibly having the instance running
on two machines in parallel (on disconnected DRBD drives).

The ``--shutdown-timeout`` is used to specify how much time to wait
before forcing the shutdown (xm destroy in xen, killing the kvm
process, for kvm). By default two minutes are given to each
instance to stop.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example::

    # gnt-instance failover instance1.example.com


MIGRATE
^^^^^^^

**migrate** [-f] {--cleanup} {*instance*}

**migrate** [-f] [--non-live] [--migration-mode=live\|non-live]
{*instance*}

Migrate will move the instance to its secondary node without
shutdown. It only works for instances having the drbd8 disk
template type.

The migration command needs a perfectly healthy instance, as we
rely on the dual-master capability of drbd8 and the disks of the
instance are not allowed to be degraded.

The ``--non-live`` and ``--migration-mode=non-live`` options will
switch (for the hypervisors that support it) between a "fully live"
(i.e. the interruption is as minimal as possible) migration and one
in which the instance is frozen, its state saved and transported to
the remote node, and then resumed there. This all depends on the
hypervisor support for two different methods. In any case, it is
not an error to pass this parameter (it will just be ignored if the
hypervisor doesn't support it). The option
``--migration-mode=live`` option will request a fully-live
migration. The default, when neither option is passed, depends on
the hypervisor parameters (and can be viewed with the
**gnt-cluster info** command).

If the ``--cleanup`` option is passed, the operation changes from
migration to attempting recovery from a failed previous migration.
In this mode, Ganeti checks if the instance runs on the correct
node (and updates its configuration if not) and ensures the
instances's disks are configured correctly. In this mode, the
``--non-live`` option is ignored.

The option ``-f`` will skip the prompting for confirmation.

Example (and expected output)::

    # gnt-instance migrate instance1
    Migrate will happen to the instance instance1. Note that migration is
    **experimental** in this version. This might impact the instance if
    anything goes wrong. Continue?
    y/[n]/?: y
    * checking disk consistency between source and target
    * ensuring the target is in secondary mode
    * changing disks into dual-master mode
     - INFO: Waiting for instance instance1 to sync disks.
     - INFO: Instance instance1's disks are in sync.
    * migrating instance to node2.example.com
    * changing the instance's disks on source node to secondary
     - INFO: Waiting for instance instance1 to sync disks.
     - INFO: Instance instance1's disks are in sync.
    * changing the instance's disks to single-master
    #


MOVE
^^^^

**move** [-f] [-n *node*] [--shutdown-timeout=*N*] [--submit]
{*instance*}

Move will move the instance to an arbitrary node in the cluster.
This works only for instances having a plain or file disk
template.

Note that since this operation is done via data copy, it will take
a long time for big disks (similar to replace-disks for a drbd
instance).

The ``--shutdown-timeout`` is used to specify how much time to wait
before forcing the shutdown (e.g. ``xm destroy`` in XEN, killing the
kvm process for KVM, etc.). By default two minutes are given to each
instance to stop.

The ``--submit`` option is used to send the job to the master
daemon but not wait for its completion. The job ID will be shown so
that it can be examined via **gnt-job info**.

Example::

    # gnt-instance move -n node3.example.com instance1.example.com


TAGS
~~~~

ADD-TAGS
^^^^^^^^

**add-tags** [--from *file*] {*instancename*} {*tag*...}

Add tags to the given instance. If any of the tags contains invalid
characters, the entire operation will abort.

If the ``--from`` option is given, the list of tags will be
extended with the contents of that file (each line becomes a tag).
In this case, there is not need to pass tags on the command line
(if you do, both sources will be used). A file name of - will be
interpreted as stdin.

LIST-TAGS
^^^^^^^^^

**list-tags** {*instancename*}

List the tags of the given instance.

REMOVE-TAGS
^^^^^^^^^^^

**remove-tags** [--from *file*] {*instancename*} {*tag*...}

Remove tags from the given instance. If any of the tags are not
existing on the node, the entire operation will abort.

If the ``--from`` option is given, the list of tags to be removed will
be extended with the contents of that file (each line becomes a tag).
In this case, there is not need to pass tags on the command line (if
you do, tags from both sources will be removed). A file name of - will
be interpreted as stdin.