"""
Reports app Celery tasks
Asynchronous report generation
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_report_task(report_id):
    """
    Generate report asynchronously
    """
    try:
        from .models import Report
        report = Report.objects.get(id=report_id)
        
        # Update status to processing
        report.status = 'processing'
        report.save()
        
        # Here you would implement actual report generation
        # For now, we'll just simulate it
        logger.info(f"Generating report {report_id} of type {report.report_type}")
        
        # Simulate report generation
        import time
        time.sleep(5)  # Simulate processing time
        
        # Update report as completed
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.file_size = 1024 * 100  # 100KB dummy size
        report.save()
        
        logger.info(f"Report {report_id} generated successfully")
        
        # TODO: Send notification to user
        
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {str(e)}")
        
        # Update report as failed
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
        except:
            pass


@shared_task
def process_scheduled_reports():
    """
    Process all scheduled reports that are due
    """
    from .models import ReportSchedule, Report
    from datetime import timedelta
    
    now = timezone.now()
    
    # Get all active schedules
    schedules = ReportSchedule.objects.filter(is_active=True)
    
    for schedule in schedules:
        # Check if schedule is due
        if schedule.is_due():
            logger.info(f"Processing scheduled report: {schedule.name}")
            
            # Calculate date range based on frequency
            if schedule.frequency == 'daily':
                period_start = now.date() - timedelta(days=1)
                period_end = now.date()
            elif schedule.frequency == 'weekly':
                period_start = now.date() - timedelta(days=7)
                period_end = now.date()
            elif schedule.frequency == 'monthly':
                period_start = (now.date().replace(day=1) - timedelta(days=1)).replace(day=1)
                period_end = now.date().replace(day=1) - timedelta(days=1)
            else:
                continue
            
            # Create report
            report = Report.objects.create(
                company=schedule.company,
                report_type=schedule.report_type,
                title=f"{schedule.name} - {now.strftime('%Y-%m-%d')}",
                period_start=period_start,
                period_end=period_end,
                created_by=schedule.created_by,
                status='pending'
            )
            
            # Queue report generation
            generate_report_task.delay(report.id)
            
            # Update schedule
            schedule.last_run_date = now
            schedule.run_count += 1
            schedule.save()
            
            logger.info(f"Scheduled report queued: {report.id}")


@shared_task
def cleanup_old_reports():
    """
    Clean up old reports to save storage
    """
    from .models import Report
    from datetime import timedelta
    
    # Delete reports older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_reports = Report.objects.filter(
        created_at__lt=cutoff_date,
        status='completed'
    )
    
    count = old_reports.count()
    old_reports.delete()
    
    logger.info(f"Cleaned up {count} old reports")
    
    return count