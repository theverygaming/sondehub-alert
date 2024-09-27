import logging
import sondehub
import datetime
from . import sonde

_logger = logging.getLogger(__name__)

def _radiosonde_frame_from_sondehub_frame(frame):
    # how the frame is structured:
    # https://github.com/projecthorus/sondehub-infra/blob/main/swagger.yaml
    # https://github.com/projecthorus/sondehub-infra/blob/46db8e1f96d778ec37a9e88d37bf49584315136b/swagger.yaml#L747

    return sonde.RadiosondeFrame(
            manufacturer=frame.get("manufacturer"),
            serial=frame.get("serial"),
            sonde_type=frame.get("type"),
            sonde_subtype=frame.get("subtype"),
            frequency=frame.get("frequency"),
            tracker_url=f"https://sondehub.org/{frame.get('serial')}",
            original_frame=frame,
            time_received=datetime.datetime.fromisoformat(frame["time_received"]),
            time_published=datetime.datetime.fromisoformat(frame["datetime"]),
            lat=frame.get("lat"),
            lon=frame.get("lon"),
            alt=frame.get("alt"),
        )

def _on_message(message):
    frame = _radiosonde_frame_from_sondehub_frame(message)
    #_logger.info(frame)
    #_logger.info(frame.get_sonde_unique_id())

    # TODO: check if frame times are
    # - sane (published and rx close)
    # - recent, we don't want old af frames
    # - not in the fucking future sob
    # if sanity checks don't pass, reject the frame

    sonde.add_sonde_frame(frame)
    sonde.send_notifications()

def start_stream():
    sondehub_mqtt = sondehub.Stream(on_message=_on_message, auto_start_loop=False)
    while True:
        sondehub_mqtt.loop_forever()
        # TODO: figure out which exceptions could be raised and catch them
        #try:
        #    sondehub_mqtt.loop_forever()
        #except:
        #    _logger.exception("Exception in MQTT loop")
