import json
import logging
import threading
import bisect
from datetime import datetime
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# In-memory storage: each service maps to a sorted list of log entries.
# Each log entry is a tuple: (timestamp, message)
logs_by_service = defaultdict(list)
lock = threading.RLock()


def parse_iso(ts_str):
    #checking if the timestamp is in ISO 8601 format
    try:
        return datetime.fromisoformat(ts_str)
    except Exception as e:
        logger.error(f"Invalid timestamp '{ts_str}': {e}")
        raise ValueError("Invalid timestamp format. Must be ISO 8601.")


def insert_log(service, log_entry):
    with lock:
        bisect.insort(logs_by_service[service], log_entry)


def handle_post(request):

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    # Validate required fields.
    for field in ("service", "timestamp", "message"):
        if field not in data:
            return JsonResponse({"error": f"Missing '{field}' in JSON body"}, status=400)

    service = data["service"]
    timestamp_str = data["timestamp"]
    message = data["message"]

    if not isinstance(service, str) or not isinstance(message, str):
        return JsonResponse({"error": "Service and message must be strings"}, status=400)

    try:
        ts = parse_iso(timestamp_str)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    try:
        insert_log(service, (ts, message))
    except Exception as e:
        logger.error(f"Error storing log for service '{service}': {e}")
        return JsonResponse({"error": "Error storing log"}, status=500)

    logger.info(f"Stored log for service '{service}' at {ts.isoformat()}")
    return JsonResponse({"status": "Log entry stored"}, status=201)


def handle_get(request):

    service = request.GET.get("service")
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    if not service or not start_str or not end_str:
        return JsonResponse({"error": "Missing 'service', 'start', or 'end' query parameter"}, status=400)

    try:
        start_dt = parse_iso(start_str)
        end_dt = parse_iso(end_str)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    if end_dt < start_dt:
        return JsonResponse({"error": "End date cannot be earlier than start date"}, status=400)


    try:
        with lock:
            logs = logs_by_service.get(service, [])
            # Use binary search to find boundaries in the sorted list.
            left_index = bisect.bisect_left(logs, (start_dt, ""))
            right_index = bisect.bisect_right(logs, (end_dt, chr(127)))
            result = [
                {"timestamp": ts.isoformat(), "message": msg}
                for ts, msg in logs[left_index:right_index]
            ]
    except Exception as e:
        logger.error(f"Error retrieving logs for service '{service}': {e}")
        return JsonResponse({"error": "Error retrieving logs"}, status=500)

    logger.info(f"Retrieved {len(result)} logs for service '{service}' between {start_dt.isoformat()} and {end_dt.isoformat()}")
    return JsonResponse({"logs": result}, status=200)


@csrf_exempt
def logs_view(request):
    if request.method == "POST":
        return handle_post(request)
    elif request.method == "GET":
        return handle_get(request)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
