"""
Batch Renamer - A Blender addon for batch renaming and organizing objects and collections.

Features:
- Sync data-block names to object names
- Batch find & replace, prefix/suffix operations
- Sequential renaming with customizable numbering
- Case conversion
- Strip orphan .001 suffixes
- Collection creation and organization tools
"""

bl_info = {
    "name": "Batch Renamer",
    "author": "Custom",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Rename",
    "description": "Batch rename and organize objects and collections",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}


# Handle reloading of modules when using Blender's reload scripts
if "bpy" in locals():
    import importlib
    if "properties" in locals():
        importlib.reload(properties)
    if "operators" in locals():
        importlib.reload(operators)
    if "panels" in locals():
        importlib.reload(panels)


import bpy
from . import properties
from . import operators
from . import panels


def register():
    """Register all addon classes and properties."""
    properties.register()
    operators.register()
    panels.register()


def unregister():
    """Unregister all addon classes and properties."""
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
