"""Prepare one ComfyUI-generated GLB for importing to Unity as an FBX.

Run: blender --background --python scripts/blender_cafe_asset.py -- --input cup.glb --output CoffeeCup.fbx --height 0.16
This script transforms an asset; it cannot establish license rights or visual quality.
"""
import argparse
import sys
from pathlib import Path


def arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--height", required=True, type=float)
    args = parser.parse_args(argv)
    if args.height <= 0 or args.height > 10:
        parser.error("--height must be > 0 and <= 10 meters")
    if not args.input.exists() or args.input.suffix.lower() != ".glb":
        parser.error("--input must be an existing GLB file")
    if args.output.suffix.lower() != ".fbx":
        parser.error("--output must end in .fbx")
    return args


def main():
    import bpy
    from mathutils import Vector
    args = arguments()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(args.input.resolve()))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("No mesh objects were imported from GLB")
    # Preserve materials and hierarchy. Normalize physical height using the total mesh bounding box.
    corners = [obj.matrix_world @ Vector(c) for obj in meshes for c in obj.bound_box]
    lo = Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners)))
    hi = Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))
    if hi.z - lo.z < 1e-8:
        raise RuntimeError("Mesh has zero height")
    ratio = args.height / (hi.z - lo.z)
    center = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    # Transform all imported roots uniformly to preserve relative positions.
    roots = [obj for obj in bpy.context.scene.objects if obj.parent is None]
    from mathutils import Matrix
    transform = Matrix.Scale(ratio, 4) @ Matrix.Translation(-center)
    for obj in roots:
        obj.matrix_world = transform @ obj.matrix_world
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(args.output.resolve()), use_selection=True,
                             object_types={"MESH"}, add_leaf_bones=False, apply_unit_scale=True,
                             axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True)
    print(f"Exported {len(meshes)} meshes to {args.output}")


if __name__ == "__main__":
    main()
