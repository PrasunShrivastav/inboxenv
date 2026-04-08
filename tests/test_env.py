from app.environment import InboxEnvironment
from app.models import Action, Category, Priority


def test_reset_returns_valid_observation():
    env = InboxEnvironment()
    result = env.reset("task_1")

    assert result.task_id == "task_1"
    assert result.observation.task_id == "task_1"
    assert result.observation.current_email.id == "email_task_1_0"
    assert result.observation.inbox_remaining == 9
    assert result.observation.emails_processed == 0


def test_step_advances_episode():
    env = InboxEnvironment("task_1")
    reset = env.reset("task_1")
    current = reset.observation.current_email

    action = Action(
        email_id=current.id,
        priority=Priority.URGENT,
        category=Category.TECHNICAL,
        should_escalate=True,
        reasoning="Production incident indicators present.",
    )

    result = env.step(action)

    assert result.done is False
    assert result.observation is not None
    assert result.observation.step_number == 2
    assert result.observation.emails_processed == 1


def test_episode_ends_correctly():
    env = InboxEnvironment("task_1")
    reset = env.reset("task_1")

    current = reset.observation.current_email
    while True:
        action = Action(
            email_id=current.id,
            priority=Priority.LOW,
            category=Category.INTERNAL,
            should_escalate=False,
        )
        result = env.step(action)
        if result.done:
            assert result.observation is None
            break
        current = result.observation.current_email

    assert env.state().done is True
    assert env.state().emails_processed == 10


def test_reward_range_always_valid():
    env = InboxEnvironment("task_3")
    reset = env.reset("task_3")

    current = reset.observation.current_email
    while True:
        action = Action(
            email_id=current.id,
            priority=Priority.SPAM,
            category=Category.SPAM,
            should_escalate=False,
            draft_response="",
            reasoning="Default stress test action.",
        )
        result = env.step(action)
        assert 0.0 <= result.reward.value <= 1.0
        if result.done:
            break
        current = result.observation.current_email


def test_all_three_tasks_complete():
    for task_id, expected_steps in [("task_1", 10), ("task_2", 15), ("task_3", 20)]:
        env = InboxEnvironment(task_id)
        reset = env.reset(task_id)
        current = reset.observation.current_email
        steps = 0

        while True:
            action = Action(
                email_id=current.id,
                priority=Priority.MEDIUM,
                category=Category.CUSTOMER_SUPPORT,
                should_escalate=False,
                draft_response="We are reviewing your request." if task_id == "task_3" else None,
            )
            result = env.step(action)
            steps += 1
            if result.done:
                break
            current = result.observation.current_email

        assert steps == expected_steps
        assert env.state().done is True


def test_spam_penalty_applied():
    env = InboxEnvironment("task_1")
    reset = env.reset("task_1")
    current = reset.observation.current_email

    action = Action(
        email_id=current.id,
        priority=Priority.SPAM,
        category=Category.SPAM,
        should_escalate=False,
    )
    result = env.step(action)

    assert result.reward.breakdown["spam_penalty"] == 0.1
    assert result.reward.value == 0.0
