import random

import pygame
import pytest

from game import config
from game.logic import Block, GameState, Player


@pytest.fixture
def state() -> GameState:
    return GameState(rng=random.Random(42))


def test_player_starts_centered_at_bottom():
    p = Player.create()
    assert p.rect.centerx == config.WIDTH // 2
    assert p.rect.bottom == config.HEIGHT - config.PLAYER_BOTTOM_MARGIN


def test_player_moves_and_stays_in_bounds():
    p = Player.create()
    p.move(-1, 10.0)  # weit nach links
    assert p.rect.left == 0
    p.move(1, 10.0)  # weit nach rechts
    assert p.rect.right == config.WIDTH


def test_player_does_not_move_without_direction():
    p = Player.create()
    x = p.rect.x
    p.move(0, 1.0)
    assert p.rect.x == x


def test_spawn_block_within_screen(state: GameState):
    for _ in range(50):
        b = state.spawn_block()
        assert 0 <= b.rect.left
        assert b.rect.right <= config.WIDTH
        assert config.BLOCK_MIN_SIZE <= b.rect.width <= config.BLOCK_MAX_SIZE
        assert b.rect.bottom <= 0  # startet oberhalb des Bildschirms


def test_spawn_interval_shrinks_but_has_floor(state: GameState):
    start = state.spawn_interval
    for _ in range(500):
        state.spawn_block()
    assert state.spawn_interval < start
    assert state.spawn_interval == pytest.approx(config.SPAWN_MIN_INTERVAL)


def test_blocks_spawn_over_time(state: GameState):
    for _ in range(60):
        state.update(1 / 60)
    assert len(state.blocks) >= 1


def test_block_off_screen_increases_score(state: GameState):
    # Block weit weg vom Spieler, kurz vor dem unteren Rand
    b = Block(rect=pygame.Rect(0, config.HEIGHT - 5, 10, 10), speed=1000.0)
    state.player.rect.x = config.WIDTH - config.PLAYER_WIDTH
    state.blocks.append(b)
    state.spawn_interval = 1e9  # kein zusätzlicher Spawn
    state.update(0.1)
    assert state.score == 1
    assert b not in state.blocks


def test_collision_sets_game_over(state: GameState):
    b = Block(rect=state.player.rect.copy(), speed=0.0)
    state.blocks.append(b)
    state.spawn_interval = 1e9
    state.update(1 / 60)
    assert state.game_over is True
    # Nach Game Over passiert nichts mehr
    score = state.score
    state.update(1.0, direction=1)
    assert state.score == score


def test_block_speed_scales_with_score(state: GameState):
    base = state.block_speed()
    state.score = 10
    assert state.block_speed() > base


def test_reset_restores_fresh_round(state: GameState):
    for _ in range(120):
        state.update(1 / 60)
    state.score = 7
    state.game_over = True
    state.reset()
    assert state.score == 0
    assert state.blocks == []
    assert state.game_over is False
    assert state.spawn_interval == config.SPAWN_START_INTERVAL


def test_deterministic_with_seed():
    a = GameState(rng=random.Random(1))
    b = GameState(rng=random.Random(1))
    for _ in range(300):
        a.update(1 / 60)
        b.update(1 / 60)
    assert [blk.rect for blk in a.blocks] == [blk.rect for blk in b.blocks]
    assert a.score == b.score
