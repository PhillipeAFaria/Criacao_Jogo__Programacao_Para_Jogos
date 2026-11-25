import asyncio
import sys
from pathlib import Path
import pygame
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
async def main():
    import platform
    if sys.platform != 'emscripten':
        raise RuntimeError('Use INICIAR_PREVIA.bat nesta copia web.')
    bridge = platform.window.fdm
    try:
        from svz.web_runtime import run
        await run(bridge)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        bridge.fail('Nao foi possivel iniciar o jogo: '+str(exc))
asyncio.run(main())
