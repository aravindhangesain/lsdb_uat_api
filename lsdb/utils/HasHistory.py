from lsdb.models import MeasurementResult
from django.db.models import Sum, Max, Q
from django.utils import timezone

def unit_history(unit):
    # check for any results that involve this unit
    # This one lazy query
    count = MeasurementResult.objects.filter(step_result__procedure_result__unit=unit)
    count = count.filter(disposition__isnull=False).count()
    return count >0

def unit_revenue(unit):
    # returns the total revenue dollars assigned to this unit
    queryset = unit.procedureresult_set.exclude(supersede=True,
        procedure_definition__group__name__iexact='calibration')
    revenue = queryset.all().aggregate(revenue=Sum('procedure_definition__project_weight')).get('revenue')
    return revenue

def unit_minutes(unit):
    # This one will compute how far along this unit is in its current test plan
    # based on aggregate duration of the procedures involved. unoptomized algorithm
    queryset = unit.procedureresult_set.exclude(supersede=True,
        procedure_definition__group__name__iexact='calibration')
    # determine total minutes
    total = queryset.all().aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')
    revenue = queryset.all().aggregate(revenue=Sum('procedure_definition__project_weight')).get('revenue')
    # Chuck empty modules:
    if queryset.filter(unit__procedureresult__disposition__isnull=False).count() == 0:
        return (0, 0)
    # determine "done to"
    done_to = queryset.all().annotate(done_to= Max('unit__procedureresult__linear_execution_group',
                filter=Q(unit__procedureresult__disposition__isnull=False)))\
                .distinct().first()
    # print(done_to.linear_execution_group)
    # determine minutes done up to the done_to EG
    if done_to:
        done_to = done_to.done_to
        minutes_past = queryset.filter(linear_execution_group__lt=done_to)\
            .exclude(disposition__name__iexact='in progress')\
            .aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')
        # add time doen in this EG:
        minutes_done = queryset.filter(linear_execution_group=done_to)\
            .exclude(disposition__isnull=True)\
            .exclude(disposition__name__iexact='in progress')\
            .aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')
        # add any time in_progress
    else:
        minutes_done = 0
        minutes_past = 0
    progress_minutes = queryset.filter(disposition__name__iexact='in progress')\
            .values('procedure_definition__aggregate_duration','start_datetime').first()
    if progress_minutes == None:
        progress_minutes = 0
        elapsed = 0
    else:
        elapsed = min(
            (timezone.now() - progress_minutes.get('start_datetime')).total_seconds() / 60
            , progress_minutes.get('procedure_definition__aggregate_duration'))
    if minutes_done == None: minutes_done = 0
    if minutes_past == None: minutes_past = 0

    minutes_completed = minutes_done + minutes_past + elapsed
    return (total, minutes_completed)


def unit_completion(unit):
    #unit_completion calls unit_minutes and returns a percent
    (total, minutes_completed) = unit_minutes(unit)
    if total == 0 and minutes_completed == 0:
        return 0
    return 100 * minutes_completed / total

def work_order_completion(work_order):
    queryset = work_order.procedureresult_set.exclude(supersede=True, procedure_definition__name__iexact='calibration')
    # determine total minutes
    total = queryset.aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')
    # determine "done to" for all procedure_results in the work_order
    queryset = queryset.annotate(done_to= Max('unit__procedureresult__linear_execution_group',
            filter=Q(unit__procedureresult__disposition__isnull=False)))
    # determine minutes done up to the done_to EG
    queryset = queryset.aggregate(past_minutes=Sum('unit__procedureresult__procedure_definition__aggregate_duration',
            filter=Q(unit__procedureresult__linear_execution_group__lt=done_to)))
            # distinct=True)

    for thing in queryset:
        print(thing.id,thing.unit.id, thing.done_to,thing.linear_execution_group,thing.past_minutes)

    queryset = queryset.exclude(disposition__name__iexact='in progress')\
        .distinct()
    # add time doen in this EG:
    minutes_done = queryset.filter(linear_execution_group=done_to)\
        .exclude(disposition__isnull=True)\
        .exclude(disposition__name__iexact='in progress')\
        .aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')
    # add any time in_progress
    progress_minutes = queryset.filter(disposition__name__iexact='in progress')\
        .values('procedure_definition__aggregate_duration','start_datetime').first()
    if progress_minutes == None:
        progress_minutes = 0
        elapsed = 0
    else:
        elapsed = min(
            (timezone.now() - progress_minutes.get('start_datetime')).total_seconds() / 60
            , progress_minutes.get('procedure_definition__aggregate_duration'))
    if minutes_done == None: minutes_done = 0
    if minutes_past == None: minutes_past = 0
    # None to zero (pandas)
    # calculate done/total %
    return 100 * (minutes_done + minutes_past + elapsed) / total


def project_history(unit, project):
    count = MeasurementResult.objects.filter(step_result__procedure_result__unit=unit)
    count = count.filter(step_result__procedure_result__unit__project=project)
    count = count.filter(disposition__isnull=False).count()
    return count >0

def measurements_completed(project):
    count = MeasurementResult.objects.filter(step_result__procedure_result__work_order__project=project)
    count = count.filter(disposition__isnull=False).count()
    return count

def measurements_requested(project):
    count = MeasurementResult.objects.filter(step_result__procedure_result__work_order__project=project).count()
    return count

def work_order_measurements_completed(work_order):
    completed_time = 0
    total_time = 0
    for unit in work_order.units.all():
        (total, minutes_completed) = unit_minutes(unit)
        completed_time += minutes_completed
        total_time += total
    if total_time == 0:
        return 0
    else:
        return 100 * completed_time / total_time

def work_order_measurements_requested(work_order):
    count = MeasurementResult.objects.filter(step_result__procedure_result__work_order=work_order).count()
    return count
