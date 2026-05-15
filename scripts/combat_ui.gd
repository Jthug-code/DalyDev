extends Control

## Minimal combat UI: Attack + log + HP readout.

const BattleActor := preload("res://scripts/battle_actor.gd")

@onready var log_label: RichTextLabel = %CombatLog
@onready var attack_button: Button = %AttackButton
@onready var status_label: Label = %StatusLabel
@onready var hp_label: Label = %HPLabel

var _player: BattleActor
var _enemy: BattleActor


func _ready() -> void:
	attack_button.pressed.connect(_on_attack_pressed)
	CombatDirector.phase_changed.connect(_on_phase)
	CombatDirector.combat_log.connect(_append_log)
	_on_phase(CombatDirector.phase)

	await get_tree().process_frame
	_player = get_tree().get_first_node_in_group(&"battle_player") as BattleActor
	_enemy = get_tree().get_first_node_in_group(&"battle_enemy") as BattleActor
	if _player:
		_player.hp_changed.connect(func(_c, _m): _refresh_hp())
	if _enemy:
		_enemy.hp_changed.connect(func(_c, _m): _refresh_hp())
	_refresh_hp()


func _on_attack_pressed() -> void:
	CombatDirector.request_player_attack()


func _on_phase(p: CombatDirector.Phase) -> void:
	var busy := (
		p == CombatDirector.Phase.ENEMY
		or p == CombatDirector.Phase.VICTORY
		or p == CombatDirector.Phase.DEFEAT
	)
	attack_button.disabled = busy or p != CombatDirector.Phase.PLAYER
	if p == CombatDirector.Phase.VICTORY:
		status_label.text = "Victory"
	elif p == CombatDirector.Phase.DEFEAT:
		status_label.text = "Defeat"
	elif p == CombatDirector.Phase.PLAYER:
		status_label.text = "Your turn"
	elif p == CombatDirector.Phase.ENEMY:
		status_label.text = "Enemy turn…"
	else:
		status_label.text = ""
	_refresh_hp()


func _append_log(line: String) -> void:
	log_label.append_text(line + "\n")


func _refresh_hp() -> void:
	var ps := "--"
	var es := "--"
	if _player:
		ps = "%d / %d" % [_player.current_hp, _player.max_hp]
	if _enemy:
		es = "%d / %d" % [_enemy.current_hp, _enemy.max_hp]
	hp_label.text = "Hero HP: %s   |   Foe HP: %s" % [ps, es]
