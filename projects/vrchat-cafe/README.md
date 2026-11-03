# VRChat Small Café | concrete build

**Finish condition:** a walkable café scene passing VRChat Build & Test, uploaded from a VRChat account, followed by a verified `vrchat.com/home/world/...` URL. A workflow JSON or GLB is not a published world.

## What works without any model

The Unity Editor script generates a **6 × 6 × 3 m** room with a doorway, window, floor colliders, counter, two chairs, a table, lighting, a placeholder cup and exactly one VRChat Scene Descriptor with a spawn. This gives a stable baseline even if every AI workflow is unavailable. The generated Unity scene is not yet tested on the user's PC.

1. Use the **VRChat Creator Companion** on Windows to create a new **Worlds** project. Keep its managed Unity/VRChat SDK versions; do not overwrite `Packages/` from this repo. The official Unity version displayed on 2026-11-03 is **2022.3.22f1**. Do not use URP/HDRP.
2. Copy [`unity/Assets/Editor/GWPCafeBuilder.cs`](../../unity/Assets/Editor/GWPCafeBuilder.cs) to `<VCC World Project>/Assets/Editor/GWPCafeBuilder.cs` (create the Editor directory if necessary).
3. Open Unity and choose **Tools → GWP → Build Small Cafe Scene**. The generator prompts to save any modified scene before creating a new one. It saves `Assets/GWPCafe/Scenes/SmallCafe.unity`.
4. Open **VRChat SDK → Show Control Panel** and sign in. Check the Builder validation, layers and player spawn. Use **Build & Test Your World**, walk through the doorway, check the windows, seating and performance.
5. Choose **Build & Publish Your World Online** only when validation passes. Upload name, description and thumbnail. Public discovery requires a separate Community Labs submission. Record the actual URL in [`publication.json`](publication.json) after a successful upload.

## Source-preserving AI workflow path

The canonical discovery catalog remains [`src/gwp/discovery.py`](../../src/gwp/discovery.py). This project's shortlist only identifies workflows to try; it never removes candidates from the global catalog.

```sh
python scripts/cafe_pipeline.py check
python scripts/cafe_pipeline.py snapshot  # downloads pinned original JSON + provenance, not model weights
python scripts/cafe_pipeline.py check --strict
python scripts/cafe_pipeline.py glb --file path/to/ComfyUI/output/cup.glb
```

For the first AI object, use the original Hunyuan3D Image-to-Model UI workflow in ComfyUI. Download the model noted in that workflow and use an original coffee-cup reference image. Run manually after inspecting dependencies and licenses. Save the generated GLB plus a separate record of upstream source, model license and creation parameters. The 12 GB RTX 3060 has **not** been verified for this model. Pixal3D/TRELLIS2 is an alternative; Qwen 360 is environment reference only, not collision geometry.

If a generated GLB passes basic container checks, normalize its physical height and export an FBX through Blender:

```sh
blender --background --python scripts/blender_cafe_asset.py -- --input cup.glb --output CoffeeCup.fbx --height 0.16
```

Place the FBX into the VCC Unity project and replace the scene's `Replaceable Coffee Cup (AI asset slot)` placeholder. Confirm normals, material/texture paths, mesh complexity, collider need and 16-cm scale manually. This conversion script does not establish legal permission to publish an AI asset.

## Publication acceptance checklist

- [ ] Windows Unity project opens without compile errors.
- [ ] Exactly one VRC Scene Descriptor; spawn is inside the room and faces the seating area.
- [ ] Floor and walls collide; the doorway remains walkable and the window is not a door.
- [ ] All imported props use appropriate materials and sizes; source license allows the intended use.
- [ ] VRChat SDK Build & Test succeeds in Desktop mode; no missing shaders or SDK errors.
- [ ] On-device VR performance is reviewed; Community Labs advises aiming for at least 45 FPS for one VR user and generally under 200 MB world size.
- [ ] World is uploaded, its world URL is independently verified and Community Labs/public visibility is recorded **separately**.

Primary documentation: [Creating your first world](https://creators.vrchat.com/worlds/creating-your-first-world/), [VRC Scene Descriptor](https://creators.vrchat.com/worlds/components/vrc_scenedescriptor/), [Community Labs](https://creators.vrchat.com/worlds/submitting-a-world-to-be-made-public/), [Unity version](https://creators.vrchat.com/sdk/upgrade/current-unity-version/).
