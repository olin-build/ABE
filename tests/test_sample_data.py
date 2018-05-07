#!/usr/bin/env python3
"""Test suite for sample_data.py
This test suite requires a local mongodb instance and writes to/drops a
database named "abe-unittest" for testing.
"""
from . import abe_unittest
from .context import abe  # noqa: F401

# This import has to happen after .context sets the environment variables
from abe import sample_data  # isort:skip


class SampleDataTestCase(abe_unittest.TestCase):

    def test_load_data(self):
        """Load sample data"""
        sample_data.load_data(self.db)
