#
#

# Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.


"""Module holding different constants."""

import re

from ganeti import _autoconf

# various versions
RELEASE_VERSION = _autoconf.PACKAGE_VERSION
OS_API_V10 = 10
OS_API_V15 = 15
OS_API_V20 = 20
OS_API_VERSIONS = frozenset([OS_API_V10, OS_API_V15, OS_API_V20])
VCS_VERSION = _autoconf.VCS_VERSION
EXPORT_VERSION = 0
RAPI_VERSION = 2


# Format for CONFIG_VERSION:
#   01 03 0123 = 01030123
#   ^^ ^^ ^^^^
#   |  |  + Configuration version/revision
#   |  + Minor version
#   + Major version
#
# It stored as an integer. Make sure not to write an octal number.

# BuildVersion and SplitVersion must be in here because we can't import other
# modules. The cfgupgrade tool must be able to read and write version numbers
# and thus requires these functions. To avoid code duplication, they're kept in
# here.

def BuildVersion(major, minor, revision):
  """Calculates int version number from major, minor and revision numbers.

  Returns: int representing version number

  """
  assert isinstance(major, int)
  assert isinstance(minor, int)
  assert isinstance(revision, int)
  return (1000000 * major +
            10000 * minor +
                1 * revision)


def SplitVersion(version):
  """Splits version number stored in an int.

  Returns: tuple; (major, minor, revision)

  """
  assert isinstance(version, int)

  (major, remainder) = divmod(version, 1000000)
  (minor, revision) = divmod(remainder, 10000)

  return (major, minor, revision)


CONFIG_MAJOR = int(_autoconf.VERSION_MAJOR)
CONFIG_MINOR = int(_autoconf.VERSION_MINOR)
CONFIG_REVISION = 0
CONFIG_VERSION = BuildVersion(CONFIG_MAJOR, CONFIG_MINOR, CONFIG_REVISION)

#: RPC protocol version
PROTOCOL_VERSION = BuildVersion(CONFIG_MAJOR, CONFIG_MINOR, 0)

# user separation
DAEMONS_GROUP = _autoconf.DAEMONS_GROUP
ADMIN_GROUP = _autoconf.ADMIN_GROUP
MASTERD_USER = _autoconf.MASTERD_USER
MASTERD_GROUP = _autoconf.MASTERD_GROUP
RAPI_USER = _autoconf.RAPI_USER
RAPI_GROUP = _autoconf.RAPI_GROUP
CONFD_USER = _autoconf.CONFD_USER
CONFD_GROUP = _autoconf.CONFD_GROUP
NODED_USER = _autoconf.NODED_USER
NODED_GROUP = _autoconf.NODED_GROUP


# Wipe
DD_CMD = "dd"
WIPE_BLOCK_SIZE = 1024**2
MAX_WIPE_CHUNK = 1024 # 1GB
MIN_WIPE_CHUNK_PERCENT = 10


# file paths
DATA_DIR = _autoconf.LOCALSTATEDIR + "/lib/ganeti"
RUN_DIR = _autoconf.LOCALSTATEDIR + "/run"
RUN_GANETI_DIR = RUN_DIR + "/ganeti"
BDEV_CACHE_DIR = RUN_GANETI_DIR + "/bdev-cache"
DISK_LINKS_DIR = RUN_GANETI_DIR + "/instance-disks"
RUN_DIRS_MODE = 0775
SOCKET_DIR = RUN_GANETI_DIR + "/socket"
SECURE_DIR_MODE = 0700
SECURE_FILE_MODE = 0600
SOCKET_DIR_MODE = 0750
CRYPTO_KEYS_DIR = RUN_GANETI_DIR + "/crypto"
CRYPTO_KEYS_DIR_MODE = SECURE_DIR_MODE
IMPORT_EXPORT_DIR = RUN_GANETI_DIR + "/import-export"
IMPORT_EXPORT_DIR_MODE = 0755
ADOPTABLE_BLOCKDEV_ROOT = "/dev/disk/"
# keep RUN_GANETI_DIR first here, to make sure all get created when the node
# daemon is started (this takes care of RUN_DIR being tmpfs)
SUB_RUN_DIRS = [ RUN_GANETI_DIR, BDEV_CACHE_DIR, DISK_LINKS_DIR ]
LOCK_DIR = _autoconf.LOCALSTATEDIR + "/lock"
SSCONF_LOCK_FILE = LOCK_DIR + "/ganeti-ssconf.lock"
# User-id pool lock directory
# The user-ids that are in use have a corresponding lock file in this directory
UIDPOOL_LOCKDIR = RUN_GANETI_DIR + "/uid-pool"
CLUSTER_CONF_FILE = DATA_DIR + "/config.data"
NODED_CERT_FILE = DATA_DIR + "/server.pem"
RAPI_CERT_FILE = DATA_DIR + "/rapi.pem"
CONFD_HMAC_KEY = DATA_DIR + "/hmac.key"
CLUSTER_DOMAIN_SECRET_FILE = DATA_DIR + "/cluster-domain-secret"
WATCHER_STATEFILE = DATA_DIR + "/watcher.data"
WATCHER_PAUSEFILE = DATA_DIR + "/watcher.pause"
INSTANCE_UPFILE = RUN_GANETI_DIR + "/instance-status"
SSH_KNOWN_HOSTS_FILE = DATA_DIR + "/known_hosts"
RAPI_USERS_FILE = DATA_DIR + "/rapi/users"
QUEUE_DIR = DATA_DIR + "/queue"
DAEMON_UTIL = _autoconf.PKGLIBDIR + "/daemon-util"
SETUP_SSH = _autoconf.TOOLSDIR + "/setup-ssh"
KVM_IFUP = _autoconf.PKGLIBDIR + "/kvm-ifup"
ETC_HOSTS = "/etc/hosts"
DEFAULT_FILE_STORAGE_DIR = _autoconf.FILE_STORAGE_DIR
DEFAULT_SHARED_FILE_STORAGE_DIR = _autoconf.SHARED_FILE_STORAGE_DIR
ENABLE_FILE_STORAGE = _autoconf.ENABLE_FILE_STORAGE
ENABLE_SHARED_FILE_STORAGE = _autoconf.ENABLE_SHARED_FILE_STORAGE
SYSCONFDIR = _autoconf.SYSCONFDIR
TOOLSDIR = _autoconf.TOOLSDIR
CONF_DIR = SYSCONFDIR + "/ganeti"

ALL_CERT_FILES = frozenset([NODED_CERT_FILE, RAPI_CERT_FILE])

MASTER_SOCKET = SOCKET_DIR + "/ganeti-master"

NODED = "ganeti-noded"
CONFD = "ganeti-confd"
RAPI = "ganeti-rapi"
MASTERD = "ganeti-masterd"
# used in the ganeti-nbma project
NLD = "ganeti-nld"

DAEMONS_PORTS = {
  # daemon-name: ("proto", "default-port")
  NODED: ("tcp", 1811),
  CONFD: ("udp", 1814),
  RAPI: ("tcp", 5080),
  "ssh": ("tcp", 22),
  # used in the ganeti-nbma project
  NLD: ("udp", 1816),
}
DEFAULT_NODED_PORT = DAEMONS_PORTS[NODED][1]
DEFAULT_CONFD_PORT = DAEMONS_PORTS[CONFD][1]
DEFAULT_RAPI_PORT = DAEMONS_PORTS[RAPI][1]
# used in the ganeti-nbma project
DEFAULT_NLD_PORT = DAEMONS_PORTS[NLD][1]

FIRST_DRBD_PORT = 11000
LAST_DRBD_PORT = 14999
MASTER_SCRIPT = "ganeti-master"

LOG_DIR = _autoconf.LOCALSTATEDIR + "/log/ganeti/"
DAEMONS_LOGFILES = {
  # "daemon-name": "logfile"
  NODED: LOG_DIR + "node-daemon.log",
  CONFD: LOG_DIR + "conf-daemon.log",
  RAPI: LOG_DIR + "rapi-daemon.log",
  MASTERD: LOG_DIR + "master-daemon.log",
  # used in the ganeti-nbma project
  NLD: LOG_DIR + "nl-daemon.log",
  }

LOG_OS_DIR = LOG_DIR + "os"
LOG_WATCHER = LOG_DIR + "watcher.log"
LOG_COMMANDS = LOG_DIR + "commands.log"
LOG_BURNIN = LOG_DIR + "burnin.log"
LOG_SETUP_SSH = LOG_DIR + "setup-ssh.log"

DEV_CONSOLE = "/dev/console"

PROC_MOUNTS = "/proc/mounts"

# Local UniX Interface related constants
LUXI_EOM = "\3"
LUXI_VERSION = CONFIG_VERSION

# one of 'no', 'yes', 'only'
SYSLOG_USAGE = _autoconf.SYSLOG_USAGE
SYSLOG_NO = "no"
SYSLOG_YES = "yes"
SYSLOG_ONLY = "only"
SYSLOG_SOCKET = "/dev/log"

OS_SEARCH_PATH = _autoconf.OS_SEARCH_PATH
EXPORT_DIR = _autoconf.EXPORT_DIR

EXPORT_CONF_FILE = "config.ini"

XEN_BOOTLOADER = _autoconf.XEN_BOOTLOADER
XEN_KERNEL = _autoconf.XEN_KERNEL
XEN_INITRD = _autoconf.XEN_INITRD

KVM_PATH = _autoconf.KVM_PATH
SOCAT_PATH = _autoconf.SOCAT_PATH
SOCAT_USE_ESCAPE = _autoconf.SOCAT_USE_ESCAPE
SOCAT_USE_COMPRESS = _autoconf.SOCAT_USE_COMPRESS
SOCAT_ESCAPE_CODE = "0x1d"

#: Console as SSH command
CONS_SSH = "ssh"

#: Console as VNC server
CONS_VNC = "vnc"

#: Display a message for console access
CONS_MESSAGE = "msg"

#: All console types
CONS_ALL = frozenset([CONS_SSH, CONS_VNC, CONS_MESSAGE])

# For RSA keys more bits are better, but they also make operations more
# expensive. NIST SP 800-131 recommends a minimum of 2048 bits from the year
# 2010 on.
RSA_KEY_BITS = 2048

# Ciphers allowed for SSL connections. For the format, see ciphers(1). A better
# way to disable ciphers would be to use the exclamation mark (!), but socat
# versions below 1.5 can't parse exclamation marks in options properly. When
# modifying the ciphers, ensure not to accidentially add something after it's
# been removed. Use the "openssl" utility to check the allowed ciphers, e.g.
# "openssl ciphers -v HIGH:-DES".
OPENSSL_CIPHERS = "HIGH:-DES:-3DES:-EXPORT:-ADH"

# Digest used to sign certificates ("openssl x509" uses SHA1 by default)
X509_CERT_SIGN_DIGEST = "SHA1"

# Default validity of certificates in days
X509_CERT_DEFAULT_VALIDITY = 365 * 5

# commonName (CN) used in certificates
X509_CERT_CN = "ganeti.example.com"

X509_CERT_SIGNATURE_HEADER = "X-Ganeti-Signature"

IMPORT_EXPORT_DAEMON = _autoconf.PKGLIBDIR + "/import-export"

# Import/export daemon mode
IEM_IMPORT = "import"
IEM_EXPORT = "export"

# Import/export transport compression
IEC_NONE = "none"
IEC_GZIP = "gzip"
IEC_ALL = frozenset([
  IEC_NONE,
  IEC_GZIP,
  ])

IE_CUSTOM_SIZE = "fd"

IE_MAGIC_RE = re.compile(r"^[-_.a-zA-Z0-9]{5,100}$")

# Import/export I/O
# Direct file I/O, equivalent to a shell's I/O redirection using '<' or '>'
IEIO_FILE = "file"
# Raw block device I/O using "dd"
IEIO_RAW_DISK = "raw"
# OS definition import/export script
IEIO_SCRIPT = "script"

VALUE_DEFAULT = "default"
VALUE_AUTO = "auto"
VALUE_GENERATE = "generate"
VALUE_NONE = "none"
VALUE_TRUE = "true"
VALUE_FALSE = "false"

# External script validation mask
EXT_PLUGIN_MASK = re.compile("^[a-zA-Z0-9_-]+$")

# hooks-related constants
HOOKS_BASE_DIR = CONF_DIR + "/hooks"
HOOKS_PHASE_PRE = "pre"
HOOKS_PHASE_POST = "post"
HOOKS_NAME_CFGUPDATE = "config-update"
HOOKS_NAME_WATCHER = "watcher"
HOOKS_VERSION = 2

# hooks subject type (what object type does the LU deal with)
HTYPE_CLUSTER = "CLUSTER"
HTYPE_NODE = "NODE"
HTYPE_GROUP = "GROUP"
HTYPE_INSTANCE = "INSTANCE"

HKR_SKIP = 0
HKR_FAIL = 1
HKR_SUCCESS = 2

# Storage types
ST_FILE = "file"
ST_LVM_PV = "lvm-pv"
ST_LVM_VG = "lvm-vg"

# Storage fields
# first two are valid in LU context only, not passed to backend
SF_NODE = "node"
SF_TYPE = "type"
# and the rest are valid in backend
SF_NAME = "name"
SF_SIZE = "size"
SF_FREE = "free"
SF_USED = "used"
SF_ALLOCATABLE = "allocatable"

# Storage operations
SO_FIX_CONSISTENCY = "fix-consistency"

# Available fields per storage type
VALID_STORAGE_FIELDS = frozenset([SF_NAME, SF_TYPE, SF_SIZE,
                                  SF_USED, SF_FREE, SF_ALLOCATABLE])

VALID_STORAGE_TYPES = frozenset([ST_FILE, ST_LVM_PV, ST_LVM_VG])

MODIFIABLE_STORAGE_FIELDS = {
  ST_LVM_PV: frozenset([SF_ALLOCATABLE]),
  }

VALID_STORAGE_OPERATIONS = {
  ST_LVM_VG: frozenset([SO_FIX_CONSISTENCY]),
  }

# Local disk status
# Note: Code depends on LDS_OKAY < LDS_UNKNOWN < LDS_FAULTY
(LDS_OKAY,
 LDS_UNKNOWN,
 LDS_FAULTY) = range(1, 4)

# disk template types
DT_DISKLESS = "diskless"
DT_PLAIN = "plain"
DT_DRBD8 = "drbd"
DT_FILE = "file"
DT_SHARED_FILE = "sharedfile"
DT_BLOCK = "blockdev"

# the set of network-mirrored disk templates
DTS_INT_MIRROR = frozenset([DT_DRBD8])

# the set of externally-mirrored disk templates (e.g. SAN, NAS)
DTS_EXT_MIRROR = frozenset([DT_SHARED_FILE, DT_BLOCK])

# the set of non-lvm-based disk templates
DTS_NOT_LVM = frozenset([DT_DISKLESS, DT_FILE, DT_SHARED_FILE, DT_BLOCK])

# the set of disk templates which can be grown
DTS_GROWABLE = frozenset([DT_PLAIN, DT_DRBD8, DT_FILE, DT_SHARED_FILE])

# the set of disk templates that allow adoption
DTS_MAY_ADOPT = frozenset([DT_PLAIN, DT_BLOCK])

# the set of disk templates that *must* use adoption
DTS_MUST_ADOPT = frozenset([DT_BLOCK])

# the set of disk templates that allow migrations
DTS_MIRRORED = frozenset.union(DTS_INT_MIRROR, DTS_EXT_MIRROR)

# the set of file based disk templates
DTS_FILEBASED = frozenset([DT_FILE, DT_SHARED_FILE])

# logical disk types
LD_LV = "lvm"
LD_DRBD8 = "drbd8"
LD_FILE = "file"
LD_BLOCKDEV = "blockdev"
LDS_BLOCK = frozenset([LD_LV, LD_DRBD8, LD_BLOCKDEV])

# drbd constants
DRBD_HMAC_ALG = "md5"
DRBD_NET_PROTOCOL = "C"
DRBD_BARRIERS = _autoconf.DRBD_BARRIERS

# file backend driver
FD_LOOP = "loop"
FD_BLKTAP = "blktap"

# the set of drbd-like disk types
LDS_DRBD = frozenset([LD_DRBD8])

# disk access mode
DISK_RDONLY = "ro"
DISK_RDWR = "rw"
DISK_ACCESS_SET = frozenset([DISK_RDONLY, DISK_RDWR])

# disk replacement mode
REPLACE_DISK_PRI = "replace_on_primary"    # replace disks on primary
REPLACE_DISK_SEC = "replace_on_secondary"  # replace disks on secondary
REPLACE_DISK_CHG = "replace_new_secondary" # change secondary node
REPLACE_DISK_AUTO = "replace_auto"
REPLACE_MODES = frozenset([
  REPLACE_DISK_PRI,
  REPLACE_DISK_SEC,
  REPLACE_DISK_CHG,
  REPLACE_DISK_AUTO,
  ])

# Instance export mode
EXPORT_MODE_LOCAL = "local"
EXPORT_MODE_REMOTE = "remote"
EXPORT_MODES = frozenset([
  EXPORT_MODE_LOCAL,
  EXPORT_MODE_REMOTE,
  ])

# Lock recalculate mode
LOCKS_REPLACE = 'replace'
LOCKS_APPEND = 'append'

# Lock timeout (sum) before we should go into blocking acquire (still
# can be reset by priority change); computed as max time (10 hours)
# before we should actually go into blocking acquire given that we
# start from default priority level; in seconds
LOCK_ATTEMPTS_TIMEOUT = 10 * 3600 / 20.0
LOCK_ATTEMPTS_MAXWAIT = 15.0
LOCK_ATTEMPTS_MINWAIT = 1.0

# instance creation modes
INSTANCE_CREATE = "create"
INSTANCE_IMPORT = "import"
INSTANCE_REMOTE_IMPORT = "remote-import"
INSTANCE_CREATE_MODES = frozenset([
  INSTANCE_CREATE,
  INSTANCE_IMPORT,
  INSTANCE_REMOTE_IMPORT,
  ])

# Remote import/export handshake message and version
RIE_VERSION = 0
RIE_HANDSHAKE = "Hi, I'm Ganeti"

# Remote import/export certificate validity in seconds
RIE_CERT_VALIDITY = 24 * 60 * 60

# Overall timeout for establishing connection
RIE_CONNECT_TIMEOUT = 180

# Export only: how long to wait per connection attempt (seconds)
RIE_CONNECT_ATTEMPT_TIMEOUT = 20

# Export only: number of attempts to connect
RIE_CONNECT_RETRIES = 10

#: Give child process up to 5 seconds to exit after sending a signal
CHILD_LINGER_TIMEOUT = 5.0

DISK_TEMPLATES = frozenset([DT_DISKLESS, DT_PLAIN, DT_DRBD8,
                            DT_FILE, DT_SHARED_FILE, DT_BLOCK])

FILE_DRIVER = frozenset([FD_LOOP, FD_BLKTAP])

# import/export config options
INISECT_EXP = "export"
INISECT_INS = "instance"
INISECT_HYP = "hypervisor"
INISECT_BEP = "backend"
INISECT_OSP = "os"

# dynamic device modification
DDM_ADD = "add"
DDM_REMOVE = "remove"
DDMS_VALUES = frozenset([DDM_ADD, DDM_REMOVE])

# common exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_NOTCLUSTER = 5
EXIT_NOTMASTER = 11
EXIT_NODESETUP_ERROR = 12
EXIT_CONFIRMATION = 13 # need user confirmation

#: Exit code for query operations with unknown fields
EXIT_UNKNOWN_FIELD = 14

# tags
TAG_CLUSTER = "cluster"
TAG_NODEGROUP = "nodegroup"
TAG_NODE = "node"
TAG_INSTANCE = "instance"
VALID_TAG_TYPES = frozenset([
  TAG_CLUSTER,
  TAG_NODEGROUP,
  TAG_NODE,
  TAG_INSTANCE,
  ])
MAX_TAG_LEN = 128
MAX_TAGS_PER_OBJ = 4096

# others
DEFAULT_BRIDGE = "xen-br0"
SYNC_SPEED = 60 * 1024
IP4_ADDRESS_LOCALHOST = "127.0.0.1"
IP4_ADDRESS_ANY = "0.0.0.0"
IP6_ADDRESS_LOCALHOST = "::1"
IP6_ADDRESS_ANY = "::"
IP4_VERSION = 4
IP6_VERSION = 6
TCP_PING_TIMEOUT = 10
GANETI_RUNAS = "root"
DEFAULT_VG = "xenvg"
DEFAULT_DRBD_HELPER = "/bin/true"
MIN_VG_SIZE = 20480
DEFAULT_MAC_PREFIX = "aa:00:00"
LVM_STRIPECOUNT = _autoconf.LVM_STRIPECOUNT
# default maximum instance wait time, in seconds.
DEFAULT_SHUTDOWN_TIMEOUT = 120
NODE_MAX_CLOCK_SKEW = 150
# Time for an intra-cluster disk transfer to wait for a connection
DISK_TRANSFER_CONNECT_TIMEOUT = 60
# Disk index separator
DISK_SEPARATOR = _autoconf.DISK_SEPARATOR

#: Key for job IDs in opcode result
JOB_IDS_KEY = "jobs"

# runparts results
(RUNPARTS_SKIP,
 RUNPARTS_RUN,
 RUNPARTS_ERR) = range(3)

RUNPARTS_STATUS = frozenset([RUNPARTS_SKIP, RUNPARTS_RUN, RUNPARTS_ERR])

# RPC constants
(RPC_ENCODING_NONE,
 RPC_ENCODING_ZLIB_BASE64) = range(2)

# os related constants
OS_SCRIPT_CREATE = 'create'
OS_SCRIPT_IMPORT = 'import'
OS_SCRIPT_EXPORT = 'export'
OS_SCRIPT_RENAME = 'rename'
OS_SCRIPT_VERIFY = 'verify'
OS_SCRIPTS = frozenset([OS_SCRIPT_CREATE, OS_SCRIPT_IMPORT,
                        OS_SCRIPT_EXPORT, OS_SCRIPT_RENAME,
                        OS_SCRIPT_VERIFY])

OS_API_FILE = 'ganeti_api_version'
OS_VARIANTS_FILE = 'variants.list'
OS_PARAMETERS_FILE = 'parameters.list'

OS_VALIDATE_PARAMETERS = 'parameters'
OS_VALIDATE_CALLS = frozenset([OS_VALIDATE_PARAMETERS])

# ssh constants
SSH_CONFIG_DIR = _autoconf.SSH_CONFIG_DIR
SSH_HOST_DSA_PRIV = SSH_CONFIG_DIR + "/ssh_host_dsa_key"
SSH_HOST_DSA_PUB = SSH_HOST_DSA_PRIV + ".pub"
SSH_HOST_RSA_PRIV = SSH_CONFIG_DIR + "/ssh_host_rsa_key"
SSH_HOST_RSA_PUB = SSH_HOST_RSA_PRIV + ".pub"
SSH = "ssh"
SCP = "scp"

# reboot types
INSTANCE_REBOOT_SOFT = "soft"
INSTANCE_REBOOT_HARD = "hard"
INSTANCE_REBOOT_FULL = "full"

REBOOT_TYPES = frozenset([INSTANCE_REBOOT_SOFT,
                          INSTANCE_REBOOT_HARD,
                          INSTANCE_REBOOT_FULL])

VTYPE_STRING = 'string'
VTYPE_MAYBE_STRING = "maybe-string"
VTYPE_BOOL = 'bool'
VTYPE_SIZE = 'size' # size, in MiBs
VTYPE_INT = 'int'
ENFORCEABLE_TYPES = frozenset([
                      VTYPE_STRING,
                      VTYPE_MAYBE_STRING,
                      VTYPE_BOOL,
                      VTYPE_SIZE,
                      VTYPE_INT,
                      ])

# HV parameter names (global namespace)
HV_BOOT_ORDER = "boot_order"
HV_CDROM_IMAGE_PATH = "cdrom_image_path"
HV_KVM_CDROM2_IMAGE_PATH = "cdrom2_image_path"
HV_KVM_FLOPPY_IMAGE_PATH = "floppy_image_path"
HV_NIC_TYPE = "nic_type"
HV_DISK_TYPE = "disk_type"
HV_KVM_CDROM_DISK_TYPE = "cdrom_disk_type"
HV_VNC_BIND_ADDRESS = "vnc_bind_address"
HV_VNC_PASSWORD_FILE = "vnc_password_file"
HV_VNC_TLS = "vnc_tls"
HV_VNC_X509 = "vnc_x509_path"
HV_VNC_X509_VERIFY = "vnc_x509_verify"
HV_ACPI = "acpi"
HV_PAE = "pae"
HV_USE_BOOTLOADER = "use_bootloader"
HV_BOOTLOADER_ARGS = "bootloader_args"
HV_BOOTLOADER_PATH = "bootloader_path"
HV_KERNEL_ARGS = "kernel_args"
HV_KERNEL_PATH = "kernel_path"
HV_INITRD_PATH = "initrd_path"
HV_ROOT_PATH = "root_path"
HV_SERIAL_CONSOLE = "serial_console"
HV_USB_MOUSE = "usb_mouse"
HV_DEVICE_MODEL = "device_model"
HV_INIT_SCRIPT = "init_script"
HV_MIGRATION_PORT = "migration_port"
HV_MIGRATION_BANDWIDTH = "migration_bandwidth"
HV_MIGRATION_DOWNTIME = "migration_downtime"
HV_MIGRATION_MODE = "migration_mode"
HV_USE_LOCALTIME = "use_localtime"
HV_DISK_CACHE = "disk_cache"
HV_SECURITY_MODEL = "security_model"
HV_SECURITY_DOMAIN = "security_domain"
HV_KVM_FLAG = "kvm_flag"
HV_VHOST_NET = "vhost_net"
HV_KVM_USE_CHROOT = "use_chroot"
HV_CPU_MASK = "cpu_mask"
HV_MEM_PATH = "mem_path"
HV_BLOCKDEV_PREFIX = "blockdev_prefix"

HVS_PARAMETER_TYPES = {
  HV_BOOT_ORDER: VTYPE_STRING,
  HV_KVM_FLOPPY_IMAGE_PATH: VTYPE_STRING,
  HV_CDROM_IMAGE_PATH: VTYPE_STRING,
  HV_KVM_CDROM2_IMAGE_PATH: VTYPE_STRING,
  HV_NIC_TYPE: VTYPE_STRING,
  HV_DISK_TYPE: VTYPE_STRING,
  HV_KVM_CDROM_DISK_TYPE: VTYPE_STRING,
  HV_VNC_PASSWORD_FILE: VTYPE_STRING,
  HV_VNC_BIND_ADDRESS: VTYPE_STRING,
  HV_VNC_TLS: VTYPE_BOOL,
  HV_VNC_X509: VTYPE_STRING,
  HV_VNC_X509_VERIFY: VTYPE_BOOL,
  HV_ACPI: VTYPE_BOOL,
  HV_PAE: VTYPE_BOOL,
  HV_USE_BOOTLOADER: VTYPE_BOOL,
  HV_BOOTLOADER_PATH: VTYPE_STRING,
  HV_BOOTLOADER_ARGS: VTYPE_STRING,
  HV_KERNEL_PATH: VTYPE_STRING,
  HV_KERNEL_ARGS: VTYPE_STRING,
  HV_INITRD_PATH: VTYPE_STRING,
  HV_ROOT_PATH: VTYPE_MAYBE_STRING,
  HV_SERIAL_CONSOLE: VTYPE_BOOL,
  HV_USB_MOUSE: VTYPE_STRING,
  HV_DEVICE_MODEL: VTYPE_STRING,
  HV_INIT_SCRIPT: VTYPE_STRING,
  HV_MIGRATION_PORT: VTYPE_INT,
  HV_MIGRATION_BANDWIDTH: VTYPE_INT,
  HV_MIGRATION_DOWNTIME: VTYPE_INT,
  HV_MIGRATION_MODE: VTYPE_STRING,
  HV_USE_LOCALTIME: VTYPE_BOOL,
  HV_DISK_CACHE: VTYPE_STRING,
  HV_SECURITY_MODEL: VTYPE_STRING,
  HV_SECURITY_DOMAIN: VTYPE_STRING,
  HV_KVM_FLAG: VTYPE_STRING,
  HV_VHOST_NET: VTYPE_BOOL,
  HV_KVM_USE_CHROOT: VTYPE_BOOL,
  HV_CPU_MASK: VTYPE_STRING,
  HV_MEM_PATH: VTYPE_STRING,
  HV_BLOCKDEV_PREFIX: VTYPE_STRING,
  }

HVS_PARAMETERS = frozenset(HVS_PARAMETER_TYPES.keys())

# Backend parameter names
BE_MEMORY = "memory"
BE_VCPUS = "vcpus"
BE_AUTO_BALANCE = "auto_balance"

BES_PARAMETER_TYPES = {
    BE_MEMORY: VTYPE_SIZE,
    BE_VCPUS: VTYPE_INT,
    BE_AUTO_BALANCE: VTYPE_BOOL,
    }

BES_PARAMETERS = frozenset(BES_PARAMETER_TYPES.keys())

# Node parameter names
ND_OOB_PROGRAM = "oob_program"

NDS_PARAMETER_TYPES = {
    ND_OOB_PROGRAM: VTYPE_MAYBE_STRING,
    }

NDS_PARAMETERS = frozenset(NDS_PARAMETER_TYPES.keys())

# OOB supported commands
OOB_POWER_ON = "power-on"
OOB_POWER_OFF = "power-off"
OOB_POWER_CYCLE = "power-cycle"
OOB_POWER_STATUS = "power-status"
OOB_HEALTH = "health"

OOB_COMMANDS = frozenset([OOB_POWER_ON, OOB_POWER_OFF, OOB_POWER_CYCLE,
                          OOB_POWER_STATUS, OOB_HEALTH])

OOB_POWER_STATUS_POWERED = "powered"

OOB_TIMEOUT = 60 # 60 seconds
OOB_POWER_DELAY = 2.0 # 2 seconds

OOB_STATUS_OK = "OK"
OOB_STATUS_WARNING = "WARNING"
OOB_STATUS_CRITICAL = "CRITICAL"
OOB_STATUS_UNKNOWN = "UNKNOWN"

OOB_STATUSES = frozenset([
  OOB_STATUS_OK,
  OOB_STATUS_WARNING,
  OOB_STATUS_CRITICAL,
  OOB_STATUS_UNKNOWN,
  ])

# Instance Parameters Profile
PP_DEFAULT = "default"

# NIC_* constants are used inside the ganeti config
NIC_MODE = "mode"
NIC_LINK = "link"

NIC_MODE_BRIDGED = "bridged"
NIC_MODE_ROUTED = "routed"

NIC_VALID_MODES = frozenset([NIC_MODE_BRIDGED, NIC_MODE_ROUTED])

NICS_PARAMETER_TYPES = {
    NIC_MODE: VTYPE_STRING,
    NIC_LINK: VTYPE_STRING,
    }

NICS_PARAMETERS = frozenset(NICS_PARAMETER_TYPES.keys())

# IDISK_* constants are used in opcodes, to create/change disks
IDISK_SIZE = "size"
IDISK_MODE = "mode"
IDISK_ADOPT = "adopt"
IDISK_VG = "vg"
IDISK_METAVG = "metavg"
IDISK_PARAMS_TYPES = {
  IDISK_SIZE: VTYPE_SIZE,
  IDISK_MODE: VTYPE_STRING,
  IDISK_ADOPT: VTYPE_STRING,
  IDISK_VG: VTYPE_STRING,
  IDISK_METAVG: VTYPE_STRING,
  }
IDISK_PARAMS = frozenset(IDISK_PARAMS_TYPES.keys())

# INIC_* constants are used in opcodes, to create/change nics
INIC_MAC = "mac"
INIC_IP = "ip"
INIC_MODE = "mode"
INIC_LINK = "link"
INIC_PARAMS_TYPES = {
  INIC_IP: VTYPE_MAYBE_STRING,
  INIC_LINK: VTYPE_STRING,
  INIC_MAC: VTYPE_STRING,
  INIC_MODE: VTYPE_STRING,
  }
INIC_PARAMS = frozenset(INIC_PARAMS_TYPES.keys())

# Hypervisor constants
HT_XEN_PVM = "xen-pvm"
HT_FAKE = "fake"
HT_XEN_HVM = "xen-hvm"
HT_KVM = "kvm"
HT_CHROOT = "chroot"
HT_LXC = "lxc"
HYPER_TYPES = frozenset([
  HT_XEN_PVM,
  HT_FAKE,
  HT_XEN_HVM,
  HT_KVM,
  HT_CHROOT,
  HT_LXC,
  ])
HTS_REQ_PORT = frozenset([HT_XEN_HVM, HT_KVM])

VNC_BASE_PORT = 5900
VNC_PASSWORD_FILE = CONF_DIR + "/vnc-cluster-password"
VNC_DEFAULT_BIND_ADDRESS = IP4_ADDRESS_ANY

# NIC types
HT_NIC_RTL8139 = "rtl8139"
HT_NIC_NE2K_PCI = "ne2k_pci"
HT_NIC_NE2K_ISA = "ne2k_isa"
HT_NIC_I82551 = "i82551"
HT_NIC_I85557B = "i82557b"
HT_NIC_I8259ER = "i82559er"
HT_NIC_PCNET = "pcnet"
HT_NIC_E1000 = "e1000"
HT_NIC_PARAVIRTUAL = HT_DISK_PARAVIRTUAL = "paravirtual"

HT_HVM_VALID_NIC_TYPES = frozenset([HT_NIC_RTL8139, HT_NIC_NE2K_PCI,
                                    HT_NIC_E1000, HT_NIC_NE2K_ISA,
                                    HT_NIC_PARAVIRTUAL])
HT_KVM_VALID_NIC_TYPES = frozenset([HT_NIC_RTL8139, HT_NIC_NE2K_PCI,
                                    HT_NIC_NE2K_ISA, HT_NIC_I82551,
                                    HT_NIC_I85557B, HT_NIC_I8259ER,
                                    HT_NIC_PCNET, HT_NIC_E1000,
                                    HT_NIC_PARAVIRTUAL])
# Disk types
HT_DISK_IOEMU = "ioemu"
HT_DISK_IDE = "ide"
HT_DISK_SCSI = "scsi"
HT_DISK_SD = "sd"
HT_DISK_MTD = "mtd"
HT_DISK_PFLASH = "pflash"

HT_CACHE_DEFAULT = "default"
HT_CACHE_NONE = "none"
HT_CACHE_WTHROUGH = "writethrough"
HT_CACHE_WBACK = "writeback"
HT_VALID_CACHE_TYPES = frozenset([HT_CACHE_DEFAULT,
                                  HT_CACHE_NONE,
                                  HT_CACHE_WTHROUGH,
                                  HT_CACHE_WBACK])

HT_HVM_VALID_DISK_TYPES = frozenset([HT_DISK_PARAVIRTUAL, HT_DISK_IOEMU])
HT_KVM_VALID_DISK_TYPES = frozenset([HT_DISK_PARAVIRTUAL, HT_DISK_IDE,
                                     HT_DISK_SCSI, HT_DISK_SD, HT_DISK_MTD,
                                     HT_DISK_PFLASH])

# Mouse types:
HT_MOUSE_MOUSE = "mouse"
HT_MOUSE_TABLET = "tablet"

HT_KVM_VALID_MOUSE_TYPES = frozenset([HT_MOUSE_MOUSE, HT_MOUSE_TABLET])

# Boot order
HT_BO_FLOPPY = "floppy"
HT_BO_CDROM = "cdrom"
HT_BO_DISK = "disk"
HT_BO_NETWORK = "network"

HT_KVM_VALID_BO_TYPES = frozenset([HT_BO_FLOPPY, HT_BO_CDROM,
                                   HT_BO_DISK, HT_BO_NETWORK])

# Security models
HT_SM_NONE = "none"
HT_SM_USER = "user"
HT_SM_POOL = "pool"

HT_KVM_VALID_SM_TYPES = frozenset([HT_SM_NONE, HT_SM_USER, HT_SM_POOL])

# Kvm flag values
HT_KVM_ENABLED = "enabled"
HT_KVM_DISABLED = "disabled"

HT_KVM_FLAG_VALUES = frozenset([HT_KVM_ENABLED, HT_KVM_DISABLED])

# Migration type
HT_MIGRATION_LIVE = "live"
HT_MIGRATION_NONLIVE = "non-live"
HT_MIGRATION_MODES = frozenset([HT_MIGRATION_LIVE, HT_MIGRATION_NONLIVE])

# Cluster Verify steps
VERIFY_NPLUSONE_MEM = 'nplusone_mem'
VERIFY_OPTIONAL_CHECKS = frozenset([VERIFY_NPLUSONE_MEM])

# Node verify constants
NV_DRBDHELPER = "drbd-helper"
NV_DRBDLIST = "drbd-list"
NV_FILELIST = "filelist"
NV_HVINFO = "hvinfo"
NV_HYPERVISOR = "hypervisor"
NV_HVPARAMS = "hvparms"
NV_INSTANCELIST = "instancelist"
NV_LVLIST = "lvlist"
NV_MASTERIP = "master-ip"
NV_NODELIST = "nodelist"
NV_NODENETTEST = "node-net-test"
NV_NODESETUP = "nodesetup"
NV_OSLIST = "oslist"
NV_PVLIST = "pvlist"
NV_TIME = "time"
NV_VERSION = "version"
NV_VGLIST = "vglist"
NV_VMNODES = "vmnodes"
NV_OOB_PATHS = "oob-paths"
NV_BRIDGES = "bridges"

# Instance status
INSTST_RUNNING = "running"
INSTST_ADMINDOWN = "ADMIN_down"
INSTST_NODEOFFLINE = "ERROR_nodeoffline"
INSTST_NODEDOWN = "ERROR_nodedown"
INSTST_WRONGNODE = "ERROR_wrongnode"
INSTST_ERRORUP = "ERROR_up"
INSTST_ERRORDOWN = "ERROR_down"
INSTST_ALL = frozenset([
  INSTST_RUNNING,
  INSTST_ADMINDOWN,
  INSTST_NODEOFFLINE,
  INSTST_NODEDOWN,
  INSTST_WRONGNODE,
  INSTST_ERRORUP,
  INSTST_ERRORDOWN,
  ])

# Node roles
NR_REGULAR = "R"
NR_MASTER = "M"
NR_MCANDIDATE = "C"
NR_DRAINED = "D"
NR_OFFLINE = "O"
NR_ALL = frozenset([
  NR_REGULAR,
  NR_MASTER,
  NR_MCANDIDATE,
  NR_DRAINED,
  NR_OFFLINE,
  ])

# SSL certificate check constants (in days)
SSL_CERT_EXPIRATION_WARN = 30
SSL_CERT_EXPIRATION_ERROR = 7

# Allocator framework constants
IALLOCATOR_VERSION = 2
IALLOCATOR_DIR_IN = "in"
IALLOCATOR_DIR_OUT = "out"
VALID_IALLOCATOR_DIRECTIONS = frozenset([
  IALLOCATOR_DIR_IN,
  IALLOCATOR_DIR_OUT,
  ])
IALLOCATOR_MODE_ALLOC = "allocate"
IALLOCATOR_MODE_RELOC = "relocate"
IALLOCATOR_MODE_MEVAC = "multi-evacuate"
IALLOCATOR_MODE_MRELOC = "multi-relocate"
IALLOCATOR_MODE_CHG_GROUP = "change-group"
IALLOCATOR_MODE_NODE_EVAC = "node-evacuate"
VALID_IALLOCATOR_MODES = frozenset([
  IALLOCATOR_MODE_ALLOC,
  IALLOCATOR_MODE_RELOC,
  IALLOCATOR_MODE_MEVAC,
  IALLOCATOR_MODE_MRELOC,
  IALLOCATOR_MODE_CHG_GROUP,
  IALLOCATOR_MODE_NODE_EVAC,
  ])
IALLOCATOR_SEARCH_PATH = _autoconf.IALLOCATOR_SEARCH_PATH

IALLOCATOR_NEVAC_PRI = "primary-only"
IALLOCATOR_NEVAC_SEC = "secondary-only"
IALLOCATOR_NEVAC_ALL = "all"
IALLOCATOR_NEVAC_MODES = frozenset([
  IALLOCATOR_NEVAC_PRI,
  IALLOCATOR_NEVAC_SEC,
  IALLOCATOR_NEVAC_ALL,
  ])

# TODO: Remove multi-relocate constants, including IALLOCATOR_MODE_MRELOC
IALLOCATOR_MRELOC_ANY = "any_group"
IALLOCATOR_MRELOC_CHANGE = "change_group"
IALLOCATOR_MRELOC_KEEP = "keep_group"
IALLOCATOR_MRELOC_MODES = frozenset([
  IALLOCATOR_MRELOC_ANY,
  IALLOCATOR_MRELOC_CHANGE,
  IALLOCATOR_MRELOC_KEEP,
  ])

# Job queue
JOB_QUEUE_VERSION = 1
JOB_QUEUE_LOCK_FILE = QUEUE_DIR + "/lock"
JOB_QUEUE_VERSION_FILE = QUEUE_DIR + "/version"
JOB_QUEUE_SERIAL_FILE = QUEUE_DIR + "/serial"
JOB_QUEUE_ARCHIVE_DIR = QUEUE_DIR + "/archive"
JOB_QUEUE_DRAIN_FILE = QUEUE_DIR + "/drain"
JOB_QUEUE_SIZE_HARD_LIMIT = 5000
JOB_QUEUE_DIRS = [QUEUE_DIR, JOB_QUEUE_ARCHIVE_DIR]
JOB_QUEUE_DIRS_MODE = SECURE_DIR_MODE

JOB_ID_TEMPLATE = r"\d+"

# unchanged job return
JOB_NOTCHANGED = "nochange"

# Job status
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_WAITLOCK = "waiting"
JOB_STATUS_CANCELING = "canceling"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_CANCELED = "canceled"
JOB_STATUS_SUCCESS = "success"
JOB_STATUS_ERROR = "error"
JOBS_FINALIZED = frozenset([
  JOB_STATUS_CANCELED,
  JOB_STATUS_SUCCESS,
  JOB_STATUS_ERROR,
  ])
JOB_STATUS_ALL = frozenset([
  JOB_STATUS_QUEUED,
  JOB_STATUS_WAITLOCK,
  JOB_STATUS_CANCELING,
  JOB_STATUS_RUNNING,
  ]) | JOBS_FINALIZED

# OpCode status
# not yet finalized
OP_STATUS_QUEUED = "queued"
OP_STATUS_WAITLOCK = "waiting"
OP_STATUS_CANCELING = "canceling"
OP_STATUS_RUNNING = "running"
# finalized
OP_STATUS_CANCELED = "canceled"
OP_STATUS_SUCCESS = "success"
OP_STATUS_ERROR = "error"
OPS_FINALIZED = frozenset([OP_STATUS_CANCELED,
                           OP_STATUS_SUCCESS,
                           OP_STATUS_ERROR])

# OpCode priority
OP_PRIO_LOWEST = +19
OP_PRIO_HIGHEST = -20

OP_PRIO_LOW = +10
OP_PRIO_NORMAL = 0
OP_PRIO_HIGH = -10

OP_PRIO_SUBMIT_VALID = frozenset([
  OP_PRIO_LOW,
  OP_PRIO_NORMAL,
  OP_PRIO_HIGH,
  ])

OP_PRIO_DEFAULT = OP_PRIO_NORMAL

# Execution log types
ELOG_MESSAGE = "message"
ELOG_PROGRESS = "progress"
ELOG_REMOTE_IMPORT = "remote-import"
ELOG_JQUEUE_TEST = "jqueue-test"

# /etc/hosts modification
ETC_HOSTS_ADD = "add"
ETC_HOSTS_REMOVE = "remove"

# Job queue test
JQT_MSGPREFIX = "TESTMSG="
JQT_EXPANDNAMES = "expandnames"
JQT_EXEC = "exec"
JQT_LOGMSG = "logmsg"
JQT_STARTMSG = "startmsg"
JQT_ALL = frozenset([
  JQT_EXPANDNAMES,
  JQT_EXEC,
  JQT_LOGMSG,
  JQT_STARTMSG,
  ])

# Query resources
QR_INSTANCE = "instance"
QR_NODE = "node"
QR_LOCK = "lock"
QR_GROUP = "group"
QR_OS = "os"

#: List of resources which can be queried using L{opcodes.OpQuery}
QR_VIA_OP = frozenset([QR_INSTANCE, QR_NODE, QR_GROUP, QR_OS])

#: List of resources which can be queried using Local UniX Interface
QR_VIA_LUXI = QR_VIA_OP.union([
  QR_LOCK,
  ])

#: List of resources which can be queried using RAPI
QR_VIA_RAPI = QR_VIA_LUXI

# Query field types
QFT_UNKNOWN = "unknown"
QFT_TEXT = "text"
QFT_BOOL = "bool"
QFT_NUMBER = "number"
QFT_UNIT = "unit"
QFT_TIMESTAMP = "timestamp"
QFT_OTHER = "other"

#: All query field types
QFT_ALL = frozenset([
  QFT_UNKNOWN,
  QFT_TEXT,
  QFT_BOOL,
  QFT_NUMBER,
  QFT_UNIT,
  QFT_TIMESTAMP,
  QFT_OTHER,
  ])

# Query result field status (don't change or reuse values as they're used by
# clients)
#: Normal field status
RS_NORMAL = 0
#: Unknown field
RS_UNKNOWN = 1
#: No data (e.g. RPC error), can be used instead of L{RS_OFFLINE}
RS_NODATA = 2
#: Value unavailable/unsupported for item; if this field is supported
#: but we cannot get the data for the moment, RS_NODATA or
#: RS_OFFLINE should be used
RS_UNAVAIL = 3
#: Resource marked offline
RS_OFFLINE = 4

RS_ALL = frozenset([
  RS_NORMAL,
  RS_UNKNOWN,
  RS_NODATA,
  RS_UNAVAIL,
  RS_OFFLINE,
  ])

#: Dictionary with special field cases and their verbose/terse formatting
RSS_DESCRIPTION = {
  RS_UNKNOWN: ("(unknown)", "??"),
  RS_NODATA:  ("(nodata)",  "?"),
  RS_OFFLINE: ("(offline)", "*"),
  RS_UNAVAIL: ("(unavail)", "-"),
  }

# max dynamic devices
MAX_NICS = 8
MAX_DISKS = 16

# SSCONF keys
SS_CLUSTER_NAME = "cluster_name"
SS_CLUSTER_TAGS = "cluster_tags"
SS_FILE_STORAGE_DIR = "file_storage_dir"
SS_SHARED_FILE_STORAGE_DIR = "shared_file_storage_dir"
SS_MASTER_CANDIDATES = "master_candidates"
SS_MASTER_CANDIDATES_IPS = "master_candidates_ips"
SS_MASTER_IP = "master_ip"
SS_MASTER_NETDEV = "master_netdev"
SS_MASTER_NODE = "master_node"
SS_NODE_LIST = "node_list"
SS_NODE_PRIMARY_IPS = "node_primary_ips"
SS_NODE_SECONDARY_IPS = "node_secondary_ips"
SS_OFFLINE_NODES = "offline_nodes"
SS_ONLINE_NODES = "online_nodes"
SS_PRIMARY_IP_FAMILY = "primary_ip_family"
SS_INSTANCE_LIST = "instance_list"
SS_RELEASE_VERSION = "release_version"
SS_HYPERVISOR_LIST = "hypervisor_list"
SS_MAINTAIN_NODE_HEALTH = "maintain_node_health"
SS_UID_POOL = "uid_pool"
SS_NODEGROUPS = "nodegroups"

# cluster wide default parameters
DEFAULT_ENABLED_HYPERVISOR = HT_XEN_PVM

HVC_DEFAULTS = {
  HT_XEN_PVM: {
    HV_USE_BOOTLOADER: False,
    HV_BOOTLOADER_PATH: XEN_BOOTLOADER,
    HV_BOOTLOADER_ARGS: '',
    HV_KERNEL_PATH: "/boot/vmlinuz-2.6-xenU",
    HV_INITRD_PATH: '',
    HV_ROOT_PATH: '/dev/sda1',
    HV_KERNEL_ARGS: 'ro',
    HV_MIGRATION_PORT: 8002,
    HV_MIGRATION_MODE: HT_MIGRATION_LIVE,
    HV_BLOCKDEV_PREFIX: "sd",
    },
  HT_XEN_HVM: {
    HV_BOOT_ORDER: "cd",
    HV_CDROM_IMAGE_PATH: '',
    HV_NIC_TYPE: HT_NIC_RTL8139,
    HV_DISK_TYPE: HT_DISK_PARAVIRTUAL,
    HV_VNC_BIND_ADDRESS: IP4_ADDRESS_ANY,
    HV_VNC_PASSWORD_FILE: VNC_PASSWORD_FILE,
    HV_ACPI: True,
    HV_PAE: True,
    HV_KERNEL_PATH: "/usr/lib/xen/boot/hvmloader",
    HV_DEVICE_MODEL: "/usr/lib/xen/bin/qemu-dm",
    HV_MIGRATION_PORT: 8002,
    HV_MIGRATION_MODE: HT_MIGRATION_NONLIVE,
    HV_USE_LOCALTIME: False,
    HV_BLOCKDEV_PREFIX: "hd",
    },
  HT_KVM: {
    HV_KERNEL_PATH: "/boot/vmlinuz-2.6-kvmU",
    HV_INITRD_PATH: '',
    HV_KERNEL_ARGS: 'ro',
    HV_ROOT_PATH: '/dev/vda1',
    HV_ACPI: True,
    HV_SERIAL_CONSOLE: True,
    HV_VNC_BIND_ADDRESS: '',
    HV_VNC_TLS: False,
    HV_VNC_X509: '',
    HV_VNC_X509_VERIFY: False,
    HV_VNC_PASSWORD_FILE: '',
    HV_KVM_FLOPPY_IMAGE_PATH: '',
    HV_CDROM_IMAGE_PATH: '',
    HV_KVM_CDROM2_IMAGE_PATH: '',
    HV_BOOT_ORDER: HT_BO_DISK,
    HV_NIC_TYPE: HT_NIC_PARAVIRTUAL,
    HV_DISK_TYPE: HT_DISK_PARAVIRTUAL,
    HV_KVM_CDROM_DISK_TYPE: '',
    HV_USB_MOUSE: '',
    HV_MIGRATION_PORT: 8102,
    HV_MIGRATION_BANDWIDTH: 32, # MiB/s
    HV_MIGRATION_DOWNTIME: 30,  # ms
    HV_MIGRATION_MODE: HT_MIGRATION_LIVE,
    HV_USE_LOCALTIME: False,
    HV_DISK_CACHE: HT_CACHE_DEFAULT,
    HV_SECURITY_MODEL: HT_SM_NONE,
    HV_SECURITY_DOMAIN: '',
    HV_KVM_FLAG: "",
    HV_VHOST_NET: False,
    HV_KVM_USE_CHROOT: False,
    HV_MEM_PATH: "",
    },
  HT_FAKE: {
    },
  HT_CHROOT: {
    HV_INIT_SCRIPT: "/ganeti-chroot",
    },
  HT_LXC: {
    HV_CPU_MASK: "",
    },
  }

HVC_GLOBALS = frozenset([
  HV_MIGRATION_PORT,
  HV_MIGRATION_BANDWIDTH,
  HV_MIGRATION_MODE,
  ])

BEC_DEFAULTS = {
  BE_MEMORY: 128,
  BE_VCPUS: 1,
  BE_AUTO_BALANCE: True,
  }

NDC_DEFAULTS = {
  ND_OOB_PROGRAM: None,
  }

NICC_DEFAULTS = {
  NIC_MODE: NIC_MODE_BRIDGED,
  NIC_LINK: DEFAULT_BRIDGE,
  }

MASTER_POOL_SIZE_DEFAULT = 10

CONFD_PROTOCOL_VERSION = 1

CONFD_REQ_PING = 0
CONFD_REQ_NODE_ROLE_BYNAME = 1
CONFD_REQ_NODE_PIP_BY_INSTANCE_IP = 2
CONFD_REQ_CLUSTER_MASTER = 3
CONFD_REQ_NODE_PIP_LIST = 4
CONFD_REQ_MC_PIP_LIST = 5
CONFD_REQ_INSTANCES_IPS_LIST = 6

# Confd request query fields. These are used to narrow down queries.
# These must be strings rather than integers, because json-encoding
# converts them to strings anyway, as they're used as dict-keys.
CONFD_REQQ_LINK = "0"
CONFD_REQQ_IP = "1"
CONFD_REQQ_IPLIST = "2"
CONFD_REQQ_FIELDS = "3"

CONFD_REQFIELD_NAME = "0"
CONFD_REQFIELD_IP = "1"
CONFD_REQFIELD_MNODE_PIP = "2"

CONFD_REQS = frozenset([
  CONFD_REQ_PING,
  CONFD_REQ_NODE_ROLE_BYNAME,
  CONFD_REQ_NODE_PIP_BY_INSTANCE_IP,
  CONFD_REQ_CLUSTER_MASTER,
  CONFD_REQ_NODE_PIP_LIST,
  CONFD_REQ_MC_PIP_LIST,
  CONFD_REQ_INSTANCES_IPS_LIST,
  ])

CONFD_REPL_STATUS_OK = 0
CONFD_REPL_STATUS_ERROR = 1
CONFD_REPL_STATUS_NOTIMPLEMENTED = 2

CONFD_REPL_STATUSES = frozenset([
  CONFD_REPL_STATUS_OK,
  CONFD_REPL_STATUS_ERROR,
  CONFD_REPL_STATUS_NOTIMPLEMENTED,
  ])

(CONFD_NODE_ROLE_MASTER,
 CONFD_NODE_ROLE_CANDIDATE,
 CONFD_NODE_ROLE_OFFLINE,
 CONFD_NODE_ROLE_DRAINED,
 CONFD_NODE_ROLE_REGULAR,
 ) = range(5)

# A few common errors for confd
CONFD_ERROR_UNKNOWN_ENTRY = 1
CONFD_ERROR_INTERNAL = 2
CONFD_ERROR_ARGUMENT = 3

# Each request is "salted" by the current timestamp.
# This constants decides how many seconds of skew to accept.
# TODO: make this a default and allow the value to be more configurable
CONFD_MAX_CLOCK_SKEW = 2 * NODE_MAX_CLOCK_SKEW

# When we haven't reloaded the config for more than this amount of seconds, we
# force a test to see if inotify is betraying us.
CONFD_CONFIG_RELOAD_TIMEOUT = 60

# If we receive more than one update in this amount of seconds, we move to
# polling every RATELIMIT seconds, rather than relying on inotify, to be able
# to serve more requests.
CONFD_CONFIG_RELOAD_RATELIMIT = 2

# Magic number prepended to all confd queries.
# This allows us to distinguish different types of confd protocols and handle
# them. For example by changing this we can move the whole payload to be
# compressed, or move away from json.
CONFD_MAGIC_FOURCC = 'plj0'

# By default a confd request is sent to the minimum between this number and all
# MCs. 6 was chosen because even in the case of a disastrous 50% response rate,
# we should have enough answers to be able to compare more than one.
CONFD_DEFAULT_REQ_COVERAGE = 6

# Timeout in seconds to expire pending query request in the confd client
# library. We don't actually expect any answer more than 10 seconds after we
# sent a request.
CONFD_CLIENT_EXPIRE_TIMEOUT = 10

# Maximum UDP datagram size.
# On IPv4: 64K - 20 (ip header size) - 8 (udp header size) = 65507
# On IPv6: 64K - 40 (ip6 header size) - 8 (udp header size) = 65487
#   (assuming we can't use jumbo frames)
# We just set this to 60K, which should be enough
MAX_UDP_DATA_SIZE = 61440

# User-id pool minimum/maximum acceptable user-ids.
UIDPOOL_UID_MIN = 0
UIDPOOL_UID_MAX = 2**32-1 # Assuming 32 bit user-ids

# Name or path of the pgrep command
PGREP = "pgrep"

# Name of the node group that gets created at cluster init or upgrade
INITIAL_NODE_GROUP_NAME = "default"

# Possible values for NodeGroup.alloc_policy
ALLOC_POLICY_PREFERRED = "preferred"
ALLOC_POLICY_LAST_RESORT = "last_resort"
ALLOC_POLICY_UNALLOCABLE = "unallocable"
VALID_ALLOC_POLICIES = [
  ALLOC_POLICY_PREFERRED,
  ALLOC_POLICY_LAST_RESORT,
  ALLOC_POLICY_UNALLOCABLE,
  ]

# Temporary external/shared storage parameters
BLOCKDEV_DRIVER_MANUAL = "manual"

# Whether htools was enabled at compilation time
HTOOLS = _autoconf.HTOOLS
# The hail iallocator
IALLOC_HAIL = "hail"
