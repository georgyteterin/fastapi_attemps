import asyncio
import uvicorn
from api import app as app_fastapi
from monitoring import app as app_monitoring
from server_settings import LOGGING_CONFIG


class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame) -> None:
        app_monitoring.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    server = Server(config=uvicorn.Config(app_fastapi, host='0.0.0.0', port=8000, workers=1, loop="asyncio",
                                          log_config=LOGGING_CONFIG, log_level="info"))

    api = asyncio.create_task(server.serve())
    monitoring = asyncio.create_task(app_monitoring.serve())

    await asyncio.wait([monitoring, api])

if __name__ == "__main__":
    asyncio.run(main())