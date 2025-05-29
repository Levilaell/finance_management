from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Report, ReportSchedule, ReportTemplate


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({"message": "Report generation started"})


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Report list"})


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        return Response({"message": f"Report {report_id} details"})


class DownloadReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        return Response({"message": f"Download report {report_id}"})


class ReportSchedulesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Report schedules list"})


class CreateScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({"message": "Create report schedule"})


class UpdateScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, schedule_id):
        return Response({"message": f"Update schedule {schedule_id}"})


class DeleteScheduleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, schedule_id):
        return Response({"message": f"Delete schedule {schedule_id}"})


class ReportTemplatesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Report templates list"})