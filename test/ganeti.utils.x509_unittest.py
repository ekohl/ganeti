#!/usr/bin/env python2
#

# Copyright (C) 2006, 2007, 2010, 2011 Google Inc.
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


"""Script for testing ganeti.utils.x509"""

import os
import tempfile
import unittest
import shutil
import time
import OpenSSL
import distutils.version
import string

from ganeti import constants
from ganeti import utils
from ganeti import compat
from ganeti import errors

import testutils


class TestParseAsn1Generalizedtime(unittest.TestCase):
  def setUp(self):
    self._Parse = utils.x509._ParseAsn1Generalizedtime

  def test(self):
    # UTC
    self.assertEqual(self._Parse("19700101000000Z"), 0)
    self.assertEqual(self._Parse("20100222174152Z"), 1266860512)
    self.assertEqual(self._Parse("20380119031407Z"), (2**31) - 1)

    # With offset
    self.assertEqual(self._Parse("20100222174152+0000"), 1266860512)
    self.assertEqual(self._Parse("20100223131652+0000"), 1266931012)
    self.assertEqual(self._Parse("20100223051808-0800"), 1266931088)
    self.assertEqual(self._Parse("20100224002135+1100"), 1266931295)
    self.assertEqual(self._Parse("19700101000000-0100"), 3600)

    # Leap seconds are not supported by datetime.datetime
    self.assertRaises(ValueError, self._Parse, "19841231235960+0000")
    self.assertRaises(ValueError, self._Parse, "19920630235960+0000")

    # Errors
    self.assertRaises(ValueError, self._Parse, "")
    self.assertRaises(ValueError, self._Parse, "invalid")
    self.assertRaises(ValueError, self._Parse, "20100222174152")
    self.assertRaises(ValueError, self._Parse, "Mon Feb 22 17:47:02 UTC 2010")
    self.assertRaises(ValueError, self._Parse, "2010-02-22 17:42:02")


class TestGetX509CertValidity(testutils.GanetiTestCase):
  def setUp(self):
    testutils.GanetiTestCase.setUp(self)

    pyopenssl_version = distutils.version.LooseVersion(OpenSSL.__version__)

    # Test whether we have pyOpenSSL 0.7 or above
    self.pyopenssl0_7 = (pyopenssl_version >= "0.7")

    if not self.pyopenssl0_7:
      warnings.warn("This test requires pyOpenSSL 0.7 or above to"
                    " function correctly")

  def _LoadCert(self, name):
    return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                           self._ReadTestData(name))

  def test(self):
    validity = utils.GetX509CertValidity(self._LoadCert("cert1.pem"))
    if self.pyopenssl0_7:
      self.assertEqual(validity, (1266919967, 1267524767))
    else:
      self.assertEqual(validity, (None, None))


class TestSignX509Certificate(unittest.TestCase):
  KEY = "My private key!"
  KEY_OTHER = "Another key"

  def test(self):
    # Generate certificate valid for 5 minutes
    (_, cert_pem) = utils.GenerateSelfSignedX509Cert(None, 300)

    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                           cert_pem)

    # No signature at all
    self.assertRaises(errors.GenericError,
                      utils.LoadSignedX509Certificate, cert_pem, self.KEY)

    # Invalid input
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      "", self.KEY)
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      "X-Ganeti-Signature: \n", self.KEY)
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      "X-Ganeti-Sign: $1234$abcdef\n", self.KEY)
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      "X-Ganeti-Signature: $1234567890$abcdef\n", self.KEY)
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      "X-Ganeti-Signature: $1234$abc\n\n" + cert_pem, self.KEY)

    # Invalid salt
    for salt in list("-_@$,:;/\\ \t\n"):
      self.assertRaises(errors.GenericError, utils.SignX509Certificate,
                        cert_pem, self.KEY, "foo%sbar" % salt)

    for salt in ["HelloWorld", "salt", string.letters, string.digits,
                 utils.GenerateSecret(numbytes=4),
                 utils.GenerateSecret(numbytes=16),
                 "{123:456}".encode("hex")]:
      signed_pem = utils.SignX509Certificate(cert, self.KEY, salt)

      self._Check(cert, salt, signed_pem)

      self._Check(cert, salt, "X-Another-Header: with a value\n" + signed_pem)
      self._Check(cert, salt, (10 * "Hello World!\n") + signed_pem)
      self._Check(cert, salt, (signed_pem + "\n\na few more\n"
                               "lines----\n------ at\nthe end!"))

  def _Check(self, cert, salt, pem):
    (cert2, salt2) = utils.LoadSignedX509Certificate(pem, self.KEY)
    self.assertEqual(salt, salt2)
    self.assertEqual(cert.digest("sha1"), cert2.digest("sha1"))

    # Other key
    self.assertRaises(errors.GenericError, utils.LoadSignedX509Certificate,
                      pem, self.KEY_OTHER)


class TestCertVerification(testutils.GanetiTestCase):
  def setUp(self):
    testutils.GanetiTestCase.setUp(self)

    self.tmpdir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def testVerifyCertificate(self):
    cert_pem = utils.ReadFile(self._TestDataFilename("cert1.pem"))
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                           cert_pem)

    # Not checking return value as this certificate is expired
    utils.VerifyX509Certificate(cert, 30, 7)


class TestVerifyCertificateInner(unittest.TestCase):
  def test(self):
    vci = utils.x509._VerifyCertificateInner

    # Valid
    self.assertEqual(vci(False, 1263916313, 1298476313, 1266940313, 30, 7),
                     (None, None))

    # Not yet valid
    (errcode, msg) = vci(False, 1266507600, 1267544400, 1266075600, 30, 7)
    self.assertEqual(errcode, utils.CERT_WARNING)

    # Expiring soon
    (errcode, msg) = vci(False, 1266507600, 1267544400, 1266939600, 30, 7)
    self.assertEqual(errcode, utils.CERT_ERROR)

    (errcode, msg) = vci(False, 1266507600, 1267544400, 1266939600, 30, 1)
    self.assertEqual(errcode, utils.CERT_WARNING)

    (errcode, msg) = vci(False, 1266507600, None, 1266939600, 30, 7)
    self.assertEqual(errcode, None)

    # Expired
    (errcode, msg) = vci(True, 1266507600, 1267544400, 1266939600, 30, 7)
    self.assertEqual(errcode, utils.CERT_ERROR)

    (errcode, msg) = vci(True, None, 1267544400, 1266939600, 30, 7)
    self.assertEqual(errcode, utils.CERT_ERROR)

    (errcode, msg) = vci(True, 1266507600, None, 1266939600, 30, 7)
    self.assertEqual(errcode, utils.CERT_ERROR)

    (errcode, msg) = vci(True, None, None, 1266939600, 30, 7)
    self.assertEqual(errcode, utils.CERT_ERROR)


class TestGenerateSelfSignedX509Cert(unittest.TestCase):
  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.tmpdir)

  def _checkRsaPrivateKey(self, key):
    lines = key.splitlines()
    return (("-----BEGIN RSA PRIVATE KEY-----" in lines and
             "-----END RSA PRIVATE KEY-----" in lines) or
            ("-----BEGIN PRIVATE KEY-----" in lines and
             "-----END PRIVATE KEY-----" in lines))

  def _checkCertificate(self, cert):
    lines = cert.splitlines()
    return ("-----BEGIN CERTIFICATE-----" in lines and
            "-----END CERTIFICATE-----" in lines)

  def test(self):
    for common_name in [None, ".", "Ganeti", "node1.example.com"]:
      (key_pem, cert_pem) = utils.GenerateSelfSignedX509Cert(common_name, 300)
      self._checkRsaPrivateKey(key_pem)
      self._checkCertificate(cert_pem)

      key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,
                                           key_pem)
      self.assert_(key.bits() >= 1024)
      self.assertEqual(key.bits(), constants.RSA_KEY_BITS)
      self.assertEqual(key.type(), OpenSSL.crypto.TYPE_RSA)

      x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                             cert_pem)
      self.failIf(x509.has_expired())
      self.assertEqual(x509.get_issuer().CN, common_name)
      self.assertEqual(x509.get_subject().CN, common_name)
      self.assertEqual(x509.get_pubkey().bits(), constants.RSA_KEY_BITS)

  def testLegacy(self):
    cert1_filename = os.path.join(self.tmpdir, "cert1.pem")

    utils.GenerateSelfSignedSslCert(cert1_filename, validity=1)

    cert1 = utils.ReadFile(cert1_filename)

    self.assert_(self._checkRsaPrivateKey(cert1))
    self.assert_(self._checkCertificate(cert1))


if __name__ == "__main__":
  testutils.GanetiTestProgram()
