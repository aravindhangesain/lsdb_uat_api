# HaveBlue: AKA DRF LSDB

## API Considerations:

- LSDB is rooted at `/api/<version>/` API version is 1.0
- Future versions will be managed by creating a new view for the same endpoint and registering it in a new url
  file `urls.py`. This is for future breaking changes only.

## Coding Convention:

- All models are named singularly and camel cased: `SequenceDefinition`
- all model columns all lowercase with underscores: `work_in_progress_must_comply`
- many to many relationships named with the plural form of the
  table: `asset_types = models.ManyToManyField('AssetType')`
- views named camel case with `ViewSet` : `OrganizationViewSet`
- Serializers named camel case with `Serializer` : `UserSerializer`
- to differentiate between local objects and Django model `objects`, use `obj` for internal object references
- filters are included in the view file where they are used.

## File organization:

- models go into lsdb/models
- one file per model, named after the model declared. like: `ModelSample.py`
- model must be imported in `__init__.py` like: `from .ModelSample import ModelSample as ModelSample`
- import models into other code like: `from lsdb.models import ModelSample`
- reverse lookups use the built in `_set` notation whenever possible.
- all code related to ASIMOV is under `./asimov`

## Branch management:

This project is going to use Gitflow branch management. git flow install not required, but it does make some tasks like
creating new branches easy.

All active development is beeing coordinated on the `develop` branch. We will merge `develop` to `root` weekly, until
release. Once we tag 1.0 we will *only*
merge to `root` for hotfixes or another release.

### Pull Requests and Reviewers:

Creating a Pull Request (PR) should be done when pushing in your feature or fix as they can be a very handy tool for
chasing down bugs. Reviewers and approvals are optional (for now), but encouraged.

### Branch naming:

/feature/issue-### OR /feature/feature-name /bugfix/### OR /bugfix/issue-###

## ASIMOV:

Welcome to the first project using Asimov environment management. Inside the
`asimov` directory you will find all of the docker files used to create your development environment. This "platform" is
still under development and only supports Django-rest and Node.js projects.

### Bring Up Development Environment

- Linux: ```asimov/scripts/dev-up.sh```
- Command line parameters are passed down to this script. If you want to detach from the docker console, include `-d` on
  the command line.
- Windows:

### Tear Down Development Environment

- Linux: ```asimov/scripts/dev-down.sh```
- Windows:

### Clean Up Development Containers

- Linux: ```asimov/scripts/dev-clean.sh```
- Windows:

## API Documentation

There are a couple of key areas that require a bit of explanation for using the endpoints. All endpoints are controlled
via permissions stored in the database which can be managed by local superusers.

### id vs name

For database optimization, all updates should be made using an `ID`. The server will return and `ID` and the `URL` for
all child and referred objects along with the human readable `name`. In cases such as Disposition, which is a foreign
key to the object being manipulated, the name is what the user will see and use to determine the selection. The client
should maintain a lookup to the ID that gets sent back to the server.

Names will not change within an API version as that would be a breaking change. Additional names may be created as
needed, and the ID associated with the name may change. Any change that would update the ID would require maintenance
and downtime, so clients can safely cache the start-up/boostrap disposition ids. (this belongs in the admin guide, not
just the developer's guide)

MeasurementType and Disposition are two places where the "shared vocabulary" of the client and server will be based on
strings, specifically the `name` string.

https://github.com/pvevolutionlabs/HaveBlue/issues/207 has background on this process.

### Attachments / files

Files are uploaded via post to `azure_files`. Azure files can be associated with
`crates`, `measurement_results`, `units`, and `unit_types`.

#### File associations with database objects

Files must be uploaded before the are linked to the database object.
`POST` a fully formed `AzureFile` object, you will get the `AzureFile` object created as a response. Use the provided ID
to link the file:
`POST`: `/api/1.0/crates/{$ID}/link_files/`
Body:

```
{
    "id":Integer
}
```

The server will respond with the updated parent object with the attached file as a child in the appropriate field.

#### Attachments for emails

Attaching a file to an email can be done by defining the `attachments` kwarg in the `throttled_email` method.

The `attachments` property must be a List of dictionaries, defined as follows:

```python
attachments = [
    {
        "file_name": "String: The file name that will be displayed on the email",
        "file_data": "The actual data to be sent",
        "mime_type": "The MIME type of the data to be sent"
    }, ...
]
```

MIME types can be seen [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types)

The files can be attached just as we are handling them now (BytesIO objects), the MIME type informs how it will be
interpreted later.

### Dispositions

disposition_codes is the endpoint to manage the available dispositions for any endpoint that allows the recording of
dispositions.

They are:
`/crates/dispositions/`
`/measurement_results/dispositions/`
`/plan_definitions/dispositions/`
`/step_results/dispositions/`
`/work_orders/dispositions/`

### Asset Communication

All of the assets have a common sequence of events that they will need to execute in order to PUT results into LSDB. The
initial sequence is the same for all test stations. Errors return HTTP error codes (404:NOT FOUND, 401:NOT AUTHORIZED,
400:BAD REQUEST ) for the common failure cases.

- Where am I?
- Who am I?
- What am I doing here?
- Submit result measurements into correct locations
- Submit completed step data
- Submit completed procedure data

#### Where Am I?

Client:
`GET` : `/api/1.0/assets/?asset_type=${id}` OR `/api/1.0/assets/?name=DiodeTestFixture_001`

*If the client calls for `asset_types` you will receive a list of assets matching that type. This example presumes that
the client knows the current asset_name via a configuration file on the local desktop, or the react client will need to
present the user a list of assets to select the correct one. The client should presume that if the length of the
response list is only 1, that the current asset is the one returned.*

Server:

```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "url": "http://localhost:8000/api/1.0/assets/1/",
            "name": "DiodeTestFixture_001",
            "description": "",
            "location": "http://localhost:8000/api/1.0/locations/1/",
            "location_name": "BKL",
            "last_action_datetime": "2020-08-18T22:56:40.641000Z",
            "asset_type_name": "Diode Tester",
            "asset_type": "http://localhost:8000/api/1.0/asset_types/11/",
            "disposition_name": "Available",
            "disposition": "http://localhost:8000/api/1.0/dispositions/16/"
        }
    ]
}
```

#### Who am I?

Client:
`GET` : `/api/1.0/units/?serial_number=${id}`

*The ${id} here should be scanned in from a bar code scanner or numeric input. The query here is very strict and will
return all units in the system with that particular serial number. If the list of units returned is 1 (the common case)
the client should proceed to the next step. Otherwise, the operator will need to be presented with a list of matching
units to select. It is a requirement of the database that the serial number of a unit be unique for all units from the
same manufacturer/customer. Presenting the user with the manufacturer & model number should be enough to verify the
correct serial number to select.*

Server:

```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "url": "http://localhost:8000/api/1.0/units/1/",
            "unit_type": "http://localhost:8000/api/1.0/unit_types/1/",
            "fixture_location": "http://localhost:8000/api/1.0/assets/1/",
            "crate": "http://localhost:8000/api/1.0/crates/1/",
            "serial_number": "001001",
            "location": "http://localhost:8000/api/1.0/locations/1/",
            "name": "",
            "model": "CASE-SM-001",
            "description": "72 cell test unit",
            "notes": "",
            "history": false,
            "project_set": [
                "http://localhost:8000/api/1.0/projects/1/"
            ],
            "unit_images": [],
            "workorder_set": [
                "http://localhost:8000/api/1.0/work_orders/1/"
            ]
        }
    ]
}
```

#### What am I doing here?

Client:
`POST` URL : `/api/1.0/units/${id}/valid_asset/`
`POST` Body:

```
{
"asset_name":"DiodeTestFixture_001"
}
```

*The ${id} above needs to come from the "id" response in the "who am I?" for the unit. The `asset_name` needs to be a
perfect match for the current test station.*

Server:

```
[
    {
        "id": 39,
        "url": "http://localhost:8000/api/1.0/procedure_results/39/",
        "unit": "http://localhost:8000/api/1.0/units/1/",
        "procedure_definition": "http://localhost:8000/api/1.0/procedure_definitions/1/",
        "disposition": null,
        "start_datetime": null,
        "end_datetime": null,
        "work_order": "http://localhost:8000/api/1.0/work_orders/1/",
        "linear_execution_group": 1,
        "name": "Diode Test",
        "work_in_progress_must_comply": false,
        "group": "http://localhost:8000/api/1.0/groups/4/",
        "supersede": null,
        "version": "0.1",
        "test_sequence_definition": "http://localhost:8000/api/1.0/test_sequence_definitions/1/",
        "step_results": [
            {
                "id": 34,
                "url": "http://localhost:8000/api/1.0/step_results/34/",
                "name": "Test Diode",
                "notes": null,
                "procedure_result": "http://localhost:8000/api/1.0/procedure_results/39/",
                "step_definition": "http://localhost:8000/api/1.0/step_definitions/4/",
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
                        "id": 109,
                        "url": "http://localhost:8000/api/1.0/measurement_results/109/",
                        "date_time": null,
                        "step_result": "http://localhost:8000/api/1.0/step_results/34/",
                        "measurement_definition": "http://localhost:8000/api/1.0/measurement_definitions/3/",
                        "user": null,
                        "location": null,
                        "software_revision": "0.0",
                        "disposition": null,
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
                        "name": "Diode Test Pass/Fail",
                        "record_only": false,
                        "allow_skip": false,
                        "requires_review": true,
                        "measurement_type": "http://localhost:8000/api/1.0/measurement_types/11/",
                        "order": 3,
                        "report_order": 3,
                        "measurement_result_type": "http://localhost:8000/api/1.0/measurement_result_types/2/",
                        "measurement_result_type_field": "result_boolean",
                        "result_files": []
                    },
                    {...},
                    {...}
                ]
            }
        ]
    }
]
```

*Additional `measurement_results` stanzas removed for brevity. The server will reply with the full set of steps and
measurements required for this procedure to be completed. The client now has all of the data required to fill in the
required data. The client needs to read the contents of `measurement_result_type_field` to determine the result field to
post the data. The client will need to ensure that the data being put matches the data type described.*

#### Submit result measurements into correct locations

Client:
`POST` URL : `/api/1.0/units/${id}/valid_asset/`
`POST` Body:

```
{
    "date_time": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "location": ID,
    "software_revision": String,
    "disposition": ID
    "result_double": FloatField,
    "result_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "result_string": String,
    "result_boolean": Boolean,
    "reviewed_by_user": username
    "review_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "notes": String,
    "tag": String,
    "station": Integer,
    "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "duration": FloatField,
    "asset": ID
    "do_not_include": Boolean,
    "requires_review": Boolean,
    "order": Integer,
    "report_order": Integer
}
```

#### Submit completed step data

`POST`: URL: `/api/1.0/step_results/${id}/submit/`
`POST` Body:

```
{
    "disposition": ID,
    "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "notes": String,
    "duration": Integer,
    "execution_number": Integer,
    "archived": Boolean,
    "test_step_result": ID
}
```

#### Submit completed procedure data

`POST`: URL: `/api/1.0/procedure_results/${id}/submit/`
`POST` Body:

```
{
    "disposition": ID,
    "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
    "end_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format
}
```

## Test Client Transaction Sequence

All `paths` are relative. Full response and request objects for these transactions listed above.

### Initialization:

1. POST `signin/` with credentials, attach token to header
1. GET `asset_types/?name="(asset type name)"` (the React app may be called from different test stations of the same
   function)
    1. If exactly one asset is returned, use it; else if more than one asset is returned, ask the user for the correct
       one; else, inform the user there are no valid assets of this type.
1. GET `dispositions/` (since we're invoking dispositions by name, I use this list to set up a dictionary of all
   dispositions IDs and names, regardless of target; you may want to
   GET `disposition_codes/?name="{disposition target}"` as needed, instead)

### Prepare to test:

1. Ask the user for a serial number
1. GET `units/?serial_number="(serial number)"`
    1. If exactly one unit is returned, use it; else if more than one unit is returned, ask the user for the correct
       one; else, inform the user there are no valid units with that serial number
1. Display the manufacturer name, model name, and BOM corresponding to the selected unit
1. POST `units/(unit id)/valid_asset/ with {"asset_name":"(asset name)"}`
    1. If exactly one procedure result is returned, use it; else if more than one procedure result is returned, ask the
       user for the correct one; else, inform the user there are no valid procedure results ("There's no work to do here
       on this unit")
1. Display the customer name, project number, work order name, test sequence definition name, and procedure name
   corresponding to the selected procedure result.

### Submit results:

1. Select the step result by name from the procedure result return object (for Visual Inspection, Wet Leakage Current,
   and Diode Test, there's only one)
1. GET the step result, which will return the list of associated measurement results
1. For each pre-defined measurement result, select the measurement result by name, then
   POST `measurement_results/(meas result id)/submit/` with:

  ```
  {
      "disposition":(disp id),
      "result_(type)":(result)
  }
  ```

(appropriate disposition TBD)

1. If new measurement results are gathered (such as visual inspection findings), determine their measurement definition
   ID with a GET `measurement_definitions/?name="(meas def name)"`
1. For each undefined measurement result, POST `step_results/(step result id)/add_measurement/` with:

  ```
  {
      "disposition":(disp id),
      "measurement_definition":(meas def id),
      "result_(type)":(result)
  }
  ```

(appropriate disposition TBD)

1. Once all measurement results are POSTed, finalize the step result with a POST `step_result/(step result id)/submit/`
   with:

  ```
  {
      "disposition":(disp id)
  }
  ```

(appropriate disposition TBD)

1. Once all step results are POSTed (should just be the one), finalize the procedure result with a
   POST `procedure_result/(proc result id)/submit/` with:

  ```
  {
      "disposition":(disp id)
  }
  ```

(appropriate disposition TBD)

### construct an EL Test result:

1. download EL images
    * https://haveblue-django.azurewebsites.net/api/1.0/azure_files/103/download/ (RAW)
    * https://haveblue-django.azurewebsites.net/api/1.0/azure_files/104/download/ (CROPPED)
2. set up test sequences
    1. assign module '001001' to DH2000 via http://localhost:3000/project_management/customer/1
    2. get procedure result from new traveler: http://localhost:8000/api/1.0/units/1/measurement_history/ look for "EL
       Image at 1.0x Isc"
       (should be ID#3)
    3. upload EL images as local azure files at http://localhost:8000/api/1.0/azure_files/ (note the ID of RAW and
       CROPPED)
    4. set procedure result disposition to 'requires review'
        1. http://localhost:8000/api/1.0/procedure_results/3/submit/ POST `{"disposition":13}`
        2. http://localhost:8000/api/1.0/step_results/3/submit/ POST `{"disposition":13}`
        3. http://localhost:8000/api/1.0/measurement_results/23/submit/ POST `{"disposition":13,"result_double":0.0}`
        4. http://localhost:8000/api/1.0/measurement_results/21/submit POST `{"disposition":13,"result_double":30.0}`
        5. http://localhost:8000/api/1.0/measurement_results/18/submit POST `{"disposition":13}`
        6. http://localhost:8000/api/1.0/measurement_results/19/submit POST `{"disposition":13}`
    5. attach RAW to raw measurement result (ID#19)
       http://localhost:8000/api/1.0/measurement_results/19/link_files/ POST `{"id":RAW ID}`
    6. attach CROPPED to "EL Image (grayscale)" result (ID#18)
       http://localhost:8000/api/1.0/measurement_results/19/link_files/ POST `{"id":CROPPED ID}`

### Construct a Test Start (for stressors)

This sample uses the 2019 DH2000 PQP test (/api/1.0/test_sequence_definitions/4/).

### Initialization:

1. POST `/signin/` with credentials, attach token to header
1. GET `/assets/stressors/` to assemble a list of assets that are compatible with "stressor" procedure definitions.
1. Present the user with a pull-down list of all stressors. Use the `id` of the asset that the user selects from the
   stressor list in future tansactions calling for `asset_id`. Store the `asset_name` for the `valid_asset` call coming
   up. (I know that's inconsistent)
    * Lock the asset selector to prevent the user from attempting to change assets.
1. GET `/assets/$ID/procedures/` to get the list of `procedure_definition` objects that are supported at this location.
1. present the user with a pull-down list of all procedures returned. Use the `id` of the procedure that the user
   selects in future transactions calling for `procedure_id`. This procedure will also need to be attached to
   the `valid asset`
    * If the user changes the procedure, clear all serial numbers from the check-in staging area
1. _this needs to be explained better:_ GET `dispositions/`
    * As of v1.1.9 the correct disposition for procedure_results is "Requires Review" (id:13)
    * Stresses must set disposition to "In Progress" (1.2 id:7) on start.

### Prepare to test:

1. Ask the user for a serial number
1. GET `units/?serial_number="(serial number)"`
    1. If exactly one unit is returned, use it; else if more than one unit is returned, ask the user for the correct
       one; else, inform the user there are no valid units with that serial number
1. Display the returned serial number as: `serial number [model name]` in the group staging area.
1. POST `units/(unit id)/valid_asset/` with:

```
{
      "asset_name":"(asset name)"
      "procedure_definition":$ID
}
```

1. If exactly one procedure result is returned, use it; else if more than one procedure result is returned, ask the user
   for the correct one; else, inform the user there are no valid procedure results ("There's no work to do here on this
   unit"). Version 1.2 introduces enforced execution order, so the client still needs to account for the possibility of
   multiple results being returned.

### Submit results:

1. Select the FIRST step result by execution group number, verify that the name corresponds to "test start"
1. GET the step result, which will return the list of associated measurement results
1. For each pre-defined measurement result, select the measurement result by name, then
   POST `measurement_results/(meas result id)/submit/` with:

  ```
  {
      "disposition":7,
      "result_(type)":(result)
  }
  ```

(appropriate disposition TBD)

1. If new measurement results are gathered (such as visual inspection findings), determine their measurement definition
   ID with a GET `measurement_definitions/?name="(meas def name)"`
1. For each undefined measurement result, POST `step_results/(step result id)/add_measurement/` with:

  ```
  {
      "disposition":(disp id),
      "measurement_definition":(meas def id),
      "result_(type)":(result)
  }
  ```

(appropriate disposition TBD)

1. Once all measurement results are POSTed, finalize the step result with a POST `step_result/(step result id)/submit/`
   with:

  ```
  {
      "disposition":(disp id)
  }
  ```

(appropriate disposition TBD)

1. Once all step results are POSTed (should just be the one), finalize the procedure result with a
   POST `procedure_result/(proc result id)/submit/` with:

  ```
  {
      "disposition":(disp id)
  }
  ```

(appropriate disposition TBD)

### return an in memory file from a view:

```
@transaction.atomic
@action(detail=False, methods=['get','post'])
def text_file(self, request, pk=None):
    mem_file = BytesIO()
    foo = "this is a string"
    mem_file.write(bytes(foo, 'utf-8'))
    mem_file.seek(0)
    filename=timezone.now().strftime('%b-%d-%Y-%H%M%S')
    response = HttpResponse(mem_file, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename={}.PAN'.format(filename)
    return response
```
