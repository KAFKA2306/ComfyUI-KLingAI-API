// VCCで作成したVRChat WorldsプロジェクトのAssets/Editorへ配置する。
// Unity標準形状だけでシーンを作り、AI生成素材を必須にしない。
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using VRC.SDK3.Components;

public static class GWPCafeBuilder
{
    private const string BasePath = "Assets/GWPCafe";

    [MenuItem("Tools/GWP/Build Small Cafe Scene")]
    public static void Build()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        EnsureFolder("Assets", "GWPCafe");
        EnsureFolder(BasePath, "Materials");
        EnsureFolder(BasePath, "Scenes");
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        Material wood = Mat("WarmWood", new Color(0.43f, 0.24f, 0.13f));
        Material floor = Mat("Floor", new Color(0.32f, 0.23f, 0.18f));
        Material wall = Mat("Wall", new Color(0.72f, 0.64f, 0.52f));
        Material trim = Mat("Trim", new Color(0.20f, 0.12f, 0.09f));
        Material cushion = Mat("Cushion", new Color(0.28f, 0.43f, 0.36f));
        Material cream = Mat("Ceramic", new Color(0.86f, 0.81f, 0.68f));
        Material glass = Mat("WindowGlass", new Color(0.21f, 0.33f, 0.42f));
        GameObject root = new GameObject("GWP_Cafe_Generated");

        Cube(root, "Floor 6x6m", new Vector3(0, -0.10f, 0), new Vector3(6f, .2f, 6f), floor);
        Cube(root, "Ceiling", new Vector3(0, 3.05f, 0), new Vector3(6f, .1f, 6f), wall);
        Cube(root, "Left Wall", new Vector3(-3, 1.5f, 0), new Vector3(.16f, 3, 6), wall);
        Cube(root, "Back Wall", new Vector3(0, 1.5f, 3), new Vector3(6, 3, .16f), wall);
        // 出入口は幅1.6m、高さ2.4m。通路をコライダーで塞がない。
        Cube(root, "Front Wall Left", new Vector3(-1.9f, 1.5f, -3), new Vector3(2.2f, 3, .16f), wall);
        Cube(root, "Front Wall Right", new Vector3(1.9f, 1.5f, -3), new Vector3(2.2f, 3, .16f), wall);
        Cube(root, "Front Door Lintel", new Vector3(0, 2.7f, -3), new Vector3(1.6f, .6f, .16f), wall);
        // 右壁の窓に薄い衝突判定なしの板を設置する。
        Cube(root, "Right Wall Front", new Vector3(3, 1.5f, -1.6f), new Vector3(.16f, 3, 2.8f), wall);
        Cube(root, "Right Wall Back", new Vector3(3, 1.5f, 2.1f), new Vector3(.16f, 3, 1.8f), wall);
        Cube(root, "Window Sill Wall", new Vector3(3, .45f, .5f), new Vector3(.16f, .9f, 1.4f), wall);
        Cube(root, "Window Header Wall", new Vector3(3, 2.6f, .5f), new Vector3(.16f, .8f, 1.4f), wall);
        Cube(root, "Window Pane", new Vector3(3, 1.55f, .5f), new Vector3(.035f, 1.3f, 1.4f), glass, false);

        Cube(root, "Counter", new Vector3(-1.25f, .55f, 2.2f), new Vector3(2.75f, 1.1f, .72f), wood);
        Cube(root, "Counter Surface", new Vector3(-1.25f, 1.13f, 2.2f), new Vector3(2.95f, .08f, .82f), trim);
        Cube(root, "Table Top", new Vector3(1.05f, .74f, .50f), new Vector3(1.15f, .08f, 1.05f), wood);
        foreach (float x in new [] { .58f, 1.52f })
            foreach (float z in new [] { .10f, .90f })
                Cube(root, "Table Leg", new Vector3(x, .36f, z), new Vector3(.08f, .72f, .08f), trim);
        Chair(root, "Chair by Door", new Vector3(1.05f, 0, -.52f), wood, cushion, false);
        Chair(root, "Chair by Window", new Vector3(1.05f, 0, 1.60f), wood, cushion, true);
        Cube(root, "Poster", new Vector3(-2.9f, 1.65f, -.5f), new Vector3(.03f, .75f, .60f), cushion, false);
        Cup(root, cream, trim);

        GameObject spawn = new GameObject("Spawn");
        spawn.transform.SetParent(root.transform);
        spawn.transform.position = new Vector3(0, .05f, -2.2f);
        spawn.transform.rotation = Quaternion.identity; // 前方（+Z）がカフェ内部を向く。
        GameObject vrcWorld = new GameObject("VRCWorld");
        VRCSceneDescriptor descriptor = vrcWorld.AddComponent<VRCSceneDescriptor>();
        descriptor.spawns = new[] { spawn.transform };
        vrcWorld.transform.position = spawn.transform.position;

        LightSource(root, "Warm Counter Light", new Vector3(-1.15f, 2.45f, 1.55f), 2.0f, 4.4f);
        LightSource(root, "Warm Table Light", new Vector3(1.05f, 2.45f, .5f), 1.6f, 3.8f);
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(.23f, .24f, .29f);
        GameObject sun = new GameObject("Ambient Directional Light");
        sun.transform.SetParent(root.transform);
        Light directional = sun.AddComponent<Light>();
        directional.type = LightType.Directional;
        directional.intensity = .25f;
        directional.shadows = LightShadows.None;
        sun.transform.rotation = Quaternion.Euler(50, -25, 0);

        string path = BasePath + "/Scenes/SmallCafe.unity";
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), path);
        AssetDatabase.SaveAssets();
        Debug.Log("GWP Small Cafe saved: " + path + ". Run VRChat SDK Build & Test before uploading.");
    }

    private static void EnsureFolder(string parent, string child)
    {
        if (!AssetDatabase.IsValidFolder(parent + "/" + child))
            AssetDatabase.CreateFolder(parent, child);
    }

    private static Material Mat(string name, Color color)
    {
        string path = BasePath + "/Materials/" + name + ".mat";
        Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material != null) return material;
        Shader shader = Shader.Find("Standard");
        if (shader == null) throw new System.InvalidOperationException("Standard shader not found; use a VCC Built-in Render Pipeline project.");
        material = new Material(shader) { color = color };
        AssetDatabase.CreateAsset(material, path);
        return material;
    }

    private static GameObject Cube(GameObject parent, string name, Vector3 position, Vector3 scale, Material material, bool collision = true)
    {
        GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.name = name;
        obj.transform.SetParent(parent.transform);
        obj.transform.localPosition = position;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = material;
        if (!collision) Object.DestroyImmediate(obj.GetComponent<Collider>());
        return obj;
    }

    private static void Chair(GameObject root, string name, Vector3 position, Material wood, Material cushion, bool facingBack)
    {
        GameObject group = new GameObject(name);
        group.transform.SetParent(root.transform);
        group.transform.position = position;
        if (facingBack) group.transform.rotation = Quaternion.Euler(0, 180, 0);
        Cube(group, "Seat", Vector3.up * .44f, new Vector3(.48f, .09f, .45f), cushion);
        Cube(group, "Back", new Vector3(0, .80f, .19f), new Vector3(.48f, .72f, .08f), wood);
        foreach (float x in new [] { -.18f, .18f })
            foreach (float z in new [] { -.16f, .16f })
                Cube(group, "Leg", new Vector3(x, .2f, z), new Vector3(.06f, .4f, .06f), wood);
    }

    private static void Cup(GameObject root, Material cream, Material coffee)
    {
        GameObject cup = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        cup.name = "Replaceable Coffee Cup (AI asset slot)";
        cup.transform.SetParent(root.transform);
        cup.transform.position = new Vector3(-.9f, 1.22f, 2.2f);
        cup.transform.localScale = new Vector3(.13f, .08f, .13f);
        cup.GetComponent<Renderer>().sharedMaterial = cream;
        Object.DestroyImmediate(cup.GetComponent<Collider>());
        Cube(root, "Coffee Surface", new Vector3(-.9f, 1.301f, 2.2f), new Vector3(.20f, .006f, .20f), coffee, false);
    }

    private static void LightSource(GameObject root, string name, Vector3 position, float intensity, float range)
    {
        GameObject obj = new GameObject(name);
        obj.transform.SetParent(root.transform);
        obj.transform.position = position;
        Light light = obj.AddComponent<Light>();
        light.type = LightType.Point;
        light.color = new Color(1f, .77f, .48f);
        light.intensity = intensity;
        light.range = range;
        light.shadows = LightShadows.None;
    }
}
