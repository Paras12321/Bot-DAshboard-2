import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import bot_service.db_access as db_access
from bot_service.discord_bot import discord_handler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("worker")


POLL_INTERVAL: int = int(os.getenv("POLL_INTERVAL", 5))
WORKER_CONCURRENCY: int = int(os.getenv("WORKER_CONCURRENCY", 5))

async def process_task(task, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        task_id = task["id"]
        bot_id = task["bot_id"]
        token = task["token"]
        target_id = task["target_id"]
        message = task["message"]
        bot_name = task["bot_name"]

        log.info("Processing task #%s | bot=%s",
        task_id, bot_name)

        try:    
            result = await discord_handler.send_message(token, int(target_id), message)

            if result["status"] == "success":
                db_access.mark_task_done(task_id, status="done")
                db_access.create_log(
                    task_id=task_id,
                    bot_id=bot_id,
                    level="info",
                    message=f"Task #{task_id} succeeded",
                    details=result.get("detail", ""),
                )
                log.info("Task #%s completed successfully.", task_id)
            else:
                db_access.mark_task_done(task_id, status="failed",
                                         error_message=result["detail"])
                db_access.create_log(
                    task_id=task_id,
                    bot_id=bot_id,
                    level="error",
                    message=f"Task #{task_id} failed",
                    details=result.get("detail", ""),
                )
                log.warning("Task #%s failed: %s", task_id, result["detail"])

        except Exception as exc:
            log.exception("Unexpected error executing task #%s", task_id)
            db_access.mark_task_done(task_id, status="failed", error_message=str(exc))
            db_access.create_log(
                task_id=task_id,
                bot_id=bot_id,
                level="error",
                message=f"Exception during task #{task_id}",
                details=str(exc),
            )


async def worker_loop(stop_event: asyncio.Event) -> None:
    semaphore = asyncio.Semaphore(WORKER_CONCURRENCY)

    log.info("Worker started | poll_interval=%ss concurrency=%s",
             POLL_INTERVAL, WORKER_CONCURRENCY)

    db_access.create_log(level="info", message="Bot service worker started")

    
    bots = db_access.get_active_bots()
    if bots:
        log.info("Active bots (%d): %s", len(bots),
                 ", ".join(b['name'] for b in bots))
    else:
        log.warning("No active bots found. Add bots via the dashboard.")

    in_flight: set[asyncio.Task] = set()

    while not stop_event.is_set():
        try:
            tasks = db_access.get_pending_tasks()

            if tasks:
                log.info("Found %d pending task(s).", len(tasks))
                for task in tasks:
                    db_access.mark_task_processing(task["id"])
                    t = asyncio.create_task(
                        process_task(task, semaphore),
                        name=f"task_{task['id']}",
                    )
                    in_flight.add(t)
                    t.add_done_callback(in_flight.discard)
            
            await asyncio.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nWorker stopped by user")
            db_access.create_log(level="info", message="Bot service worker stopped")
            break

        except Exception as e:
            print(f"\nWorker error: {e}")
            db_access.create_log(level="error", message="Worker loop error", details=str(e))
            await asyncio.sleep(POLL_INTERVAL)


async def main():
    """Entry point for the worker."""
    stop_event = asyncio.Event()
    try:
        await worker_loop(stop_event)
    except KeyboardInterrupt:
        print("\nShutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
