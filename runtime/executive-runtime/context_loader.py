"""
Context Loader

Combines Executive OS and Executive Package into one runtime context.
"""

from datetime import datetime


def build_context(executive_os, executive_package):

    return {

        "executive_os": executive_os,

        "executive_package": executive_package,

        "executive_os_documents": len(executive_os),

        "executive_documents": len(executive_package),

        "generated_at": datetime.now().isoformat()

    }