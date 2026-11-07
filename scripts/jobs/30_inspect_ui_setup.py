# Job 30: inspect the existing UI / controller / pawn setup before wiring the sliders.
import unreal

EAL = unreal.EditorAssetLibrary


def cdo(path):
    bp = EAL.load_asset(path)
    if not bp:
        print("MISSING", path)
        return None, None
    gen = bp.generated_class()
    return bp, unreal.get_default_object(gen)


def safe(obj, prop):
    try:
        return obj.get_editor_property(prop)
    except Exception as e:  # noqa
        return "<n/a>"


print("=== Game mode / controller")
for p in ["/Game/Blueprints/BP_GameMode", "/Game/Blueprints/BP_PlayerController"]:
    bp, d = cdo(p)
    if not d:
        continue
    print(p, "class:", d.get_class().get_name(), "mro:", [c.__name__ for c in type(d).__mro__[:4]])
    for prop in ["default_pawn_class", "player_controller_class", "hud_class",
                 "mouse_manager", "mouse_move", "mouse_zoom",
                 "speed_slider_widget", "timeline_widget_class", "anatomy_view_switcher_widget_class",
                 "pawn_switcher_widget_class", "target_meta_human"]:
        v = safe(d, prop)
        if v != "<n/a>":
            print("   ", prop, "=", v.get_name() if hasattr(v, "get_name") else v)

print("=== World settings of Main")
world = unreal.EditorLevelLibrary.get_editor_world()
ws = world.get_world_settings()
print("level:", world.get_name(), "GameModeOverride:", safe(ws, "default_game_mode"))
pawns = []
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    cls = a.get_class().get_name()
    if any(k in cls for k in ["Abby", "PlaceHolder", "PlayerStart", "MH_", "Pawn", "Character", "Skeleton"]):
        print("  actor:", a.get_actor_label(), cls, "auto_possess:", safe(a, "auto_possess_player"))
        if "PlaceHolderManager" in cls:
            print("     placeholders:", [x.get_actor_label() if x else None for x in safe(a, "player_place_holders")])

print("=== Widgets")
for p in ["/Game/Widget/WB_AmationTimeline", "/Game/Widget/WB_AnatomyViewSwitcher", "/Game/Widget/WB_PawnSwitcher",
          "/Game/UserInterface/Widgets/WBP_Header", "/Game/Blueprints/BP_SpeedSlider"]:
    a = EAL.load_asset(p)
    if not a:
        print("MISSING", p)
        continue
    gd = unreal.get_default_object(a.generated_class()) if hasattr(a, "generated_class") else None
    print(p, a.get_class().get_name(), "mro:", [c.__name__ for c in type(gd).__mro__[:4]] if gd else None)
    tree = safe(a, "widget_tree")
    if tree not in (None, "<n/a>"):
        try:
            for w in tree.get_editor_property("all_widgets") if False else []:
                pass
        except Exception:
            pass
    d = unreal.get_default_object(a.generated_class()) if hasattr(a, "generated_class") else None
    if d:
        for prop in ["groom_strands_asset", "groom_cards_asset", "pawn_to_spawn", "min_speed", "max_speed"]:
            v = safe(d, prop)
            if v != "<n/a>":
                print("   ", prop, "=", v.get_path_name() if hasattr(v, "get_path_name") else v)
