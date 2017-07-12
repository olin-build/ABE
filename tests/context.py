#!/usr/bin/env python3
"""Provide context for imports of ABE.
Referenced from The Hitchhiker's Guide to Python.
https://python-guide-pt-br.readthedocs.io/en/latest/writing/structure/#test-suite
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sample
