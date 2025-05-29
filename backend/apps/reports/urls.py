"""
Reports app URLs
"""
from django.urls import path

from .views import (
    GenerateReportView,
    ReportListView,
    ReportDetailView,
    DownloadReportView,
    ReportSchedulesView,
    CreateScheduleView,
    UpdateScheduleView,
    DeleteScheduleView,
    ReportTemplatesView,
)

app_name = 'reports'

urlpatterns = [
    # Report generation and management
    path('generate/', GenerateReportView.as_view(), name='generate-report'),
    path('list/', ReportListView.as_view(), name='report-list'),
    path('<int:report_id>/', ReportDetailView.as_view(), name='report-detail'),
    path('<int:report_id>/download/', DownloadReportView.as_view(), name='download-report'),
    
    # Scheduled reports
    path('schedules/', ReportSchedulesView.as_view(), name='report-schedules'),
    path('schedules/create/', CreateScheduleView.as_view(), name='create-schedule'),
    path('schedules/<int:schedule_id>/update/', UpdateScheduleView.as_view(), name='update-schedule'),
    path('schedules/<int:schedule_id>/delete/', DeleteScheduleView.as_view(), name='delete-schedule'),
    
    # Report templates
    path('templates/', ReportTemplatesView.as_view(), name='report-templates'),
]