#!/usr/bin/env python2
#

# Copyright (C) 2006, 2007, 2010 Google Inc.
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


"""Script for unittesting the bdev module"""


import os
import unittest

from ganeti import bdev
from ganeti import errors

import testutils


class TestBaseDRBD(testutils.GanetiTestCase):
  def testGetVersion(self):
    data = [
      ["version: 8.0.12 (api:76/proto:86-91)"],
      ["version: 8.2.7 (api:88/proto:0-100)"],
      ["version: 8.3.7.49 (api:188/proto:13-191)"],
    ]
    result = [
      {
      "k_major": 8,
      "k_minor": 0,
      "k_point": 12,
      "api": 76,
      "proto": 86,
      "proto2": "91",
      },
      {
      "k_major": 8,
      "k_minor": 2,
      "k_point": 7,
      "api": 88,
      "proto": 0,
      "proto2": "100",
      },
      {
      "k_major": 8,
      "k_minor": 3,
      "k_point": 7,
      "api": 188,
      "proto": 13,
      "proto2": "191",
      }
    ]
    for d,r in zip(data, result):
      self.assertEqual(bdev.BaseDRBD._GetVersion(d), r)


class TestDRBD8Runner(testutils.GanetiTestCase):
  """Testing case for DRBD8"""

  @staticmethod
  def _has_disk(data, dname, mname):
    """Check local disk corectness"""
    retval = (
      "local_dev" in data and
      data["local_dev"] == dname and
      "meta_dev" in data and
      data["meta_dev"] == mname and
      "meta_index" in data and
      data["meta_index"] == 0
      )
    return retval

  @staticmethod
  def _has_net(data, local, remote):
    """Check network connection parameters"""
    retval = (
      "local_addr" in data and
      data["local_addr"] == local and
      "remote_addr" in data and
      data["remote_addr"] == remote
      )
    return retval

  def testParserCreation(self):
    """Test drbdsetup show parser creation"""
    bdev.DRBD8._GetShowParser()

  def testParser80(self):
    """Test drbdsetup show parser for disk and network version 8.0"""
    data = self._ReadTestData("bdev-drbd-8.0.txt")
    result = bdev.DRBD8._GetDevInfo(data)
    self.failUnless(self._has_disk(result, "/dev/xenvg/test.data",
                                   "/dev/xenvg/test.meta"),
                    "Wrong local disk info")
    self.failUnless(self._has_net(result, ("192.0.2.1", 11000),
                                  ("192.0.2.2", 11000)),
                    "Wrong network info (8.0.x)")

  def testParser83(self):
    """Test drbdsetup show parser for disk and network version 8.3"""
    data = self._ReadTestData("bdev-drbd-8.3.txt")
    result = bdev.DRBD8._GetDevInfo(data)
    self.failUnless(self._has_disk(result, "/dev/xenvg/test.data",
                                   "/dev/xenvg/test.meta"),
                    "Wrong local disk info")
    self.failUnless(self._has_net(result, ("192.0.2.1", 11000),
                                  ("192.0.2.2", 11000)),
                    "Wrong network info (8.0.x)")

  def testParserNetIP4(self):
    """Test drbdsetup show parser for IPv4 network"""
    data = self._ReadTestData("bdev-drbd-net-ip4.txt")
    result = bdev.DRBD8._GetDevInfo(data)
    self.failUnless(("local_dev" not in result and
                     "meta_dev" not in result and
                     "meta_index" not in result),
                    "Should not find local disk info")
    self.failUnless(self._has_net(result, ("192.0.2.1", 11002),
                                  ("192.0.2.2", 11002)),
                    "Wrong network info (IPv4)")

  def testParserNetIP6(self):
    """Test drbdsetup show parser for IPv6 network"""
    data = self._ReadTestData("bdev-drbd-net-ip6.txt")
    result = bdev.DRBD8._GetDevInfo(data)
    self.failUnless(("local_dev" not in result and
                     "meta_dev" not in result and
                     "meta_index" not in result),
                    "Should not find local disk info")
    self.failUnless(self._has_net(result, ("2001:db8:65::1", 11048),
                                  ("2001:db8:66::1", 11048)),
                    "Wrong network info (IPv6)")

  def testParserDisk(self):
    """Test drbdsetup show parser for disk"""
    data = self._ReadTestData("bdev-drbd-disk.txt")
    result = bdev.DRBD8._GetDevInfo(data)
    self.failUnless(self._has_disk(result, "/dev/xenvg/test.data",
                                   "/dev/xenvg/test.meta"),
                    "Wrong local disk info")
    self.failUnless(("local_addr" not in result and
                     "remote_addr" not in result),
                    "Should not find network info")


class TestDRBD8Status(testutils.GanetiTestCase):
  """Testing case for DRBD8 /proc status"""

  def setUp(self):
    """Read in txt data"""
    testutils.GanetiTestCase.setUp(self)
    proc_data = self._TestDataFilename("proc_drbd8.txt")
    proc80e_data = self._TestDataFilename("proc_drbd80-emptyline.txt")
    proc83_data = self._TestDataFilename("proc_drbd83.txt")
    self.proc_data = bdev.DRBD8._GetProcData(filename=proc_data)
    self.proc80e_data = bdev.DRBD8._GetProcData(filename=proc80e_data)
    self.proc83_data = bdev.DRBD8._GetProcData(filename=proc83_data)
    self.mass_data = bdev.DRBD8._MassageProcData(self.proc_data)
    self.mass80e_data = bdev.DRBD8._MassageProcData(self.proc80e_data)
    self.mass83_data = bdev.DRBD8._MassageProcData(self.proc83_data)

  def testIOErrors(self):
    """Test handling of errors while reading the proc file."""
    temp_file = self._CreateTempFile()
    os.unlink(temp_file)
    self.failUnlessRaises(errors.BlockDeviceError,
                          bdev.DRBD8._GetProcData, filename=temp_file)

  def testHelper(self):
    """Test reading usermode_helper in /sys."""
    sys_drbd_helper = self._TestDataFilename("sys_drbd_usermode_helper.txt")
    drbd_helper = bdev.DRBD8.GetUsermodeHelper(filename=sys_drbd_helper)
    self.failUnlessEqual(drbd_helper, "/bin/true")

  def testHelperIOErrors(self):
    """Test handling of errors while reading usermode_helper in /sys."""
    temp_file = self._CreateTempFile()
    os.unlink(temp_file)
    self.failUnlessRaises(errors.BlockDeviceError,
                          bdev.DRBD8.GetUsermodeHelper, filename=temp_file)

  def testMinorNotFound(self):
    """Test not-found-minor in /proc"""
    self.failUnless(9 not in self.mass_data)
    self.failUnless(9 not in self.mass83_data)
    self.failUnless(3 not in self.mass80e_data)

  def testLineNotMatch(self):
    """Test wrong line passed to DRBD8Status"""
    self.assertRaises(errors.BlockDeviceError, bdev.DRBD8Status, "foo")

  def testMinor0(self):
    """Test connected, primary device"""
    for data in [self.mass_data, self.mass83_data]:
      stats = bdev.DRBD8Status(data[0])
      self.failUnless(stats.is_in_use)
      self.failUnless(stats.is_connected and stats.is_primary and
                      stats.peer_secondary and stats.is_disk_uptodate)

  def testMinor1(self):
    """Test connected, secondary device"""
    for data in [self.mass_data, self.mass83_data]:
      stats = bdev.DRBD8Status(data[1])
      self.failUnless(stats.is_in_use)
      self.failUnless(stats.is_connected and stats.is_secondary and
                      stats.peer_primary and stats.is_disk_uptodate)

  def testMinor2(self):
    """Test unconfigured device"""
    for data in [self.mass_data, self.mass83_data, self.mass80e_data]:
      stats = bdev.DRBD8Status(data[2])
      self.failIf(stats.is_in_use)

  def testMinor4(self):
    """Test WFconn device"""
    for data in [self.mass_data, self.mass83_data]:
      stats = bdev.DRBD8Status(data[4])
      self.failUnless(stats.is_in_use)
      self.failUnless(stats.is_wfconn and stats.is_primary and
                      stats.rrole == 'Unknown' and
                      stats.is_disk_uptodate)

  def testMinor6(self):
    """Test diskless device"""
    for data in [self.mass_data, self.mass83_data]:
      stats = bdev.DRBD8Status(data[6])
      self.failUnless(stats.is_in_use)
      self.failUnless(stats.is_connected and stats.is_secondary and
                      stats.peer_primary and stats.is_diskless)

  def testMinor8(self):
    """Test standalone device"""
    for data in [self.mass_data, self.mass83_data]:
      stats = bdev.DRBD8Status(data[8])
      self.failUnless(stats.is_in_use)
      self.failUnless(stats.is_standalone and
                      stats.rrole == 'Unknown' and
                      stats.is_disk_uptodate)

if __name__ == '__main__':
  testutils.GanetiTestProgram()
