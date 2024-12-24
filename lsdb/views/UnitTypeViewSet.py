import json
from io import BytesIO

from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.serializers import UnitTypeSerializer
from lsdb.serializers import UnitSerializer
from lsdb.serializers import AzureFileSerializer
from lsdb.models import UnitType
from lsdb.models import AzureFile
from lsdb.permissions import ConfiguredPermission


class UnitTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UnitType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer
    permission_classes = [ConfiguredPermission]

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=UnitTypeSerializer,
    )
    def link_files(self, request, pk=None):
        """
        This action will link an existing AzureFile to this unit type.
        POST: {"id":1} to link azurefile id=1 to this unittype
        """
        self.context={'request':request}
        queryset = UnitType.objects.get(id=pk)
        if request.method == 'POST':
            params = json.loads(request.body)
            file_id = params.get('id')
            if file_id:
                # TODO: This could end up throwing a 500 on bad ID from the client
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.datasheets.add(attachment)
                queryset.save()
        serializer = UnitTypeSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=UnitTypeSerializer,
    )
    def unlink_files(self, request, pk=None):
        """
        This action will unlink an existing AzureFile from this unit type.
        POST: {"id":1} to unlink azurefile id=1 to this unittype
        """
        self.context={'request':request}
        queryset = UnitType.objects.get(id=pk)
        if request.method == 'POST':
            params = json.loads(request.body)
            file_id = params.get('id')
            if file_id:
                # TODO: This could end up throwing a 500 on bad ID from the client
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.datasheets.remove(attachment)
                queryset.save()
        serializer = UnitTypeSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
        serializer_class=UnitSerializer,
    )
    def units(self, request, pk=None):
        '''
        Return list of units with this type
        '''
        self.context ={'request':request}
        unit_type = UnitType.objects.get(id=pk)
        serializer = UnitSerializer(unit_type.unit_set.all(),many=True,context=self.context)

        return Response (serializer.data)

    @action(detail=True, methods=['get'],
        serializer_class=UnitTypeSerializer,
    )
    def panfile(self, request, pk=None):
        '''
        Baseline PVsyst .PAN File Optimized from Nameplate Datasheet Values on LSDB HaveBlue, e.g., Virtual Traveler VT
        Author: Kenneth J. Sauer (kjsauer on GitHub)
        Acknowledgments:
            Dr. André Mermoud (PVsyst)
            Dr. Thomas Roessler
            Dr. Cliff Hansen (Sandia National Laboratories; cwhanse on GitHub)
            Junaid H. Fatehi (jhfatehi on GitHub)

        Script contents/coverage:
            1. .PAN file parameter optimizer based on datasheet values in LSDB HaveBlue Virtual Traveler VT
            2. .PAN file writer

        Function outputs description:
            - Important, output PVsyst .PAN file "optimized" parameters:
                u_n: Temperature coefficient of gamma (TODO: Revisit; fix at 0)
                Rs: Series resistance [Ohms]
                Rsh: Shunt resistance [Ohms]
                Rsh0: Shunt resistance at reference irradiance [Ohms]
                Rsh_exp: Shunt resistance existential term [unitless] (set equal to PVsyst default value of 5.5)

        Notes:
            - Alpha v1 applies a default efficiency deviation from STC at Low Irradiance Conditions (LIC) of -3.5%. TODO: Consider other default value strategies OR record value in LSDB HaveBlue, e.g., Virtual Traveler VT.
            - TEL: should record this in module technology (Mono-PERC, MonoPERC, Bifi, N-Type)
            - MD: LIC is 200W/m^2, STC=1000, temp:25c "relative effeciency" -- for later when making MeasuredPAN
            - MD: Defaults for DatasheetPAN TBD and should be used here
        TODO:
            1. See TODO throughout this code (& elsewhere).
            2. Transcribe default Hidden Parameters in PVsyst. Get exact match to PVsyst .PAN default nameplate baseline datasheet .PAN file using default gamma values in Hidden Parameters of PVsyst.

        Work instructions WIs for running Unit Test example PV module - Method #1:
            1. Go to:
                http://localhost:8000/api/1.0/unit_types/1/
            2. Enter the following PV module parameters required for PVsyst .PAN file parameter optimization and click "Put"*:
            *Put means "Make a PUT request on the Unit Type Instance resource"
                    Short-circuit current, Isc      = 9.91;  [Amps]
                    Open-circuit voltage, Voc       = 49.2;  [Volts]
                    Max. power current, Imp         = 9.4;   [Amps]
                    Max. power voltage, Vmp         = 40.2;  [Volts]
                    Cells in series, Ns             = 72;    [unitless]; cells in series; cannot handle N_p
                Needed for .PAN writer, not .PAN optimizer:
                    Nameplate Pmax, nameplate_pmax  = 380;   [Watts]
                    TempCo of Isc, alpha_isc        = 0.04;  [%/degC]; TODO: Confirm units in LSDB HaveBlue, e.g., Virtual Traveler VT
                    TempCo of Voc, beta_voc         = -0.33; [%/degC]; TODO: Confirm units in LSDB HaveBlue, e.g., Virtual Traveler VT
                    TempCo of Pmp, gamma_pmp        = -0.43  [%/degC]; TODO: Confirm units in LSDB HaveBLue, e.g., Virtual Traveler VT
                    Cell area, cell_area            = 243.36 [mm^2];
                LSDB HaveBlue also presently requires the following parameter inputs (beyond those required for PVsyst .PAN file parameter optimization):
                    Module length, module_length    = 2000   [mm]
                    Module width, module_width      = 1000   [mm]
                    Nameplate power, nameplate_pmax = 380    [Watts]
                    System voltage, system_voltage  = 1000   [Volts]
            3. Click Extra Actions\panfile.
                http://localhost:8000/api/1.0/unit_types/1/panfile/

        Work instructions - Method #2
            1. http://localhost:8000/api/1.0/unit_types/
            2. Enter above PV module's characteristics values
            3. Click "Post"
            4. Record unique ID, e.g., 1021
            5. Enter unique ID it the following URL: http://localhost:8000/api/1.0/unit_types/1021/panfile/
        '''
        self.context ={'request':request}
        unit_type = UnitType.objects.get(id=pk)
        # Voc = unit_type.module_property.voc
        # Isc = unit_type.module_property.isc
        # Imp = unit_type.module_property.imp

        ##############################################################################
        # Introduction
        ##############################################################################
        # Function "make_pan_baseline.py":

        # Function to Make a Baseline PVsyst .PAN File from a PV Module's Nameplate
        # Datasheet Parameters Listed on PV Evolution Lab's (PVEL's) Laboratory
        # Services Database (LSDB) HaveBlue, e.g., in the LSDB HaveBlue Virtual
        # Traveler VT Form

        # Author(s)
        # Kenneth J. Sauer (kjsauer on GitHub)

        # Acknowledgment(s) for Sauer-based open-source PVLIB functions
        # Dr. Thomas Roessler
        # Dr. André Mermoud (PVsyst)
        # Dr. Cliff Hansen (Sandia National Laboratories; cwhanse on GitHub)
        # Junaid H. Fatehi (jhfatehi on GitHub)

        # TODO:
        # Add open-source pvlib-python (PVLIB) 3-clause BSD license to LSDB HaveBlue

        ##############################################################################
        # Learning
        ##############################################################################
        # Function in MATLAB: Broadcast a function over a collection/matrix/vector
        # f = @(x) x.^2
        # g = @(x, y) x + 2 + y.^2
        # x = 1:10
        # y = 2:11
        # f(x)
        # g(x, y)

        # Function in Python (functions broadcast directly)
        # def f(x):
        #     return x**2
        # def g(x, y):
        #     return x + 2 + y**2
        # x = np.arange(1, 10, 1)
        # y = np.arange(2, 11, 1)
        # f(x)
        # g(x, y)

        ##############################################################################
        # TODO
        ##############################################################################
        # TODO: Define where these values come from (datasheet, manufacturer, witness)

        # TODO: Clarify (GpoaEff_LIC, GpoaEff_STC) vs. (GpoaInc_LIC, GpoaInc_STC)

        # TODO: Clarify GpoaEff vs. GpoaInc; see more above; go w/ Gpoa for now

        # TODO: Clarify Tmod vs. Tcell; go w/ Tcell for now

        # TODO:
        # --Pull from other LSDB data structure containing IEC 61853-1 matrix data
        # --Find out these variable names in LSDB
        # --Need to get/retrieve: Mes P-G-T from LSDB
        # data_mes = {
        # ...
        # }

        # TODO:
        # --Define default Hidden Parameters in LSDB
        # --Decide on values to use
        # --Start w/ default dEtaRel_STC_LIC assumption
        # --Later see if default gamma makes more sense
        # -3.5% represents median strategy, e.g., p50
        # -5.0% represents more conservative strategy, e.g., p90

        # TODO:
        # Need to fit mugamma w/ gPmpRef

        # TODO:
        # 1. First G - Then T Approach
        # 2. G-T Matrix Approach

        # TODO:
        # Restore as much fidelity as possible to PAN solver functions, i.e.,
        # unalter as much as possible; revisit later after first pass working.

        # TODO:
        # Add QA/QC flags if ideality factor (gamma) is outside range of 0.9-1.1.

        ##############################################################################
        # Algorithm - Pseudocode
        ##############################################################################

        # Calc.P_200
        # Build "data"
        # Build "datasheet"

        ##############################################################################
        # Algorithm - Code
        ##############################################################################

        # Import Python package dependencies
        import json
        import pandas as pd
        pd.__version__ # confirm pandas is working (no bug)

        # Function schematic
        # function [make_pan_baseline] = f(module_property)

        # Gather required input variables from LSDB HaveBlue
        # TODO: Add to LSDB HaveBlue defaults (default values) in LSDB HaveBlue Hidden Parameters HP
        # LIC is equivalent to _g200_t25
        dEtaRel_STC_LIC = -0.03 # unitless; assumption -0.035 is something closer to typical median (-3.5%); NEW: Update to match unit test example LIC behavior of -3%
        # alternatively, use -0.05 (5%); NEWER: Approx. & bypass default Gamma method using -3% to roughly align w/ PVsyst default Gamma method end results for multiple module types tested w/in PVsyst GUI.

        # NEW Sauer 2021-05-20
        # dEtaRel_STC_LIC = -0.032
        # dEtaRel_STC_g800_t25 = 0.005
        # dEtaRel_STC_g600_t25 = 0.004
        # dEtaRel_STC_g400_t25 = -0.004

        # TODO:
        # Explore possibility to estimate using default gamma values specific to
        # each PV cell technology--see PVsyst Hidden Parameters.

        # Button in LSDB HaveBlue, e.g., Virtual Traveler VT: Make PVsyst .PAN Baseline

        # JSON data object/structure
        # module_property = """
        # {
        #     "id": 1,
        #     "url": "https://haveblue-django.azurewebsites.net/api/1.0/module_properties/1/",
        #     "number_of_cells": 72,
        #     "nameplate_pmax": 380.0,
        #     "module_width": 1090.0,
        #     "module_height": 1700.0,
        #     "system_voltage": 1000.0,
        #     "module_technology": "https://haveblue-django.azurewebsites.net/api/1.0/module_technologies/4/",
        #     "module_technology_name": "Mono-PERC",
        #     "auditor": "",
        #     "audit_date": null,
        #     "audit_report_id": "",
        #     "isc": 9.91,
        #     "voc": 49.2,
        #     "imp": 9.4,
        #     "vmp": 40.2,
        #     "alpha_isc": 0.06,
        #     "beta_voc": -0.23,
        #     "gamma_pmp": -0.34,
        #     "cells_in_series": 72,
        #     "cells_in_parallel": 1,
        #     "cell_area": 243.36,
        #     }
        # """
        # mod_props = json.loads(module_property)

        # Gather required input variables from LSDB HaveBlue
        # id                     = mod_props['id']
        # url                    = mod_props['url']
        # number_of_cells        = mod_props['number_of_cells']
        # nameplate_pmax         = mod_props['nameplate_pmax']
        # module_width           = mod_props['module_width']
        # module_height          = mod_props['module_height']
        # system_voltage         = mod_props['system_voltage']
        # module_technology      = mod_props['module_technology']
        # module_technology_name = mod_props['module_technology_name']
        # auditor                = mod_props['auditor']
        # audit_date             = mod_props['audit_date']
        # audit_report_id        = mod_props['audit_report_id']
        # Isc                    = mod_props['isc']
        # Vmp                    = mod_props['vmp']
        # Imp                    = mod_props['imp']
        # Voc                    = mod_props['voc']
        # alpha_isc              = mod_props['alpha_isc']/100 # convert %/C to 1/C
        # beta_voc               = mod_props['beta_voc']
        # gamma_pmp              = mod_props['gamma_pmp']
        # Ns                     = mod_props['cells_in_series']
        # cells_in_parallel      = mod_props['cells_in_parallel']
        # cell_area              = mod_props['cell_area']

        # Gather required input variables from LSDB HaveBlue
        # id                     = unit_type.module_property['id']
        # url                    = unit_type.module_property['url']
        number_of_cells        = unit_type.module_property.number_of_cells
        nameplate_pmax         = unit_type.module_property.nameplate_pmax
        module_width           = unit_type.module_property.module_width
        module_height          = unit_type.module_property.module_height
        system_voltage         = unit_type.module_property.system_voltage
        # module_technology      = unit_type.module_property['module_technology']
        module_technology_name = unit_type.module_property.module_technology.name
        # auditor                = unit_type.module_property['auditor']
        # audit_date             = unit_type.module_property['audit_date']
        # audit_report_id        = unit_type.module_property['audit_report_id']
        Isc                    = unit_type.module_property.isc
        Vmp                    = unit_type.module_property.vmp
        Imp                    = unit_type.module_property.imp
        Voc                    = unit_type.module_property.voc
        alpha_isc              = unit_type.module_property.alpha_isc/100     # Convert %/degC to 1/degC
        beta_voc               = unit_type.module_property.beta_voc/100      # Convert %/degC to 1/degC
        gamma_pmp              = unit_type.module_property.gamma_pmp/100     # Convert %/degC to 1/degC
        cells_in_series        = unit_type.module_property.cells_in_series
        cells_in_parallel      = unit_type.module_property.cells_in_parallel # Consider renaming "cells_in_parallel" to "substrings_in_parallel" or "cell_substrings_in_parallel"
        cell_area              = unit_type.module_property.cell_area
        # KJS 2021-05-12: Addition of Bifacial Bifi
        bifacial               = unit_type.module_property.bifacial # PICKUP; Bifacial Bifi Boolean in LSDB HaveBlue

        # Gather additional required inputs from LSDB HaveBlue
        manufacturer_name      = unit_type.manufacturer.name
        model                  = unit_type.model
        # MD: Diode count (3 is typical)
        # Twin half-cells (if number of cells >72 )

        # Essential LSDB HaveBlue inputs QA/QC checkpoints [PICKUP]

        # Prepare inputs for PVsyst.

        # Pseudocode (KJS 2021-04-19)
        # If string > 1
        # Turn into string = 1
        # Maintain same total number of cells
        # Multiply series S X parallel P
        # Send result through .PAN opt function(s)

        # PICKUP: Move error section to HERE (!!!) (***)

        # TODO: Update to match LSDB HaveBlue inputs formats, e.g., "Mono-PERC".

        # BifacialityFactor for Bifi
        # if str2double(BifacialityFactor) ~= 0
        # except ValueError:
        #     print('.PAN file parameter optimization script does not handle bifacial modules.')

        # D2MuTau
        # if str2double(D2MuTau) ~= 0
        # except ValueError:
        #     print('.PAN file optimization script does not handle recombination term D2MuTau.')

        # NCelP
        # if str2double(NCelP) ~= 1
        # except ValueError:
        #     print('.PAN file optimization script does not handle substrings in parallel.')

        # Technol
        # if strcmp(Technol(1),'01: si-Mono')
        #     Technol = 'mtSiMono';
        # elif strcmp(Technol(1),'02: si-Poly')
        #     Technol = 'mtSiPoly';
        # except ValueError:
        #     print('.PAN file parameter optimization script does not handle this cell technology.')

        # Available PV cell technologies in LSDB HaveBlue: init.json
        # 1. Multi-Si.......Done.                       -> LSDB HaveBlue module_technologies #1
        # 2. Mono-Si........Done.                       -> LSDB HaveBlue module_technologies #2
        # 3. Multi-PERC.....Done.                       -> LSDB HaveBlue module_technologies #3
        # 4. Mono-PERC......Done.                       -> LSDB HaveBlue module_technologies #4
        # 5. N-type Mono....Done.                       -> LSDB HaveBlue module_technologies #5
        # 6. CdTe...........Not implemented/not tested. -> LSDB HaveBlue module_technologies #6
        # 7. CIGs...........Not implemented/not tested. -> LSDB HaveBlue module_technologies #7
        # 8. a-Si...........Not implemented/not tested. -> LSDB HaveBlue module_technologies #8
        # 9. c-Si...........Done.                       -> LSDB HaveBlue module_technologies #9
        # 10. p-Si..........Done.                       -> LSDB HaveBlue module_technologies #10
        # 11. poly-Si.......Done.                       -> LSDB HaveBlue module_technologies #11
        # 12. CIGS..........Not implemented/not tested. -> LSDB HaveBlue module_technologies #12
        # 13. CIS...........Not implemented/not tested. -> LSDB HaveBlue module_technologies #13
        # .
        # .
        # .
        # 20. HJT...........not implemented/not tested -> LSDB HaveBlue module_technologies #20

        # Available PV cell technologies in PVsyst v6.88 (v6.8.8 aka v688):
        # 1. Si-mono...........Done.
        # 2. Si-poly...........Done. In-scope.
        # 3. Si-EFG............not implemented/not tested
        # 4. a-Si:H single.....not implemented/not tested
        # 5. a-Si:H tandem.....not implemented/not tested
        # 6. a-Si:H tripple....not implemented/not tested
        # 7. uCSi-aSi:H........not implemented/not tested
        # 8. CdTe..............not implemented/not tested
        # 9. CIS...............not implemented/not tested
        # 10. CSG..............not implemented/not tested
        # 11. HIT..............not implemented/not tested
        # 12. GaAs.............not implemented/not tested
        # 13. GaInP2/GaAs/Ge...not implemented/not tested
        # 14. Not Specified....not implemented/not tested

        # TODO PICKUP: Document meaning & use of VBiD

        # VBiD
        # if str2double(VBiD) ~= 0
        # except ValueError:
        #     print('.PAN file parameter optimization script does not handle recombination term VBiD.')

        ##################################################################################################
        # START of SAUER MakePAN SCRIPT - INDENTED IN-SCOPE/OUT-OF-SCOPE ERROR HANDLING SECTION
        ##################################################################################################

        # New Sauer "if errors" section [PICKUP]
        errors = [] # ["test"] # {"test1","test2"}

        # Initial infrastructure from MD:
        if request.method == "GET": # use "GET" in development environment (DEV ENV); use "POST" in production environment (PRO ENV) (e.g., make button in UI); if POST:

            # Later: Consider Baseline vs. Measured in "GET" vs. "POST"
            # When Measured, need IF statement to change optimization metadata (e.g., boundary constraints aka limits) to open muGamma for optimization instead of forcing it to be equal to zero (=0)

            # OFFICIAL START OF INDENTATION (in the event you activate the above line of code)

            # Do the needful...
            # Run into a problem (example):
            # if assigned >= units_required:
            # # Write the error as a dictionary, added to error array:
                # errors.append({'error':"unit {} not assigned to {}. {} units already allocated.".format(unit.serial_number,test_sequence.name,assigned)})
            # continue

            # Error handling: Bifacial Bifi (New KJS 2021-05-14)
            # NB KJS 2021-05-13: LSDB HaveBlue initiates value "null" (None in Python); if you activate toggle button in UI, Boolean is 1 or True; if you then deactivate toggle button, Boolean is 0 or False (not None)
            if bifacial is None or bifacial == False:
                BifacialityFactor = None # PICKUP; TODO; OPTIONAL; DECISION POINT: Comment this line out altogether for monofacial, and then it won't show up in .PAN at all
                Flags1 = "$0043" # PVsyst monofacial flag code
            else:
                # TEL Wants to default to 0.7 if unknown
                BifacialityFactor = 0.8 # PICKUP TODO; Default value in PVsyst
                Flags1 = "$00800243" # PVsyst bifacial flag code

            # PICKUP OTHER CONDITIONS!!!

            # Error handling: Check number of cells in series, number of substrings in parallel, and total number of cells [in-scope/out-of-scope for optimization]
            # Check to make sure user-inputted Ns x Np = Ntot
            if cells_in_series*cells_in_parallel != number_of_cells:
                errors.append({'error':".PAN file parameter optimization script does not handle this combination of {} solar PV cells in series, {} cell substrings in parallel, and {} total number of cells.".format(cells_in_series,cells_in_parallel,number_of_cells)})
            else:
                # Ns = number_of_cells # Optimization script does not handle parallel substrings; convert cells in series to total number of cells for sake of optimization
                # MD Changed with JW on 2/17/22
                Ns = cells_in_series # Optimization script does not handle parallel substrings; convert cells in series to total number of cells for sake of optimization

            # Error handling: Check PV cell technology (Technol) [in-scope/out-of-scope for optimization]
            # NB: If mono-Si or multi-Si, run; else, don't (KJS 2021-04-15)
            if module_technology_name == "Mono-Si" or module_technology_name == "Mono-PERC" or module_technology_name == "N-type Mono" or module_technology_name == "c-Si":
                Technol = "mtSiMono" # for PVsyst's "Si-mono" PV cell technology option
            elif module_technology_name == "Multi-Si" or module_technology_name == "Multi-PERC" or module_technology_name == "p-Si" or module_technology_name == "poly-Si":
                Technol = "mtSiPoly" # for PVsyst's "Si-poly" PV cell technology option
            elif module_technology_name == "CIGs" or module_technology_name == "CIGS" or module_technology_name == "CIS":
                Technol = "mtCIS" # for PVsyst's "CIGS/CIS" PV cell technology option
            else:
                # e.g., CdTe
                errors.append({'error':".PAN file parameter optimization script does not handle cell technology {}.".format(module_technology_name)})

            # If we ran into any trouble...
            if len(errors):
            # Short circuit response, send errors to user instead
                # return Response(errors)
                return Response({'panfile':errors})

            # TODO:
            # - Switch to default PVsyst gamma method
            # - Confirm in-house .PAN file generator produces
            # same results as built-in PVsyst .PAN tool for
            # each technology & corresponding default gamma
            # - Figure out default muPmp & muGamma also

            # Design "data".
            # data_base = {
            # Gpoa Tmod  Pmax
            # 1000 25 TBD
            # 200 25 TBD
            # }

            # Rename existing variables.
            PmpDC_STC = nameplate_pmax # W

            # Define new variables.
            Gpoa_LIC = 200 # W/m^2; TODO: Add to some existing LSDB data structure & then
            # TODO: Pull reference conditions from LSDB HaveBlue, e.g., Virtual Traveler VT or better yet Hidden Parameter HP instead of defining it here
            Gpoa_STC = 1000 # W/m^2
            # gPmpRef = TBD; see above # 1/C
            Tcell_LIC = 25 # degC
            Tcell_STC = 25 # degC; TODO: Pull from some LSDB HaveBlue JSON data structure

            # NEW Sauer added 2021-05-20
            # Gpoa
            # Gpoa_g800_t25 = 800
            # Gpoa_g600_t25 = 600
            # Gpoa_g400_t25 = 400

            # Tcell
            # Tcell_g800_t25 = 25
            # Tcell_g600_t25 = 25
            # Tcell_g400_t25 = 25

            # Calculate PmpDC_LIC.
            # dEtaRel_STC_LIC = [(PmpDC_LIC/PmpDC_STC)*(Gpoa_STC/Gpoa_LIC)] - 1
            PmpDC_LIC = (dEtaRel_STC_LIC + 1)*(Gpoa_LIC/Gpoa_STC)*PmpDC_STC; # W

            # NEW Sauer 2021-05-20
            # PmpDC_g800_t25 = (dEtaRel_STC_g800_t25 + 1)*(Gpoa_g800_t25/Gpoa_STC)*PmpDC_STC; # W
            # PmpDC_g600_t25 = (dEtaRel_STC_g600_t25 + 1)*(Gpoa_g600_t25/Gpoa_STC)*PmpDC_STC; # W
            # PmpDC_g400_t25 = (dEtaRel_STC_g400_t25 + 1)*(Gpoa_g400_t25/Gpoa_STC)*PmpDC_STC; # W

            # NEW Sauer 2021-05-20
            # PICKUP
            # ADD TEMPCOS INTO MATRIX
            # Gpoa
            # Gpoa_g1000_t30 = 1000
            # Gpoa_g1000_t35 = 1000
            # Gpoa_g1000_t40 = 1000
            # Gpoa_g1000_t45 = 1000
            # Gpoa_g1000_t50 = 1000
            # Gpoa_g1000_t55 = 1000
            # Gpoa_g1000_t60 = 1000
            # Gpoa_g1000_t65 = 1000

            # Tcell
            # Tcell_g1000_t30 = 30
            # Tcell_g1000_t35 = 35
            # Tcell_g1000_t40 = 40
            # Tcell_g1000_t45 = 45
            # Tcell_g1000_t50 = 50
            # Tcell_g1000_t55 = 55
            # Tcell_g1000_t60 = 60
            # Tcell_g1000_t65 = 65

            # Pmp
            # PmpDC_g1000_t30 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t30-Tcell_STC)) # W
            # PmpDC_g1000_t35 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t35-Tcell_STC)) # W
            # PmpDC_g1000_t40 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t40-Tcell_STC)) # W
            # PmpDC_g1000_t45 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t45-Tcell_STC)) # W
            # PmpDC_g1000_t50 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t50-Tcell_STC)) # W
            # PmpDC_g1000_t55 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t55-Tcell_STC)) # W
            # PmpDC_g1000_t60 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t60-Tcell_STC)) # W
            # PmpDC_g1000_t65 = PmpDC_STC*(1+gamma_pmp*(Tcell_g1000_t65-Tcell_STC)) # W

            # Make "data" data frame.
            # NEW Sauer 2021-05-20
            pan_data = pd.DataFrame()

            pan_data['G'] = [Gpoa_STC]*3 + [Gpoa_LIC]*9 # W/m^2
            pan_data['T'] = [Tcell_STC]*3 + [Tcell_LIC]*9 # degC
            pan_data['Pmp'] = [PmpDC_STC]*3 + [PmpDC_LIC]*9 # W

            # pan_data['G'] = [Gpoa_STC]*3 + [Gpoa_g800_t25]*3 + [Gpoa_g600_t25]*3 + [Gpoa_g400_t25]*3 + [Gpoa_LIC]*9 # W/m^2
            # pan_data['T'] = [Tcell_STC]*3 + [Tcell_g800_t25]*3 + [Tcell_g600_t25]*3 + [Tcell_g400_t25]*3 + [Tcell_LIC]*9 # degC
            # pan_data['Pmp'] = [PmpDC_STC]*3 + [PmpDC_g800_t25]*3 + [PmpDC_g600_t25]*3 + [PmpDC_g400_t25]*3 + [PmpDC_LIC]*9 # W

            # pan_data['G'] = [Gpoa_STC]*3 + [Gpoa_g800_t25]*3 + [Gpoa_g600_t25]*3 + [Gpoa_g400_t25]*3 + [Gpoa_LIC]*9 + [Gpoa_g1000_t30]*4 + [Gpoa_g1000_t35]*4 + [Gpoa_g1000_t40]*4 + [Gpoa_g1000_t45]*4 + [Gpoa_g1000_t50]*4 + [Gpoa_g1000_t55]*4 + [Gpoa_g1000_t60]*4 + [Gpoa_g1000_t65]*4 # W/m^2
            # pan_data['T'] = [Tcell_STC]*3 + [Tcell_g800_t25]*3 + [Tcell_g600_t25]*3 + [Tcell_g400_t25]*3 + [Tcell_LIC]*9 + [Tcell_g1000_t30]*4 + [Tcell_g1000_t35]*4 + [Tcell_g1000_t40]*4 + [Tcell_g1000_t45]*4 + [Tcell_g1000_t50]*4 + [Tcell_g1000_t55]*4 + [Tcell_g1000_t60]*4 + [Tcell_g1000_t65]*4 # degC
            # pan_data['Pmp'] = [PmpDC_STC]*3 + [PmpDC_g800_t25]*3 + [PmpDC_g600_t25]*3 + [PmpDC_g400_t25]*3 + [PmpDC_LIC]*9 + [PmpDC_g1000_t30]*4 + [PmpDC_g1000_t35]*4 + [PmpDC_g1000_t40]*4 + [PmpDC_g1000_t45]*4 + [PmpDC_g1000_t50]*4 + [PmpDC_g1000_t55]*4 + [PmpDC_g1000_t60]*4 + [PmpDC_g1000_t65]*4 # W

            pan_data.to_csv('gtp.csv',index=None)

            # pan_datasheet = {'Isc':9.69,'Voc':47,'Imp':9.17,'Vmp':38.7,'Ns':72,'u_sc':0.0004}

            # TODO: Figure out series vs. parallel.
            # TODO: Address bifacial (Bifi).
            # TODO: Address thin film (TF): Amorphous-Si, CdTe, CIGS, etc.
            # TODO: Move all TODO to top (i.e., consolidate).

            pan_datasheet = {'Isc':Isc,
                             'Voc':Voc,
                             'Imp':Imp,
                             'Vmp':Vmp,
                             'Ns':Ns,
                             'u_sc':alpha_isc}

            # 1. Solved for parameters. Use JHF Python. Verify later using MATLAB, etc.
            # 2. Write .PAN file based on metadata + solved parameters.

            # 1. Call JHF Function.
            # Send function what it needs.
            # Get back everything you can. Put auxiliary parameters into the
            # PVsyst .PAN file text field.

            # 2. Write PVsyst .PAN text file.
            # Insert code here to write text .txt file.

            # Example MATLAB-style syntax.
            # [u_n,Rs,Rsh_ref,Rsh_0,Rsh_exp] = pan_solver_jhf_kjs(pan_datasheet,pan_data)

            # # Algorithm
            # x = 3+3
            # print(x)
            # print('Hello World!')
            # print('Complete!')

            # Source:
            # https://raw.githubusercontent.com/jhfatehi/pv/main/pan_solver.py
            # Last accessed by kjsauer on: 2021-02-03

            '''
            References:

            [1] K. J. Sauer and T. Roessler, "Systematic Approaches to Ensure Correct Representation of
                Measured Multi-Irradiance Module Performance in PV System Energy Production Forecasting
                Software Programs," in IEEE Journal of Photovoltaics, vol. 3, no. 1, pp. 422-428, Jan. 2013,
                doi: 10.1109/JPHOTOV.2012.2221080.

            [2] https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.pvsystem.singlediode.html#id5
                    -> S.R. Wenham, M.A. Green, M.E. Watt, “Applied Photovoltaics” ISBN 0 86758 909 4

            [3] K. J. Sauer, T. Roessler and C. W. Hansen, "Modeling the Irradiance and Temperature Dependence
                of Photovoltaic Modules in PVsyst," in IEEE Journal of Photovoltaics, vol. 5, no. 1, pp. 152-158,
                Jan. 2015, doi: 10.1109/JPHOTOV.2014.2364133.
            '''

            ##################################################################################################

            from pvlib.pvsystem import calcparams_pvsyst, singlediode
            from lmfit import Minimizer, Parameters, report_fit
            from numpy import exp, random
            from scipy.optimize import root_scalar
            from pandas import read_csv

            ##################################################################################################
            ############# User Interface #####################################################################

            # These values are from the module datasheet.  All IV values are at STC.
            # datasheet = {'Isc':9.69, 'Voc':47, 'Imp':9.17, 'Vmp':38.7, 'Ns':72, 'u_sc':0.0004}

            # CSV file with irradiance and temperature test conditions and resulting Pmp value.
            # Column headers in CSV file must be G, T, Pmp
            pan_data_file = 'gtp.csv'

            # Number of times the fitting algorithm should run.  The Levenberg-Marquardt algorithm will
            # provide a local minima.  Running the fit multiple times with randomized starting points
            # can help find the global minimum but will not guarantee the global minimum is found.
            runs = 1 # TODO: Add Mermoud-Sauer equation constraining the relationship between Rsh_0, Rsh_exp, and Rsh_ref values (it check/qualifies/treats the inputted optimization initial guesses); setting runs = 1 is a HACK to force the intrinsic requirement that the initial guess for Rsh_0 > Rsh_ref; ideally, use runs > 1 to find more global optimization solution

            # Parameters that are being solved for
            # value = initial guess
            # min = minimum of the range the parameter can be for the solution
            # max = maximum of the range the parameter can be for the solution
            # vary = parameter will be solved for if True.  parameter will not change form initial guess if False
            # rand = if True the initial guess will be randomized uniformly within the range
            # OG JHF value, min, and max: 0, -0.001, and 0.001 [KJS-added comment]
            # TODO: Remove u_n altogether from the optimization [KJS-added comment]
            # u_n=        {'value':0, 'min':-0.001, 'max':0.001, 'vary':True, 'rand':True} #diode ideality temp co
            u_n=        {'value':0, 'min':-0.001, 'max':0.001, 'vary':True, 'rand':True} #diode ideality temp co
            # OG JHF value, min, and max: 0, 0.1, and 0.6 [KJS-added comment]
            # Rs=         {'value':0, 'min':0.1, 'max':0.6, 'vary':True, 'rand':True} #series resistance
            Rs=         {'value':0.35, 'min':0.05, 'max':0.65, 'vary':True, 'rand':True} #series resistance
            # OG JHF value, min, and max: 0, 1000, and 10000 [KJS-added comment]
            # KJS modified optimization metadata values on 2021-05-09 to fix JHF bug (reverse order of Rsh_0 and Rsh_ref bounds)
            # Rsh_ref=  {'value':0, 'min':1000, 'max':10000, 'vary':True, 'rand':True} #shunt resistance at 1000 W/m^2
            Rsh_ref=    {'value':150, 'min':150, 'max':1000, 'vary':True, 'rand':True} #shunt resistance at 1000 W/m^2
            # OG JHF value, min, and max: 0, 100, and 1000 [KJS-added comment]
            # KJS modified optimization metadata values on 2021-05-09 to fix JHF bug (reverse order of Rsh_0 and Rsh_ref bounds)
            # Rsh_0=        {'value':0, 'min':100, 'max':1000, 'vary':True, 'rand':True} #shunt resistance at 0 W/m^2
            Rsh_0=      {'value':1500, 'min':1500, 'max':10000, 'vary':True, 'rand':True} #shunt resistance at 0 W/m^2
            # KJS-modified boundary conditions. (kjsauer) [KJS-added comment]
            # TODO: Rewrite function to not require RshExp input in the event user says it
            # is not an open parameter for optimization. [KJS-added comment]
            # OG JHF value, min, and max: 0, 5, and 6 [KJS-added comment]
            # KJS-modified: 5.5, 0, and 6 [KJS-added comment]
            # Rsh_exp=    {'value':0, 'min':5, 'max':6, 'vary':True, 'rand':True} #s hunt resistance exponential factor
            Rsh_exp=    {'value':5.5, 'min':5, 'max':6, 'vary':True, 'rand':True} #shunt resistance exponential factor
            # NOTE  if the min and mac values for Rs and Rsh_ref are not realistic the diode ideality will be outside
            #       the solution range of [0.5, 2] and there will be an error.

            ##################################################################################################

            pan_data = read_csv(pan_data_file)

            # TODO: O-K to remove this section (read_csv); not needed.

            for ii in range(runs):

                # print('Fit #'+str(ii+1)+':')

                if u_n['rand'] == True : u_n['value'] = random.uniform(u_n['min'], u_n['max'])
                if Rs['rand'] == True : Rs['value'] = random.uniform(Rs['min'], Rs['max'])
                if Rsh_ref['rand'] == True : Rsh_ref['value'] = random.uniform(Rsh_ref['min'], Rsh_ref['max'])
                if Rsh_0['rand'] == True : Rsh_0['value'] = random.uniform(Rsh_0['min'], Rsh_0['max'])
                if Rsh_exp['rand'] == True : Rsh_exp['value'] = random.uniform(Rsh_exp['min'], Rsh_exp['max'])

                # print('[[Initial Values]]')
                # print('    u_n      = ' +str(u_n['value']))
                # print('    Rs       = ' +str(Rs['value']))
                # print('    Rsh_ref  = ' +str(Rsh_ref['value']))
                # print('    Rsh_0    = ' +str(Rsh_0['value']))
                # print('    Rsh_exp  = ' +str(Rsh_exp['value']))

                params = Parameters()
                params.add('u_n',       value=u_n['value'], min=u_n['min'], max=u_n['max'], vary=u_n['vary'])
                params.add('Rs',        value=Rs['value'], min=Rs['min'], max=Rs['max'], vary=Rs['vary'])
                params.add('Rsh_ref',   value=Rsh_ref['value'], min=Rsh_ref['min'], max=Rsh_ref['max'], vary=Rsh_ref['vary'])
                params.add('Rsh_0',     value=Rsh_0['value'], min=Rsh_0['min'], max=Rsh_0['max'], vary=Rsh_0['vary'])
                params.add('Rsh_exp',   value=Rsh_exp['value'], min=Rsh_exp['min'], max=Rsh_exp['max'], vary=Rsh_exp['vary'])

                '''
                Minimization is done as described in [3] using the G-T Matrix model.
                The 'leastsq' method is Levenberg-Marquardt.
                '''
                minner = Minimizer(self.fcn2min, params, fcn_args=(pan_data, pan_datasheet))
                result = minner.minimize(method='leastsq')

                report_fit(result)
                # print('')

            # https://groups.google.com/g/lmfit-py/c/-5n7PYF0bIc?pli=1/
            # print(report_fit(result,show_correl=True)) # print the statistics

            # plt.figure(figsize=(10,8))
            # plt.plot(x,data,'x',label='Data')
            # plt.plot(x,residual(result.params,x),'r-',color="brown",label='Fitting') # plot the fitting result
            # plt.legend()
            # plt.title('B_sphere',fontsize=16)
            # plt.ylabel('B^-1/3',fontsize=12)
            # plt.xlabel('x',fontsize=12)
            # plt.savefig('B_sphere.png') # save the graph
            # plt.show()

            # Save results.
            # self.savePar('leastsq',result)

            # Access JSON string of lmfit results.
            pan_results_params_json = result.params.dumps()

            # Convert JSON string to Python data.
            pan_results_params_py = json.loads(pan_results_params_json)

            # Gather key .PAN optimization outputs.
            pan_out_u_n = pan_results_params_py['params'][0][1]
            pan_out_Rs = pan_results_params_py['params'][1][1]
            pan_out_Rsh_ref = pan_results_params_py['params'][2][1]
            pan_out_Rsh_0 = pan_results_params_py['params'][3][1]
            pan_out_Rsh_exp = pan_results_params_py['params'][4][1]

            # Calculate simulated DC power matrix here. [Future Work]
            # # t25
            # PmpDC_g1000_t25_sim = TBD
            # PmpDC_g800_t25_sim = TBD
            # PmpDC_g600_t25_sim = TBD
            # PmpDC_g400_t25_sim = TBD
            # PmpDC_g200_t25_sim = TBD
            # # t30
            # PmpDC_g1000_t30_sim = TBD
            # PmpDC_g800_t30_sim = TBD
            # PmpDC_g600_t30_sim = TBD
            # PmpDC_g400_t30_sim = TBD
            # PmpDC_g200_t30_sim = TBD
            # # t35
            # PmpDC_g1000_t35_sim = TBD
            # PmpDC_g800_t35_sim = TBD
            # PmpDC_g600_t35_sim = TBD
            # PmpDC_g400_t35_sim = TBD
            # PmpDC_g200_t35_sim = TBD
            # # t40
            # PmpDC_g1000_t40_sim = TBD
            # PmpDC_g800_t40_sim = TBD
            # PmpDC_g600_t40_sim = TBD
            # PmpDC_g400_t40_sim = TBD
            # PmpDC_g200_t40_sim = TBD
            # # t45
            # PmpDC_g1000_t45_sim = TBD
            # PmpDC_g800_t45_sim = TBD
            # PmpDC_g600_t45_sim = TBD
            # PmpDC_g400_t45_sim = TBD
            # PmpDC_g200_t45_sim = TBD
            # # t50
            # PmpDC_g1000_t50_sim = TBD
            # PmpDC_g800_t50_sim = TBD
            # PmpDC_g600_t50_sim = TBD
            # PmpDC_g400_t50_sim = TBD
            # PmpDC_g200_t50_sim = TBD
            # # t55
            # PmpDC_g1000_t55_sim = TBD
            # PmpDC_g800_t55_sim = TBD
            # PmpDC_g600_t55_sim = TBD
            # PmpDC_g400_t55_sim = TBD
            # PmpDC_g200_t55_sim = TBD
            # # t60
            # PmpDC_g1000_t60_sim = TBD
            # PmpDC_g800_t60_sim = TBD
            # PmpDC_g600_t60_sim = TBD
            # PmpDC_g400_t60_sim = TBD
            # PmpDC_g200_t60_sim = TBD

            # Gather inputs from PVEL .PAN file LSDB HaveBlue, e.g., Virtual Traveler VT
            # function [runbool,resultsdirectory,datafilename,pvobject,pvsystversion,flags1,pvobjectcommercial,comment,flags2,manufacturer,datasource,yearbeg,remarkscount,str1,str2,str3,str4,str5,endofremarks,endofpvobjectpvcommercial,ndiode,submodlayout,endofpvobjectpvmodule,panfilename] = get_string_from_csv(filename,startRow,endRow)

            # README Sauer v1: PVsyst .PAN file parameters descriptions [PICKUP]
            # Kenneth J. Sauer (kjsauer on GitHub)
            # Purpose:
            # - What exactly is required in the .PAN & what is not
            # - Brief description
            # - Move comments from above section into here
            # START of README Sauer v1
            # resultsdir: Full path name of results directory; required
            # datafilename: Filename of optim macro data file including path; required
            # comment: Manufacturer website; not required
            # manufacturer: Manufacturer name; not required
            # datasource: Lab company name; not required
            # yearbeg: Year of product or .PAN file release; not required
            # str1: 1st line of .PAN file comment field; not required
            # str2: 2nd line of .PAN file comment field; not required
            # str3: 3rd line of .PAN file comment field; not required
            # str4: 4th line of .PAN file comment field; not required
            # str5: 5th line of .PAN file comment field; not required
            # ndiode: Number of bypass diodes; not required
            # submodlayout: Substrings typically lengthwise in module (input=1); otherwise, ask Engineering Eng; not required
            # panfilename: Name of .PAN file, e.g., anon1.PAN; required
            # END of README Sauer v1

            # README Sauer v2
            # Required
            # Not required
            # Needs addition into LSDB HaveBlue

            # TODO: Re-check for correct ordering throughout this file/function/script.
            # TODO: Fill in all cases of TBD throughout document.

            # .PAN File Writer
            # Kenneth J. Sauer (kjsauer on GitHub)
            # Purpose: Write a .PAN File Driver to Convert Data in PVEL's LSDB HaveBlue into a Functional PVsyst .PAN File
            # PVEL LSDB HaveBlue Variable Name -> PVsyst Variable Name

            # PICKUP: Sync Git/GitHub. See all cases of Future Work, PICKUP, TBD, & TODO throughout this document.

            # TODO: Need dictionary of LSDB HaveBlue variables incl. data types.

            # Metadata (not in .PAN):
            # 0. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***) (panfilename)   -> TBD???                       # Algorithm: TBD
            # 0. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***) (runbool)       -> TBD???                       # Algorithm: TBD; Description: Designates the run ID, e.g., in the event of multiple runs; not incl. in .PAN

            # Data (in .PAN):
            # 1. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> PVObject_                    # Algorithm: Hard-code string "pvModule"
            # 2. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> Version                      # Algorithm: Hard-code string "6.88" for PVsyst v6.88
            # 3. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> Flags1                       # Algorithm: Test empty (blank) string ""; TODO: Hard-code string "43"
            # 4. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> PVObject_Commercial          # Algorithm: TBD
            # 5. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> Comment                      # Algorithm: TBD
            # 6. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> Flags2                       # Algorithm: Test empty (blank) string ""; TODO: Hard-code string "41"
            # 7. unit_type.manufacturer.name                                                -> Manufacturer                 # Algorithm: Pull string from unit_type.manufacturer.name
            # 8. unit_type.model                                                            -> Model                        # Algorithm: Pull string unit_type.model
            # 9. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                 -> DataSource                   # Algorithm: TBD; TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT
            # 10. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> YearBeg                      # Algorithm: Hard-code string year of time "now"
            # 11. unit_type.module_property.module_width                                    -> Width                        # Algorithm: TBD
            # 12. unit_type.module_property.module_height                                   -> Height                       # Algorithm: TBD
            # 13. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Depth                        # Algorithm: Hard-code string "-999" (TEST import into PVsyst); TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT
            # 14. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Weight                       # Algorithm: TBD; Consider adding to LSDB HaveBlue, e.g., Virtual Traveler VT
            # 15. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Remarks_Count                # Algorithm: TBD
            # 16. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Str_1                        # Algorithm: TBD
            # 17. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Str_2                        # Algorithm: TBD
            # 18. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Str_3                        # Algorithm: TBD
            # 19. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Str_4                        # Algorithm: TBD
            # 20. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> Str_5                        # Algorithm: TBD
            # 21. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> End_of_Remarks               # Algorithm: Hard-code string "End of Remarks"
            # 22. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> End_of_PVObject_pvCommercial # Algorithm: Hard-code string "End of PVObject pvCommercial"
            # 23. unit_type.module_property.module_technology.name (module_technology_name) -> Technol                      # Algorithm: Pull from string unit_type.module_property.module_technology.name; TODO: Determine difference b/w unit_type.module_property.module_technology.name vs. unit_type.module_property.module_technology and unit_type.module_property['module_technology']['name']
            # 24. unit_type.module_property.cells_in_series (cells_in_series) (Ns)          -> NCelS                        # Algorithm: OUTPUT; solved for result of unit_type.module_property.cells_in_series and unit_type.module_property.cells_in_parallel--convert to in-series only
            # 25. unit_type.module_property.cells_in_parallel (cells_in_parallel)           -> NCelP                        # Algorithm: Hard-code string "1"; convert to in-series only
            # 26. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> NDiode                       # Algorithm: Hard-code string "3" representing three bypass diodes (TEMP); TODO: Add to/pull string from LSDB HaveBlue, e.g., Virtual Traveler VT
            # 27. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> SubModLayout                 # Algorithm: Hard-code string "1" representing lengthwise substrings (TEMP); TODO: Add to/pull string from LSDB HaveBlue, e.g., Virtual Traveler VT
            # 28. TBD - MISSING IN HIDDEN PARAMETERS HP (!!!) (***) (Gpoa_STC)              -> GRef                         # Algorithm: Defined above; hard-code string "1000"; consider adding to LSDB HaveBlue Virtual Traveler VT or LSDB HaveBlue, e.g., Hidden Parameters HP
            # 29. TBD - MISSING IN HIDDEN PARAMETERS HP (!!!) (***) (Tcell_STC)             -> TRef                         # Algorithm: Defined above; hard-code string "25"; consider adding to LSDB HaveBlue Virtual Traveler VT or LSDB HaveBlue, e.g., Hidden Parameters HP
            # 30. unit_type.module_property.nameplate_pmax                                  -> PNom                         # Algorithm: Pull from unit_type.module_property.nameplate_pmax; convert to string
            # 31. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> PNomTolLow                   # Algorithm: TBD
            # 32. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> PNomTolUp                    # Algorithm: TBD
            # 33. unit_type.module_property.isc                                             -> Isc                          # Algorithm: Pull from unit_type.module_property.isc; convert to string?
            # 34. unit_type.module_property.voc                                             -> Voc                          # Algorithm: TBD
            # 35. unit_type.module_property.imp                                             -> Imp                          # Algorithm: TBD
            # 36. unit_type.module_property.vmp                                             -> Vmp                          # Algorithm: TBD
            # 37. unit_type.module_property.alpha_isc (alpha_isc)                           -> muISC                        # Algorithm: Defined above; divide by 100 to convert %/degC to 1/degC
            # 38. unit_type.module_property.beta_voc (beta_voc)                             -> muVocSpec                    # Algorithm: Defined above; divide by 100 to convert %/degC to 1/degC
            # 39. unit_type.module_property.gamma_pmp (gamma_pmp)                           -> muPmpReq                     # Algorithm: Defined above; divide by 100 to convert %/degC to 1/degC
            # 40. Rsh_ref (OUTPUT) (pan_out_Rsh_ref)                                        -> RShunt                       # Algorithm: OUTPUT; defined above; solved for (optimized)
            # 41. Rsh_0 (OUTPUT) (pan_out_Rsh_0)                                            -> Rp_0                         # Algorithm: OUTPUT; defined above; solved for (optimized)
            # 42. Rsh_exp (OUTPUT) (pan_out_Rsh_exp)                                        -> Rp_Exp                       # Algorithm: OUTPUT; defined above; solved for (optimized)
            # 43. Rs (OUTPUT of this script) (pan_out_Rs)                                   -> RSerie                       # Algorithm: Output; defined above; solved for (optimized)
            # 44. u_n (OUTPUT of this script) (pan_out_u_n)                                 -> Gamma                        # Algorithm: Output; defined above; solved for (optimized)
            # 45. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> muGamma                      # Algorithm: TBD
            # 46. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> D2MuTau                      # Algorithm: TBD
            # 47. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> VMaxIEC                      # Algorithm: TBD
            # 48. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> VMaxUL                       # Algorithm: TBD
            # 49. unit_type.module_property.cell_area                                       -> CellArea                     # Algorithm: Pull from unit_type.module_property.cell_area; convert to string
            # 50. TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)                -> End_of_PVObject_pvModule     # Algorithm: TBD
            # TODO/Future work:
            # Add parameters here based on other PVsyst .PAN variants.

            # TODO: Here is a good place to ceil/floor/round/truncate (if needed).

            # runbool                      = "1"                                # TBD: Not presently in use; reintroduce when running multiple files at once (i.e., 0/1 Boolean to run present run or skip to next)

            # Define required PVsyst variables for .PAN file
            PVObject_                    = "pvModule"                         # pan_line1; Hard-code string "pvModule"
            Version                      = "6.88"                             # pan_line2; Previous placeholder: "Insert PVsyst Version Number"
            Flags1                       = Flags1                             # UPDATED (Bifi); pan_line3; Test empty (blank) string ""; TODO: Hard-code string "43" or "$0043" (depending on PVsyst version)
            PVObject_Commercial          = "pvCommercial"                     # pan_line4; Hard-code string "pvCommercial"
            Comment                      = ""                                 # pan_line5; Hard-code string "Insert MFG Website URL"; NEW: Try leaving blank
            Flags2                       = ""                                 # pan_line6; Test empty (blank) string ""; TODO: Hard-code string "41" or "$0041" (depending on PVsyst version)
            Manufacturer                 = manufacturer_name                  # pan_line7; Pull string from unit_type.manufacturer.name; previous placeholder: "Insert MFG Name"
            Model                        = model                              # pan_line8; Pull string from unit_type.model; previous placeholder: "Insert Model Name"
            DataSource                   = "PV Evolution Labs (PVEL)"         # pan_line9; Hard-code string "PV Evolution Labs (PVEL)"

            # Get year of time "now"
            import datetime
            now = datetime.datetime.now()
            year = now.year

            YearBeg                      = str(year)                          # pan_line10; Hard-code string year of time "now"
            Width                        = str(module_width/1000)             # pan_line11; Pull from unit_type.module_property.module_width; convert to string; NEW: PVsyst requires units of m (convert accordingly)
            Height                       = str(module_height/1000)            # pan_line12; Pull from unit_type.module_property.module_height; convert to string; NEW: PVsyst requires units of m (convert accordingly)
            Depth                        = "0"                                # pan_line13; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code test string "999"
            Weight                       = "0"                                # pan_line14; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code test string "-999"; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> HARD-CODE STRING "-999" -> TEST IMPORT TO PVsyst
            Remarks_Count                = "5"                                # pan_line15; Hard-code string "5" representing 5 lines of comments
            Str_1                        = "Number of optimization runs = {}".format(str(runs)) # pan_line16; Hard-code string "Insert Comment String 1"; NEW: "Comment String 1"
            Str_2                        = "Resultant muGamma = {}".format(str(pan_out_u_n))    # pan_line17; Hard-code string "Insert Comment String 2"; NEW: "Comment String 2"
            Str_3                        = "Comment String 3"                 # pan_line18; Hard-code string "Insert Comment String 3"; NEW: "Comment String 3"
            Str_4                        = "Comment String 4"                 # pan_line19; Hard-code string "Insert Comment String 4"; NEW: "Comment String 4"
            Str_5                        = "Comment String 5"                 # pan_line20; Hard-code string "Insert Comment String 5"; NEW: "Comment String 5"
            End_of_Remarks               = "End of Remarks"                   # pan_line21; Hard-code string "End of Remarks"
            End_of_PVObject_pvCommercial = "End of PVObject pvCommercial"     # pan_line22; Hard-code string "End of PVObject pvCommercial"
            Technol                      = Technol                            # pan_line23; Pull from string unit_type.module_property.module_technology.name
            NCelS                        = str(cells_in_series)               # pan_line24; Optimization script does not handle parallel substrings; convert cells in series to total number of cells for sake of optimization; preserve correct module characteristics detail here in .PAN writer
            NCelP                        = str(cells_in_parallel)             # pan_line25; Optimization script does not handle parallel substrings; convert cells in series to total number of cells for sake of optimization; preserve correct module characteristics detail here in .PAN writer
            NDiode                       = "3"                                # pan_line26; Hard-code string "3" representing three bypass diodes (TEMP); previous placeholder: "Insert Number of Diodes"; TODO: Add to/pull from LSDB HaveBlue Virtual Traveler VT; TODO: FIX THIS AFTER THIS MEETING (TEMP HACK) -> NUMBER OF BYPASS DIODES; NEW: Try leaving as blank string ""; NEWER: Revert to "3" b/c PVsyst v6.88 defaults NDiode as "3" anyway
            SubModLayout                 = "1"                                # pan_line27; UPDATED: Revert back to "1" upon testing ("1" activates toggle button in PVsyst GUI while "slInLength" does not) UPDATED: slInLength seems to have replaced "1" in PVsyst .PAN (expect no difference b/w the two); Hard-code string "1" representing lengthwise substrings (TEMP); previous placeholder: "Insert Sub-module Layout Boolean"; TODO: FIX THIS AFTER THIS MEETING (TEMP HACK) -> PV MODULE SUBSTRINGS LENGTHWISE IS "1"; NEW: Try leaving as blank string ""; NEWER: Revert to "1" b/c PVsyst v6.88 defaults NDiode to "3"
            GRef                         = str(Gpoa_STC)                      # pan_line28; Hard-code string "1000"; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> HARD-CODE
            TRef                         = str(Tcell_STC)                     # pan_line29; Hard-code string "25"; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> HARD-CODE
            PNom                         = str(nameplate_pmax)                # pan_line30; Pull from unit_type.module_property.nameplate_pmax; convert to string
            PNomTolLow                   = "0"                                # pan_line31; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code string "999" (TEST import into PVsyst); TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> USE ERROR CODE STRING "-999" FOR NOW
            PNomTolUp                    = "0"                                # pan_line32; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code string "-999" (TEST import into PVsyst); TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> USE ERROR CODE -999 FOR NOW
            # Bifacial Bifi New KJS 2020-05-14
            if BifacialityFactor is None:
                pass
            else:
                BifacialityFactor        = str(BifacialityFactor)                 # UPDATED; Bifacial Bifi New KJS 2021-05-14
            Isc                          = str(Isc)                           # pan_line33; Pull from unit_type.module_property.isc; convert to string
            Voc                          = str(Voc)                           # pan_line34; Pull from unit_type.module_property.voc; convert to string
            Imp                          = str(Imp)                           # pan_line35; Pull from unit_type.module_property.imp; convert to string
            Vmp                          = str(Vmp)                           # pan_line36; Pull from unit_type.module_property.vmp; convert to string
            muISC                        = str(alpha_isc*float(Isc)*1000)     # pan_line37; Pull from unit_type.module_property.alpha_isc; divided by 100 to convert %/degC to 1/degC; convert to string; NEW: PVsyst requires units of mA/degC (convert accordingly)
            muVocSpec                    = str(beta_voc*float(Voc)*1000)      # pan_line38; Pull from unit_type.module_property.beta_voc; divided by 100 to convert %/degC to 1/degC; convert to string; NEW: PVsyst requires units of mV/degC (convert accordingly)
            muPmpReq                     = str(gamma_pmp*100)                 # pan_line39; Pull from unit_type.module_property.gamma_pmp; divided by 100 to convert %/degC to 1/degC; convert to string; NEW: PVsyst requires units of %/degC (convert accordingly)
            RShunt                       = str(pan_out_Rsh_ref)               # pan_line40; Output; solved for by this file/function/script; convert to string
            Rp_0                         = str(pan_out_Rsh_0)                 # pan_line41; Output; solved for by this file/function/script; convert to string
            Rp_Exp                       = str(pan_out_Rsh_exp)               # pan_line42; Output; solved for by this file/function/script; convert to string
            RSerie                       = str(pan_out_Rs)                    # pan_line43; Output; solved for by this file/function/script; convert to string
            Gamma                        = ""                                 # pan_line44; Output; solved for by this file/function/script; convert to string; NEW: Replace str(pan_out_u_n) with blank string ""
            muGamma                      = ""                                 # pan_line45; Hard-code empty (blank) string "" (TEST import into PVsyst); TODO: TEST LEAVE BLANK (EMPTY) & IMPORT INTO PVsyst
            D2MuTau                      = ""                                 # pan_line46; Hard-code string "0" representing NO amorphous-Si (a-Si) empirical spectral adjustments applied; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT -> HARD-CODE (ALSO VBiD?); NEW: Try leaving it blank
            VMaxIEC                      = str(system_voltage)                # pan_line47; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code string "-999"; TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT; NEW: Leave as "0" for now to avoid safety issues (will trigger warning in PVsyst upon running energy simulation)
            VMaxUL                       = str(system_voltage)                # pan_line48; !!!DANGER ZONE - NEED TO REPLACE (SOFT-CODE) THIS VALUE!!!; Previous: Hard-code string "-999"; TODO: Add to/pull from LSDB HaveBlue, e.g., Virtual Traveler VT; TODO: MISSING INPUT; ADD TO/PULL FROM LSDB HaveBlue, e.g., VIRTUAL TRAVELER VT; NEW: Leave as "0" for now to avoid safety issues (will trigger warning in PVsyst upon running energy simulation)
            CellArea                     = str(cell_area)                     # pan_line49; Pull from unit_type.module_property.cell_area; convert to string
            End_of_PVObject_pvModule     = "End of PVObject pvCommercial"     # pan_line50; Hard-code string "End of PVObject pvCommercial"
            # TODO: WHERE IS VBiD!?!?!? I'M THINKING YOU DON'T STRICTLY NEED IT TO MAKE A WORKING .PAN FILE (???); TEST IMPORT INTO PVSYST & FIGURE IT OUT; TODO/PICKUP: DOCUMENT MEANING & USE OF D2MuTau AND VBiD.

            # panfilename                 = "Insert PAN File Name.PAN"          # TBD - MISSING INPUT in LSDB HaveBlue, e.g., VT (!!!) (***)

            # Write each line of .PAN file
            # NB: Includes descriptions of active dev experiment/implementation.
            pan_line1  = 'PVObject_=%s'%PVObject_                       # Hard-code string "pvModule"
            pan_line2  = '  Version=%s'%Version                         # Hard-code string "6.88" for PVsyst v6.88
            pan_line3  = '  Flags=%s'%Flags1                            # Test empty (blank) string ""; TODO: Hard-code string "43"
            pan_line4  = '  PVObject_Commercial=%s'%PVObject_Commercial # Hard-code string "pvCommercial"
            pan_line5  = '    Comment=%s'%Comment                       # Hard-code string "Insert MFG Website URL"
            pan_line6  = '    Flags=%s'%Flags2                          # Test empty (blank) string ""; TODO: Hard-code string "41"
            pan_line7  = '    Manufacturer=%s'%Manufacturer             # Pull string from unit_type.manufacturer.name
            pan_line8  = '    Model=%s'%Model                           # Pull string from unit_type.model
            pan_line9  = '    DataSource=%s'%DataSource                 # Hard-code string "PV Evolution Labs (PVEL)"
            pan_line10 = '    YearBeg=%s'%YearBeg                       # Hard-code string year of time "now"
            pan_line11 = '    Width=%s'%Width                           # TBD
            pan_line12 = '    Height=%s'%Height                         # TBD
            pan_line13 = '    Depth=%s'%Depth                           # Test string "-999"
            pan_line14 = '    Weight=%s'%Weight                         # Test string "-999"
            pan_line15 = '    Remarks, Count=%s'%Remarks_Count          # Hard-code string "5" representing 5 lines of comments
            pan_line16 = '      Str_1=%s'%Str_1                         # Hard-code string "Insert Comment String 1"
            pan_line17 = '      Str_2=%s'%Str_2                         # Hard-code string "Insert Comment String 2"
            pan_line18 = '      Str_3=%s'%Str_3                         # Hard-code string "Insert Comment String 3"
            pan_line19 = '      Str_4=%s'%Str_4                         # Hard-code string "Insert Comment String 4"
            pan_line20 = '      Str_5=%s'%Str_5                         # Hard-code string "Insert Comment String 5"
            pan_line21 = '    End of Remarks=%s'%End_of_Remarks         # Hard-code string "End of Remarks"
            pan_line22 = '  %s'%End_of_PVObject_pvCommercial            # Hard-code string "End of PVObject pvCommercial"
            pan_line23 = '  Technol=%s'%Technol                         # TBD
            pan_line24 = '  NCelS=%s'%NCelS                             # TBD
            pan_line25 = '  NCelP=%s'%NCelP                             # TBD
            pan_line26 = '  NDiode=%s'%NDiode                           # Hard-code string "3" representing three bypass diodes; TODO: Pull string from LSDB HaveBlue, e.g., Virtual Traveler VT; run through in-scope parameter space IF statement(s)
            pan_line27 = '  SubModLayout=%s'%SubModLayout               # Hard-code string "1" representing lengthwise substrings; TODO: Pull string from LSDB HaveBlue, e.g., Virtual Traveler VT & run through in-scope parameter space IF statement(s)
            pan_line28 = '  GRef=%s'%GRef                               # Hard-code string "1000"; TODO: Pull string from LSDB HaveBlue, e.g., Virtual Traveler VT or better yet Hidden Parameters HP
            pan_line29 = '  TRef=%s'%TRef                               # Hard-code string "25"; TODO: Pull string from LSDB HaveBlue, e.g., Virtual Traveler VT or better yet Hidden Parameters HP
            pan_line30 = '  PNom=%s'%PNom                               # TBD
            pan_line31 = '  PNomTolLow=%s'%PNomTolLow                   # TBD
            pan_line32 = '  PNomTolUp=%s'%PNomTolUp                     # TBD
            # Bifacial Bifi New KJS 2021-05-14
            if BifacialityFactor is None:
                pan_line33 = None
            else:
                pan_line33 = '  BifacialityFactor=%s'%BifacialityFactor     # TBD; Bifacial Bifi New KJS 2021-05-14
            pan_line34 = '  Isc=%s'%Isc                                 # TBD
            pan_line35 = '  Voc=%s'%Voc                                 # TBD
            pan_line36 = '  Imp=%s'%Imp                                 # TBD
            pan_line37 = '  Vmp=%s'%Vmp                                 # TBD
            pan_line38 = '  muISC=%s'%muISC                             # TBD
            pan_line39 = '  muVocSpec=%s'%muVocSpec                     # TBD
            pan_line40 = '  muPmpReq=%s'%muPmpReq                       # TBD
            pan_line41 = '  RShunt=%s'%RShunt                           # TBD
            pan_line42 = '  Rp_0=%s'%Rp_0                               # TBD
            pan_line43 = '  Rp_Exp=%s'%Rp_Exp                           # TBD
            pan_line44 = '  RSerie=%s'%RSerie                           # TBD
            pan_line45 = '  Gamma=%s'%Gamma     # number of decimals??? # TBD
            pan_line46 = '  muGamma=%s'%muGamma # number of decimals??? # TBD
            pan_line47 = '  D2MuTau=%s'%D2MuTau                         # TBD
            pan_line48 = '  VMaxIEC=%s'%VMaxIEC                         # Test string "-999"
            pan_line49 = '  VMaxUL=%s'%VMaxUL                           # Test string "-999"
            pan_line50 = '  CellArea=%s'%CellArea                       # TBD
            pan_line51 = '%s'%End_of_PVObject_pvModule                  # Hard-code string "End of PVObject pvCommercial"

            # Save As .PAN filename.
            # panfilename = panfilename                                   # Test "Insert PAN File Name.PAN"; turned off for now; TODO: Reactivate once added to VT.

            # pan_string = '%s\r%s'%(pan_line1,pan_line2)

            # PICKUP: NEW .PAN STRING WRITER (from: MD)
            # Remove all of the prints on lines 682-731 and replace them with the following pattern:
            # pan_lines = []
            # pan_lines.append('PVObject_=%s'%PVObject_)
            # pan_lines.append('  Version=%s'%Version)
            # Lines 735-837 get deleted.
            # To construct the final string:
            # pan_string = "\n".join(pan_lines)
            # If PVsyst is stupid about DOS newlines, the last line changes to:
            # pan_string = "\r\n".join(pan_lines)

            # Bifacial Bifi New KJS 2021-05-14
            # IF not Bifi, pan_string is 50 lines; else (IF Bifi), pan_string is 51 lines
            if BifacialityFactor is None:
                pan_string = '''%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s'''%(
    pan_line1,
    pan_line2,
    pan_line3,
    pan_line4,
    pan_line5,
    pan_line6,
    pan_line7,
    pan_line8,
    pan_line9,
    pan_line10,
    pan_line11,
    pan_line12,
    pan_line13,
    pan_line14,
    pan_line15,
    pan_line16,
    pan_line17,
    pan_line18,
    pan_line19,
    pan_line20,
    pan_line21,
    pan_line22,
    pan_line23,
    pan_line24,
    pan_line25,
    pan_line26,
    pan_line27,
    pan_line28,
    pan_line29,
    pan_line30,
    pan_line31,
    pan_line32,
    pan_line34,
    pan_line35,
    pan_line36,
    pan_line37,
    pan_line38,
    pan_line39,
    pan_line40,
    pan_line41,
    pan_line42,
    pan_line43,
    pan_line44,
    pan_line45,
    pan_line46,
    pan_line47,
    pan_line48,
    pan_line49,
    pan_line50,
    pan_line51,
    )
            else:
                pan_string = '''%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s
%s'''%(
    pan_line1,
    pan_line2,
    pan_line3,
    pan_line4,
    pan_line5,
    pan_line6,
    pan_line7,
    pan_line8,
    pan_line9,
    pan_line10,
    pan_line11,
    pan_line12,
    pan_line13,
    pan_line14,
    pan_line15,
    pan_line16,
    pan_line17,
    pan_line18,
    pan_line19,
    pan_line20,
    pan_line21,
    pan_line22,
    pan_line23,
    pan_line24,
    pan_line25,
    pan_line26,
    pan_line27,
    pan_line28,
    pan_line29,
    pan_line30,
    pan_line31,
    pan_line32,
    pan_line33,
    pan_line34,
    pan_line35,
    pan_line36,
    pan_line37,
    pan_line38,
    pan_line39,
    pan_line40,
    pan_line41,
    pan_line42,
    pan_line43,
    pan_line44,
    pan_line45,
    pan_line46,
    pan_line47,
    pan_line48,
    pan_line49,
    pan_line50,
    pan_line51,
    )

            # Note to MD:
            # Please see panfilename + pan_string.
            # Please send both to Azure file generator.
            # Please return a .PAN file of filename panfilename w/ contents of pan_string.
            # Thanks. --KJS

            # Begin to write .PAN text output file here.
            foo = {# 'data1':"hello world",
                   # 'data2':self.square(Voc + Isc + Imp),
                   # 'data3':self.fcn2min(Isc,Voc,Imp,Vmp,Ns,Rs,Rsh),
                   # 'data3':self.readPar('leastsq',result),
                   'pan_out_u_n':pan_out_u_n,
                   'pan_out_Rs':pan_out_Rs,
                   'pan_out_Rsh_ref':pan_out_Rsh_ref,
                   'pan_out_Rsh_0':pan_out_Rsh_0,
                   'pan_out_Rsh_exp':pan_out_Rsh_exp,
                   }

            # Sauer practice .PAN file response (& other practice responses)
            # foo = self.readPar('leastsq',result)
            # foo = '    {}--{}'.format(Voc,self.square(Voc + Isc + Imp))
            # foo2 = '    {}--{}'.format(I0_ref,self.fcn2min(Isc, Voc, Imp, Vmp, Ns, Rs, Rsh))
            # Stubbed code for example usage:
            # foo = self.calc_ref_vals(
            #     Isc = unit_type.module_property.isc,
            #     Voc = unit_type.module_property.voc,
            #     Imp = unit_type.module_property.imp,
            #     Ns = unit_type.module_property.cells_in_series,
            #     Rs = unit_type.module_property.Rs_TBD,
            #     Rsh = unit_type.module_property.Rsh_TBD,
            # )
            # return Response({'panfile':foo})
            # return Response(self.readPar('leastsq',result))

            def square(self, value=None):
                return value*value

            # TODO: Output .PAN file here.

            # Begin file here.download response: (MD 06Apr2021)
            mem_file = BytesIO()
            mem_file.write(bytes(pan_string,'utf-8'))
            mem_file.seek(0)
            # Change the value of filename as needed:
            filename=timezone.now().strftime('%b-%d-%Y-%H%M%S') # this names it with current time (in Coordinated Universal Time UTC) to guarantee uniqueness
            response = HttpResponse(mem_file, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename={}.PAN'.format(filename)
            return response

            ##################################################################################################
            # END of SAUER MakePAN SCRIPT - INDENTED IN-SCOPE/OUT-OF-SCOPE ERROR HANDLING SECTION
            ##################################################################################################

    ##################################################################################################

    def calc_ref_vals(self, Isc, Voc, Imp, Vmp, Ns, Rs, Rsh):
        '''
        author: JHF (open-source jhfatehi on GitHub) based on papers by KJS.
        edited by: KJS (kjsauer on GitHub)
        reference conditions assumed to be STC (1000 W/m^2, 25 C)

        Isc = STC value from datasheet
        Voc = STC value from datasheet
        Imp = STC value from datasheet
        Vmp = STC value from datasheet
        Ns = cells in series from datasheet
        Rs = series resistance (solving for)
        Rsh = shunt resistance at 1000 W/m^2 (solving for)
        '''

        from scipy.optimize import root_scalar
        from numpy import exp, random

        q = 1.60217662e-19 # KJS updated number of decimals to match Google Search
        k = 1.38064852e-23
        T = 298.15

        # Solve for diode ideality factor (presented as gamma in reference) using the method described in eq7 from [1].
        # NOTE      This could be done faster if the solution range of [0.5,2] is reduced.
        def f(n):
            return ((1-exp(q*(Imp*Rs-(Voc-Vmp))/Ns/k/T/n))/(1-exp(q*(Isc*Rs-Voc)/Ns/k/T/n))-(Imp*(Rsh+Rs)-(Voc-Vmp))/(Isc*(Rsh+Rs)-Voc))
        sol = root_scalar(f, bracket=[0.5,2], method='brentq')
        n_ref = sol.root

        '''
        Single Diode pv cell model circuit from [2]
            I=IL-I0*(exp((V+I*Rs)/(n*Ns*Vth))-1)-(V+I*Rs)/Rsh

        rearrange to take the form y=mx+b
        IL = I0*(exp((V+I*Rs)/(n*Nsc*Vth))-1) + (V+I*Rs)/Rsh + I

        Use Isc and Voc at STC to make 2 equations with 2 unknowns
        '''
        nNsVth_ref = n_ref*Ns*k*T/q

        m1=exp((0+Isc*Rs)/(nNsVth_ref))-1
        b1=(0+Isc*Rs)/Rsh+Isc
        m2=exp((Voc+0*Rs)/(nNsVth_ref))-1
        b2=(Voc+0*Rs)/Rsh+0

        I0_ref = (b2-b1)/(m1-m2)
        IL_ref = m1*I0_ref+b1

        return I0_ref, IL_ref, n_ref

    ##################################################################################################

    def singlediodePVSYST(self, G, T, I0_ref, IL_ref, n_ref, Ns, u_sc, u_n, Rs, Rsh_ref, Rsh_0, Rsh_exp):
        '''
        author: JHF (open-source jhfatehi on GitHub) based on papers by KJS.
        edited by: KJS (kjsauer on GitHub)
        reference conditions assumed to be STC (1000 W/m^2, 25 C)

        G = module irradiance under test
        T = cell temperature under test
        I0_ref = diode saturation current at STC (from calc_ref_vals)
        IL_ref = cell photo current at STC (from calc_ref_vals)
        n_ref = diode ideality factor at STC (from calc_ref_vals)
        Nsc = number of cells in series (datasheet)
        u_sc = short circuit current temperature coefficient at 1000W/M^2 (datasheet)
        u_n = diode ideality factor temperature coefficient (solving for)
        Rs = series resistance (solving for)
        Rsh_ref = shunt resistance at 1000 W/m^2 (solving for)
        Rsh_0 = shunt resistance at 0 W/m^2 (solving for)
        Rsh_exp = shunt resistance exponential factor (solving for)
        '''

        from pvlib.pvsystem import calcparams_pvsyst, singlediode

        IL, I0, Rs, Rsh, nNsVth = calcparams_pvsyst(G, T, u_sc, n_ref, u_n, IL_ref, I0_ref, Rsh_ref, Rsh_0, Rs, Ns, Rsh_exp,
                        EgRef=1.12, irrad_ref=1000, temp_ref=25) # kjs updated from 1.121 to 1.21 to match PVsyst Hidden Parameters

        out = singlediode(IL, I0, Rs, Rsh, nNsVth,
                          ivcurve_pnts=None, method='lambertw')

        return(out['p_mp'])

    ##################################################################################################

    def fcn2min(self, params, pan_data, pan_ds):
        '''
        author: JHF (open-source jhfatehi on GitHub) based on papers by KJS.
        edited by: KJS (kjsauer on GitHub)
        params = parameters to minimize as a lmfit Parameters object (u_n, Rs, Rsh_ref, Rsh_0, Rsh_exp)
        pan_data = dataframe with G, T, and Pmp flash test values
        pan_ds  = dictionary with datasheet values for diode model

        This function returns the difference between the measured and the modeled Pmp
        '''

        v = params.valuesdict()

        I0_ref, IL_ref, n_ref = self.calc_ref_vals(pan_ds['Isc'], pan_ds['Voc'], pan_ds['Imp'], pan_ds['Vmp'], pan_ds['Ns'], v['Rs'], v['Rsh_ref'])
        model = self.singlediodePVSYST(pan_data['G'], pan_data['T'], I0_ref, IL_ref, n_ref, pan_ds['Ns'], pan_ds['u_sc'], v['u_n'], v['Rs'], v['Rsh_ref'], v['Rsh_0'], v['Rsh_exp'])

        return model - pan_data['Pmp']

    # Sauer addition 2021-02-05: Write Minimizer results to JSON file/string.
    # TODO: Clarify JSON file vs. string.
    # https://groups.google.com/g/lmfit-py/c/-5n7PYF0bIc?pli=1/
    # Start
    # def savePar(self,name,result): # get name and result from fitting
    #     par_j = result.params.dumps() # dump results into JSON string
    #     with open(name,'w') as json_file:
    #         json.dump(par_j,json_file) # write JSON string into file
    # def readPar(self,name,result): # get name and result object
    #     with open(name,'r') as json_file: # open previous result
    #         json_str = json.load(json_file)
    #         result.params.loads(json_str) # load previous result into input variable
    #         return result
    # End
