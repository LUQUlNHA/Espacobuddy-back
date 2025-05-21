from datetime import datetime
import json

class Routine:
    def __init__(self, id, routine_name, feeder_id, schedule_time, portion_size, user_id):
        self.id = id
        self.routine_name = routine_name
        self.feeder_id = feeder_id
        self.schedule_time = schedule_time
        self.portion_size = portion_size
        self.user_id = user_id

    def to_dict(self):
        now = datetime.now()
        return {
            "device_id": self.feeder_id,
            "executed_at": now.strftime("%Y-%m-%dT%H:%M"),
            "routine_name": self.routine_name,
            "portion": self.portion_size,
            "schedule_time": self.schedule_time.strftime("%H:%M")
        }

    def already_exists(self, some_list) -> bool:
        for item in some_list:
            if item.id == self.id:
                return True
        return False
