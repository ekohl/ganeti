#!/usr/bin/env python2
#

# Copyright (C) 2010 Google Inc.
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


"""Script for testing tools/cfgupgrade"""

import os
import sys
import unittest
import shutil
import tempfile
import operator

from ganeti import constants
from ganeti import utils
from ganeti import errors
from ganeti import serializer
from ganeti import netutils

import testutils


def _RunUpgrade(path, dry_run, no_verify, ignore_hostname=True):
  cmd = [sys.executable, "%s/tools/cfgupgrade" % testutils.GetSourceDir(),
         "--debug", "--force", "--path=%s" % path]

  if ignore_hostname:
    cmd.append("--ignore-hostname")
  if dry_run:
    cmd.append("--dry-run")
  if no_verify:
    cmd.append("--no-verify")

  result = utils.RunCmd(cmd, cwd=os.getcwd())
  if result.failed:
    raise Exception("cfgupgrade failed: %s, output %r" %
                    (result.fail_reason, result.output))


class TestCfgupgrade(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()

    self.config_path = utils.PathJoin(self.tmpdir, "config.data")
    self.noded_cert_path = utils.PathJoin(self.tmpdir, "server.pem")
    self.rapi_cert_path = utils.PathJoin(self.tmpdir, "rapi.pem")
    self.rapi_users_path = utils.PathJoin(self.tmpdir, "rapi", "users")
    self.rapi_users_path_pre24 = utils.PathJoin(self.tmpdir, "rapi_users")
    self.known_hosts_path = utils.PathJoin(self.tmpdir, "known_hosts")
    self.confd_hmac_path = utils.PathJoin(self.tmpdir, "hmac.key")
    self.cds_path = utils.PathJoin(self.tmpdir, "cluster-domain-secret")
    self.ss_master_node_path = utils.PathJoin(self.tmpdir, "ssconf_master_node")

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def _LoadConfig(self):
    return serializer.LoadJson(utils.ReadFile(self.config_path))

  def _CreateValidConfigDir(self):
    utils.WriteFile(self.noded_cert_path, data="")
    utils.WriteFile(self.known_hosts_path, data="")
    utils.WriteFile(self.ss_master_node_path,
                    data="node.has.another.name.example.net")

  def testNoConfigDir(self):
    self.assertFalse(utils.ListVisibleFiles(self.tmpdir))
    self.assertRaises(Exception, _RunUpgrade, self.tmpdir, False, True)
    self.assertRaises(Exception, _RunUpgrade, self.tmpdir, True, True)

  def testWrongHostname(self):
    self._CreateValidConfigDir()

    utils.WriteFile(self.config_path, data=serializer.DumpJson({
      "version": constants.CONFIG_VERSION,
      "cluster": {},
      }))

    hostname = netutils.GetHostname().name
    assert hostname != utils.ReadOneLineFile(self.ss_master_node_path)

    self.assertRaises(Exception, _RunUpgrade, self.tmpdir, False, True,
                      ignore_hostname=False)

  def testCorrectHostname(self):
    self._CreateValidConfigDir()

    utils.WriteFile(self.config_path, data=serializer.DumpJson({
      "version": constants.CONFIG_VERSION,
      "cluster": {},
      }))

    utils.WriteFile(self.ss_master_node_path,
                    data="%s\n" % netutils.GetHostname().name)

    _RunUpgrade(self.tmpdir, False, True, ignore_hostname=False)

  def testInconsistentConfig(self):
    self._CreateValidConfigDir()
    # There should be no "config_version"
    cfg = {
      "version": 0,
      "cluster": {
        "config_version": 0,
        },
      }
    utils.WriteFile(self.config_path, data=serializer.DumpJson(cfg))
    self.assertRaises(Exception, _RunUpgrade, self.tmpdir, False, True)

  def testInvalidConfig(self):
    self._CreateValidConfigDir()
    # Missing version from config
    utils.WriteFile(self.config_path, data=serializer.DumpJson({}))
    self.assertRaises(Exception, _RunUpgrade, self.tmpdir, False, True)

  def _TestSimpleUpgrade(self, from_version, dry_run):
    cfg = {
      "version": from_version,
      "cluster": {},
      }
    self._CreateValidConfigDir()
    utils.WriteFile(self.config_path, data=serializer.DumpJson(cfg))

    self.assertFalse(os.path.isfile(self.rapi_cert_path))
    self.assertFalse(os.path.isfile(self.confd_hmac_path))
    self.assertFalse(os.path.isfile(self.cds_path))

    _RunUpgrade(self.tmpdir, dry_run, True)

    if dry_run:
      expversion = from_version
      checkfn = operator.not_
    else:
      expversion = constants.CONFIG_VERSION
      checkfn = operator.truth

    self.assert_(checkfn(os.path.isfile(self.rapi_cert_path)))
    self.assert_(checkfn(os.path.isfile(self.confd_hmac_path)))
    self.assert_(checkfn(os.path.isfile(self.cds_path)))

    newcfg = self._LoadConfig()
    self.assertEqual(newcfg["version"], expversion)

  def testRapiUsers(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))
    self.assertFalse(os.path.exists(os.path.dirname(self.rapi_users_path)))

    utils.WriteFile(self.rapi_users_path_pre24, data="some user\n")
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), False)

    self.assertTrue(os.path.isdir(os.path.dirname(self.rapi_users_path)))
    self.assert_(os.path.islink(self.rapi_users_path_pre24))
    self.assert_(os.path.isfile(self.rapi_users_path))
    self.assertEqual(os.readlink(self.rapi_users_path_pre24),
                     self.rapi_users_path)
    for path in [self.rapi_users_path, self.rapi_users_path_pre24]:
      self.assertEqual(utils.ReadFile(path), "some user\n")

  def testRapiUsers24AndAbove(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    os.mkdir(os.path.dirname(self.rapi_users_path))
    utils.WriteFile(self.rapi_users_path, data="other user\n")
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), False)

    self.assert_(os.path.islink(self.rapi_users_path_pre24))
    self.assert_(os.path.isfile(self.rapi_users_path))
    self.assertEqual(os.readlink(self.rapi_users_path_pre24),
                     self.rapi_users_path)
    for path in [self.rapi_users_path, self.rapi_users_path_pre24]:
      self.assertEqual(utils.ReadFile(path), "other user\n")

  def testRapiUsersExistingSymlink(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    os.mkdir(os.path.dirname(self.rapi_users_path))
    os.symlink(self.rapi_users_path, self.rapi_users_path_pre24)
    utils.WriteFile(self.rapi_users_path, data="hello world\n")

    self._TestSimpleUpgrade(constants.BuildVersion(2, 2, 0), False)

    self.assert_(os.path.isfile(self.rapi_users_path) and
                 not os.path.islink(self.rapi_users_path))
    self.assert_(os.path.islink(self.rapi_users_path_pre24))
    self.assertEqual(os.readlink(self.rapi_users_path_pre24),
                     self.rapi_users_path)
    for path in [self.rapi_users_path, self.rapi_users_path_pre24]:
      self.assertEqual(utils.ReadFile(path), "hello world\n")

  def testRapiUsersExistingTarget(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    os.mkdir(os.path.dirname(self.rapi_users_path))
    utils.WriteFile(self.rapi_users_path, data="other user\n")
    utils.WriteFile(self.rapi_users_path_pre24, data="hello world\n")

    self.assertRaises(Exception, self._TestSimpleUpgrade,
                      constants.BuildVersion(2, 2, 0), False)

    for path in [self.rapi_users_path, self.rapi_users_path_pre24]:
      self.assert_(os.path.isfile(path) and not os.path.islink(path))
    self.assertEqual(utils.ReadFile(self.rapi_users_path), "other user\n")
    self.assertEqual(utils.ReadFile(self.rapi_users_path_pre24),
                     "hello world\n")

  def testRapiUsersDryRun(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    utils.WriteFile(self.rapi_users_path_pre24, data="some user\n")
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), True)

    self.assertFalse(os.path.isdir(os.path.dirname(self.rapi_users_path)))
    self.assertTrue(os.path.isfile(self.rapi_users_path_pre24) and
                    not os.path.islink(self.rapi_users_path_pre24))
    self.assertFalse(os.path.exists(self.rapi_users_path))

  def testRapiUsers24AndAboveDryRun(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    os.mkdir(os.path.dirname(self.rapi_users_path))
    utils.WriteFile(self.rapi_users_path, data="other user\n")
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), True)

    self.assertTrue(os.path.isfile(self.rapi_users_path) and
                    not os.path.islink(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))
    self.assertEqual(utils.ReadFile(self.rapi_users_path), "other user\n")

  def testRapiUsersExistingSymlinkDryRun(self):
    self.assertFalse(os.path.exists(self.rapi_users_path))
    self.assertFalse(os.path.exists(self.rapi_users_path_pre24))

    os.mkdir(os.path.dirname(self.rapi_users_path))
    os.symlink(self.rapi_users_path, self.rapi_users_path_pre24)
    utils.WriteFile(self.rapi_users_path, data="hello world\n")

    self._TestSimpleUpgrade(constants.BuildVersion(2, 2, 0), True)

    self.assertTrue(os.path.islink(self.rapi_users_path_pre24))
    self.assertTrue(os.path.isfile(self.rapi_users_path) and
                    not os.path.islink(self.rapi_users_path))
    self.assertEqual(os.readlink(self.rapi_users_path_pre24),
                     self.rapi_users_path)
    for path in [self.rapi_users_path, self.rapi_users_path_pre24]:
      self.assertEqual(utils.ReadFile(path), "hello world\n")

  def testUpgradeFrom_2_0(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 0, 0), False)

  def testUpgradeFrom_2_1(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 1, 0), False)

  def testUpgradeFrom_2_2(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 2, 0), False)

  def testUpgradeFrom_2_3(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), False)

  def testUpgradeFrom_2_4(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 4, 0), False)

  def testUpgradeCurrent(self):
    self._TestSimpleUpgrade(constants.CONFIG_VERSION, False)

  def testUpgradeDryRunFrom_2_0(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 0, 0), True)

  def testUpgradeDryRunFrom_2_1(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 1, 0), True)

  def testUpgradeDryRunFrom_2_2(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 2, 0), True)

  def testUpgradeDryRunFrom_2_3(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 3, 0), True)

  def testUpgradeDryRunFrom_2_4(self):
    self._TestSimpleUpgrade(constants.BuildVersion(2, 4, 0), True)

  def testUpgradeCurrentDryRun(self):
    self._TestSimpleUpgrade(constants.CONFIG_VERSION, True)


if __name__ == "__main__":
  testutils.GanetiTestProgram()
