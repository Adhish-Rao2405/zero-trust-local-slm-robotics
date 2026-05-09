from __future__ import annotations


SUPPORTED_ACTIONS: frozenset[str] = frozenset(
    {
        "describe_scene",
        "move_ee",
        "open_gripper",
        "close_gripper",
        "pick",
        "place",
        "reset",
    }
)

ALLOWED_ZONES: frozenset[str] = frozenset(
    {
        "bin_A",
        "bin_B",
        "bin_C",
        "left_tray",
        "right_tray",
        "staging_area",
        "home",
    }
)

WORKSPACE_BOUNDS: dict[str, tuple[float, float]] = {
    "x": (-1.0, 1.0),
    "y": (-1.0, 1.0),
    "z": (0.0, 1.0),
}

GRIPPER_WIDTH_BOUNDS: tuple[float, float] = (0.0, 0.085)
FORCE_BOUNDS: tuple[float, float] = (0.0, 40.0)

KNOWN_OBJECTS: frozenset[str] = frozenset(
    {
        "red_cube",
        "blue_cylinder",
        "green_cube",
        "yellow_sphere",
    }
)

ALLOWED_FIELDS_BY_ACTION: dict[str, frozenset[str]] = {
    "describe_scene": frozenset({"action"}),
    "move_ee": frozenset({"action", "target", "target_xyz", "speed", "force"}),
    "open_gripper": frozenset({"action", "width", "speed", "force"}),
    "close_gripper": frozenset({"action", "width", "speed", "force"}),
    "pick": frozenset({"action", "object", "width", "force", "speed"}),
    "place": frozenset({"action", "object", "target", "target_xyz", "force", "speed"}),
    "reset": frozenset({"action"}),
}

REQUIRED_FIELDS_BY_ACTION: dict[str, frozenset[str]] = {
    "describe_scene": frozenset({"action"}),
    "move_ee": frozenset({"action"}),
    "open_gripper": frozenset({"action"}),
    "close_gripper": frozenset({"action"}),
    "pick": frozenset({"action", "object"}),
    "place": frozenset({"action", "object"}),
    "reset": frozenset({"action"}),
}

TARGET_REQUIRED_ACTIONS: frozenset[str] = frozenset({"move_ee", "place"})

