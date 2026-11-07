import unreal
EAL = unreal.EditorAssetLibrary
ENH = "/Game/Abby_Animation/Enhanced"
bs = unreal.load_asset(f"{ENH}/BS_Abby_Locomotion")
walk, jog, run = (unreal.load_asset(f"{ENH}/{n}") for n in ("AbbyWalk_Sync", "AbbyJog_Sync", "AbbyRun_Sync"))
bp = bs.get_editor_property("blend_parameters")
p0 = bp[0]
print("BlendParameter fields:", [k for k in dir(p0) if not k.startswith("_") and not callable(getattr(p0, k, None))])
p0.set_editor_property("display_name", "Speed"); p0.set_editor_property("min", 0.0); p0.set_editor_property("max", 1.0)
p0.set_editor_property("grid_num", 20)
bp[0] = p0
bs.set_editor_property("blend_parameters", bp)
ip = bs.get_editor_property("interpolation_param"); i0 = ip[0]
print("InterpolationParameter fields:", [k for k in dir(i0) if not k.startswith("_") and not callable(getattr(i0, k, None))])
i0.set_editor_property("interpolation_time", 0.25); ip[0] = i0
bs.set_editor_property("interpolation_param", ip)
samples = []
for anim, x, rate in [(walk, 0.0, 0.85), (walk, 0.45, 1.0), (jog, 0.62, 1.0), (run, 0.80, 1.0), (run, 1.0, 1.15)]:
    s = unreal.BlendSample()
    s.set_editor_property("animation", anim)
    s.set_editor_property("sample_value", unreal.Vector(x, 0, 0))
    s.set_editor_property("rate_scale", rate)
    samples.append(s)
print("BlendSample fields:", [k for k in dir(samples[0]) if not k.startswith("_") and not callable(getattr(samples[0], k, None))])
bs.set_editor_property("sample_data", samples)
bs.modify()
EAL.save_loaded_asset(bs, only_if_is_dirty=False)
bs2 = unreal.load_asset(f"{ENH}/BS_Abby_Locomotion")
print("samples now:", [(s.get_editor_property("animation").get_name() if s.get_editor_property("animation") else None, round(s.get_editor_property("sample_value").x, 2), s.get_editor_property("rate_scale")) for s in bs2.get_editor_property("sample_data")])
print("axis:", bs2.get_editor_property("blend_parameters")[0].get_editor_property("display_name"), bs2.get_editor_property("blend_parameters")[0].get_editor_property("max"))
