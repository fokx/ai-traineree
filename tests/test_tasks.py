from ai_traineree.tasks import GymTask

import mock
import numbers


def test_gym_task_actual_openai_discrete():
    # Assign
    gym_name = "CartPole-v1"

    # Act
    task = GymTask(gym_name)

    # Assert
    assert task.name == gym_name
    assert task.env is not None
    assert task.can_render is True
    assert task.is_discrete is True
    assert task.state_size == 4
    assert task.action_size == 2


def test_gym_task_actual_openai_continious():
    # Assign
    gym_name = 'Pendulum-v0'

    # Act
    task = GymTask(gym_name, can_render=False)

    # Assert
    assert task.name == gym_name
    assert task.env is not None
    assert task.can_render is False
    assert task.is_discrete is False
    assert task.state_size == 3
    assert task.action_size == 1


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_reset(mock_gym, fix_env):
    # Assign
    mock_gym.make.return_value = fix_env
    task = GymTask("example")

    # Act
    out = task.reset()

    # Assert
    assert fix_env.reset.called_once()
    assert len(out) > 0


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_step(mock_gym, fix_env):
    # Assign
    mock_gym.make.return_value = fix_env
    task = GymTask("example")
    action = 2.13

    # Act
    out = task.step(actions=action)

    # Assert
    assert fix_env.step.called_once_with(int(action))
    assert len(out) == 4
    assert hasattr(out[0], "__iter__")
    assert isinstance(out[1], numbers.Number)
    assert isinstance(out[2], bool)
    assert isinstance(out[3], str)


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_step_discrete(mock_gym, fix_env_discrete):
    # Assign
    mock_gym.make.return_value = fix_env_discrete
    task = GymTask("example")
    action = 2.

    # Act
    out = task.step(actions=action)

    # Assert
    assert fix_env_discrete.step.called_once_with(int(action))
    assert len(out) == 4
    assert hasattr(out[0], "__iter__")
    assert isinstance(out[1], numbers.Number)
    assert isinstance(out[2], bool)
    assert isinstance(out[3], str)


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_render(mock_gym, fix_env):
    # Assign
    mock_gym.make.return_value = fix_env
    task = GymTask("CanRender", can_render=True)

    # Act
    task.render()

    # Assert
    assert fix_env.render.called_once_with("rgb_array")


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_render_human(mock_gym, fix_env):
    # Assign
    mock_gym.make.return_value = fix_env
    task = GymTask("CanRender", can_render=True)

    # Act
    task.render(mode="human")

    # Assert
    assert fix_env.render.called_once_with("human")


@mock.patch("ai_traineree.tasks.gym")
def test_gym_task_render_cannot_render(mock_gym, fix_env):
    # Assign
    mock_gym.make.return_value = fix_env
    task = GymTask("CanRender", can_render=False)

    # Act
    task.render()

    # Assert
    assert not fix_env.render.called
