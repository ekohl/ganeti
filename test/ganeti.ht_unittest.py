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


"""Script for testing ganeti.ht"""

import unittest

from ganeti import ht

import testutils


class TestTypeChecks(unittest.TestCase):
  def testNone(self):
    self.assertFalse(ht.TNotNone(None))
    self.assertTrue(ht.TNone(None))

    for val in [0, True, "", "Hello World", [], range(5)]:
      self.assertTrue(ht.TNotNone(val))
      self.assertFalse(ht.TNone(val))

  def testBool(self):
    self.assertTrue(ht.TBool(True))
    self.assertTrue(ht.TBool(False))

    for val in [0, None, "", [], "Hello"]:
      self.assertFalse(ht.TBool(val))

    for val in [True, -449, 1, 3, "x", "abc", [1, 2]]:
      self.assertTrue(ht.TTrue(val))

    for val in [False, 0, None, []]:
      self.assertFalse(ht.TTrue(val))

  def testInt(self):
    for val in [-100, -3, 0, 16, 128, 923874]:
      self.assertTrue(ht.TInt(val))

    for val in [False, True, None, "", [], "Hello", 0.0, 0.23, -3818.163]:
      self.assertFalse(ht.TInt(val))

    for val in range(0, 100, 4):
      self.assertTrue(ht.TPositiveInt(val))
      neg = -(val + 1)
      self.assertFalse(ht.TPositiveInt(neg))
      self.assertFalse(ht.TStrictPositiveInt(neg))

      self.assertFalse(ht.TPositiveInt(0.1 + val))
      self.assertFalse(ht.TStrictPositiveInt(0.1 + val))

    for val in [0, 0.1, 0.9, -0.3]:
      self.assertFalse(ht.TStrictPositiveInt(val))

    for val in range(1, 100, 4):
      self.assertTrue(ht.TStrictPositiveInt(val))
      self.assertFalse(ht.TStrictPositiveInt(0.1 + val))

  def testFloat(self):
    for val in [-100.21, -3.0, 0.0, 16.12, 128.3433, 923874.928]:
      self.assertTrue(ht.TFloat(val))

    for val in [False, True, None, "", [], "Hello", 0, 28, -1, -3281]:
      self.assertFalse(ht.TFloat(val))

  def testString(self):
    for val in ["", "abc", "Hello World", "123",
                u"", u"\u272C", u"abc"]:
      self.assertTrue(ht.TString(val))

    for val in [False, True, None, [], 0, 1, 5, -193, 93.8582]:
      self.assertFalse(ht.TString(val))

  def testElemOf(self):
    fn = ht.TElemOf(range(10))
    self.assertTrue(fn(0))
    self.assertTrue(fn(3))
    self.assertTrue(fn(9))
    self.assertFalse(fn(-1))
    self.assertFalse(fn(100))

    fn = ht.TElemOf([])
    self.assertFalse(fn(0))
    self.assertFalse(fn(100))
    self.assertFalse(fn(True))

    fn = ht.TElemOf(["Hello", "World"])
    self.assertTrue(fn("Hello"))
    self.assertTrue(fn("World"))
    self.assertFalse(fn("e"))

  def testList(self):
    for val in [[], range(10), ["Hello", "World", "!"]]:
      self.assertTrue(ht.TList(val))

    for val in [False, True, None, {}, 0, 1, 5, -193, 93.8582]:
      self.assertFalse(ht.TList(val))

  def testDict(self):
    for val in [{}, dict.fromkeys(range(10)), {"Hello": [], "World": "!"}]:
      self.assertTrue(ht.TDict(val))

    for val in [False, True, None, [], 0, 1, 5, -193, 93.8582]:
      self.assertFalse(ht.TDict(val))

  def testIsLength(self):
    fn = ht.TIsLength(10)
    self.assertTrue(fn(range(10)))
    self.assertFalse(fn(range(1)))
    self.assertFalse(fn(range(100)))

  def testAnd(self):
    fn = ht.TAnd(ht.TNotNone, ht.TString)
    self.assertTrue(fn(""))
    self.assertFalse(fn(1))
    self.assertFalse(fn(None))

  def testOr(self):
    fn = ht.TOr(ht.TNone, ht.TAnd(ht.TString, ht.TIsLength(5)))
    self.assertTrue(fn("12345"))
    self.assertTrue(fn(None))
    self.assertFalse(fn(1))
    self.assertFalse(fn(""))
    self.assertFalse(fn("abc"))

  def testMap(self):
    self.assertTrue(ht.TMap(str, ht.TString)(123))
    self.assertTrue(ht.TMap(int, ht.TInt)("9999"))
    self.assertFalse(ht.TMap(lambda x: x + 100, ht.TString)(123))

  def testNonEmptyString(self):
    self.assertTrue(ht.TNonEmptyString("xyz"))
    self.assertTrue(ht.TNonEmptyString("Hello World"))
    self.assertFalse(ht.TNonEmptyString(""))
    self.assertFalse(ht.TNonEmptyString(None))
    self.assertFalse(ht.TNonEmptyString([]))

  def testMaybeString(self):
    self.assertTrue(ht.TMaybeString("xyz"))
    self.assertTrue(ht.TMaybeString("Hello World"))
    self.assertTrue(ht.TMaybeString(None))
    self.assertFalse(ht.TMaybeString(""))
    self.assertFalse(ht.TMaybeString([]))

  def testMaybeBool(self):
    self.assertTrue(ht.TMaybeBool(False))
    self.assertTrue(ht.TMaybeBool(True))
    self.assertTrue(ht.TMaybeBool(None))
    self.assertFalse(ht.TMaybeBool([]))
    self.assertFalse(ht.TMaybeBool("0"))
    self.assertFalse(ht.TMaybeBool("False"))

  def testListOf(self):
    fn = ht.TListOf(ht.TNonEmptyString)
    self.assertTrue(fn([]))
    self.assertTrue(fn(["x"]))
    self.assertTrue(fn(["Hello", "World"]))
    self.assertFalse(fn(None))
    self.assertFalse(fn(False))
    self.assertFalse(fn(range(3)))
    self.assertFalse(fn(["x", None]))

  def testDictOf(self):
    fn = ht.TDictOf(ht.TNonEmptyString, ht.TInt)
    self.assertTrue(fn({}))
    self.assertTrue(fn({"x": 123, "y": 999}))
    self.assertFalse(fn(None))
    self.assertFalse(fn({1: "x"}))
    self.assertFalse(fn({"x": ""}))
    self.assertFalse(fn({"x": None}))
    self.assertFalse(fn({"": 8234}))

  def testStrictDictRequireAllExclusive(self):
    fn = ht.TStrictDict(True, True, { "a": ht.TInt, })
    self.assertFalse(fn(1))
    self.assertFalse(fn(None))
    self.assertFalse(fn({}))
    self.assertFalse(fn({"a": "Hello", }))
    self.assertFalse(fn({"unknown": 999,}))
    self.assertFalse(fn({"unknown": None,}))

    self.assertTrue(fn({"a": 123, }))
    self.assertTrue(fn({"a": -5, }))

    fn = ht.TStrictDict(True, True, { "a": ht.TInt, "x": ht.TString, })
    self.assertFalse(fn({}))
    self.assertFalse(fn({"a": -5, }))
    self.assertTrue(fn({"a": 123, "x": "", }))
    self.assertFalse(fn({"a": 123, "x": None, }))

  def testStrictDictExclusive(self):
    fn = ht.TStrictDict(False, True, { "a": ht.TInt, "b": ht.TList, })
    self.assertTrue(fn({}))
    self.assertTrue(fn({"a": 123, }))
    self.assertTrue(fn({"b": range(4), }))
    self.assertFalse(fn({"b": 123, }))

    self.assertFalse(fn({"foo": {}, }))
    self.assertFalse(fn({"bar": object(), }))

  def testStrictDictRequireAll(self):
    fn = ht.TStrictDict(True, False, { "a": ht.TInt, "m": ht.TInt, })
    self.assertTrue(fn({"a": 1, "m": 2, "bar": object(), }))
    self.assertFalse(fn({}))
    self.assertFalse(fn({"a": 1, "bar": object(), }))
    self.assertFalse(fn({"a": 1, "m": [], "bar": object(), }))

  def testStrictDict(self):
    fn = ht.TStrictDict(False, False, { "a": ht.TInt, })
    self.assertTrue(fn({}))
    self.assertFalse(fn({"a": ""}))
    self.assertTrue(fn({"a": 11}))
    self.assertTrue(fn({"other": 11}))
    self.assertTrue(fn({"other": object()}))

  def testJobId(self):
    for i in [0, 1, 4395, 2347625220]:
      self.assertTrue(ht.TJobId(i))
      self.assertTrue(ht.TJobId(str(i)))
      self.assertFalse(ht.TJobId(-(i + 1)))

    for i in ["", "-", ".", ",", "a", "99j", "job-123", "\t", " 83 ",
              None, [], {}, object()]:
      self.assertFalse(ht.TJobId(i))

  def testItems(self):
    self.assertRaises(AssertionError, ht.TItems, [])

    fn = ht.TItems([ht.TString])
    self.assertFalse(fn([0]))
    self.assertFalse(fn([None]))
    self.assertTrue(fn(["Hello"]))
    self.assertTrue(fn(["Hello", "World"]))
    self.assertTrue(fn(["Hello", 0, 1, 2, "anything"]))

    fn = ht.TItems([ht.TAny, ht.TInt, ht.TAny])
    self.assertTrue(fn(["Hello", 0, []]))
    self.assertTrue(fn(["Hello", 893782]))
    self.assertTrue(fn([{}, -938210858947, None]))
    self.assertFalse(fn(["Hello", []]))


if __name__ == "__main__":
  testutils.GanetiTestProgram()
