Visual inspection POST Sequence

test Setup:
from clean dev-up login to api
`http://localhost:8000/api/1.0/work_orders/1/test_units/` POST:
```
[
    { "unit": 1, "copy_history":true, "test_sequence":1 },
    { "unit": 2, "copy_history":true, "test_sequence":2 }
]
```
Pretend to be a client:
`http://localhost:8000/api/1.0/units/1/valid_asset/` POST:
```
{
    "asset_name":"VisualInspectionTestFixture_001"
}
```
Response:
```
[
    {
        "id": 2,
        "url": "http://localhost:8000/api/1.0/procedure_results/2/",
        "unit": "http://localhost:8000/api/1.0/units/1/",
        "procedure_definition": "http://localhost:8000/api/1.0/procedure_definitions/2/",
        "disposition": null,
        "start_datetime": null,
        "end_datetime": null,
        "customer_name": "Cypress Ave. Solar Equipment",
        "project_number": "PVEL-TEST-Project",
        "work_order": "http://localhost:8000/api/1.0/work_orders/1/",
        "work_order_name": "Test Work Order",
        "linear_execution_group": 2,
        "name": "Visual Inspection",
        "work_in_progress_must_comply": false,
        "group": "http://localhost:8000/api/1.0/groups/4/",
        "supersede": null,
        "version": "LSDB",
        "test_sequence_definition": "http://localhost:8000/api/1.0/test_sequence_definitions/1/",
        "test_sequence_definition_name": "Basic Characterizations",
        "step_results": [
            {
                "id": 2,
                "url": "http://localhost:8000/api/1.0/step_results/2/",
                "name": "Inspect Module",
                "notes": null,
                "procedure_result": "http://localhost:8000/api/1.0/procedure_results/2/",
                "step_definition": "http://localhost:8000/api/1.0/step_definitions/12/",
                "execution_number": 0,
                "disposition": null,
                "start_datetime": null,
                "duration": 0.0,
                "test_step_result": null,
                "archived": false,
                "description": null,
                "step_number": "0",
                "step_type": "http://localhost:8000/api/1.0/step_types/1/",
                "linear_execution_group": 1.0,
                "measurement_results": [
                    {
                        "id": 4,
                        "url": "http://localhost:8000/api/1.0/measurement_results/4/",
                        "date_time": null,
                        "step_result": "http://localhost:8000/api/1.0/step_results/2/",
                        "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/27/",
                        "user": null,
                        "location": null,
                        "software_revision": "0.0",
                        "disposition": null,
                        "result_defect": null,
                        "result_double": null,
                        "result_datetime": null,
                        "result_string": null,
                        "result_boolean": null,
                        "limit": "http://localhost:8000/api/1.0/limits/19/",
                        "reviewed_by_user": null,
                        "review_datetime": null,
                        "notes": null,
                        "tag": null,
                        "station": 0,
                        "start_datetime": null,
                        "duration": null,
                        "asset": null,
                        "do_not_include": false,
                        "name": "Defects Observed?",
                        "record_only": false,
                        "allow_skip": false,
                        "requires_review": false,
                        "measurement_type": "http://localhost:8000/api/1.0/measurement_types/52/",
                        "order": 1,
                        "report_order": 1,
                        "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/2/",
                        "measurement_result_type_field": "result_boolean",
                        "within_limits": false,
                        "result_files": []
                    }
                ]
            },
            {
                "id": 3,
                "url": "http://localhost:8000/api/1.0/step_results/3/",
                "name": "Record Visual Defect",
                "notes": null,
                "procedure_result": "http://localhost:8000/api/1.0/procedure_results/2/",
                "step_definition": "http://localhost:8000/api/1.0/step_definitions/7/",
                "execution_number": 0,
                "disposition": null,
                "start_datetime": null,
                "duration": 0.0,
                "test_step_result": null,
                "archived": false,
                "description": null,
                "step_number": "0",
                "step_type": "http://localhost:8000/api/1.0/step_types/1/",
                "linear_execution_group": 2.0,
                "measurement_results": [
                    {
                        "id": 5,
                        "url": "http://localhost:8000/api/1.0/measurement_results/5/",
                        "date_time": null,
                        "step_result": "http://localhost:8000/api/1.0/step_results/3/",
                        "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/28/",
                        "user": null,
                        "location": null,
                        "software_revision": "0.0",
                        "disposition": null,
                        "result_defect": null,
                        "result_double": null,
                        "result_datetime": null,
                        "result_string": null,
                        "result_boolean": null,
                        "limit": "http://localhost:8000/api/1.0/limits/19/",
                        "reviewed_by_user": null,
                        "review_datetime": null,
                        "notes": null,
                        "tag": null,
                        "station": 0,
                        "start_datetime": null,
                        "duration": null,
                        "asset": null,
                        "do_not_include": false,
                        "name": "Visual Inspection Defect",
                        "record_only": false,
                        "allow_skip": false,
                        "requires_review": false,
                        "measurement_type": "http://localhost:8000/api/1.0/measurement_types/43/",
                        "order": 1,
                        "report_order": 1,
                        "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/6/",
                        "measurement_result_type_field": "result_defect",
                        "within_limits": false,
                        "result_files": []
                    },
                    {
                        "id": 6,
                        "url": "http://localhost:8000/api/1.0/measurement_results/6/",
                        "date_time": null,
                        "step_result": "http://localhost:8000/api/1.0/step_results/3/",
                        "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/29/",
                        "user": null,
                        "location": null,
                        "software_revision": "0.0",
                        "disposition": null,
                        "result_defect": null,
                        "result_double": null,
                        "result_datetime": null,
                        "result_string": null,
                        "result_boolean": null,
                        "limit": "http://localhost:8000/api/1.0/limits/19/",
                        "reviewed_by_user": null,
                        "review_datetime": null,
                        "notes": null,
                        "tag": null,
                        "station": 0,
                        "start_datetime": null,
                        "duration": null,
                        "asset": null,
                        "do_not_include": false,
                        "name": "Visual Inspection Observation",
                        "record_only": false,
                        "allow_skip": true,
                        "requires_review": false,
                        "measurement_type": "http://localhost:8000/api/1.0/measurement_types/44/",
                        "order": 2,
                        "report_order": 2,
                        "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/3/",
                        "measurement_result_type_field": "result_string",
                        "within_limits": false,
                        "result_files": []
                    },
                    {
                        "id": 7,
                        "url": "http://localhost:8000/api/1.0/measurement_results/7/",
                        "date_time": null,
                        "step_result": "http://localhost:8000/api/1.0/step_results/3/",
                        "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/30/",
                        "user": null,
                        "location": null,
                        "software_revision": "0.0",
                        "disposition": null,
                        "result_defect": null,
                        "result_double": null,
                        "result_datetime": null,
                        "result_string": null,
                        "result_boolean": null,
                        "limit": "http://localhost:8000/api/1.0/limits/19/",
                        "reviewed_by_user": null,
                        "review_datetime": null,
                        "notes": null,
                        "tag": null,
                        "station": 0,
                        "start_datetime": null,
                        "duration": null,
                        "asset": null,
                        "do_not_include": false,
                        "name": "Visual Inspection Photo",
                        "record_only": false,
                        "allow_skip": true,
                        "requires_review": false,
                        "measurement_type": "http://localhost:8000/api/1.0/measurement_types/45/",
                        "order": 3,
                        "report_order": 3,
                        "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/4/",
                        "measurement_result_type_field": "result_files",
                        "within_limits": true,
                        "result_files": []
                    }
                ]
            }
        ]
    }
]
```
Test Scenario: Tech sees no defects.
`http://localhost:8000/api/1.0/measurement_results/4/submit/` POST:
(disposition here is "Pass")
```
{
    "result_boolean": true,
    "asset": 4,
    "disposition":2
}
```
... and then you can close the step and the procedure with the same disposition.

Test Scenario: user notices 2 defects. These interactions all assume that the
user has completed making observations then hits the "submit" button

fill in "Inspect Module" step's measurement_result
(this ID should be the measurement_result attached to the "Inspect Module" step_result)
(disposition here is: "Requires Review")
`http://localhost:8000/api/1.0/measurement_results/4/submit/` POST:
```
{
    "result_boolean": false,
    "asset": 4,
    "disposition": 13
}
```
... and then you can close the step with the same disposition

Every visual inspection procedure_result has 2 step results, the first is the
boolean we just finished the second is "Record Visual Defect". In our scenario
we are recording 2 defects, we'll use one and then add a second. For the sake of
brevity, we'll skip the first one as it follows the same patterns.

Step 1 Add a step that matches the definition of the included one:
`http://localhost:8000/api/1.0/procedure_results/2/add_step/` POST:
```
{
    "step_definition": 7,
    "execution_number": 0,
    "disposition": 13,
    "start_datetime": "2020-12-17T22:43:59.379447Z"
}
```
Response:
```
{
    "id": 14,
    "url": "http://localhost:8000/api/1.0/step_results/14/",
    "name": "Record Visual Defect",
    "notes": null,
    "procedure_result": "http://localhost:8000/api/1.0/procedure_results/2/",
    "step_definition": "http://localhost:8000/api/1.0/step_definitions/7/",
    "execution_number": 0,
    "disposition": "http://localhost:8000/api/1.0/dispositions/13/",
    "start_datetime": "2020-12-17T22:43:59.379447Z",
    "duration": null,
    "test_step_result": null,
    "archived": false,
    "description": null,
    "step_number": null,
    "step_type": "http://localhost:8000/api/1.0/step_types/1/",
    "linear_execution_group": 0.0,
    "measurement_results": [
        {
            "id": 34,
            "url": "http://localhost:8000/api/1.0/measurement_results/34/",
            "date_time": null,
            "step_result": "http://localhost:8000/api/1.0/step_results/14/",
            "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/28/",
            "user": null,
            "location": null,
            "software_revision": "0.0",
            "disposition": null,
            "result_defect": null,
            "result_double": null,
            "result_datetime": null,
            "result_string": null,
            "result_boolean": null,
            "limit": "http://localhost:8000/api/1.0/limits/19/",
            "reviewed_by_user": null,
            "review_datetime": null,
            "notes": null,
            "tag": null,
            "station": 0,
            "start_datetime": null,
            "duration": null,
            "asset": null,
            "do_not_include": false,
            "name": "Visual Inspection Defect",
            "record_only": false,
            "allow_skip": false,
            "requires_review": false,
            "measurement_type": "http://localhost:8000/api/1.0/measurement_types/43/",
            "order": 1,
            "report_order": 1,
            "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/6/",
            "measurement_result_type_field": "result_defect",
            "within_limits": false,
            "result_files": []
        },
        {
            "id": 35,
            "url": "http://localhost:8000/api/1.0/measurement_results/35/",
            "date_time": null,
            "step_result": "http://localhost:8000/api/1.0/step_results/14/",
            "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/29/",
            "user": null,
            "location": null,
            "software_revision": "0.0",
            "disposition": null,
            "result_defect": null,
            "result_double": null,
            "result_datetime": null,
            "result_string": null,
            "result_boolean": null,
            "limit": "http://localhost:8000/api/1.0/limits/19/",
            "reviewed_by_user": null,
            "review_datetime": null,
            "notes": null,
            "tag": null,
            "station": 0,
            "start_datetime": null,
            "duration": null,
            "asset": null,
            "do_not_include": false,
            "name": "Visual Inspection Observation",
            "record_only": false,
            "allow_skip": true,
            "requires_review": false,
            "measurement_type": "http://localhost:8000/api/1.0/measurement_types/44/",
            "order": 2,
            "report_order": 2,
            "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/3/",
            "measurement_result_type_field": "result_string",
            "within_limits": false,
            "result_files": []
        },
        {
            "id": 36,
            "url": "http://localhost:8000/api/1.0/measurement_results/36/",
            "date_time": null,
            "step_result": "http://localhost:8000/api/1.0/step_results/14/",
            "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/30/",
            "user": null,
            "location": null,
            "software_revision": "0.0",
            "disposition": null,
            "result_defect": null,
            "result_double": null,
            "result_datetime": null,
            "result_string": null,
            "result_boolean": null,
            "limit": "http://localhost:8000/api/1.0/limits/19/",
            "reviewed_by_user": null,
            "review_datetime": null,
            "notes": null,
            "tag": null,
            "station": 0,
            "start_datetime": null,
            "duration": null,
            "asset": null,
            "do_not_include": false,
            "name": "Visual Inspection Photo",
            "record_only": false,
            "allow_skip": true,
            "requires_review": false,
            "measurement_type": "http://localhost:8000/api/1.0/measurement_types/45/",
            "order": 3,
            "report_order": 3,
            "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/4/",
            "measurement_result_type_field": "result_files",
            "within_limits": true,
            "result_files": []
        }
    ]
}
```
Now we have an empty `step_result` and all of the measurement_results required to post.
