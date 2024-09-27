import logging
import threading
import asyncio
import multiprocessing
import os
from . import telegram, sondehub

_logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
    _logger.info("hiii :3")
    # This threading shit is stupid i give up sob
    # this probably works well enough :tm:
    def tg_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            telegram.launch_bot()
        except:
            _logger.exception("Exception in telegram thread")
            os._exit(1)
        finally:
            os._exit(0)
    def sondehub_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sondehub.start_stream()
        except:
            _logger.exception("Exception in sondehub thread")
            os._exit(1)
        finally:
            os._exit(0)
    t_tg = multiprocessing.Process(target=tg_thread)
    t_sondehub = threading.Thread(target=sondehub_thread)
    t_tg.start()
    t_sondehub.start()
    t_tg.join() # this is a child process, it should never die
    os._exit(0)
    t_sondehub.join()
