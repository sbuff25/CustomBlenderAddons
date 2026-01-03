# \# CustomBlenderAddons

# 

# A collection of custom Blender addons focused on quality-of-life improvements for everyday workflows. These addons target Blender 4.0+ and follow Blender's Python API conventions.

# 

# ---

# 

# \## Addons

# 

# \### Batch Renamer

# 

# A comprehensive renaming and organization toolkit that streamlines object and collection management in Blender.

# 

# \*\*Location:\*\* View3D > Sidebar (N) > Rename

# 

# \*\*Installation:\*\*

# 1\. Download `batch\_renamer.zip`

# 2\. In Blender: Edit > Preferences > Add-ons > Install

# 3\. Select the zip file and enable "Object: Batch Renamer"

# 

# ---

# 

# \## Batch Renamer Tools

# 

# \### Data Name Sync

# 

# Keeps object names and their underlying data-block names in sync. By default, Blender names these independently, which can cause confusion when examining data in the Outliner or when linking/appending assets.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Sync Data Names\*\* | Renames the data-block (mesh, curve, etc.) of each selected object to match the object's name. Optionally appends a custom suffix. |

# | \*\*Select Mismatched\*\* | Selects all objects in the scene where the data-block name doesn't match the object name, making it easy to audit naming consistency. |

# 

# \*\*Options:\*\*

# \- \*\*Data Suffix\*\* — Optional suffix appended to data-block names (e.g., `\_mesh` results in `Chair` → `Chair\_mesh`)

# 

# ---

# 

# \### Find \& Replace

# 

# Performs text substitution across all selected object names.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Find \& Replace\*\* | Replaces all occurrences of the "Find" string with the "Replace" string in selected object names. |

# 

# \*\*Options:\*\*

# \- \*\*Find\*\* — Text to search for

# \- \*\*Replace\*\* — Text to substitute (leave empty to delete matches)

# 

# ---

# 

# \### Prefix / Suffix

# 

# Adds or removes text at the beginning or end of object names.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Add Prefix\*\* | Prepends the specified text to all selected object names. |

# | \*\*Remove Prefix\*\* | Removes the specified text from the beginning of selected object names (only if present). |

# | \*\*Add Suffix\*\* | Appends the specified text to all selected object names. |

# | \*\*Remove Suffix\*\* | Removes the specified text from the end of selected object names (only if present). |

# 

# \*\*Options:\*\*

# \- \*\*Prefix\*\* — Text to add/remove at the start

# \- \*\*Suffix\*\* — Text to add/remove at the end

# 

# ---

# 

# \### Sequential Rename

# 

# Renames selected objects with a consistent base name and incrementing numbers. Useful for organizing duplicated objects like chairs, trees, or lights.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Sequential Rename\*\* | Renames all selected objects using the pattern `BaseName\_###`. Objects are sorted alphabetically before numbering for consistent results. |

# 

# \*\*Options:\*\*

# \- \*\*Base Name\*\* — The name portion before the number (e.g., `Chair`)

# \- \*\*Start\*\* — The starting number for the sequence

# \- \*\*Padding\*\* — Number of digits, zero-padded (3 = `001`, `002`, etc.)

# 

# \*\*Example:\*\* With Base Name `Prop`, Start `1`, Padding `3`:

# \- `Prop\_001`, `Prop\_002`, `Prop\_003`...

# 

# ---

# 

# \### Case Conversion

# 

# Converts the case of selected object names.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Convert Case\*\* | Transforms selected object names to the chosen case format. |

# 

# \*\*Options:\*\*

# \- \*\*No Change\*\* — Leaves names unchanged

# \- \*\*lowercase\*\* — Converts to all lowercase

# \- \*\*UPPERCASE\*\* — Converts to all uppercase

# \- \*\*Title Case\*\* — Capitalizes the first letter of each word

# 

# ---

# 

# \### Cleanup

# 

# Utilities for cleaning up messy object names.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Strip .001 Suffixes\*\* | Removes trailing `.001`, `.002`, etc. suffixes from selected objects. Only removes the suffix if doing so won't create a naming conflict with another object. |

# 

# \*\*Use case:\*\* After duplicating objects multiple times, Blender appends `.001`, `.002` suffixes. This tool cleans them up safely.

# 

# ---

# 

# \### Collections

# 

# Tools for organizing objects into collections and managing collection names.

# 

# | Tool | Description |

# |------|-------------|

# | \*\*Create Collection\*\* | Creates a new collection containing all selected objects. Uses the specified name, or falls back to the active object's name if left blank. Objects are unlinked from their current collections. |

# | \*\*Rename Collection\*\* | Renames the currently active collection. Optionally propagates the new name as a prefix to all objects within the collection. |

# | \*\*Prefix from Collection\*\* | Adds each selected object's parent collection name as a prefix (e.g., an object `Chair` in collection `Furniture` becomes `Furniture\_Chair`). |

# | \*\*Sort by Type\*\* | Organizes selected objects into collections based on their type (Meshes, Lights, Cameras, Empties, etc.). Creates new collections as needed. |

# 

# \*\*Options:\*\*

# \- \*\*Collection Name\*\* — Name for new/renamed collection (blank = use active object name)

# \- \*\*Propagate to Objects\*\* — When renaming a collection, also update child object names with the new prefix

# 

# ---

# 

# \## General Usage Notes

# 

# \- All rename operations work on \*\*selected objects\*\* in Object mode

# \- All operations support \*\*single-step undo\*\* (Ctrl+Z)

# \- Sub-panels are collapsible to reduce UI clutter

# \- The addon reports operation results in Blender's status bar

# 

# ---

# 

# \## Roadmap

# 

# Potential future additions:

# \- Regex-based find and replace

# \- Rename presets/templates

# \- Hierarchy-based renaming (parent-child relationships)

# \- Batch rename materials and textures

# \- Name validation and conflict warnings

# 

# ---

# 

# \## Contributing

# 

# Feel free to submit issues or pull requests for bug fixes and new features.

# 

# \## License

# 

# MIT License

