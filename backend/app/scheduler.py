"""
Task scheduler for checking due tasks and sending reminders
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import List, Dict
import logging

from app.database import db
from app.email_service import email_service

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Scheduler for checking due tasks and sending email reminders"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.check_due_tasks,
            trigger=IntervalTrigger(minutes=5),
            id="check_due_tasks",
            name="Check due tasks and send reminders",
            replace_existing=True
        )

    async def check_due_tasks(self):
        """Check for due tasks and send reminders"""
        try:
            with db.get_connection() as conn:
                # Get tasks that are due and haven't had reminders sent
                cursor = conn.execute("""
                    SELECT
                        t.task_id,
                        t.title,
                        t.description,
                        t.due_date,
                        t.reminder_email,
                        t.user_id,
                        u.email as user_email
                    FROM tasks t
                    JOIN users u ON t.user_id = u.user_id
                    WHERE t.due_date <= ?
                    AND t.status = 'pending'
                    AND t.reminder_enabled = 1
                    AND t.email_sent = 0
                """, (datetime.utcnow(),))

                due_tasks = cursor.fetchall()

                for task in due_tasks:
                    await self.send_task_reminder(dict(task))

                # Mark overdue tasks
                conn.execute("""
                    UPDATE tasks
                    SET status = 'overdue'
                    WHERE due_date < ?
                    AND status = 'pending'
                """, (datetime.utcnow(),))

                logger.info(f"Checked {len(due_tasks)} due tasks")

        except Exception as e:
            logger.error(f"Error checking due tasks: {str(e)}")

    async def send_task_reminder(self, task: Dict):
        """Send email reminder for a task"""
        try:
            # Use reminder email if set, otherwise use user email
            recipient = task.get("reminder_email") or task.get("user_email")

            if not recipient:
                logger.warning(f"No email found for task {task['task_id']}")
                return

            # Format due date
            due_date = task["due_date"]
            if isinstance(due_date, str):
                due_date_str = due_date
            else:
                due_date_str = due_date.strftime("%Y-%m-%d %H:%M")

            # Send email
            success = await email_service.send_task_reminder(
                to_email=recipient,
                task_title=task["title"],
                task_description=task.get("description"),
                due_date=due_date_str
            )

            # Update task and record notification
            with db.get_connection() as conn:
                if success:
                    # Mark email as sent
                    conn.execute("""
                        UPDATE tasks
                        SET email_sent = 1
                        WHERE task_id = ?
                    """, (task["task_id"],))

                    # Record notification
                    notification_id = db.generate_uuid()
                    conn.execute("""
                        INSERT INTO email_notifications
                        (notification_id, task_id, recipient_email, status, sent_at)
                        VALUES (?, ?, ?, 'sent', ?)
                    """, (notification_id, task["task_id"], recipient, datetime.utcnow()))

                    logger.info(f"Reminder sent for task {task['task_id']}")
                else:
                    # Record failed notification
                    notification_id = db.generate_uuid()
                    conn.execute("""
                        INSERT INTO email_notifications
                        (notification_id, task_id, recipient_email, status, error_message)
                        VALUES (?, ?, ?, 'failed', 'Failed to send email')
                    """, (notification_id, task["task_id"], recipient))

                    logger.error(f"Failed to send reminder for task {task['task_id']}")

        except Exception as e:
            logger.error(f"Error sending task reminder: {str(e)}")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")

    def running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running


# Global scheduler instance
task_scheduler = TaskScheduler()
