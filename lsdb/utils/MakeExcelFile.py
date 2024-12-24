import hashlib
import time
from io import BytesIO
from threading import Thread

import openpyxl
from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from django.utils import timezone

from lsdb.models import AzureFile
from lsdb.utils.Notification import Notification


class ExcelFile(openpyxl.Workbook):
    """
    This is supposed to make it easer to make in-memory excel files
    """

    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self.default_filename = 'lsdb_excel_file'

    def get_memory_file(self):
        return BytesIO(openpyxl.writer.excel.save_virtual_workbook(self.workbook))

    def get_response(self, filename=None):
        if not filename:
            filename = self.default_filename
        response = HttpResponse(self.get_memory_file(), content_type=self.content_type)
        response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(filename)
        return response


class DeferredFile(Thread):
    def __init__(self, **kwargs):
        Thread.__init__(self)

    def revenue_report(self, **kwargs):
        self.command = '_revenue_report'
        self.user = kwargs['user']
        self.start()

    def run(self):
        start = time.perf_counter_ns()
        report, expires, file_name = getattr(self, self.command)()
        end = time.perf_counter_ns()
        newfile = self._make_azurefile(report, expires=expires, file_name=file_name)
        print(newfile)

        # except Exception as e:
        #     print(e)
        # send an email when it's done
        email_notify = Notification()

        email_notify.throttled_email(
            template='requested_file',
            user=self.user,
            file_duration=f"{(end - start) / 1000000000} Seconds",
            ticket_link=f"{settings.CLIENT_HOST}/project_management/download_file/{newfile.id}"
        )

    # moved to the Uti temporarily, belongs as a plugin
    def _revenue_report(self):
        start = time.perf_counter_ns()
        from lsdb.models import Project
        from lsdb.utils.HasHistory import unit_completion, unit_revenue
        excel_file = ExcelFile()
        sheet = excel_file.workbook.active
        report = []
        projects = Project.objects.filter(disposition__complete=False).prefetch_related('customer',
                                                                                        'workorder_set').order_by(
            'customer__name')
        # pandas dump to sheet:
        # for row in dataframe_to_rows(df, index=False, header=True):
        #     sheet.append(r)
        # HUGE KLUGE! this is execeptionally unoptomized.
        for project in projects:
            for work_order in project.workorder_set.all():
                row = [project.customer.name, project.number, work_order.name, 0.0, 0.0, 0.0, 0.0]
                for unit in work_order.units.all():
                    complete = unit_completion(unit)
                    if complete > 0:
                        revenue = unit_revenue(unit)
                        row[3] += 1  # units counted
                        row[4] += revenue  # revenue for the unit
                        row[5] += revenue * complete / 100  # recognizable revenue
                        row[6] += complete
                        # print(revenue, complete, revenue*complete)
                if row[3] > 0:
                    row[6] = row[6] / row[3]
                # report.append(row)
                sheet.append(row)
                # print('"{0}","{1}","{2}",{3:.0f},{4:.3f},{5:.3f},{6:.3f}'.format(*row))
        file_name = 'RevenueReport-{}.xlsx'.format(timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        # foo = excel_file.get_memory_file()
        print(file_name)
        end = time.perf_counter_ns()
        # azurefile = self.make_azurefile(excel_file.get_memory_file(), expires=True, file_name=file_name)
        # print('elapsed:',(end - start)/1000000000)
        # print(azurefile.file)
        # file_object = File(foo)
        # hasher = hashlib.new('sha256')
        # for buf in file_object.chunks(chunk_size = 65536):
        #         hasher.update(buf)
        # # if file_name:
        # file_object.name=file_name
        # # else:
        # #     file_object.name='binary_blob-{}.bin'.format(timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        # expires = False
        # azure_file = AzureFile.objects.create(
        #     file = file_object,
        #     hash = hasher.hexdigest(),
        #     hash_algorithm = 'sha256',
        #     length = file_object.size,
        #     name = file_object.name,
        #     uploaded_datetime = timezone.now(),
        #     blob_container = None,
        #     expires=expires,
        # )
        # return azure_file

        return excel_file.get_memory_file(), True, file_name

    # TODO: This
    # Make an azurefile and return the ... URL?
    def _make_azurefile(self, bytes_object, expires=False, file_name=None):
        print('CALLED')
        file_object = File(bytes_object)
        hasher = hashlib.new('sha256')
        for buf in file_object.chunks(chunk_size=65536):
            hasher.update(buf)
        if file_name:
            file_object.name = file_name
        else:
            file_object.name = 'binary_blob-{}.bin'.format(timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        azure_file = AzureFile.objects.create(
            file=file_object,
            hash=hasher.hexdigest(),
            hash_algorithm='sha256',
            length=file_object.size,
            name=file_object.name,
            uploaded_datetime=timezone.now(),
            blob_container=None,
            expires=expires,
        )
        return azure_file
