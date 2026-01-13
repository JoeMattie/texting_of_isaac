import pytest
import esper
from src.systems.render import RenderSystem
from src.components.core import Position, Sprite
from src.config import Config


def test_render_system_creates_grid():
    system = RenderSystem()

    grid = system.create_grid()

    assert len(grid) == Config.ROOM_HEIGHT
    assert len(grid[0]) == Config.ROOM_WIDTH


def test_render_system_draws_entity():
    world = "test_render_entity"
    esper.switch_world(world)
    esper.clear_database()

    system = RenderSystem()
    esper.add_processor(system)

    # Create entity
    entity = esper.create_entity()
    esper.add_component(entity, Position(10.0, 5.0))
    esper.add_component(entity, Sprite('@', 'cyan'))

    grid = system.render(world)

    # Check entity appears in grid
    cell = grid[5][10]
    assert cell['char'] == '@'
    assert cell['color'] == 'cyan'
