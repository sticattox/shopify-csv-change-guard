"""Shopify CSV Change Guard — local preflight for product catalog imports."""

from .engine import CompareOptions, GuardResult, compare_csvs

__all__ = ["compare_csvs", "GuardResult", "CompareOptions"]
__version__ = "0.3.0"
