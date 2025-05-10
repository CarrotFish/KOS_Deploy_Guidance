
from better_utils import BetterKOS
import asyncio

async def main():
    async with BetterKOS('192.168.42.1', 50051) as kos:
        try:
            await kos.load_session('model_100.onnx')
            input('press to continue')
            await kos.loop()
        except:
            pass
        await kos.reset()

asyncio.run(main())