"""Shopify CSV Change Guard — local preflight for product catalog imports."""

from .engine import compare_csvs, GuardResult

__all__ = ["compare_csvs", "GuardResult"]
__version__ = "0.2.0"
