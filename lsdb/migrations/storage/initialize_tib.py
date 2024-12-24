# Migration script to run for 1.2 launch
def initialize_tib():
    from lsdb.modles import WorkOrder
    work_orders = WorkOrder.objects.all()
    for work_order in work_orders:
        if work_order.units.all():
            for unit in work_order.units.all():
                unit.tib = work_order.tib
                unit.save()
