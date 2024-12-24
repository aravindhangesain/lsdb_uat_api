import json
from functools import reduce

from django.contrib.auth.models import User
from django.apps import apps
from django.db import IntegrityError, transaction
from django.conf import settings
from django.utils import timezone

from lsdb.models import Group, Plugin
from lsdb.models import ActionResult


@transaction.atomic
def create_action(**kwargs):
    action_definition = kwargs.pop('action_definition')  # this should be an object at this point
    disposition = kwargs.pop('disposition')
    groups = kwargs.pop('groups')
    parent_object = kwargs.pop('parent_object')  # this should be an object at this point
    params = kwargs.pop('request_params')

    try:
        action = ActionResult.objects.create(
            name=params.get('name'),
            description=params.get('description'),
            disposition=disposition,
            action_definition=action_definition,
            execution_group=params.get('execution_group'),
            done_datetime=params.get('done_datetime'),
            start_datetime=params.get('start_datetime'),
            promise_datetime=params.get('promise_datetime'),
            eta_datetime=params.get('eta_datetime'),
            content_object=parent_object
        )
    except IntegrityError as e:
        return e, False
    action.completion_criteria.set(action_definition.completion_criteria.all())
    if groups:
        for group in groups:
            action.groups.add(Group.objects.get(id=group))
    return action, True


def is_completion_criteria_complete(completion_criteria_values):
    return bool(completion_criteria_values) and False not in completion_criteria_values


def check_completion_criteria(action_result, action_completion_result_set, plugin_compile):
    response_dict = {}
    for criterion in action_completion_result_set:
        if not criterion.criteria_completed:
            plugin = Plugin.objects.get(name=criterion.action_completion_definition.plugin_name)
            params = json.loads(criterion.action_completion_definition.plugin_params)
            for key in params.keys():
                try:
                    params[key] = reduce(getattr, params[key].split(','), action_result)
                except:
                    pass
            errors, byte_code = plugin_compile(plugin)
            exec(byte_code)
            plugin_class = locals().get(plugin.name)
            plugin_instance = plugin_class()
            response_dict[criterion.action_completion_definition.name] = (
                    plugin_instance._run(**params) == criterion.action_completion_definition.expected_result)
            criterion.criteria_completed = response_dict[criterion.action_completion_definition.name]
            criterion.completed_datetime = timezone.now()
            criterion.save()

    return response_dict
