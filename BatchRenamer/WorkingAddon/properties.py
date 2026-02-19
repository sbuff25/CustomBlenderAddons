"""Property groups for Batch Renamer addon UI state."""

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import PropertyGroup


class BATCHRENAME_PG_settings(PropertyGroup):
    """Main settings property group for the Batch Renamer addon."""
    
    # Data sync options
    sync_suffix: StringProperty(
        name="Data Suffix",
        description="Optional suffix to add to data-block names (e.g., '_mesh')",
        default=""
    )
    
    # Batch rename options
    find_string: StringProperty(
        name="Find",
        description="Text to search for in names",
        default=""
    )
    replace_string: StringProperty(
        name="Replace",
        description="Text to replace with",
        default=""
    )
    prefix_string: StringProperty(
        name="Prefix",
        description="Prefix to add to names",
        default=""
    )
    suffix_string: StringProperty(
        name="Suffix",
        description="Suffix to add to names",
        default=""
    )
    
    # Sequential numbering
    base_name: StringProperty(
        name="Base Name",
        description="Base name for sequential renaming",
        default="Object"
    )
    start_number: IntProperty(
        name="Start",
        description="Starting number for sequence",
        default=1,
        min=0
    )
    zero_padding: IntProperty(
        name="Padding",
        description="Number of digits (zero-padded)",
        default=3,
        min=1,
        max=6
    )
    
    # Case conversion
    case_mode: EnumProperty(
        name="Case",
        description="Case conversion mode",
        items=[
            ('NONE', "No Change", "Keep original case"),
            ('LOWER', "lowercase", "Convert to lowercase"),
            ('UPPER', "UPPERCASE", "Convert to uppercase"),
            ('TITLE', "Title Case", "Convert to title case"),
        ],
        default='NONE'
    )
    
    # Collection options
    collection_name: StringProperty(
        name="Collection Name",
        description="Name for new collection (blank = use active object name)",
        default=""
    )
    propagate_to_children: BoolProperty(
        name="Propagate to Objects",
        description="Apply collection name as prefix to child objects",
        default=False
    )

    # Sort to collections by name options
    sort_by_name_delimiter: StringProperty(
        name="Delimiter",
        description="Character(s) separating the base name from the trailing number (e.g., '_' for Chair_001)",
        default="_"
    )
    sort_by_name_scope: EnumProperty(
        name="Scope",
        description="Which objects to sort into collections by name",
        items=[
            ('SELECTED', "Selected Only", "Sort only selected objects"),
            ('ALL', "All in Scene", "Sort all objects in the scene"),
        ],
        default='SELECTED'
    )

    # Sort to collections by type options
    sort_scope: EnumProperty(
        name="Scope",
        description="Which objects to sort into collections",
        items=[
            ('SELECTED', "Selected Only", "Sort only selected objects"),
            ('ALL', "All in Scene", "Sort all objects in the scene"),
        ],
        default='SELECTED'
    )

    # Per-type toggles for sort to collections
    sort_type_mesh: BoolProperty(
        name="Meshes",
        description="Sort mesh objects into a Meshes collection",
        default=True
    )
    sort_type_curve: BoolProperty(
        name="Curves",
        description="Sort curve objects into a Curves collection",
        default=True
    )
    sort_type_surface: BoolProperty(
        name="Surfaces",
        description="Sort surface objects into a Surfaces collection",
        default=True
    )
    sort_type_meta: BoolProperty(
        name="Metaballs",
        description="Sort metaball objects into a Metaballs collection",
        default=True
    )
    sort_type_font: BoolProperty(
        name="Text",
        description="Sort text objects into a Text collection",
        default=True
    )
    sort_type_curves: BoolProperty(
        name="Hair Curves",
        description="Sort hair curve objects into a Hair Curves collection",
        default=True
    )
    sort_type_pointcloud: BoolProperty(
        name="Point Clouds",
        description="Sort point cloud objects into a Point Clouds collection",
        default=True
    )
    sort_type_volume: BoolProperty(
        name="Volumes",
        description="Sort volume objects into a Volumes collection",
        default=True
    )
    sort_type_gpencil: BoolProperty(
        name="Grease Pencil",
        description="Sort grease pencil objects into a Grease Pencil collection",
        default=True
    )
    sort_type_armature: BoolProperty(
        name="Armatures",
        description="Sort armature objects into an Armatures collection",
        default=True
    )
    sort_type_lattice: BoolProperty(
        name="Lattices",
        description="Sort lattice objects into a Lattices collection",
        default=True
    )
    sort_type_empty: BoolProperty(
        name="Empties",
        description="Sort empty objects into an Empties collection",
        default=True
    )
    sort_type_light: BoolProperty(
        name="Lights",
        description="Sort light objects into a Lights collection",
        default=True
    )
    sort_type_light_probe: BoolProperty(
        name="Light Probes",
        description="Sort light probe objects into a Light Probes collection",
        default=True
    )
    sort_type_camera: BoolProperty(
        name="Cameras",
        description="Sort camera objects into a Cameras collection",
        default=True
    )
    sort_type_speaker: BoolProperty(
        name="Speakers",
        description="Sort speaker objects into a Speakers collection",
        default=True
    )


classes = (
    BATCHRENAME_PG_settings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.batch_rename_settings = bpy.props.PointerProperty(
        type=BATCHRENAME_PG_settings
    )


def unregister():
    del bpy.types.Scene.batch_rename_settings
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
