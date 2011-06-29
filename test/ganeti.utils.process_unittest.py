#!/usr/bin/env python2
#

# Copyright (C) 2011 Google Inc.
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


"""Script for testing ganeti.utils.process"""

import unittest
import tempfile
import shutil
import os
import stat
import time
import select
import signal

from ganeti import constants
from ganeti import utils
from ganeti import errors

import testutils


class TestIsProcessAlive(unittest.TestCase):
  """Testing case for IsProcessAlive"""

  def testExists(self):
    mypid = os.getpid()
    self.assert_(utils.IsProcessAlive(mypid), "can't find myself running")

  def testNotExisting(self):
    pid_non_existing = os.fork()
    if pid_non_existing == 0:
      os._exit(0)
    elif pid_non_existing < 0:
      raise SystemError("can't fork")
    os.waitpid(pid_non_existing, 0)
    self.assertFalse(utils.IsProcessAlive(pid_non_existing),
                     "nonexisting process detected")


class TestGetProcStatusPath(unittest.TestCase):
  def test(self):
    self.assert_("/1234/" in utils.process._GetProcStatusPath(1234))
    self.assertNotEqual(utils.process._GetProcStatusPath(1),
                        utils.process._GetProcStatusPath(2))


class TestIsProcessHandlingSignal(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def testParseSigsetT(self):
    parse_sigset_t_fn = utils.process._ParseSigsetT
    self.assertEqual(len(parse_sigset_t_fn("0")), 0)
    self.assertEqual(parse_sigset_t_fn("1"), set([1]))
    self.assertEqual(parse_sigset_t_fn("1000a"), set([2, 4, 17]))
    self.assertEqual(parse_sigset_t_fn("810002"), set([2, 17, 24, ]))
    self.assertEqual(parse_sigset_t_fn("0000000180000202"),
                     set([2, 10, 32, 33]))
    self.assertEqual(parse_sigset_t_fn("0000000180000002"),
                     set([2, 32, 33]))
    self.assertEqual(parse_sigset_t_fn("0000000188000002"),
                     set([2, 28, 32, 33]))
    self.assertEqual(parse_sigset_t_fn("000000004b813efb"),
                     set([1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 17,
                          24, 25, 26, 28, 31]))
    self.assertEqual(parse_sigset_t_fn("ffffff"), set(range(1, 25)))

  def testGetProcStatusField(self):
    for field in ["SigCgt", "Name", "FDSize"]:
      for value in ["", "0", "cat", "  1234 KB"]:
        pstatus = "\n".join([
          "VmPeak: 999 kB",
          "%s: %s" % (field, value),
          "TracerPid: 0",
          ])
        result = utils.process._GetProcStatusField(pstatus, field)
        self.assertEqual(result, value.strip())

  def test(self):
    sp = utils.PathJoin(self.tmpdir, "status")

    utils.WriteFile(sp, data="\n".join([
      "Name:   bash",
      "State:  S (sleeping)",
      "SleepAVG:       98%",
      "Pid:    22250",
      "PPid:   10858",
      "TracerPid:      0",
      "SigBlk: 0000000000010000",
      "SigIgn: 0000000000384004",
      "SigCgt: 000000004b813efb",
      "CapEff: 0000000000000000",
      ]))

    self.assert_(utils.IsProcessHandlingSignal(1234, 10, status_path=sp))

  def testNoSigCgt(self):
    sp = utils.PathJoin(self.tmpdir, "status")

    utils.WriteFile(sp, data="\n".join([
      "Name:   bash",
      ]))

    self.assertRaises(RuntimeError, utils.IsProcessHandlingSignal,
                      1234, 10, status_path=sp)

  def testNoSuchFile(self):
    sp = utils.PathJoin(self.tmpdir, "notexist")

    self.assertFalse(utils.IsProcessHandlingSignal(1234, 10, status_path=sp))

  @staticmethod
  def _TestRealProcess():
    signal.signal(signal.SIGUSR1, signal.SIG_DFL)
    if utils.IsProcessHandlingSignal(os.getpid(), signal.SIGUSR1):
      raise Exception("SIGUSR1 is handled when it should not be")

    signal.signal(signal.SIGUSR1, lambda signum, frame: None)
    if not utils.IsProcessHandlingSignal(os.getpid(), signal.SIGUSR1):
      raise Exception("SIGUSR1 is not handled when it should be")

    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    if utils.IsProcessHandlingSignal(os.getpid(), signal.SIGUSR1):
      raise Exception("SIGUSR1 is not handled when it should be")

    signal.signal(signal.SIGUSR1, signal.SIG_DFL)
    if utils.IsProcessHandlingSignal(os.getpid(), signal.SIGUSR1):
      raise Exception("SIGUSR1 is handled when it should not be")

    return True

  def testRealProcess(self):
    self.assert_(utils.RunInSeparateProcess(self._TestRealProcess))


class _PostforkProcessReadyHelper:
  """A helper to use with _postfork_fn in RunCmd.

  It makes sure a process has reached a certain state by reading from a fifo.

  @ivar write_fd: The fd number to write to

  """
  def __init__(self, timeout):
    """Initialize the helper.

    @param fifo_dir: The dir where we can create the fifo
    @param timeout: The time in seconds to wait before giving up

    """
    self.timeout = timeout
    (self.read_fd, self.write_fd) = os.pipe()

  def Ready(self, pid):
    """Waits until the process is ready.

    @param pid: The pid of the process

    """
    (read_ready, _, _) = select.select([self.read_fd], [], [], self.timeout)

    if not read_ready:
      # We hit the timeout
      raise AssertionError("Timeout %d reached while waiting for process %d"
                           " to become ready" % (self.timeout, pid))

  def Cleanup(self):
    """Cleans up the helper.

    """
    os.close(self.read_fd)
    os.close(self.write_fd)


class TestRunCmd(testutils.GanetiTestCase):
  """Testing case for the RunCmd function"""

  def setUp(self):
    testutils.GanetiTestCase.setUp(self)
    self.magic = time.ctime() + " ganeti test"
    self.fname = self._CreateTempFile()
    self.fifo_tmpdir = tempfile.mkdtemp()
    self.fifo_file = os.path.join(self.fifo_tmpdir, "ganeti_test_fifo")
    os.mkfifo(self.fifo_file)

    # If the process is not ready after 20 seconds we have bigger issues
    self.proc_ready_helper = _PostforkProcessReadyHelper(20)

  def tearDown(self):
    self.proc_ready_helper.Cleanup()
    shutil.rmtree(self.fifo_tmpdir)
    testutils.GanetiTestCase.tearDown(self)

  def testOk(self):
    """Test successful exit code"""
    result = utils.RunCmd("/bin/sh -c 'exit 0'")
    self.assertEqual(result.exit_code, 0)
    self.assertEqual(result.output, "")

  def testFail(self):
    """Test fail exit code"""
    result = utils.RunCmd("/bin/sh -c 'exit 1'")
    self.assertEqual(result.exit_code, 1)
    self.assertEqual(result.output, "")

  def testStdout(self):
    """Test standard output"""
    cmd = 'echo -n "%s"' % self.magic
    result = utils.RunCmd("/bin/sh -c '%s'" % cmd)
    self.assertEqual(result.stdout, self.magic)
    result = utils.RunCmd("/bin/sh -c '%s'" % cmd, output=self.fname)
    self.assertEqual(result.output, "")
    self.assertFileContent(self.fname, self.magic)

  def testStderr(self):
    """Test standard error"""
    cmd = 'echo -n "%s"' % self.magic
    result = utils.RunCmd("/bin/sh -c '%s' 1>&2" % cmd)
    self.assertEqual(result.stderr, self.magic)
    result = utils.RunCmd("/bin/sh -c '%s' 1>&2" % cmd, output=self.fname)
    self.assertEqual(result.output, "")
    self.assertFileContent(self.fname, self.magic)

  def testCombined(self):
    """Test combined output"""
    cmd = 'echo -n "A%s"; echo -n "B%s" 1>&2' % (self.magic, self.magic)
    expected = "A" + self.magic + "B" + self.magic
    result = utils.RunCmd("/bin/sh -c '%s'" % cmd)
    self.assertEqual(result.output, expected)
    result = utils.RunCmd("/bin/sh -c '%s'" % cmd, output=self.fname)
    self.assertEqual(result.output, "")
    self.assertFileContent(self.fname, expected)

  def testSignal(self):
    """Test signal"""
    result = utils.RunCmd(["python", "-c",
                           "import os; os.kill(os.getpid(), 15)"])
    self.assertEqual(result.signal, 15)
    self.assertEqual(result.output, "")

  def testTimeoutClean(self):
    cmd = ("trap 'exit 0' TERM; echo >&%d; read < %s" %
           (self.proc_ready_helper.write_fd, self.fifo_file))
    result = utils.RunCmd(["/bin/sh", "-c", cmd], timeout=0.2,
                          noclose_fds=[self.proc_ready_helper.write_fd],
                          _postfork_fn=self.proc_ready_helper.Ready)
    self.assertEqual(result.exit_code, 0)

  def testTimeoutKill(self):
    cmd = ["/bin/sh", "-c", "trap '' TERM; echo >&%d; read < %s" %
           (self.proc_ready_helper.write_fd, self.fifo_file)]
    timeout = 0.2
    (out, err, status, ta) = \
      utils.process._RunCmdPipe(cmd, {}, False, "/", False,
                                timeout, [self.proc_ready_helper.write_fd],
                                _linger_timeout=0.2,
                                _postfork_fn=self.proc_ready_helper.Ready)
    self.assert_(status < 0)
    self.assertEqual(-status, signal.SIGKILL)

  def testTimeoutOutputAfterTerm(self):
    cmd = ("trap 'echo sigtermed; exit 1' TERM; echo >&%d; read < %s" %
           (self.proc_ready_helper.write_fd, self.fifo_file))
    result = utils.RunCmd(["/bin/sh", "-c", cmd], timeout=0.2,
                          noclose_fds=[self.proc_ready_helper.write_fd],
                          _postfork_fn=self.proc_ready_helper.Ready)
    self.assert_(result.failed)
    self.assertEqual(result.stdout, "sigtermed\n")

  def testListRun(self):
    """Test list runs"""
    result = utils.RunCmd(["true"])
    self.assertEqual(result.signal, None)
    self.assertEqual(result.exit_code, 0)
    result = utils.RunCmd(["/bin/sh", "-c", "exit 1"])
    self.assertEqual(result.signal, None)
    self.assertEqual(result.exit_code, 1)
    result = utils.RunCmd(["echo", "-n", self.magic])
    self.assertEqual(result.signal, None)
    self.assertEqual(result.exit_code, 0)
    self.assertEqual(result.stdout, self.magic)

  def testFileEmptyOutput(self):
    """Test file output"""
    result = utils.RunCmd(["true"], output=self.fname)
    self.assertEqual(result.signal, None)
    self.assertEqual(result.exit_code, 0)
    self.assertFileContent(self.fname, "")

  def testLang(self):
    """Test locale environment"""
    old_env = os.environ.copy()
    try:
      os.environ["LANG"] = "en_US.UTF-8"
      os.environ["LC_ALL"] = "en_US.UTF-8"
      result = utils.RunCmd(["locale"])
      for line in result.output.splitlines():
        key, value = line.split("=", 1)
        # Ignore these variables, they're overridden by LC_ALL
        if key == "LANG" or key == "LANGUAGE":
          continue
        self.failIf(value and value != "C" and value != '"C"',
            "Variable %s is set to the invalid value '%s'" % (key, value))
    finally:
      os.environ = old_env

  def testDefaultCwd(self):
    """Test default working directory"""
    self.failUnlessEqual(utils.RunCmd(["pwd"]).stdout.strip(), "/")

  def testCwd(self):
    """Test default working directory"""
    self.failUnlessEqual(utils.RunCmd(["pwd"], cwd="/").stdout.strip(), "/")
    self.failUnlessEqual(utils.RunCmd(["pwd"], cwd="/tmp").stdout.strip(),
                         "/tmp")
    cwd = os.getcwd()
    self.failUnlessEqual(utils.RunCmd(["pwd"], cwd=cwd).stdout.strip(), cwd)

  def testResetEnv(self):
    """Test environment reset functionality"""
    self.failUnlessEqual(utils.RunCmd(["env"], reset_env=True).stdout.strip(),
                         "")
    self.failUnlessEqual(utils.RunCmd(["env"], reset_env=True,
                                      env={"FOO": "bar",}).stdout.strip(),
                         "FOO=bar")

  def testNoFork(self):
    """Test that nofork raise an error"""
    self.assertFalse(utils.process._no_fork)
    utils.DisableFork()
    try:
      self.assertTrue(utils.process._no_fork)
      self.assertRaises(errors.ProgrammerError, utils.RunCmd, ["true"])
    finally:
      utils.process._no_fork = False
    self.assertFalse(utils.process._no_fork)

  def testWrongParams(self):
    """Test wrong parameters"""
    self.assertRaises(errors.ProgrammerError, utils.RunCmd, ["true"],
                      output="/dev/null", interactive=True)

  def testNocloseFds(self):
    """Test selective fd retention (noclose_fds)"""
    temp = open(self.fname, "r+")
    try:
      temp.write("test")
      temp.seek(0)
      cmd = "read -u %d; echo $REPLY" % temp.fileno()
      result = utils.RunCmd(["/bin/bash", "-c", cmd])
      self.assertEqual(result.stdout.strip(), "")
      temp.seek(0)
      result = utils.RunCmd(["/bin/bash", "-c", cmd],
                            noclose_fds=[temp.fileno()])
      self.assertEqual(result.stdout.strip(), "test")
    finally:
      temp.close()


class TestRunParts(testutils.GanetiTestCase):
  """Testing case for the RunParts function"""

  def setUp(self):
    self.rundir = tempfile.mkdtemp(prefix="ganeti-test", suffix=".tmp")

  def tearDown(self):
    shutil.rmtree(self.rundir)

  def testEmpty(self):
    """Test on an empty dir"""
    self.failUnlessEqual(utils.RunParts(self.rundir, reset_env=True), [])

  def testSkipWrongName(self):
    """Test that wrong files are skipped"""
    fname = os.path.join(self.rundir, "00test.dot")
    utils.WriteFile(fname, data="")
    os.chmod(fname, stat.S_IREAD | stat.S_IEXEC)
    relname = os.path.basename(fname)
    self.failUnlessEqual(utils.RunParts(self.rundir, reset_env=True),
                         [(relname, constants.RUNPARTS_SKIP, None)])

  def testSkipNonExec(self):
    """Test that non executable files are skipped"""
    fname = os.path.join(self.rundir, "00test")
    utils.WriteFile(fname, data="")
    relname = os.path.basename(fname)
    self.failUnlessEqual(utils.RunParts(self.rundir, reset_env=True),
                         [(relname, constants.RUNPARTS_SKIP, None)])

  def testError(self):
    """Test error on a broken executable"""
    fname = os.path.join(self.rundir, "00test")
    utils.WriteFile(fname, data="")
    os.chmod(fname, stat.S_IREAD | stat.S_IEXEC)
    (relname, status, error) = utils.RunParts(self.rundir, reset_env=True)[0]
    self.failUnlessEqual(relname, os.path.basename(fname))
    self.failUnlessEqual(status, constants.RUNPARTS_ERR)
    self.failUnless(error)

  def testSorted(self):
    """Test executions are sorted"""
    files = []
    files.append(os.path.join(self.rundir, "64test"))
    files.append(os.path.join(self.rundir, "00test"))
    files.append(os.path.join(self.rundir, "42test"))

    for fname in files:
      utils.WriteFile(fname, data="")

    results = utils.RunParts(self.rundir, reset_env=True)

    for fname in sorted(files):
      self.failUnlessEqual(os.path.basename(fname), results.pop(0)[0])

  def testOk(self):
    """Test correct execution"""
    fname = os.path.join(self.rundir, "00test")
    utils.WriteFile(fname, data="#!/bin/sh\n\necho -n ciao")
    os.chmod(fname, stat.S_IREAD | stat.S_IEXEC)
    (relname, status, runresult) = \
      utils.RunParts(self.rundir, reset_env=True)[0]
    self.failUnlessEqual(relname, os.path.basename(fname))
    self.failUnlessEqual(status, constants.RUNPARTS_RUN)
    self.failUnlessEqual(runresult.stdout, "ciao")

  def testRunFail(self):
    """Test correct execution, with run failure"""
    fname = os.path.join(self.rundir, "00test")
    utils.WriteFile(fname, data="#!/bin/sh\n\nexit 1")
    os.chmod(fname, stat.S_IREAD | stat.S_IEXEC)
    (relname, status, runresult) = \
      utils.RunParts(self.rundir, reset_env=True)[0]
    self.failUnlessEqual(relname, os.path.basename(fname))
    self.failUnlessEqual(status, constants.RUNPARTS_RUN)
    self.failUnlessEqual(runresult.exit_code, 1)
    self.failUnless(runresult.failed)

  def testRunMix(self):
    files = []
    files.append(os.path.join(self.rundir, "00test"))
    files.append(os.path.join(self.rundir, "42test"))
    files.append(os.path.join(self.rundir, "64test"))
    files.append(os.path.join(self.rundir, "99test"))

    files.sort()

    # 1st has errors in execution
    utils.WriteFile(files[0], data="#!/bin/sh\n\nexit 1")
    os.chmod(files[0], stat.S_IREAD | stat.S_IEXEC)

    # 2nd is skipped
    utils.WriteFile(files[1], data="")

    # 3rd cannot execute properly
    utils.WriteFile(files[2], data="")
    os.chmod(files[2], stat.S_IREAD | stat.S_IEXEC)

    # 4th execs
    utils.WriteFile(files[3], data="#!/bin/sh\n\necho -n ciao")
    os.chmod(files[3], stat.S_IREAD | stat.S_IEXEC)

    results = utils.RunParts(self.rundir, reset_env=True)

    (relname, status, runresult) = results[0]
    self.failUnlessEqual(relname, os.path.basename(files[0]))
    self.failUnlessEqual(status, constants.RUNPARTS_RUN)
    self.failUnlessEqual(runresult.exit_code, 1)
    self.failUnless(runresult.failed)

    (relname, status, runresult) = results[1]
    self.failUnlessEqual(relname, os.path.basename(files[1]))
    self.failUnlessEqual(status, constants.RUNPARTS_SKIP)
    self.failUnlessEqual(runresult, None)

    (relname, status, runresult) = results[2]
    self.failUnlessEqual(relname, os.path.basename(files[2]))
    self.failUnlessEqual(status, constants.RUNPARTS_ERR)
    self.failUnless(runresult)

    (relname, status, runresult) = results[3]
    self.failUnlessEqual(relname, os.path.basename(files[3]))
    self.failUnlessEqual(status, constants.RUNPARTS_RUN)
    self.failUnlessEqual(runresult.output, "ciao")
    self.failUnlessEqual(runresult.exit_code, 0)
    self.failUnless(not runresult.failed)

  def testMissingDirectory(self):
    nosuchdir = utils.PathJoin(self.rundir, "no/such/directory")
    self.assertEqual(utils.RunParts(nosuchdir), [])


class TestStartDaemon(testutils.GanetiTestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp(prefix="ganeti-test")
    self.tmpfile = os.path.join(self.tmpdir, "test")

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def testShell(self):
    utils.StartDaemon("echo Hello World > %s" % self.tmpfile)
    self._wait(self.tmpfile, 60.0, "Hello World")

  def testShellOutput(self):
    utils.StartDaemon("echo Hello World", output=self.tmpfile)
    self._wait(self.tmpfile, 60.0, "Hello World")

  def testNoShellNoOutput(self):
    utils.StartDaemon(["pwd"])

  def testNoShellNoOutputTouch(self):
    testfile = os.path.join(self.tmpdir, "check")
    self.failIf(os.path.exists(testfile))
    utils.StartDaemon(["touch", testfile])
    self._wait(testfile, 60.0, "")

  def testNoShellOutput(self):
    utils.StartDaemon(["pwd"], output=self.tmpfile)
    self._wait(self.tmpfile, 60.0, "/")

  def testNoShellOutputCwd(self):
    utils.StartDaemon(["pwd"], output=self.tmpfile, cwd=os.getcwd())
    self._wait(self.tmpfile, 60.0, os.getcwd())

  def testShellEnv(self):
    utils.StartDaemon("echo \"$GNT_TEST_VAR\"", output=self.tmpfile,
                      env={ "GNT_TEST_VAR": "Hello World", })
    self._wait(self.tmpfile, 60.0, "Hello World")

  def testNoShellEnv(self):
    utils.StartDaemon(["printenv", "GNT_TEST_VAR"], output=self.tmpfile,
                      env={ "GNT_TEST_VAR": "Hello World", })
    self._wait(self.tmpfile, 60.0, "Hello World")

  def testOutputFd(self):
    fd = os.open(self.tmpfile, os.O_WRONLY | os.O_CREAT)
    try:
      utils.StartDaemon(["pwd"], output_fd=fd, cwd=os.getcwd())
    finally:
      os.close(fd)
    self._wait(self.tmpfile, 60.0, os.getcwd())

  def testPid(self):
    pid = utils.StartDaemon("echo $$ > %s" % self.tmpfile)
    self._wait(self.tmpfile, 60.0, str(pid))

  def testPidFile(self):
    pidfile = os.path.join(self.tmpdir, "pid")
    checkfile = os.path.join(self.tmpdir, "abort")

    pid = utils.StartDaemon("while sleep 5; do :; done", pidfile=pidfile,
                            output=self.tmpfile)
    try:
      fd = os.open(pidfile, os.O_RDONLY)
      try:
        # Check file is locked
        self.assertRaises(errors.LockError, utils.LockFile, fd)

        pidtext = os.read(fd, 100)
      finally:
        os.close(fd)

      self.assertEqual(int(pidtext.strip()), pid)

      self.assert_(utils.IsProcessAlive(pid))
    finally:
      # No matter what happens, kill daemon
      utils.KillProcess(pid, timeout=5.0, waitpid=False)
      self.failIf(utils.IsProcessAlive(pid))

    self.assertEqual(utils.ReadFile(self.tmpfile), "")

  def _wait(self, path, timeout, expected):
    # Due to the asynchronous nature of daemon processes, polling is necessary.
    # A timeout makes sure the test doesn't hang forever.
    def _CheckFile():
      if not (os.path.isfile(path) and
              utils.ReadFile(path).strip() == expected):
        raise utils.RetryAgain()

    try:
      utils.Retry(_CheckFile, (0.01, 1.5, 1.0), timeout)
    except utils.RetryTimeout:
      self.fail("Apparently the daemon didn't run in %s seconds and/or"
                " didn't write the correct output" % timeout)

  def testError(self):
    self.assertRaises(errors.OpExecError, utils.StartDaemon,
                      ["./does-NOT-EXIST/here/0123456789"])
    self.assertRaises(errors.OpExecError, utils.StartDaemon,
                      ["./does-NOT-EXIST/here/0123456789"],
                      output=os.path.join(self.tmpdir, "DIR/NOT/EXIST"))
    self.assertRaises(errors.OpExecError, utils.StartDaemon,
                      ["./does-NOT-EXIST/here/0123456789"],
                      cwd=os.path.join(self.tmpdir, "DIR/NOT/EXIST"))
    self.assertRaises(errors.OpExecError, utils.StartDaemon,
                      ["./does-NOT-EXIST/here/0123456789"],
                      output=os.path.join(self.tmpdir, "DIR/NOT/EXIST"))

    fd = os.open(self.tmpfile, os.O_WRONLY | os.O_CREAT)
    try:
      self.assertRaises(errors.ProgrammerError, utils.StartDaemon,
                        ["./does-NOT-EXIST/here/0123456789"],
                        output=self.tmpfile, output_fd=fd)
    finally:
      os.close(fd)


class RunInSeparateProcess(unittest.TestCase):
  def test(self):
    for exp in [True, False]:
      def _child():
        return exp

      self.assertEqual(exp, utils.RunInSeparateProcess(_child))

  def testArgs(self):
    for arg in [0, 1, 999, "Hello World", (1, 2, 3)]:
      def _child(carg1, carg2):
        return carg1 == "Foo" and carg2 == arg

      self.assert_(utils.RunInSeparateProcess(_child, "Foo", arg))

  def testPid(self):
    parent_pid = os.getpid()

    def _check():
      return os.getpid() == parent_pid

    self.failIf(utils.RunInSeparateProcess(_check))

  def testSignal(self):
    def _kill():
      os.kill(os.getpid(), signal.SIGTERM)

    self.assertRaises(errors.GenericError,
                      utils.RunInSeparateProcess, _kill)

  def testException(self):
    def _exc():
      raise errors.GenericError("This is a test")

    self.assertRaises(errors.GenericError,
                      utils.RunInSeparateProcess, _exc)


if __name__ == "__main__":
  testutils.GanetiTestProgram()
