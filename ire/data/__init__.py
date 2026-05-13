"""Data conversion utilities for Independent Replication Experiment outputs."""

import os
import sys

sys.path.append(os.getcwd())

from ire.data.conversion import convert_psb_data

__all__ = ["convert_psb_data"]
