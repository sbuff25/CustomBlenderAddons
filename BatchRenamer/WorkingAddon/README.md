# Batch Renamer

A Blender addon (4.0+) for batch renaming and organizing objects and collections.

## Installation

1. Download `batch_renamer.zip`
2. In Blender, go to **Edit > Preferences > Add-ons**
3. Click **Install...** and select the zip file
4. Enable the addon by checking the checkbox next to "Object: Batch Renamer"

## Location

**View3D > Sidebar (N) > Rename** tab

## Features

### Data Name Sync
Sync mesh/curve/etc. data-block names to match their object names.

- **Sync Data Names** - Renames data-blocks for all selected objects
- **Select Mismatched** - Selects objects where data name doesn't match
- **Data Suffix** - Optional suffix to add (e.g., `_mesh`)

### Find & Replace
Simple find and replace in selected object names.

### Prefix / Suffix
Add or remove prefix/suffix from selected object names.

### Sequential Rename
Rename selected objects with incrementing numbers.

- **Base Name** - The name before the number (e.g., `Chair`)
- **Start** - Starting number
- **Padding** - Zero-padding (3 = `001`, `002`, etc.)

Result: `Chair_001`, `Chair_002`, `Chair_003`...

### Case Conversion
Convert selected object names to lowercase, UPPERCASE, or Title Case.

### Cleanup
- **Strip .001 Suffixes** - Remove trailing `.001`, `.002` etc. where no naming conflict exists

### Collections
- **Create Collection** - Create a new collection from selection (uses active object name if no name specified)
- **Rename Collection** - Rename the active collection, optionally prefixing all child objects
- **Prefix from Collection** - Add parent collection name as prefix to selected objects
- **Sort by Type** - Organize selected objects into collections by type (Meshes, Lights, Empties, etc.)

## Tips

- All operations work on **selected objects** (in Object mode)
- Operations are **undo-able** as a single step (Ctrl+Z)
- The addon uses the current **active collection** for collection rename operations
- Sequential rename sorts objects alphabetically first for consistent ordering

## Version History

### 1.0.0
- Initial release
- Data name sync with mismatch detection
- Batch rename: find/replace, prefix/suffix, sequential, case conversion
- Cleanup: strip orphan number suffixes
- Collection tools: create, rename, prefix propagation, sort by type
