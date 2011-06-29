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


"""Script for testing ganeti.utils.algo"""

import unittest
import random
import operator

from ganeti import constants
from ganeti.utils import algo

import testutils


class TestUniqueSequence(unittest.TestCase):
  """Test case for UniqueSequence"""

  def _test(self, input, expected):
    self.assertEqual(algo.UniqueSequence(input), expected)

  def runTest(self):
    # Ordered input
    self._test([1, 2, 3], [1, 2, 3])
    self._test([1, 1, 2, 2, 3, 3], [1, 2, 3])
    self._test([1, 2, 2, 3], [1, 2, 3])
    self._test([1, 2, 3, 3], [1, 2, 3])

    # Unordered input
    self._test([1, 2, 3, 1, 2, 3], [1, 2, 3])
    self._test([1, 1, 2, 3, 3, 1, 2], [1, 2, 3])

    # Strings
    self._test(["a", "a"], ["a"])
    self._test(["a", "b"], ["a", "b"])
    self._test(["a", "b", "a"], ["a", "b"])


class TestFindDuplicates(unittest.TestCase):
  """Test case for FindDuplicates"""

  def _Test(self, seq, expected):
    result = algo.FindDuplicates(seq)
    self.assertEqual(result, algo.UniqueSequence(result))
    self.assertEqual(set(result), set(expected))

  def test(self):
    self._Test([], [])
    self._Test([1, 2, 3], [])
    self._Test([9, 8, 8, 0, 5, 1, 7, 0, 6, 7], [8, 0, 7])
    for exp in [[1, 2, 3], [3, 2, 1]]:
      self._Test([1, 1, 2, 2, 3, 3], exp)

    self._Test(["A", "a", "B"], [])
    self._Test(["a", "A", "a", "B"], ["a"])
    self._Test("Hello World out there!", ["e", " ", "o", "r", "t", "l"])

    self._Test(self._Gen(False), [])
    self._Test(self._Gen(True), range(1, 10))

  @staticmethod
  def _Gen(dup):
    for i in range(10):
      yield i
      if dup:
        for _ in range(i):
          yield i


class TestNiceSort(unittest.TestCase):
  def test(self):
    self.assertEqual(algo.NiceSort([]), [])
    self.assertEqual(algo.NiceSort(["foo"]), ["foo"])
    self.assertEqual(algo.NiceSort(["bar", ""]), ["", "bar"])
    self.assertEqual(algo.NiceSort([",", "."]), [",", "."])
    self.assertEqual(algo.NiceSort(["0.1", "0.2"]), ["0.1", "0.2"])
    self.assertEqual(algo.NiceSort(["0;099", "0,099", "0.1", "0.2"]),
                     ["0,099", "0.1", "0.2", "0;099"])

    data = ["a0", "a1", "a99", "a20", "a2", "b10", "b70", "b00", "0000"]
    self.assertEqual(algo.NiceSort(data),
                     ["0000", "a0", "a1", "a2", "a20", "a99",
                      "b00", "b10", "b70"])

    data = ["a0-0", "a1-0", "a99-10", "a20-3", "a0-4", "a99-3", "a09-2",
            "Z", "a9-1", "A", "b"]
    self.assertEqual(algo.NiceSort(data),
                     ["A", "Z", "a0-0", "a0-4", "a1-0", "a9-1", "a09-2",
                      "a20-3", "a99-3", "a99-10", "b"])
    self.assertEqual(algo.NiceSort(data, key=str.lower),
                     ["A", "a0-0", "a0-4", "a1-0", "a9-1", "a09-2",
                      "a20-3", "a99-3", "a99-10", "b", "Z"])
    self.assertEqual(algo.NiceSort(data, key=str.upper),
                     ["A", "a0-0", "a0-4", "a1-0", "a9-1", "a09-2",
                      "a20-3", "a99-3", "a99-10", "b", "Z"])

  def testLargeA(self):
    data = [
      "Eegah9ei", "xij88brTulHYAv8IEOyU", "3jTwJPtrXOY22bwL2YoW",
      "Z8Ljf1Pf5eBfNg171wJR", "WvNJd91OoXvLzdEiEXa6", "uHXAyYYftCSG1o7qcCqe",
      "xpIUJeVT1Rp", "KOt7vn1dWXi", "a07h8feON165N67PIE", "bH4Q7aCu3PUPjK3JtH",
      "cPRi0lM7HLnSuWA2G9", "KVQqLPDjcPjf8T3oyzjcOsfkb",
      "guKJkXnkULealVC8CyF1xefym", "pqF8dkU5B1cMnyZuREaSOADYx",
      ]
    self.assertEqual(algo.NiceSort(data), [
      "3jTwJPtrXOY22bwL2YoW", "Eegah9ei", "KOt7vn1dWXi",
      "KVQqLPDjcPjf8T3oyzjcOsfkb", "WvNJd91OoXvLzdEiEXa6",
      "Z8Ljf1Pf5eBfNg171wJR", "a07h8feON165N67PIE", "bH4Q7aCu3PUPjK3JtH",
      "cPRi0lM7HLnSuWA2G9", "guKJkXnkULealVC8CyF1xefym",
      "pqF8dkU5B1cMnyZuREaSOADYx", "uHXAyYYftCSG1o7qcCqe",
      "xij88brTulHYAv8IEOyU", "xpIUJeVT1Rp"
      ])

  def testLargeB(self):
    data = [
      "inst-0.0.0.0-0.0.0.0",
      "inst-0.1.0.0-0.0.0.0",
      "inst-0.2.0.0-0.0.0.0",
      "inst-0.2.1.0-0.0.0.0",
      "inst-0.2.2.0-0.0.0.0",
      "inst-0.2.2.0-0.0.0.9",
      "inst-0.2.2.0-0.0.3.9",
      "inst-0.2.2.0-0.2.0.9",
      "inst-0.2.2.0-0.9.0.9",
      "inst-0.20.2.0-0.0.0.0",
      "inst-0.20.2.0-0.9.0.9",
      "inst-10.020.2.0-0.9.0.10",
      "inst-15.020.2.0-0.9.1.00",
      "inst-100.020.2.0-0.9.0.9",

      # Only the last group, not converted to a number anymore, differs
      "inst-100.020.2.0a999",
      "inst-100.020.2.0b000",
      "inst-100.020.2.0c10",
      "inst-100.020.2.0c101",
      "inst-100.020.2.0c2",
      "inst-100.020.2.0c20",
      "inst-100.020.2.0c3",
      "inst-100.020.2.0c39123",
      ]

    rnd = random.Random(16205)
    for _ in range(10):
      testdata = data[:]
      rnd.shuffle(testdata)
      assert testdata != data
      self.assertEqual(algo.NiceSort(testdata), data)

  class _CallCount:
    def __init__(self, fn):
      self.count = 0
      self.fn = fn

    def __call__(self, *args):
      self.count += 1
      return self.fn(*args)

  def testKeyfuncA(self):
    # Generate some random numbers
    rnd = random.Random(21131)
    numbers = [rnd.randint(0, 10000) for _ in range(999)]
    assert numbers != sorted(numbers)

    # Convert to hex
    data = [hex(i) for i in numbers]
    datacopy = data[:]

    keyfn = self._CallCount(lambda value: str(int(value, 16)))

    # Sort with key function converting hex to decimal
    result = algo.NiceSort(data, key=keyfn)

    self.assertEqual([hex(i) for i in sorted(numbers)], result)
    self.assertEqual(data, datacopy, msg="Input data was modified in NiceSort")
    self.assertEqual(keyfn.count, len(numbers),
                     msg="Key function was not called once per value")

  class _TestData:
    def __init__(self, name, value):
      self.name = name
      self.value = value

  def testKeyfuncB(self):
    rnd = random.Random(27396)
    data = []
    for i in range(123):
      v1 = rnd.randint(0, 5)
      v2 = rnd.randint(0, 5)
      data.append(self._TestData("inst-%s-%s-%s" % (v1, v2, i),
                                 (v1, v2, i)))
    rnd.shuffle(data)
    assert data != sorted(data, key=operator.attrgetter("name"))

    keyfn = self._CallCount(operator.attrgetter("name"))

    # Sort by name
    result = algo.NiceSort(data, key=keyfn)

    self.assertEqual(result, sorted(data, key=operator.attrgetter("value")))
    self.assertEqual(keyfn.count, len(data),
                     msg="Key function was not called once per value")

  def testNiceSortKey(self):
    self.assertEqual(algo.NiceSortKey(""),
                     ([None] * algo._SORTER_GROUPS) + [""])
    self.assertEqual(algo.NiceSortKey("Hello World"),
                     ["Hello World"] +
                     ([None] * int(algo._SORTER_GROUPS - 1)) + [""])
    self.assertEqual(algo.NiceSortKey("node1.net75.bld3.example.com"),
                     ["node", 1, ".net", 75, ".bld", 3, ".example.com",
                      None, ""])


class TestInvertDict(unittest.TestCase):
  def testInvertDict(self):
    test_dict = { "foo": 1, "bar": 2, "baz": 5 }
    self.assertEqual(algo.InvertDict(test_dict),
                     { 1: "foo", 2: "bar", 5: "baz"})


class TimeMock:
  def __init__(self, values):
    self.values = values

  def __call__(self):
    return self.values.pop(0)


class TestRunningTimeout(unittest.TestCase):
  def setUp(self):
    self.time_fn = TimeMock([0.0, 0.3, 4.6, 6.5])

  def testRemainingFloat(self):
    timeout = algo.RunningTimeout(5.0, True, _time_fn=self.time_fn)
    self.assertAlmostEqual(timeout.Remaining(), 4.7)
    self.assertAlmostEqual(timeout.Remaining(), 0.4)
    self.assertAlmostEqual(timeout.Remaining(), -1.5)

  def testRemaining(self):
    self.time_fn = TimeMock([0, 2, 4, 5, 6])
    timeout = algo.RunningTimeout(5, True, _time_fn=self.time_fn)
    self.assertEqual(timeout.Remaining(), 3)
    self.assertEqual(timeout.Remaining(), 1)
    self.assertEqual(timeout.Remaining(), 0)
    self.assertEqual(timeout.Remaining(), -1)

  def testRemainingNonNegative(self):
    timeout = algo.RunningTimeout(5.0, False, _time_fn=self.time_fn)
    self.assertAlmostEqual(timeout.Remaining(), 4.7)
    self.assertAlmostEqual(timeout.Remaining(), 0.4)
    self.assertEqual(timeout.Remaining(), 0.0)

  def testNegativeTimeout(self):
    self.assertRaises(ValueError, algo.RunningTimeout, -1.0, True)


if __name__ == "__main__":
  testutils.GanetiTestProgram()
