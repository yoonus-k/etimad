"""
Configuration Module
Contains browser configuration and company context settings
"""

from .browser_config import *
from .company_context import CompanyContext, get_company_context

__all__ = ['CompanyContext', 'get_company_context']
