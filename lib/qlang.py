#
#

# Copyright (C) 2010, 2011 Google Inc.
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


"""Module for a simple query language

A query filter is always a list. The first item in the list is the operator
(e.g. C{[OP_AND, ...]}), while the other items depend on the operator. For
logic operators (e.g. L{OP_AND}, L{OP_OR}), they are subfilters whose results
are combined. Unary operators take exactly one other item (e.g. a subfilter for
L{OP_NOT} and a field name for L{OP_TRUE}). Binary operators take exactly two
operands, usually a field name and a value to compare against. Filters are
converted to callable functions by L{query._CompileFilter}.

"""

import re
import string # pylint: disable-msg=W0402

import pyparsing as pyp

from ganeti import errors
from ganeti import netutils


# Logic operators with one or more operands, each of which is a filter on its
# own
OP_OR = "|"
OP_AND = "&"


# Unary operators with exactly one operand
OP_NOT = "!"
OP_TRUE = "?"


# Binary operators with exactly two operands, the field name and an
# operator-specific value
OP_EQUAL = "="
OP_NOT_EQUAL = "!="
OP_REGEXP = "=~"
OP_CONTAINS = "=[]"


#: Characters used for detecting user-written filters (see L{MaybeFilter})
FILTER_DETECTION_CHARS = frozenset("()=/!~" + string.whitespace)


def MakeSimpleFilter(namefield, values):
  """Builds simple a filter.

  @param namefield: Name of field containing item name
  @param values: List of names

  """
  if values:
    return [OP_OR] + [[OP_EQUAL, namefield, i] for i in values]

  return None


def _ConvertLogicOp(op):
  """Creates parsing action function for logic operator.

  @type op: string
  @param op: Operator for data structure, e.g. L{OP_AND}

  """
  def fn(toks):
    """Converts parser tokens to query operator structure.

    @rtype: list
    @return: Query operator structure, e.g. C{[OP_AND, ["=", "foo", "bar"]]}

    """
    operands = toks[0]

    if len(operands) == 1:
      return operands[0]

    # Build query operator structure
    return [[op] + operands.asList()]

  return fn


_KNOWN_REGEXP_DELIM = "/#^|"
_KNOWN_REGEXP_FLAGS = frozenset("si")


def _ConvertRegexpValue(_, loc, toks):
  """Regular expression value for condition.

  """
  (regexp, flags) = toks[0]

  # Ensure only whitelisted flags are used
  unknown_flags = (frozenset(flags) - _KNOWN_REGEXP_FLAGS)
  if unknown_flags:
    raise pyp.ParseFatalException("Unknown regular expression flags: '%s'" %
                                  "".join(unknown_flags), loc)

  if flags:
    re_flags = "(?%s)" % "".join(sorted(flags))
  else:
    re_flags = ""

  re_cond = re_flags + regexp

  # Test if valid
  try:
    re.compile(re_cond)
  except re.error, err:
    raise pyp.ParseFatalException("Invalid regular expression (%s)" % err, loc)

  return [re_cond]


def BuildFilterParser():
  """Builds a parser for query filter strings.

  @rtype: pyparsing.ParserElement

  """
  field_name = pyp.Word(pyp.alphas, pyp.alphanums + "_/.")

  # Integer
  num_sign = pyp.Word("-+", exact=1)
  number = pyp.Combine(pyp.Optional(num_sign) + pyp.Word(pyp.nums))
  number.setParseAction(lambda toks: int(toks[0]))

  # Right-hand-side value
  rval = (number | pyp.quotedString.setParseAction(pyp.removeQuotes))

  # Boolean condition
  bool_cond = field_name.copy()
  bool_cond.setParseAction(lambda (fname, ): [[OP_TRUE, fname]])

  # Simple binary conditions
  binopstbl = {
    "==": OP_EQUAL,
    "!=": OP_NOT_EQUAL,
    }

  binary_cond = (field_name + pyp.oneOf(binopstbl.keys()) + rval)
  binary_cond.setParseAction(lambda (lhs, op, rhs): [[binopstbl[op], lhs, rhs]])

  # "in" condition
  in_cond = (rval + pyp.Suppress("in") + field_name)
  in_cond.setParseAction(lambda (value, field): [[OP_CONTAINS, field, value]])

  # "not in" condition
  not_in_cond = (rval + pyp.Suppress("not") + pyp.Suppress("in") + field_name)
  not_in_cond.setParseAction(lambda (value, field): [[OP_NOT, [OP_CONTAINS,
                                                               field, value]]])

  # Regular expression, e.g. m/foobar/i
  regexp_val = pyp.Group(pyp.Optional("m").suppress() +
                         pyp.MatchFirst([pyp.QuotedString(i, escChar="\\")
                                         for i in _KNOWN_REGEXP_DELIM]) +
                         pyp.Optional(pyp.Word(pyp.alphas), default=""))
  regexp_val.setParseAction(_ConvertRegexpValue)
  regexp_cond = (field_name + pyp.Suppress("=~") + regexp_val)
  regexp_cond.setParseAction(lambda (field, value): [[OP_REGEXP, field, value]])

  not_regexp_cond = (field_name + pyp.Suppress("!~") + regexp_val)
  not_regexp_cond.setParseAction(lambda (field, value):
                                 [[OP_NOT, [OP_REGEXP, field, value]]])

  # All possible conditions
  condition = (binary_cond ^ bool_cond ^
               in_cond ^ not_in_cond ^
               regexp_cond ^ not_regexp_cond)

  # Associativity operators
  filter_expr = pyp.operatorPrecedence(condition, [
    (pyp.Keyword("not").suppress(), 1, pyp.opAssoc.RIGHT,
     lambda toks: [[OP_NOT, toks[0][0]]]),
    (pyp.Keyword("and").suppress(), 2, pyp.opAssoc.LEFT,
     _ConvertLogicOp(OP_AND)),
    (pyp.Keyword("or").suppress(), 2, pyp.opAssoc.LEFT,
     _ConvertLogicOp(OP_OR)),
    ])

  parser = pyp.StringStart() + filter_expr + pyp.StringEnd()
  parser.parseWithTabs()

  # Originally C{parser.validate} was called here, but there seems to be some
  # issue causing it to fail whenever the "not" operator is included above.

  return parser


def ParseFilter(text, parser=None):
  """Parses a query filter.

  @type text: string
  @param text: Query filter
  @type parser: pyparsing.ParserElement
  @param parser: Pyparsing object
  @rtype: list

  """
  if parser is None:
    parser = BuildFilterParser()

  try:
    return parser.parseString(text)[0]
  except pyp.ParseBaseException, err:
    raise errors.QueryFilterParseError("Failed to parse query filter"
                                       " '%s': %s" % (text, err), err)


def MaybeFilter(text):
  """Try to determine if a string is a filter or a name.

  If in doubt, this function treats a text as a name.

  @type text: string
  @param text: String to be examined
  @rtype: bool

  """
  # Quick check for punctuation and whitespace
  if frozenset(text) & FILTER_DETECTION_CHARS:
    return True

  try:
    netutils.Hostname.GetNormalizedName(text)
  except errors.OpPrereqError:
    # Not a valid hostname, treat as filter
    return True

  # Most probably a name
  return False
