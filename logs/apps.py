from django.apps import AppConfig
from threading import Thread
from datetime import datetime, timedelta
import bisect
import time

from .views import logs_by_service, lock

def purge_old_logs():
# purging older logs
    while True:
        try:
            now = datetime.now()
            threshold = now - timedelta(hours=1)
            with lock:
                for service, logs in list(logs_by_service.items()):
                    cutoff = bisect.bisect_left(logs, (threshold, ""))
                    if cutoff > 0:
                        logs_by_service[service] = logs[cutoff:]
        except Exception as e:
            print("Error during log purge:", e)
        time.sleep(60)

class LogsConfig(AppConfig):
    name = 'logs'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Start the auto-purge thread once the app is ready.
        Thread(target=purge_old_logs, daemon=True).start()
