class SkipDCLChars():
    from django.db import IntegrityError, transaction
    """
    This plugin looks for the Execution Group named "Post Light Soak"
    To use this plugin:
    POST {
        "work_order_id":WORK_ORDER_ID
        }
    """
    # Not needed here?
    # def __init__(self):


    def _test(self:object):
        return(None)

    def _run(self:object, work_order_id:int=None):

        from lsdb.models import ProcedureResult
        from lsdb.models import WorkOrder
        from lsdb.models import Unit

        from django.core.exceptions import ObjectDoesNotExist

        try:
            work_order = WorkOrder.objects.get(id=work_order_id)
        except ObjectDoesNotExist:
            return {'Error':'Work Order ID {} does not exist'.format(self.work_order_id)}

        number_modified = 0
        for unit in work_order.units.all():
            for proc_result in unit.procedureresult_set.filter(name="Post Light Soak", disposition__isnull=True):
                proc_result.allow_skip=True
                proc_result.save()
                number_modified += 1
        return "{} Procedure Results now skippable".format(number_modified)
