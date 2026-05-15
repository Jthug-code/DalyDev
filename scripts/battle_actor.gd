extends Node3D

## Minimal combat stats + procedural idle loop on child `Body` (AnimationPlayer `IdleAnim`).

@export var display_name: String = "Actor"
@export var max_hp: int = 12
@export var attack_damage: int = 4
@export var is_player: bool = false

var current_hp: int

signal hp_changed(current: int, maximum: int)
signal died(actor: Node3D)


func _ready() -> void:
	current_hp = max_hp
	if is_player:
		add_to_group(&"battle_player")
	else:
		add_to_group(&"battle_enemy")
	_setup_idle_animation()
	hp_changed.emit(current_hp, max_hp)
	_play_idle_loop()


func _setup_idle_animation() -> void:
	var body := get_node_or_null(^"Body") as Node3D
	var ap := get_node_or_null(^"IdleAnim") as AnimationPlayer
	if body == null or ap == null:
		return

	var base_pos := body.position
	var anim := Animation.new()
	anim.length = 2.4
	anim.loop_mode = Animation.LOOP_LINEAR
	var ti := anim.add_track(Animation.TYPE_POSITION_3D)
	anim.track_set_path(ti, ^"Body")
	anim.position_track_insert_key(ti, 0.0, base_pos)
	anim.position_track_insert_key(ti, 1.2, base_pos + Vector3(0.0, 0.08, 0.0))
	anim.position_track_insert_key(ti, 2.4, base_pos)

	var lib := AnimationLibrary.new()
	lib.add_animation(&"idle", anim)
	for name in ap.get_animation_library_list():
		ap.remove_animation_library(name)
	ap.add_animation_library(&"", lib)


func _play_idle_loop() -> void:
	var ap := get_node_or_null(^"IdleAnim") as AnimationPlayer
	if ap and ap.has_animation(&"idle"):
		ap.play(&"idle")


func take_damage(amount: int) -> void:
	amount = maxi(amount, 0)
	current_hp = maxi(current_hp - amount, 0)
	hp_changed.emit(current_hp, max_hp)
	if current_hp <= 0:
		died.emit(self)


func is_alive() -> bool:
	return current_hp > 0
