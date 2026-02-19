"""Operators for Batch Renamer addon."""

import bpy
import re
from bpy.types import Operator


# Mapping: Blender object type -> (collection name, settings property name)
SORT_TYPE_CONFIG = {
    'MESH':        ('Meshes',        'sort_type_mesh'),
    'CURVE':       ('Curves',        'sort_type_curve'),
    'SURFACE':     ('Surfaces',      'sort_type_surface'),
    'META':        ('Metaballs',     'sort_type_meta'),
    'FONT':        ('Text',          'sort_type_font'),
    'CURVES':      ('Hair Curves',   'sort_type_curves'),
    'POINTCLOUD':  ('Point Clouds',  'sort_type_pointcloud'),
    'VOLUME':      ('Volumes',       'sort_type_volume'),
    'GPENCIL':     ('Grease Pencil', 'sort_type_gpencil'),
    'ARMATURE':    ('Armatures',     'sort_type_armature'),
    'LATTICE':     ('Lattices',      'sort_type_lattice'),
    'EMPTY':       ('Empties',       'sort_type_empty'),
    'LIGHT':       ('Lights',        'sort_type_light'),
    'LIGHT_PROBE': ('Light Probes',  'sort_type_light_probe'),
    'CAMERA':      ('Cameras',       'sort_type_camera'),
    'SPEAKER':     ('Speakers',      'sort_type_speaker'),
}


# -----------------------------------------------------------------------------
# Data Name Sync Operators
# -----------------------------------------------------------------------------

class BATCHRENAME_OT_sync_data_names(Operator):
    """Sync data-block names to match their object names for all selected objects"""
    bl_idname = "batch_rename.sync_data_names"
    bl_label = "Sync Data Names"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        suffix = settings.sync_suffix
        
        synced_count = 0
        for obj in context.selected_objects:
            if obj.data and hasattr(obj.data, 'name'):
                new_name = obj.name + suffix
                obj.data.name = new_name
                synced_count += 1
        
        self.report({'INFO'}, f"Synced {synced_count} data-block name(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_select_mismatched(Operator):
    """Select objects where data-block name doesn't match object name"""
    bl_idname = "batch_rename.select_mismatched"
    bl_label = "Select Mismatched"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        suffix = settings.sync_suffix
        
        bpy.ops.object.select_all(action='DESELECT')
        
        count = 0
        for obj in context.scene.objects:
            if obj.data and hasattr(obj.data, 'name'):
                expected_name = obj.name + suffix
                # Also check without .001 etc suffixes
                base_expected = re.sub(r'\.\d{3}$', '', expected_name)
                base_actual = re.sub(r'\.\d{3}$', '', obj.data.name)
                
                if obj.data.name != expected_name and base_actual != base_expected:
                    obj.select_set(True)
                    count += 1
        
        self.report({'INFO'}, f"Selected {count} mismatched object(s)")
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Batch Rename Operators
# -----------------------------------------------------------------------------

class BATCHRENAME_OT_find_replace(Operator):
    """Find and replace text in selected object names"""
    bl_idname = "batch_rename.find_replace"
    bl_label = "Find & Replace"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        find = settings.find_string
        replace = settings.replace_string
        
        if not find:
            self.report({'WARNING'}, "Find string is empty")
            return {'CANCELLED'}
        
        count = 0
        for obj in context.selected_objects:
            if find in obj.name:
                obj.name = obj.name.replace(find, replace)
                count += 1
        
        self.report({'INFO'}, f"Renamed {count} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_add_prefix(Operator):
    """Add prefix to selected object names"""
    bl_idname = "batch_rename.add_prefix"
    bl_label = "Add Prefix"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        prefix = settings.prefix_string
        
        if not prefix:
            self.report({'WARNING'}, "Prefix is empty")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            obj.name = prefix + obj.name
        
        self.report({'INFO'}, f"Added prefix to {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_add_suffix(Operator):
    """Add suffix to selected object names"""
    bl_idname = "batch_rename.add_suffix"
    bl_label = "Add Suffix"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        suffix = settings.suffix_string
        
        if not suffix:
            self.report({'WARNING'}, "Suffix is empty")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            obj.name = obj.name + suffix
        
        self.report({'INFO'}, f"Added suffix to {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_remove_prefix(Operator):
    """Remove prefix from selected object names"""
    bl_idname = "batch_rename.remove_prefix"
    bl_label = "Remove Prefix"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        prefix = settings.prefix_string
        
        if not prefix:
            self.report({'WARNING'}, "Prefix is empty")
            return {'CANCELLED'}
        
        count = 0
        for obj in context.selected_objects:
            if obj.name.startswith(prefix):
                obj.name = obj.name[len(prefix):]
                count += 1
        
        self.report({'INFO'}, f"Removed prefix from {count} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_remove_suffix(Operator):
    """Remove suffix from selected object names"""
    bl_idname = "batch_rename.remove_suffix"
    bl_label = "Remove Suffix"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        suffix = settings.suffix_string
        
        if not suffix:
            self.report({'WARNING'}, "Suffix is empty")
            return {'CANCELLED'}
        
        count = 0
        for obj in context.selected_objects:
            if obj.name.endswith(suffix):
                obj.name = obj.name[:-len(suffix)]
                count += 1
        
        self.report({'INFO'}, f"Removed suffix from {count} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_sequential_rename(Operator):
    """Rename selected objects sequentially (e.g., Chair_001, Chair_002)"""
    bl_idname = "batch_rename.sequential_rename"
    bl_label = "Sequential Rename"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        base = settings.base_name
        start = settings.start_number
        padding = settings.zero_padding
        
        if not base:
            self.report({'WARNING'}, "Base name is empty")
            return {'CANCELLED'}
        
        # Sort by name for consistent ordering
        sorted_objects = sorted(context.selected_objects, key=lambda o: o.name)
        
        for i, obj in enumerate(sorted_objects):
            number = str(start + i).zfill(padding)
            obj.name = f"{base}_{number}"
        
        self.report({'INFO'}, f"Renamed {len(sorted_objects)} object(s) sequentially")
        return {'FINISHED'}


class BATCHRENAME_OT_convert_case(Operator):
    """Convert case of selected object names"""
    bl_idname = "batch_rename.convert_case"
    bl_label = "Convert Case"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        mode = settings.case_mode
        
        if mode == 'NONE':
            self.report({'INFO'}, "No case conversion selected")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            if mode == 'LOWER':
                obj.name = obj.name.lower()
            elif mode == 'UPPER':
                obj.name = obj.name.upper()
            elif mode == 'TITLE':
                obj.name = obj.name.title()
        
        self.report({'INFO'}, f"Converted case for {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_strip_numbers(Operator):
    """Remove trailing .001 style suffixes from selected objects (when safe)"""
    bl_idname = "batch_rename.strip_numbers"
    bl_label = "Strip .001 Suffixes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        # Pattern matches .001, .002, etc at end of name
        pattern = re.compile(r'\.\d{3}$')
        
        # Get all existing names to check for conflicts
        all_names = {obj.name for obj in bpy.data.objects}
        
        count = 0
        skipped = 0
        for obj in context.selected_objects:
            match = pattern.search(obj.name)
            if match:
                new_name = obj.name[:match.start()]
                # Check if the stripped name would conflict
                if new_name not in all_names or new_name == obj.name:
                    obj.name = new_name
                    all_names.add(new_name)  # Track the new name
                    count += 1
                else:
                    skipped += 1
        
        msg = f"Stripped suffixes from {count} object(s)"
        if skipped:
            msg += f" ({skipped} skipped due to conflicts)"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Collection Operators
# -----------------------------------------------------------------------------

class BATCHRENAME_OT_create_collection_from_selection(Operator):
    """Create a new collection from selected objects"""
    bl_idname = "batch_rename.create_collection"
    bl_label = "Create Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        
        # Determine collection name
        if settings.collection_name:
            coll_name = settings.collection_name
        elif context.active_object:
            coll_name = context.active_object.name
        else:
            coll_name = context.selected_objects[0].name
        
        # Create collection
        new_collection = bpy.data.collections.new(coll_name)
        context.scene.collection.children.link(new_collection)
        
        # Move objects to new collection
        for obj in context.selected_objects:
            # Remove from current collections
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            # Add to new collection
            new_collection.objects.link(obj)
        
        self.report({'INFO'}, f"Created collection '{new_collection.name}' with {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_rename_collection(Operator):
    """Rename the active collection"""
    bl_idname = "batch_rename.rename_collection"
    bl_label = "Rename Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.collection is not None
    
    def execute(self, context):
        settings = context.scene.batch_rename_settings
        collection = context.collection
        
        if not settings.collection_name:
            self.report({'WARNING'}, "Collection name is empty")
            return {'CANCELLED'}
        
        old_name = collection.name
        collection.name = settings.collection_name
        
        # Optionally propagate as prefix to child objects
        if settings.propagate_to_children:
            for obj in collection.objects:
                # Remove old prefix if present
                if obj.name.startswith(old_name + "_"):
                    obj.name = obj.name[len(old_name) + 1:]
                # Add new prefix
                obj.name = collection.name + "_" + obj.name
        
        self.report({'INFO'}, f"Renamed collection to '{collection.name}'")
        return {'FINISHED'}


class BATCHRENAME_OT_prefix_from_collection(Operator):
    """Add parent collection name as prefix to selected objects"""
    bl_idname = "batch_rename.prefix_from_collection"
    bl_label = "Prefix from Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            if obj.users_collection:
                # Use first collection the object belongs to
                coll_name = obj.users_collection[0].name
                if not obj.name.startswith(coll_name + "_"):
                    obj.name = coll_name + "_" + obj.name
                    count += 1
        
        self.report({'INFO'}, f"Added collection prefix to {count} object(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_sort_to_collections_by_name(Operator):
    """Sort selected objects into collections based on their base name (stripping trailing numbers)"""
    bl_idname = "batch_rename.sort_by_name"
    bl_label = "Sort by Name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.batch_rename_settings
        if settings.sort_by_name_scope == 'SELECTED':
            return bool(context.selected_objects)
        return bool(context.scene.objects)

    def _get_base_name(self, name, delimiter):
        """Strip trailing delimiter+numbers and Blender .NNN suffixes to get the base name."""
        # First strip Blender's .001 style suffixes
        base = re.sub(r'\.\d{3}$', '', name)

        # Then strip trailing delimiter+digits (e.g., _001, _01, _1)
        if delimiter:
            pattern = re.escape(delimiter) + r'\d+$'
            base = re.sub(pattern, '', base)

        # If stripping produced an empty string, fall back to original name
        return base if base else name

    def execute(self, context):
        settings = context.scene.batch_rename_settings
        delimiter = settings.sort_by_name_delimiter

        # Determine object source
        if settings.sort_by_name_scope == 'SELECTED':
            source_objects = list(context.selected_objects)
        else:
            source_objects = list(context.scene.objects)

        if not source_objects:
            self.report({'WARNING'}, "No objects to sort")
            return {'CANCELLED'}

        # Group objects by base name
        name_groups = {}
        for obj in source_objects:
            base = self._get_base_name(obj.name, delimiter)
            if base not in name_groups:
                name_groups[base] = []
            name_groups[base].append(obj)

        # Create/get collections and move objects
        moved_count = 0
        for base_name, objects in name_groups.items():
            if base_name in bpy.data.collections:
                collection = bpy.data.collections[base_name]
            else:
                collection = bpy.data.collections.new(base_name)
                context.scene.collection.children.link(collection)

            for obj in objects:
                # Remove from current collections
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
                moved_count += 1

        self.report({'INFO'}, f"Sorted {moved_count} object(s) into {len(name_groups)} collection(s)")
        return {'FINISHED'}


class BATCHRENAME_OT_sort_select_all_types(Operator):
    """Enable all object type filters for sort to collections"""
    bl_idname = "batch_rename.sort_select_all_types"
    bl_label = "Select All Types"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.batch_rename_settings
        for _blender_type, (_coll_name, prop_name) in SORT_TYPE_CONFIG.items():
            setattr(settings, prop_name, True)
        return {'FINISHED'}


class BATCHRENAME_OT_sort_deselect_all_types(Operator):
    """Disable all object type filters for sort to collections"""
    bl_idname = "batch_rename.sort_deselect_all_types"
    bl_label = "Deselect All Types"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.batch_rename_settings
        for _blender_type, (_coll_name, prop_name) in SORT_TYPE_CONFIG.items():
            setattr(settings, prop_name, False)
        return {'FINISHED'}


class BATCHRENAME_OT_sort_to_collections_by_type(Operator):
    """Sort objects into collections based on their type (filtered by enabled types)"""
    bl_idname = "batch_rename.sort_by_type"
    bl_label = "Sort by Type"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.batch_rename_settings
        if settings.sort_scope == 'SELECTED':
            return bool(context.selected_objects)
        return bool(context.scene.objects)

    def execute(self, context):
        settings = context.scene.batch_rename_settings

        # Determine object source based on scope
        if settings.sort_scope == 'SELECTED':
            source_objects = context.selected_objects
        else:
            source_objects = context.scene.objects

        # Build set of enabled types
        enabled_types = set()
        for blender_type, (_coll_name, prop_name) in SORT_TYPE_CONFIG.items():
            if getattr(settings, prop_name):
                enabled_types.add(blender_type)

        if not enabled_types:
            self.report({'WARNING'}, "No object types are enabled")
            return {'CANCELLED'}

        # Group objects by type, filtering to enabled types only
        type_groups = {}
        for obj in source_objects:
            if obj.type in enabled_types:
                if obj.type not in type_groups:
                    type_groups[obj.type] = []
                type_groups[obj.type].append(obj)

        if not type_groups:
            self.report({'INFO'}, "No objects matched the enabled types")
            return {'CANCELLED'}

        # Create/get collections and move objects
        moved_count = 0
        for obj_type, objects in type_groups.items():
            coll_name = SORT_TYPE_CONFIG[obj_type][0]

            if coll_name in bpy.data.collections:
                collection = bpy.data.collections[coll_name]
            else:
                collection = bpy.data.collections.new(coll_name)
                context.scene.collection.children.link(collection)

            for obj in objects:
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
                moved_count += 1

        self.report({'INFO'}, f"Sorted {moved_count} object(s) into {len(type_groups)} collection(s)")
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------

classes = (
    BATCHRENAME_OT_sync_data_names,
    BATCHRENAME_OT_select_mismatched,
    BATCHRENAME_OT_find_replace,
    BATCHRENAME_OT_add_prefix,
    BATCHRENAME_OT_add_suffix,
    BATCHRENAME_OT_remove_prefix,
    BATCHRENAME_OT_remove_suffix,
    BATCHRENAME_OT_sequential_rename,
    BATCHRENAME_OT_convert_case,
    BATCHRENAME_OT_strip_numbers,
    BATCHRENAME_OT_create_collection_from_selection,
    BATCHRENAME_OT_rename_collection,
    BATCHRENAME_OT_prefix_from_collection,
    BATCHRENAME_OT_sort_to_collections_by_name,
    BATCHRENAME_OT_sort_select_all_types,
    BATCHRENAME_OT_sort_deselect_all_types,
    BATCHRENAME_OT_sort_to_collections_by_type,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
