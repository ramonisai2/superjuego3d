import math

ATTACK_RANGE = 3
ATTACK_DAMAGE = 25

def _hit_enemy(player, enemy, damage=1):
    if hasattr(enemy, "take_hit"):
        enemy.take_hit(damage, player.pos_x, player.pos_z)
    else:
        enemy.health -= damage

def _in_front_of_player(player, enemy, max_angle_deg=95.0):
    dx = enemy.x - player.pos_x
    dz = enemy.z - player.pos_z
    dist2 = dx * dx + dz * dz
    if dist2 <= 0.01 * 0.01:
        return True
    dist = math.sqrt(dist2)
    yaw = math.radians(player.yaw)
    fx = math.cos(yaw)
    fz = math.sin(yaw)
    dot = (dx / dist) * fx + (dz / dist) * fz
    dot = max(-1.0, min(1.0, dot))
    angle = math.degrees(math.acos(dot))
    return angle <= max_angle_deg

def attack_enemy(player, enemies, locked_target=None, attack_range=ATTACK_RANGE):
    """Ataca primero el objetivo fijado. En tercera persona usa asistencia frontal."""
    hit_any = False
    attack_range = float(getattr(player, "current_attack_range", lambda: attack_range)())
    attack_damage = float(getattr(player, "current_attack_damage", lambda: 1.0)())

    if locked_target is not None and locked_target in enemies:
        dx = player.pos_x - locked_target.x
        dz = player.pos_z - locked_target.z
        range_limit = attack_range + 1.0
        dist2 = dx * dx + dz * dz
        if dist2 < range_limit * range_limit:
            _hit_enemy(player, locked_target, attack_damage)
            hit_any = True

    if not hit_any:
        assist_range = attack_range + (1.4 if getattr(player, "camera_mode", "first") == "third" else 0.0)
        assist_range2 = assist_range * assist_range
        for enemy in enemies:
            dx = player.pos_x - enemy.x
            dz = player.pos_z - enemy.z
            dist2 = dx * dx + dz * dz
            if dist2 < assist_range2 and _in_front_of_player(player, enemy):
                _hit_enemy(player, enemy, attack_damage)
                hit_any = True
                break

    enemies[:] = [e for e in enemies if e.health > 0]
    if hit_any and hasattr(player, "use_weapon_once"):
        player.use_weapon_once()
    return hit_any
