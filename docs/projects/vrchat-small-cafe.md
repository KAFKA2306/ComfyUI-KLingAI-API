# VRChat small café: publication pipeline (2026-11-03)

## Definition of done
A public VRChat world with a small walkable café, one entrance, seating, ambient lighting, clear spawn, tested on desktop, with published world URL and screenshots. A GitHub plan or generated image is NOT a published world.

## Workflow-first sourcing
Preserve upstream workflow JSON unchanged, with source URL, commit SHA, license, model weights, custom nodes, GPU requirements, cost, input/output and generated samples. Do not reject community workflows by popularity or subjective scoring. Maintain a complete discovery inventory and separately record execution results.

## Selected production path
1. Reference concept: cozy night café, small single room, 4 seats, counter, window, warm lighting. Create an original design and verify third-party asset licenses.
2. Background: Qwen Image 2512 360 LoRA template (official JSON: https://github.com/Comfy-Org/workflow_templates/blob/main/templates/template_qwen_Image_2512_360_lora.json). Use as inspiration/skybox candidate, not collision geometry. Its linked text encoder alone is 8.74 GB; local 12 GB VRAM feasibility unverified.
3. Props: Hunyuan3D image-to-model template (https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_hunyuan3d_image_to_model.json) for one chair or cup. Original workflow has LoadImage, generation group, SaveGLB; validate export geometry, normals, texture and license. Alternative Meshy 7.1 API, if paid service is acceptable: https://comfy.org/hub/workflows/meshy-7-1-text-to-model-fc1427a80e70/
4. World shell: build floors/walls/ceiling/windows/counter directly in Blender or Unity using simple meshes. AI image panorama must not be treated as navigable 3D.
5. Blender cleanup: real-world scale, apply transforms, remove unwanted geometry, check UV/PBR, reduce triangles, verify texture paths; export FBX/GLB suitable for Unity import.
6. Unity: use the Unity version required by the current VRChat Creator Companion project; install VRChat Worlds SDK through VCC. Configure spawn, VRC Scene Descriptor, colliders, baked lighting, materials, audio permissions and camera views.
7. VRChat Build & Test: desktop entry, collision, chair access, lighting, frame rate, missing shaders, console errors, asset licensing; optimize for Quest separately rather than claiming support.
8. Upload through VRChat SDK with an authorized VRChat account and required publishing eligibility. Set name, description, thumbnail and visibility; record actual world URL. Never claim publication until confirmed in VRChat.

## First reproducible vertical slice
- One 6m x 6m room with 3m ceiling, 1 door, 1 window, 1 counter, 1 table and 2 chairs.
- Generate or import exactly one AI-created prop (cup), while structural meshes remain deterministic.
- Produce a Unity scene that opens without missing references and passes local VRChat Build & Test.
- Expand to four seats and ambience only after this baseline works.

## Verification matrix
| Gate | Evidence | Status |
|---|---|---|
| Workflow source JSON exists | Official Hunyuan3D and Qwen files inspected | confirmed |
| Workflow executes on RTX 3060 12GB | ComfyUI runtime logs and saved artifact | not tested |
| Mesh imports to Blender | screenshot + import log | not tested |
| Unity project opens with correct SDK | Unity console + project metadata | not tested |
| VRChat Build & Test succeeds | local client test | not tested |
| VRChat upload and public URL | live world page | not done |

## Registry schema for each discovered workflow
source_url, upstream_revision, title, author, date_observed, category, raw_json_path, sample_urls, model_urls, model_sizes, node_dependencies, runtime_type(local/API), estimated_cost, license_workflow, license_model, commercial_terms, required_vram, tested_hardware, execution_status, failure_log, output_format, downstream_tool.

## Primary sources
- https://github.com/Comfy-Org/workflow_templates
- https://github.com/pjecuacion/comfyui_workflows
- https://docs.vrchat.com/docs/creating-your-first-world
- https://creators.vrchat.com/worlds/
- https://vcc.docs.vrchat.com/
