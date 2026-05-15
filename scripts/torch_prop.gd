extends Node3D

## Looped sway for the torch + subtle spotlight flicker (no value animation tracks).

@onready var _light: SpotLight3D = $SpotLight3D


func _ready() -> void:
	var ap := $AnimationPlayer as AnimationPlayer
	var anim := Animation.new()
	anim.length = 3.6
	anim.loop_mode = Animation.LOOP_LINEAR

	var tr := anim.add_track(Animation.TYPE_ROTATION_3D)
	anim.track_set_path(tr, ^".")
	anim.rotation_track_insert_key(tr, 0.0, Quaternion.IDENTITY)
	anim.rotation_track_insert_key(
		tr,
		1.8,
		Quaternion.from_euler(Vector3(deg_to_rad(5.0), deg_to_rad(12.0), 0.0))
	)
	anim.rotation_track_insert_key(tr, 3.6, Quaternion.IDENTITY)

	var lib := AnimationLibrary.new()
	lib.add_animation(&"sway", anim)
	ap.add_animation_library(&"", lib)
	ap.play(&"sway")


func _process(_delta: float) -> void:
	if _light == null:
		return
	var t := Time.get_ticks_msec() * 0.004
	_light.light_energy = 3.2 + 0.9 * sin(t)
	_light.shadow_enabled = true
