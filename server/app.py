from openenv.core.env_server.http_server import create_app

from models import InboxAction, InboxObservation
from server.inbox_environment import InboxEnvironment

app = create_app(
    InboxEnvironment,
    InboxAction,
    InboxObservation,
    env_name="inboxenv",
    max_concurrent_envs=10,
)


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
