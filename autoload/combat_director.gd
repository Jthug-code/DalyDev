extends Node

## Minimal turn-based encounter: player Attack only, simple enemy reply.

const BattleActor := preload("res://scripts/battle_actor.gd")

enum Phase { IDLE, PLAYER, ENEMY, VICTORY, DEFEAT }

var phase: Phase = Phase.IDLE
var player_actor: BattleActor
var enemy_actor: BattleActor

signal phase_changed(new_phase: Phase)
signal combat_log(message: String)


func start_encounter(player: BattleActor, enemy: BattleActor) -> void:
	player_actor = player
	enemy_actor = enemy
	phase = Phase.PLAYER
	phase_changed.emit(phase)
	combat_log.emit("Encounter started. Your turn — choose Attack.")


func request_player_attack() -> void:
	if phase != Phase.PLAYER:
		return
	if player_actor == null or enemy_actor == null:
		return
	if not player_actor.is_alive() or not enemy_actor.is_alive():
		return

	var dmg: int = player_actor.attack_damage
	enemy_actor.take_damage(dmg)
	combat_log.emit("%s hits %s for %d." % [player_actor.display_name, enemy_actor.display_name, dmg])

	if not enemy_actor.is_alive():
		_set_phase(Phase.VICTORY)
		combat_log.emit("%s is defeated. Victory!" % enemy_actor.display_name)
		return

	_set_phase(Phase.ENEMY)
	await get_tree().create_timer(0.6).timeout
	_enemy_act()


func _enemy_act() -> void:
	if phase != Phase.ENEMY or enemy_actor == null or player_actor == null:
		return
	if not enemy_actor.is_alive() or not player_actor.is_alive():
		return

	var dmg: int = enemy_actor.attack_damage
	player_actor.take_damage(dmg)
	combat_log.emit("%s strikes %s for %d." % [enemy_actor.display_name, player_actor.display_name, dmg])

	if not player_actor.is_alive():
		_set_phase(Phase.DEFEAT)
		combat_log.emit("Your party champion falls. Defeat.")
		return

	_set_phase(Phase.PLAYER)
	combat_log.emit("Your turn.")


func _set_phase(p: Phase) -> void:
	phase = p
	phase_changed.emit(phase)
