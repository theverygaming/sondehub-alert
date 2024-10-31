import dataclasses
import datetime
import logging
import threading
import geopy.distance
from . import config
from . import telegram

_logger = logging.getLogger(__name__)

@dataclasses.dataclass
class RadiosondeFrame:
    # identification purposes
    manufacturer: str
    serial: str
    sonde_type: str
    sonde_subtype: str
    frequency: float

    # other stuff
    tracker_url: str
    original_frame: dict

    # times
    time_received: datetime.datetime
    time_published: datetime.datetime

    # location data
    lat: float
    lon: float
    alt: float

    def get_sonde_unique_id(self):
        fields = [
            self.manufacturer,
            self.serial,
            self.sonde_type,
            self.sonde_subtype,
            self.frequency,
        ]
        fields = [str(f) for f in fields]
        return " + ".join(fields)

    def get_age_seconds(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.time_received).total_seconds()

recent_sondes = {}
recent_sondes_lock = threading.Lock()

inactive_sondes = {}
inactive_sondes_lock = threading.Lock()

def add_sonde_frame(frame):
    sonde_id = frame.get_sonde_unique_id()
    with recent_sondes_lock:
        recent_sondes[sonde_id] = frame
    with inactive_sondes_lock:
        if sonde_id in inactive_sondes:
            del inactive_sondes[sonde_id] # well it aint inactive anymore

def _update_inactive_sondes():
    with recent_sondes_lock, inactive_sondes_lock:
        # check if sondes are past the "inactive" time limit
        keys_to_delete = [] # done because deleting keys inside a dict iteration seems to be a bad idea
        for k in recent_sondes:
            age_secs = recent_sondes[k].get_age_seconds()
            if age_secs < config.SONDE_INACTIVE_SECONDS:
                continue
            # move to inactive
            _logger.info(f"Moving sonde with ID '{k}' to inactive after {age_secs} seconds")
            inactive_sondes[k] = recent_sondes[k]
            keys_to_delete.append(k)
        for k in keys_to_delete:
            del recent_sondes[k]

def send_notifications():
    def get_inactive_sondes():
        _update_inactive_sondes()
        global inactive_sondes
        with inactive_sondes_lock:
            inactive_sondes_clone = inactive_sondes
            inactive_sondes = {}
        return inactive_sondes_clone

    def send_frame_notifs(frame, notify, distance_m):
        msg = f"""A sonde landed nearby!
Info about the sonde:
    Manufacturer: {frame.manufacturer}
    Type: {frame.sonde_type}
    Subtype: {frame.sonde_subtype}
    Frequency: {frame.frequency}
    Serial: {frame.serial}
Last frame:
    Lat, Lon: `{frame.lat}, {frame.lon}`
    Alt: {frame.alt:.1f}m
    {frame.get_age_seconds():.1f}s ago
    {distance_m/1000:.1f}km from your set location
    gmaps: https://www.google.com/maps/place/{frame.lat},{frame.lon}
Unique ID: `{frame.get_sonde_unique_id()}`
Tracker link: {frame.tracker_url}
"""
        for notif in notify:
            match notif["platform"]:
                case "telegram":
                    telegram.send_message(notif["chatID"], msg)

    for k, last_frame in get_inactive_sondes().items():
        for notif in config.NOTIFICATIONS:
            distance_m = geopy.distance.distance((last_frame.lat, last_frame.lon), (notif["lat"], notif["lon"])).m
            if notif["radius"] < distance_m:
                continue
            if last_frame.alt > notif["maxHeight"]:
                continue
            send_frame_notifs(last_frame, notif["notify"], distance_m)
