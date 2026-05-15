extends Node3D

## Wires the instanced `BattleActor`s into `CombatDirector` when the floor loads.

const BattleActor := preload("res://scripts/battle_actor.gd")

@export var hero_path: NodePath = ^"Actors/Hero"
@export var monster_path: NodePath = ^"Actors/Monster"


func _ready() -> void:
	var hero: BattleActor = get_node_or_null(hero_path) as BattleActor
	var monster: BattleActor = get_node_or_null(monster_path) as BattleActor
	if hero and monster:
		CombatDirector.start_encounter(hero, monster)
