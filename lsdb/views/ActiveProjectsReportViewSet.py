from openpyxl import Workbook
from rest_framework import viewsets
from lsdb.serializers import ActiveProjectsReportSerializer
from lsdb.models import Project
from lsdb.permissions import ConfiguredPermission
from rest_framework.decorators import action
import csv
from django.http import HttpResponse

class ActiveProjectsReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ActionCompletionDefinitions to be created, viewed, or edited.
    """
    logging_methods = ['POST', 'PATCH', 'DELETE']
    queryset = Project.objects.all()
    serializer_class = ActiveProjectsReportSerializer
    permission_classes = [ConfiguredPermission]


    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ActiveProjectsReportSerializer,)
    def active_projects(self, request, pk=None):
        """
        This action allows all interested parties dig into active project status.
        adding a `?show_archived=true` query parameter on GET will disable the active filter.
        The value can equal any string, I only test for the presence of the parameter.
        """
        self.context = {'request': request}
        show_archived = request.query_params.get('show_archived', 'TRUE')
        if show_archived.upper() == 'TRUE':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(disposition__complete=False)
        serializer = self.serializer_class(projects, many=True, context=self.context)
        data = serializer.data

        # Create an Excel workbook
        wb = Workbook()
        ws = wb.active

        # Assuming serializer.data is a list of dictionaries
        if data:

            # Define custom header names
            custom_header_names = {
                'number': 'Project Number',
                'project_manager_name': 'Project Manager',
                'customer_name': 'Customer',
                'disposition_name': 'Disposition',
                'percent_complete': 'Percentage Completed(%)',
                'work_order_name': 'Work Order Name',
                'last_action_date': 'Last Action Date'
            }

            # Write header with custom column names
            ws.append([custom_header_names.get(key, key) for key in data[0].keys()])

            # Write rows
            for item in data:

                # Include % symbol for percent_complete field
                percent_complete_value = item.get('percent_complete', '')
                if percent_complete_value:
                    item['percent_complete'] = f"{percent_complete_value}%"

                # Convert last_action_date to string representation
                last_action_date_value = item.get('last_action_date', '')
                if last_action_date_value:

                    # Assuming last_action_date_value is a datetime object
                    last_action_date_value = last_action_date_value.strftime('%Y-%m-%d')
                    item['last_action_date'] = last_action_date_value

                # Convert odict_values to list before appending
                ws.append(list(item.values()))

        # Create a response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Active_projects_report.xlsx"'

        # Save the workbook to the response
        wb.save(response)

        return response














    

  