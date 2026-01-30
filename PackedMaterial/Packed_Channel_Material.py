# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025

bl_info = {
    "name": "Enhanced PBR Packed Material Setup",
    "author": "Spencer",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "Shader Editor > N-panel > Packed Shader Setup | Properties > Material",
    "description": (
        "Creates PBR materials with user-configurable packed channel maps. "
        "Supports normal map green channel flip, emission maps, displacement, "
        "channel presets, batch processing, and modern node compatibility."
    ),
    "doc_url": "",
    "tracker_url": "",
    "category": "Material",
}

import bpy
import os
import logging
from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    StringProperty,
    PointerProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
    FloatProperty,
    IntProperty,
)
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
    OperatorFileListElement,
    AddonPreferences,
)

# Configure logging for debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# =============================================================================
# Version Compatibility Utilities
# =============================================================================

def get_blender_version():
    """Return Blender version as tuple (major, minor, patch)."""
    return bpy.app.version


def is_blender_4_plus():
    """Check if running Blender 4.0 or newer."""
    return bpy.app.version >= (4, 0, 0)


def is_blender_3_4_plus():
    """Check if running Blender 3.4 or newer (when Separate/Combine Color nodes were added)."""
    return bpy.app.version >= (3, 4, 0)


def get_principled_socket(bsdf, socket_names):
    """
    Safely get a socket from Principled BSDF by trying multiple possible names.
    
    Args:
        bsdf: The Principled BSDF node
        socket_names: List of possible socket names to try (in order of preference)
    
    Returns:
        The socket if found, None otherwise
    """
    if isinstance(socket_names, str):
        socket_names = [socket_names]
    
    for name in socket_names:
        socket = bsdf.inputs.get(name)
        if socket is not None:
            return socket
    return None


# =============================================================================
# Constants and Enums
# =============================================================================

# Channel usage options for packed maps
CHANNEL_ITEMS = [
    ('NONE', "None", "Ignore this channel"),
    ('METALLIC', "Metallic", "Use for Metallic input"),
    ('ROUGHNESS', "Roughness", "Use for Roughness input"),
    ('AO', "Ambient Occlusion", "Multiply with Base Color"),
    ('EMISSION', "Emission Strength", "Link to Emission Strength"),
    ('ALPHA', "Alpha (Transparency)", "Link to Material Alpha"),
    ('SPECULAR', "Specular", "Use for Specular/IOR Level input"),
    ('DISPLACEMENT', "Displacement Height", "Use for Displacement (requires setup)"),
    ('SUBSURFACE', "Subsurface Weight", "Use for Subsurface Scattering weight"),
]

# Preset configurations for common packed map formats
PRESET_ITEMS = [
    ('CUSTOM', "Custom", "User-defined channel configuration"),
    ('UNITY_HDRP', "Unity HDRP (MADS)", "Metallic(R), AO(G), Detail(B), Smoothness(A)"),
    ('UNITY_URP', "Unity URP", "Metallic(R), Occlusion(G), unused(B), Smoothness(A)"),
    ('UNREAL', "Unreal Engine (ORM)", "AO(R), Roughness(G), Metallic(B)"),
    ('SUBSTANCE', "Substance (ORM)", "AO(R), Roughness(G), Metallic(B)"),
    ('GLTF', "glTF (ORM)", "Occlusion(R), Roughness(G), Metallic(B)"),
    ('SOURCE', "Source Engine", "Phong Exp(R), Metallic/Env(G), unused(B), Phong mask(A)"),
    ('GODOT', "Godot Engine (ORM)", "AO(R), Roughness(G), Metallic(B)"),
]

# Texture coordinate options
TEXCOORD_ITEMS = [
    ('UV', "UV", "Use UV coordinates"),
    ('GENERATED', "Generated", "Use generated coordinates"),
    ('OBJECT', "Object", "Use object coordinates"),
    ('CAMERA', "Camera", "Use camera coordinates"),
]

# Image file filter for file browsers
IMAGE_FILTER = "*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp;*.tga;*.exr;*.hdr;*.webp"


# =============================================================================
# Property Groups
# =============================================================================

class EPM_ChannelSettings(PropertyGroup):
    """Settings for a single channel in the packed map."""
    
    channel_usage: EnumProperty(
        name="Usage",
        description="What does this channel represent?",
        items=CHANNEL_ITEMS,
        default='NONE'
    )
    
    channel_invert: BoolProperty(
        name="Invert",
        description="Invert this channel's values (e.g., smoothness to roughness)",
        default=False
    )


class EPM_SceneProperties(PropertyGroup):
    """Main property group for the addon."""
    
    # Material Settings
    material_name: StringProperty(
        name="Material Name",
        description="Name for the new material",
        default=""
    )
    
    # Texture Maps
    col_image: PointerProperty(
        name="Color Map",
        description="Base Color (Albedo/Diffuse) texture",
        type=bpy.types.Image
    )
    
    normal_image: PointerProperty(
        name="Normal Map",
        description="Normal Map texture (tangent space)",
        type=bpy.types.Image
    )
    
    emission_image: PointerProperty(
        name="Emission Map",
        description="Emission color texture for emissive areas",
        type=bpy.types.Image
    )
    
    packed_image: PointerProperty(
        name="Packed Map",
        description="RGBA-packed map containing multiple PBR channels",
        type=bpy.types.Image
    )
    
    displacement_image: PointerProperty(
        name="Displacement Map",
        description="Separate displacement/height map (optional)",
        type=bpy.types.Image
    )
    
    # Normal Map Settings
    normal_invert_green: BoolProperty(
        name="Flip Green Channel",
        description="Invert the green (Y) channel of the normal map for DirectX/OpenGL conversion",
        default=False
    )
    
    normal_strength: FloatProperty(
        name="Normal Strength",
        description="Strength of the normal map effect",
        default=1.0,
        min=0.0,
        max=5.0,
        soft_max=2.0,
        step=10,
        precision=3
    )
    
    # Displacement Settings
    displacement_strength: FloatProperty(
        name="Displacement Strength",
        description="Strength/scale of displacement",
        default=0.1,
        min=0.0,
        max=10.0,
        soft_max=1.0,
        step=1,
        precision=3
    )
    
    displacement_midlevel: FloatProperty(
        name="Displacement Midlevel",
        description="Midlevel value for displacement (0.5 = centered)",
        default=0.5,
        min=0.0,
        max=1.0,
        step=1,
        precision=3
    )
    
    use_displacement: BoolProperty(
        name="Enable Displacement",
        description="Add displacement node setup (requires Cycles and subdivision)",
        default=False
    )
    
    # Texture Coordinate Settings
    texcoord_type: EnumProperty(
        name="Texture Coordinates",
        description="Type of texture coordinates to use",
        items=TEXCOORD_ITEMS,
        default='UV'
    )
    
    uv_map_name: StringProperty(
        name="UV Map",
        description="Name of UV map to use (leave empty for active UV)",
        default=""
    )
    
    # Preset System
    preset: EnumProperty(
        name="Preset",
        description="Quick setup for common packed channel configurations",
        items=PRESET_ITEMS,
        default='CUSTOM',
        update=lambda self, ctx: apply_preset(self, ctx)
    )
    
    # Channel Settings (R, G, B, A)
    channel_r: PointerProperty(type=EPM_ChannelSettings)
    channel_g: PointerProperty(type=EPM_ChannelSettings)
    channel_b: PointerProperty(type=EPM_ChannelSettings)
    channel_a: PointerProperty(type=EPM_ChannelSettings)
    
    # Material Options
    use_alpha_blend: BoolProperty(
        name="Alpha Blend Mode",
        description="Set material blend mode to Alpha Blend (for transparent materials)",
        default=False
    )
    
    apply_to_all_selected: BoolProperty(
        name="Apply to All Selected",
        description="Apply material to all selected mesh objects instead of just active",
        default=False
    )


def apply_preset(props, context):
    """Apply a preset configuration to the channel settings."""
    preset = props.preset
    
    if preset == 'CUSTOM':
        return  # Don't modify custom settings
    
    # Reset all channels first
    props.channel_r.channel_usage = 'NONE'
    props.channel_r.channel_invert = False
    props.channel_g.channel_usage = 'NONE'
    props.channel_g.channel_invert = False
    props.channel_b.channel_usage = 'NONE'
    props.channel_b.channel_invert = False
    props.channel_a.channel_usage = 'NONE'
    props.channel_a.channel_invert = False
    
    if preset == 'UNITY_HDRP':
        props.channel_r.channel_usage = 'METALLIC'
        props.channel_g.channel_usage = 'AO'
        props.channel_a.channel_usage = 'ROUGHNESS'
        props.channel_a.channel_invert = True  # Smoothness to Roughness
    
    elif preset == 'UNITY_URP':
        props.channel_r.channel_usage = 'METALLIC'
        props.channel_g.channel_usage = 'AO'
        props.channel_a.channel_usage = 'ROUGHNESS'
        props.channel_a.channel_invert = True  # Smoothness to Roughness
    
    elif preset in ('UNREAL', 'SUBSTANCE', 'GLTF', 'GODOT'):
        props.channel_r.channel_usage = 'AO'
        props.channel_g.channel_usage = 'ROUGHNESS'
        props.channel_b.channel_usage = 'METALLIC'
    
    elif preset == 'SOURCE':
        props.channel_g.channel_usage = 'METALLIC'
        props.channel_a.channel_usage = 'SPECULAR'


# =============================================================================
# Utility Functions
# =============================================================================

def load_image_safely(filepath):
    """
    Load an image safely, checking for existing images to avoid duplicates.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        The loaded image or None if loading failed
    """
    if not filepath or not os.path.isfile(filepath):
        logger.warning(f"Invalid filepath: {filepath}")
        return None
    
    try:
        img = bpy.data.images.load(filepath, check_existing=True)
        logger.info(f"Loaded image: {img.name}")
        return img
    except RuntimeError as e:
        logger.error(f"Failed to load image '{filepath}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading image '{filepath}': {e}")
        return None


def create_node(node_tree, node_type, label="", location=(0, 0)):
    """
    Create a new node with common setup.
    
    Args:
        node_tree: The node tree to add the node to
        node_type: Type string for the node (e.g., 'ShaderNodeTexImage')
        label: Optional label for the node
        location: (x, y) location tuple
        
    Returns:
        The created node
    """
    node = node_tree.nodes.new(type=node_type)
    if label:
        node.label = label
    node.location = location
    return node


def create_separate_color_node(node_tree, location=(0, 0)):
    """
    Create a Separate Color node (version-compatible).
    Uses SeparateColor for 3.4+ or SeparateRGB for older versions.
    """
    if is_blender_3_4_plus():
        node = node_tree.nodes.new(type='ShaderNodeSeparateColor')
        node.mode = 'RGB'
    else:
        node = node_tree.nodes.new(type='ShaderNodeSeparateRGB')
    node.location = location
    return node


def create_combine_color_node(node_tree, location=(0, 0)):
    """
    Create a Combine Color node (version-compatible).
    Uses CombineColor for 3.4+ or CombineRGB for older versions.
    """
    if is_blender_3_4_plus():
        node = node_tree.nodes.new(type='ShaderNodeCombineColor')
        node.mode = 'RGB'
    else:
        node = node_tree.nodes.new(type='ShaderNodeCombineRGB')
    node.location = location
    return node


def get_separate_color_outputs(node):
    """Get the R, G, B output sockets from a Separate Color/RGB node."""
    if is_blender_3_4_plus():
        return node.outputs['Red'], node.outputs['Green'], node.outputs['Blue']
    else:
        return node.outputs['R'], node.outputs['G'], node.outputs['B']


def get_combine_color_inputs(node):
    """Get the R, G, B input sockets from a Combine Color/RGB node."""
    if is_blender_3_4_plus():
        return node.inputs['Red'], node.inputs['Green'], node.inputs['Blue']
    else:
        return node.inputs['R'], node.inputs['G'], node.inputs['B']


def create_mix_node(node_tree, blend_type='MIX', location=(0, 0)):
    """
    Create a Mix node (version-compatible).
    Uses ShaderNodeMix for 3.4+ or ShaderNodeMixRGB for older versions.
    """
    if is_blender_3_4_plus():
        node = node_tree.nodes.new(type='ShaderNodeMix')
        node.data_type = 'RGBA'
        node.blend_type = blend_type
        node.clamp_factor = True
    else:
        node = node_tree.nodes.new(type='ShaderNodeMixRGB')
        node.blend_type = blend_type
    node.location = location
    return node


def get_mix_node_sockets(node):
    """
    Get the factor, color1, color2 inputs and result output for a Mix node.
    Returns tuple: (factor_input, color1_input, color2_input, result_output)
    """
    if is_blender_3_4_plus():
        return (
            node.inputs['Factor'],
            node.inputs['A'],  # In Blender 4.0+ Mix node
            node.inputs['B'],
            node.outputs['Result']
        )
    else:
        return (
            node.inputs['Fac'],
            node.inputs['Color1'],
            node.inputs['Color2'],
            node.outputs['Color']
        )


def set_mix_node_factor(node, value):
    """Set the factor/fac value for a mix node."""
    if is_blender_3_4_plus():
        node.inputs['Factor'].default_value = value
    else:
        node.inputs['Fac'].default_value = value


# =============================================================================
# Image Loading Operators
# =============================================================================

class EPM_OT_LoadColorImage(Operator, ImportHelper):
    """Load a base color (albedo/diffuse) texture"""
    bl_idname = "epm.load_color_image"
    bl_label = "Load Color Image"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')
    filter_glob: StringProperty(default=IMAGE_FILTER, options={'HIDDEN'})
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}
        
        filepath = os.path.join(self.directory, self.files[0].name)
        img = load_image_safely(filepath)
        
        if not img:
            self.report({'ERROR'}, f"Could not load image: {filepath}")
            return {'CANCELLED'}
        
        context.scene.epm_props.col_image = img
        self.report({'INFO'}, f"Loaded color image: {img.name}")
        return {'FINISHED'}


class EPM_OT_LoadNormalImage(Operator, ImportHelper):
    """Load a normal map texture"""
    bl_idname = "epm.load_normal_image"
    bl_label = "Load Normal Image"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')
    filter_glob: StringProperty(default=IMAGE_FILTER, options={'HIDDEN'})
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}
        
        filepath = os.path.join(self.directory, self.files[0].name)
        img = load_image_safely(filepath)
        
        if not img:
            self.report({'ERROR'}, f"Could not load image: {filepath}")
            return {'CANCELLED'}
        
        context.scene.epm_props.normal_image = img
        self.report({'INFO'}, f"Loaded normal image: {img.name}")
        return {'FINISHED'}


class EPM_OT_LoadEmissionImage(Operator, ImportHelper):
    """Load an emission map texture"""
    bl_idname = "epm.load_emission_image"
    bl_label = "Load Emission Image"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')
    filter_glob: StringProperty(default=IMAGE_FILTER, options={'HIDDEN'})
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}
        
        filepath = os.path.join(self.directory, self.files[0].name)
        img = load_image_safely(filepath)
        
        if not img:
            self.report({'ERROR'}, f"Could not load image: {filepath}")
            return {'CANCELLED'}
        
        context.scene.epm_props.emission_image = img
        self.report({'INFO'}, f"Loaded emission image: {img.name}")
        return {'FINISHED'}


class EPM_OT_LoadPackedImage(Operator, ImportHelper):
    """Load a packed channel map (RGBA with multiple PBR channels)"""
    bl_idname = "epm.load_packed_image"
    bl_label = "Load Packed Image"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')
    filter_glob: StringProperty(default=IMAGE_FILTER, options={'HIDDEN'})
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}
        
        filepath = os.path.join(self.directory, self.files[0].name)
        img = load_image_safely(filepath)
        
        if not img:
            self.report({'ERROR'}, f"Could not load image: {filepath}")
            return {'CANCELLED'}
        
        context.scene.epm_props.packed_image = img
        self.report({'INFO'}, f"Loaded packed image: {img.name}")
        return {'FINISHED'}


class EPM_OT_LoadDisplacementImage(Operator, ImportHelper):
    """Load a displacement/height map texture"""
    bl_idname = "epm.load_displacement_image"
    bl_label = "Load Displacement Image"
    bl_options = {'REGISTER', 'UNDO'}
    
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')
    filter_glob: StringProperty(default=IMAGE_FILTER, options={'HIDDEN'})
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}
        
        filepath = os.path.join(self.directory, self.files[0].name)
        img = load_image_safely(filepath)
        
        if not img:
            self.report({'ERROR'}, f"Could not load image: {filepath}")
            return {'CANCELLED'}
        
        context.scene.epm_props.displacement_image = img
        self.report({'INFO'}, f"Loaded displacement image: {img.name}")
        return {'FINISHED'}


# =============================================================================
# Clear/Reset Operator
# =============================================================================

class EPM_OT_ClearAllImages(Operator):
    """Clear all loaded images from the addon"""
    bl_idname = "epm.clear_all_images"
    bl_label = "Clear All Images"
    bl_description = "Remove all image references from the addon panel"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.epm_props
        props.col_image = None
        props.normal_image = None
        props.emission_image = None
        props.packed_image = None
        props.displacement_image = None
        props.material_name = ""
        props.preset = 'CUSTOM'
        
        # Reset channel settings
        for channel in [props.channel_r, props.channel_g, props.channel_b, props.channel_a]:
            channel.channel_usage = 'NONE'
            channel.channel_invert = False
        
        self.report({'INFO'}, "All images and settings cleared")
        return {'FINISHED'}


# =============================================================================
# Material Creation Operator
# =============================================================================

class EPM_OT_CreateMaterial(Operator):
    """Create a PBR material with the configured texture maps and channel settings"""
    bl_idname = "epm.create_material"
    bl_label = "Create Material"
    bl_description = (
        "Create a PBR material using the loaded textures and packed channel configuration. "
        "Supports normal map flipping, emission, displacement, and various presets."
    )
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Check if the operator can run."""
        props = context.scene.epm_props
        # At least one texture should be loaded
        return any([
            props.col_image,
            props.normal_image,
            props.emission_image,
            props.packed_image,
            props.displacement_image
        ])
    
    def execute(self, context):
        props = context.scene.epm_props
        
        # Determine material name
        mat_name = props.material_name.strip() or "Enhanced_Packed_Material"
        
        # Create new material
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Track node positions for auto-layout
        x_offset = -800
        y_base = 300
        
        # Create Principled BSDF and Output
        bsdf = create_node(mat.node_tree, 'ShaderNodeBsdfPrincipled', "Principled BSDF", (300, y_base))
        output = create_node(mat.node_tree, 'ShaderNodeOutputMaterial', "Material Output", (600, y_base))
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Create texture coordinate and mapping nodes if needed
        texcoord_node = None
        mapping_node = None
        
        if props.texcoord_type != 'UV' or props.uv_map_name:
            texcoord_node = create_node(mat.node_tree, 'ShaderNodeTexCoord', "Texture Coordinate", (x_offset - 400, y_base))
            mapping_node = create_node(mat.node_tree, 'ShaderNodeMapping', "Mapping", (x_offset - 200, y_base))
            
            # Connect appropriate output based on coordinate type
            coord_output = props.texcoord_type.capitalize()
            if props.texcoord_type == 'UV' and props.uv_map_name:
                # Use UV Map node for specific UV set
                uv_node = create_node(mat.node_tree, 'ShaderNodeUVMap', "UV Map", (x_offset - 400, y_base - 100))
                uv_node.uv_map = props.uv_map_name
                links.new(uv_node.outputs['UV'], mapping_node.inputs['Vector'])
            else:
                links.new(texcoord_node.outputs[coord_output], mapping_node.inputs['Vector'])
        
        def get_vector_input():
            """Get the vector output to connect to image textures."""
            if mapping_node:
                return mapping_node.outputs['Vector']
            return None
        
        # ---------------------------------------------------------------------
        # 1) BASE COLOR MAP
        # ---------------------------------------------------------------------
        if props.col_image:
            col_node = create_node(mat.node_tree, 'ShaderNodeTexImage', "Base Color", (x_offset, y_base + 200))
            col_node.image = props.col_image
            col_node.image.colorspace_settings.name = 'sRGB'
            
            if vector_input := get_vector_input():
                links.new(vector_input, col_node.inputs['Vector'])
            
            links.new(col_node.outputs['Color'], bsdf.inputs['Base Color'])
            
            # Connect alpha to material alpha
            alpha_socket = get_principled_socket(bsdf, ['Alpha'])
            if alpha_socket:
                links.new(col_node.outputs['Alpha'], alpha_socket)
        
        # ---------------------------------------------------------------------
        # 2) NORMAL MAP
        # ---------------------------------------------------------------------
        if props.normal_image:
            normal_tex = create_node(mat.node_tree, 'ShaderNodeTexImage', "Normal Map", (x_offset, y_base))
            normal_tex.image = props.normal_image
            normal_tex.image.colorspace_settings.name = 'Non-Color'
            
            if vector_input := get_vector_input():
                links.new(vector_input, normal_tex.inputs['Vector'])
            
            # Create normal map node
            normal_map = create_node(mat.node_tree, 'ShaderNodeNormalMap', "Normal Map Node", (x_offset + 400, y_base))
            normal_map.inputs['Strength'].default_value = props.normal_strength
            
            if props.normal_invert_green:
                # Flip green channel (DirectX to OpenGL or vice versa)
                sep_node = create_separate_color_node(mat.node_tree, (x_offset + 150, y_base))
                sep_node.label = "Separate Normal"
                
                inv_node = create_node(mat.node_tree, 'ShaderNodeInvert', "Invert Green", (x_offset + 250, y_base - 50))
                
                comb_node = create_combine_color_node(mat.node_tree, (x_offset + 350, y_base))
                comb_node.label = "Combine Normal"
                
                links.new(normal_tex.outputs['Color'], sep_node.inputs[0])
                
                r_out, g_out, b_out = get_separate_color_outputs(sep_node)
                r_in, g_in, b_in = get_combine_color_inputs(comb_node)
                
                links.new(g_out, inv_node.inputs['Color'])
                links.new(r_out, r_in)
                links.new(inv_node.outputs['Color'], g_in)
                links.new(b_out, b_in)
                
                links.new(comb_node.outputs[0], normal_map.inputs['Color'])
            else:
                links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
            
            normal_socket = get_principled_socket(bsdf, ['Normal'])
            if normal_socket:
                links.new(normal_map.outputs['Normal'], normal_socket)
        
        # ---------------------------------------------------------------------
        # 3) EMISSION MAP
        # ---------------------------------------------------------------------
        if props.emission_image:
            emiss_node = create_node(mat.node_tree, 'ShaderNodeTexImage', "Emission Map", (x_offset, y_base - 200))
            emiss_node.image = props.emission_image
            emiss_node.image.colorspace_settings.name = 'sRGB'
            
            if vector_input := get_vector_input():
                links.new(vector_input, emiss_node.inputs['Vector'])
            
            # Try different emission socket names for compatibility
            emission_socket = get_principled_socket(bsdf, ['Emission Color', 'Emission'])
            if emission_socket:
                links.new(emiss_node.outputs['Color'], emission_socket)
            
            # Set emission strength to 1 if socket exists
            strength_socket = get_principled_socket(bsdf, ['Emission Strength'])
            if strength_socket:
                strength_socket.default_value = 1.0
        
        # ---------------------------------------------------------------------
        # 4) PACKED MAP (Metallic, Roughness, AO, etc.)
        # ---------------------------------------------------------------------
        if props.packed_image:
            pack_node = create_node(mat.node_tree, 'ShaderNodeTexImage', "Packed Map", (x_offset, y_base - 400))
            pack_node.image = props.packed_image
            pack_node.image.colorspace_settings.name = 'Non-Color'
            
            if vector_input := get_vector_input():
                links.new(vector_input, pack_node.inputs['Vector'])
            
            # Create Separate Color node
            sep_node = create_separate_color_node(mat.node_tree, (x_offset + 200, y_base - 400))
            sep_node.label = "Separate Packed Channels"
            links.new(pack_node.outputs['Color'], sep_node.inputs[0])
            
            r_out, g_out, b_out = get_separate_color_outputs(sep_node)
            
            # Channel mapping
            channel_outputs = {
                'R': r_out,
                'G': g_out,
                'B': b_out,
                'A': pack_node.outputs['Alpha']
            }
            
            channel_settings = {
                'R': props.channel_r,
                'G': props.channel_g,
                'B': props.channel_b,
                'A': props.channel_a
            }
            
            # Track AO nodes for potential chaining
            ao_outputs = []
            
            for channel_name, channel_output in channel_outputs.items():
                settings = channel_settings[channel_name]
                usage = settings.channel_usage
                invert = settings.channel_invert
                
                if usage == 'NONE':
                    continue
                
                # Apply inversion if needed
                final_output = channel_output
                if invert:
                    inv_node = create_node(mat.node_tree, 'ShaderNodeInvert', 
                                          f"Invert {channel_name}", (x_offset + 350, y_base - 450))
                    links.new(channel_output, inv_node.inputs['Color'])
                    final_output = inv_node.outputs['Color']
                
                # Route to appropriate socket
                self._handle_channel_usage(
                    context, mat, nodes, links, bsdf,
                    usage, final_output, channel_name, ao_outputs
                )
        
        # ---------------------------------------------------------------------
        # 5) DISPLACEMENT MAP (separate)
        # ---------------------------------------------------------------------
        if props.use_displacement and props.displacement_image:
            disp_tex = create_node(mat.node_tree, 'ShaderNodeTexImage', "Displacement Map", (x_offset, y_base - 600))
            disp_tex.image = props.displacement_image
            disp_tex.image.colorspace_settings.name = 'Non-Color'
            
            if vector_input := get_vector_input():
                links.new(vector_input, disp_tex.inputs['Vector'])
            
            disp_node = create_node(mat.node_tree, 'ShaderNodeDisplacement', "Displacement", (400, y_base - 200))
            disp_node.inputs['Scale'].default_value = props.displacement_strength
            disp_node.inputs['Midlevel'].default_value = props.displacement_midlevel
            
            links.new(disp_tex.outputs['Color'], disp_node.inputs['Height'])
            links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])
            
            # Set displacement method
            mat.cycles.displacement_method = 'BOTH'
        
        # ---------------------------------------------------------------------
        # 6) MATERIAL SETTINGS
        # ---------------------------------------------------------------------
        if props.use_alpha_blend:
            mat.blend_method = 'BLEND'
            mat.shadow_method = 'HASHED'
        
        # ---------------------------------------------------------------------
        # 7) APPLY TO OBJECTS
        # ---------------------------------------------------------------------
        applied_count = 0
        
        if props.apply_to_all_selected:
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    obj.data.materials.append(mat)
                    applied_count += 1
        else:
            obj = context.object
            if obj and obj.type == 'MESH':
                obj.data.materials.append(mat)
                applied_count = 1
        
        # Report success
        if applied_count > 0:
            self.report({'INFO'}, f"Material '{mat.name}' created and applied to {applied_count} object(s)")
        else:
            self.report({'INFO'}, f"Material '{mat.name}' created (no mesh object selected)")
        
        return {'FINISHED'}
    
    def _handle_channel_usage(self, context, mat, nodes, links, bsdf, 
                               usage, channel_output, channel_name, ao_outputs):
        """Handle routing a channel to its appropriate destination."""
        
        if usage == 'METALLIC':
            socket = get_principled_socket(bsdf, ['Metallic'])
            if socket:
                links.new(channel_output, socket)
        
        elif usage == 'ROUGHNESS':
            socket = get_principled_socket(bsdf, ['Roughness'])
            if socket:
                links.new(channel_output, socket)
        
        elif usage == 'SPECULAR':
            # Blender 4.0+ uses "Specular IOR Level", older uses "Specular"
            socket = get_principled_socket(bsdf, ['Specular IOR Level', 'Specular'])
            if socket:
                links.new(channel_output, socket)
        
        elif usage == 'AO':
            # Multiply AO with Base Color
            base_color_socket = bsdf.inputs.get('Base Color')
            if base_color_socket and base_color_socket.is_linked:
                # Create mix node for AO multiplication
                ao_mix = create_mix_node(mat.node_tree, 'MULTIPLY', (150, 200))
                ao_mix.label = f"AO Multiply ({channel_name})"
                
                factor_in, color1_in, color2_in, result_out = get_mix_node_sockets(ao_mix)
                set_mix_node_factor(ao_mix, 1.0)
                
                # Get current connection to base color
                existing_link = base_color_socket.links[0]
                prev_output = existing_link.from_socket
                links.remove(existing_link)
                
                # Insert AO multiplication
                links.new(prev_output, color1_in)
                links.new(channel_output, color2_in)
                links.new(result_out, base_color_socket)
        
        elif usage == 'EMISSION':
            # Single-channel emission strength
            strength_socket = get_principled_socket(bsdf, ['Emission Strength'])
            if strength_socket:
                links.new(channel_output, strength_socket)
                # Set emission color to white
                emission_socket = get_principled_socket(bsdf, ['Emission Color', 'Emission'])
                if emission_socket:
                    emission_socket.default_value = (1.0, 1.0, 1.0, 1.0)
        
        elif usage == 'ALPHA':
            socket = get_principled_socket(bsdf, ['Alpha'])
            if socket:
                links.new(channel_output, socket)
        
        elif usage == 'SUBSURFACE':
            # Blender 4.0+ uses "Subsurface Weight", older uses "Subsurface"
            socket = get_principled_socket(bsdf, ['Subsurface Weight', 'Subsurface'])
            if socket:
                links.new(channel_output, socket)
        
        elif usage == 'DISPLACEMENT':
            # Create displacement from packed channel
            disp_node = nodes.get("Displacement")
            if not disp_node:
                disp_node = create_node(mat.node_tree, 'ShaderNodeDisplacement', "Displacement", (400, -200))
                disp_node.inputs['Scale'].default_value = context.scene.epm_props.displacement_strength
                disp_node.inputs['Midlevel'].default_value = context.scene.epm_props.displacement_midlevel
                
                output = nodes.get("Material Output")
                if output:
                    links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])
                    mat.cycles.displacement_method = 'BOTH'
            
            links.new(channel_output, disp_node.inputs['Height'])


# =============================================================================
# UI Panels
# =============================================================================

class EPM_PT_MainPanel(Panel):
    """Main panel in the Shader Editor sidebar."""
    bl_label = "Packed PBR Material"
    bl_idname = "EPM_PT_main_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Packed Shader Setup"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.epm_props
        
        # Material Name
        box = layout.box()
        box.label(text="Material Name", icon='MATERIAL')
        box.prop(props, "material_name", text="")
        
        # Create button at top for convenience
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("epm.create_material", text="Create Material", icon='CHECKMARK')


class EPM_PT_TextureMaps(Panel):
    """Texture maps sub-panel."""
    bl_label = "Texture Maps"
    bl_idname = "EPM_PT_texture_maps"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Packed Shader Setup"
    bl_parent_id = "EPM_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.epm_props
        
        # Color Map
        box = layout.box()
        box.label(text="Base Color", icon='IMAGE_RGB')
        row = box.row(align=True)
        row.prop(props, "col_image", text="")
        row.operator("epm.load_color_image", text="", icon='FILE_FOLDER')
        
        # Normal Map
        box = layout.box()
        box.label(text="Normal Map", icon='NORMALS_FACE')
        row = box.row(align=True)
        row.prop(props, "normal_image", text="")
        row.operator("epm.load_normal_image", text="", icon='FILE_FOLDER')
        
        col = box.column(align=True)
        col.prop(props, "normal_invert_green")
        col.prop(props, "normal_strength")
        
        # Emission Map
        box = layout.box()
        box.label(text="Emission Map", icon='LIGHT_SUN')
        row = box.row(align=True)
        row.prop(props, "emission_image", text="")
        row.operator("epm.load_emission_image", text="", icon='FILE_FOLDER')
        
        # Displacement Map
        box = layout.box()
        box.label(text="Displacement Map", icon='MOD_DISPLACE')
        row = box.row(align=True)
        row.prop(props, "displacement_image", text="")
        row.operator("epm.load_displacement_image", text="", icon='FILE_FOLDER')
        
        col = box.column(align=True)
        col.prop(props, "use_displacement")
        if props.use_displacement:
            col.prop(props, "displacement_strength")
            col.prop(props, "displacement_midlevel")


class EPM_PT_PackedChannels(Panel):
    """Packed channel configuration sub-panel."""
    bl_label = "Packed Channels"
    bl_idname = "EPM_PT_packed_channels"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Packed Shader Setup"
    bl_parent_id = "EPM_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.epm_props
        
        # Packed Image
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "packed_image", text="Packed Map")
        row.operator("epm.load_packed_image", text="", icon='FILE_FOLDER')
        
        # Preset selector
        box.prop(props, "preset")
        
        # Channel configuration
        if props.packed_image:
            col = box.column(align=True)
            col.separator()
            
            for channel, label in [('channel_r', 'R'), ('channel_g', 'G'), 
                                   ('channel_b', 'B'), ('channel_a', 'A')]:
                channel_props = getattr(props, channel)
                row = col.row(align=True)
                row.label(text=f"{label}:")
                row.prop(channel_props, "channel_usage", text="")
                row.prop(channel_props, "channel_invert", text="", icon='ARROW_LEFTRIGHT')


class EPM_PT_Options(Panel):
    """Options sub-panel."""
    bl_label = "Options"
    bl_idname = "EPM_PT_options"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Packed Shader Setup"
    bl_parent_id = "EPM_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.epm_props
        
        # Texture Coordinates
        box = layout.box()
        box.label(text="Texture Coordinates", icon='UV')
        box.prop(props, "texcoord_type", text="")
        if props.texcoord_type == 'UV':
            box.prop(props, "uv_map_name", text="UV Map")
        
        # Material Options
        box = layout.box()
        box.label(text="Material Options", icon='OPTIONS')
        box.prop(props, "use_alpha_blend")
        box.prop(props, "apply_to_all_selected")
        
        # Clear button
        layout.separator()
        layout.operator("epm.clear_all_images", text="Clear All", icon='X')


# Also register panel in Material Properties for convenience
class EPM_PT_MaterialProperties(Panel):
    """Panel in Material Properties."""
    bl_label = "Packed PBR Setup"
    bl_idname = "EPM_PT_material_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.epm_props
        
        # Quick access controls
        layout.prop(props, "material_name", text="Name")
        
        row = layout.row(align=True)
        row.prop(props, "col_image", text="Color")
        row.operator("epm.load_color_image", text="", icon='FILE_FOLDER')
        
        row = layout.row(align=True)
        row.prop(props, "packed_image", text="Packed")
        row.operator("epm.load_packed_image", text="", icon='FILE_FOLDER')
        
        layout.prop(props, "preset")
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("epm.create_material", icon='CHECKMARK')


# =============================================================================
# Registration
# =============================================================================

classes = (
    # Property Groups
    EPM_ChannelSettings,
    EPM_SceneProperties,
    # Operators
    EPM_OT_LoadColorImage,
    EPM_OT_LoadNormalImage,
    EPM_OT_LoadEmissionImage,
    EPM_OT_LoadPackedImage,
    EPM_OT_LoadDisplacementImage,
    EPM_OT_ClearAllImages,
    EPM_OT_CreateMaterial,
    # Panels
    EPM_PT_MainPanel,
    EPM_PT_TextureMaps,
    EPM_PT_PackedChannels,
    EPM_PT_Options,
    EPM_PT_MaterialProperties,
)


def register():
    """Register all classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.epm_props = PointerProperty(type=EPM_SceneProperties)
    
    logger.info(f"Registered {bl_info['name']} v{'.'.join(map(str, bl_info['version']))}")


def unregister():
    """Unregister all classes and clean up properties."""
    # Remove scene property first
    if hasattr(bpy.types.Scene, 'epm_props'):
        del bpy.types.Scene.epm_props
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    
    logger.info(f"Unregistered {bl_info['name']}")


if __name__ == "__main__":
    register()
