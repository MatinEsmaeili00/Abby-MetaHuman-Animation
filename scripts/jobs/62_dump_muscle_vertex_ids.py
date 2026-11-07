# Job 62: read the IMPORTED muscle mesh back (GeometryScript) and dump vertex positions + vertex-colour red, so the
# IDs the GPU sees can be compared with the labels (tools/muscle_atlas) in UE space.
import json
import unreal

MESH = "/MetaHumanAnatomyLayers/Anatomy/Meshes/SKM_Anatomy_Muscles_UpperBody"
OUT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "MetaHumanAnatomyLayers/imported_vertex_ids.json"
mesh = unreal.load_asset(MESH)
dm = unreal.DynamicMesh()
opts = unreal.GeometryScriptCopyMeshFromAssetOptions()
res = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh, dm, opts, unreal.GeometryScriptMeshReadLOD())
print("copy:", res if not isinstance(res, tuple) else res[1:])
Q = unreal.GeometryScript_MeshQueries
pos = Q.get_all_vertex_positions(dm, False)
pos = [x for x in (pos if isinstance(pos, tuple) else [pos]) if isinstance(x, unreal.GeometryScriptVectorList)][0]
cols = unreal.GeometryScript_VertexColors.get_mesh_per_vertex_colors(dm)
print("colors ret types:", [type(x).__name__ for x in (cols if isinstance(cols, tuple) else [cols])])
clist = [x for x in cols if isinstance(x, unreal.GeometryScriptColorList)][0]
P = unreal.GeometryScript_List.convert_vector_list_to_array(pos)
C = unreal.GeometryScript_List.convert_color_list_to_array(clist)
P = P[0] if isinstance(P, tuple) else P
C = C[0] if isinstance(C, tuple) else C
print("verts", len(P), "colors", len(C), "first colors", [(round(c.r, 4), round(c.g, 4)) for c in C[:5]])
json.dump({"p": [[round(p.x, 3), round(p.y, 3), round(p.z, 3)] for p in P], "r": [round(c.r, 6) for c in C]}, open(OUT, "w"))
print("->", OUT)
