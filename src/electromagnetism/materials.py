"""One shared palette keeps the whole lesson visually consistent."""

import bpy
from .config import PALETTE


def make_materials():
    result = {}
    for name, color in PALETTE.items():
        mat = bpy.data.materials.new("EM / " + name)
        mat.diffuse_color = color
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = 0.28 if "copper" in name else 0.4
        shader.inputs["Metallic"].default_value = 0.95 if name in ("copper", "silver", "copper_light") else 0.0
        result[name] = mat

        # Emission-based text stays legible under changing scene lighting.
        ink = bpy.data.materials.new("EM / ink / " + name)
        ink.diffuse_color = color
        ink.use_nodes = True
        nodes = ink.node_tree.nodes
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = color
        emission.inputs["Strength"].default_value = 1.0
        ink.node_tree.links.new(emission.outputs[0], out.inputs["Surface"])
        result["ink_" + name] = ink
    # Subtle procedural texture gives the apparatus real material surfaces.
    for name, colour, roughness in [
        ("worktop", (.045,.055,.052,1), .32),
        ("wood", (.19,.07,.025,1), .45),
        ("floor", (.29,.31,.27,1), .65),
        ("grout", (.09,.11,.10,1), .8),
        ("plaster", (.68,.66,.51,1), .9),
        ("wall_green", (.20,.32,.27,1), .85),
        ("window_frame", (.65,.67,.59,1), .5),
        ("chalkboard", (.018,.065,.042,1), .95),
        ("chalk", (.72,.77,.68,1), 1),
        ("rubber", (.016,.018,.016,1), .7),
    ]:
        mat = bpy.data.materials.new("EM / laboratory / " + name)
        mat.diffuse_color = colour
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        shader = nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = colour
        shader.inputs["Roughness"].default_value = roughness
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 85 if name == "worktop" else 12
        noise.inputs["Detail"].default_value = 3
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .16
        bump.inputs["Distance"].default_value = .006 if name == "worktop" else .02
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
        if name == "wood":
            tex = nodes.new("ShaderNodeTexCoord")
            scale = nodes.new("ShaderNodeVectorMath")
            scale.operation = "MULTIPLY"
            scale.inputs[1].default_value = (1,35,35)
            links.new(tex.outputs["Generated"], scale.inputs[0])
            links.new(scale.outputs[0], noise.inputs["Vector"])
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].color = (.09,.025,.007,1)
            ramp.color_ramp.elements[1].color = (.28,.12,.045,1)
            links.new(noise.outputs["Fac"], ramp.inputs[0])
            links.new(ramp.outputs[0], shader.inputs["Base Color"])
        result[name] = mat
    result["window_light"] = result["ink_white"]
    return result


def cutaway_cover(base, lesson):
    """Fade the wire surface to reveal the model in place, then close it again."""
    mat = base.copy()
    mat.name = "EM / animated copper cutaway cover"
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    out = nodes.get("Material Output")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    blend = nodes.new("ShaderNodeMixShader")
    links.new(shader.outputs[0], blend.inputs[1])
    links.new(transparent.outputs[0], blend.inputs[2])
    links.new(blend.outputs[0], out.inputs["Surface"])
    for seconds, value in [(0, 0), (lesson.microscope_in-1.2, 0), (lesson.microscope_in, 1),
                           (lesson.microscope_out, 1), (lesson.microscope_out+1, 0), (lesson.duration, 0)]:
        blend.inputs[0].default_value = value
        blend.inputs[0].keyframe_insert("default_value", frame=lesson.frame(seconds))
    return mat
