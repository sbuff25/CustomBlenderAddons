"""UI Panels for Batch Renamer addon."""

import bpy
from bpy.types import Panel


class BATCHRENAME_PT_main_panel(Panel):
    """Main panel in the 3D View sidebar."""
    bl_label = "Batch Renamer"
    bl_idname = "BATCHRENAME_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    
    def draw(self, context):
        layout = self.layout
        # Main panel is just a container for sub-panels
        pass


class BATCHRENAME_PT_data_sync(Panel):
    """Sub-panel for data-block name syncing."""
    bl_label = "Data Name Sync"
    bl_idname = "BATCHRENAME_PT_data_sync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=True)
        col.prop(settings, "sync_suffix")
        
        col.separator()
        
        row = col.row(align=True)
        row.operator("batch_rename.sync_data_names", icon='FILE_REFRESH')
        
        row = col.row(align=True)
        row.operator("batch_rename.select_mismatched", icon='RESTRICT_SELECT_OFF')


class BATCHRENAME_PT_find_replace(Panel):
    """Sub-panel for find and replace."""
    bl_label = "Find & Replace"
    bl_idname = "BATCHRENAME_PT_find_replace"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=True)
        col.prop(settings, "find_string")
        col.prop(settings, "replace_string")
        
        col.separator()
        
        col.operator("batch_rename.find_replace", icon='ARROW_LEFTRIGHT')


class BATCHRENAME_PT_prefix_suffix(Panel):
    """Sub-panel for prefix/suffix operations."""
    bl_label = "Prefix / Suffix"
    bl_idname = "BATCHRENAME_PT_prefix_suffix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        # Prefix section
        col = layout.column(align=True)
        col.prop(settings, "prefix_string")
        
        row = col.row(align=True)
        row.operator("batch_rename.add_prefix", text="Add", icon='ADD')
        row.operator("batch_rename.remove_prefix", text="Remove", icon='REMOVE')
        
        col.separator()
        
        # Suffix section
        col.prop(settings, "suffix_string")
        
        row = col.row(align=True)
        row.operator("batch_rename.add_suffix", text="Add", icon='ADD')
        row.operator("batch_rename.remove_suffix", text="Remove", icon='REMOVE')


class BATCHRENAME_PT_sequential(Panel):
    """Sub-panel for sequential renaming."""
    bl_label = "Sequential Rename"
    bl_idname = "BATCHRENAME_PT_sequential"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=True)
        col.prop(settings, "base_name")
        
        row = col.row(align=True)
        row.prop(settings, "start_number")
        row.prop(settings, "zero_padding")
        
        col.separator()
        
        col.operator("batch_rename.sequential_rename", icon='LINENUMBERS_ON')


class BATCHRENAME_PT_case(Panel):
    """Sub-panel for case conversion."""
    bl_label = "Case Conversion"
    bl_idname = "BATCHRENAME_PT_case"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=True)
        col.prop(settings, "case_mode")
        col.operator("batch_rename.convert_case", icon='SMALL_CAPS')


class BATCHRENAME_PT_cleanup(Panel):
    """Sub-panel for name cleanup operations."""
    bl_label = "Cleanup"
    bl_idname = "BATCHRENAME_PT_cleanup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator("batch_rename.strip_numbers", icon='X')


class BATCHRENAME_PT_collections(Panel):
    """Sub-panel for collection operations."""
    bl_label = "Collections"
    bl_idname = "BATCHRENAME_PT_collections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=True)
        col.prop(settings, "collection_name")
        col.prop(settings, "propagate_to_children")
        
        col.separator()
        
        col.operator("batch_rename.create_collection", icon='COLLECTION_NEW')
        col.operator("batch_rename.rename_collection", icon='OUTLINER_COLLECTION')
        
        col.separator()

        col.operator("batch_rename.prefix_from_collection", icon='FONT_DATA')


class BATCHRENAME_PT_sort_by_name(Panel):
    """Sub-panel for sorting objects into collections by name."""
    bl_label = "Sort to Collections by Name"
    bl_idname = "BATCHRENAME_PT_sort_by_name"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        # Scope toggle
        row = col.row(align=True)
        row.prop(settings, "sort_by_name_scope", expand=True)

        col.separator()

        col.prop(settings, "sort_by_name_delimiter")

        col.separator()

        col.operator("batch_rename.sort_by_name", icon='SORTALPHA')


class BATCHRENAME_PT_sort_by_type(Panel):
    """Sub-panel for sorting objects into collections by type."""
    bl_label = "Sort to Collections"
    bl_idname = "BATCHRENAME_PT_sort_by_type"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rename'
    bl_parent_id = "BATCHRENAME_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.batch_rename_settings

        layout.use_property_split = True
        layout.use_property_decorate = False

        # Scope toggle
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(settings, "sort_scope", expand=True)

        col.separator()

        # Select All / Deselect All
        row = col.row(align=True)
        row.operator("batch_rename.sort_select_all_types", text="All", icon='CHECKBOX_HLT')
        row.operator("batch_rename.sort_deselect_all_types", text="None", icon='CHECKBOX_DEHLT')

        col.separator()

        # Geometry types
        box = layout.box()
        box.label(text="Geometry", icon='MESH_DATA')
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(settings, "sort_type_mesh", icon='MESH_DATA')
        grid.prop(settings, "sort_type_curve", icon='CURVE_DATA')
        grid.prop(settings, "sort_type_surface", icon='SURFACE_DATA')
        grid.prop(settings, "sort_type_meta", icon='META_DATA')
        grid.prop(settings, "sort_type_font", icon='FONT_DATA')
        grid.prop(settings, "sort_type_curves", icon='OUTLINER_OB_CURVES')
        grid.prop(settings, "sort_type_pointcloud", icon='OUTLINER_OB_POINTCLOUD')
        grid.prop(settings, "sort_type_volume", icon='VOLUME_DATA')
        grid.prop(settings, "sort_type_gpencil", icon='OUTLINER_OB_GREASEPENCIL')

        # Rigging types
        box = layout.box()
        box.label(text="Rigging", icon='ARMATURE_DATA')
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(settings, "sort_type_armature", icon='ARMATURE_DATA')
        grid.prop(settings, "sort_type_lattice", icon='LATTICE_DATA')

        # Scene types
        box = layout.box()
        box.label(text="Scene", icon='SCENE_DATA')
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(settings, "sort_type_empty", icon='EMPTY_DATA')
        grid.prop(settings, "sort_type_light", icon='LIGHT')
        grid.prop(settings, "sort_type_light_probe", icon='OUTLINER_OB_LIGHTPROBE')
        grid.prop(settings, "sort_type_camera", icon='CAMERA_DATA')
        grid.prop(settings, "sort_type_speaker", icon='SPEAKER')

        # Execute button
        layout.separator()
        layout.operator("batch_rename.sort_by_type", icon='SORTALPHA')


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

classes = (
    BATCHRENAME_PT_main_panel,
    BATCHRENAME_PT_data_sync,
    BATCHRENAME_PT_find_replace,
    BATCHRENAME_PT_prefix_suffix,
    BATCHRENAME_PT_sequential,
    BATCHRENAME_PT_case,
    BATCHRENAME_PT_cleanup,
    BATCHRENAME_PT_collections,
    BATCHRENAME_PT_sort_by_name,
    BATCHRENAME_PT_sort_by_type,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
