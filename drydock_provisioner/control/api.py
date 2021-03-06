# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import falcon

from .designs import *
from .tasks import *
from .bootdata import *

from .base import DrydockRequest
from .middleware import AuthMiddleware, ContextMiddleware, LoggingMiddleware


def start_api(state_manager=None, ingester=None, orchestrator=None):
    """
    Start the Drydock API service

    :param state_manager:   Instance of drydock_provisioner.statemgmt.manager.DesignState for accessing
                            state persistence
    :param ingester:        Instance of drydock_provisioner.ingester.ingester.Ingester for handling design
                            part input
    :param orchestrator:    Instance of drydock_provisioner.orchestrator.Orchestrator for managing tasks
    """
    control_api = falcon.API(
        request_type=DrydockRequest,
        middleware=[
            AuthMiddleware(),
            ContextMiddleware(),
            LoggingMiddleware()
        ])

    # v1.0 of Drydock API
    v1_0_routes = [
        # API for managing orchestrator tasks
        ('/tasks', TasksResource(
            state_manager=state_manager, orchestrator=orchestrator)),
        ('/tasks/{task_id}', TaskResource(state_manager=state_manager)),

        # API for managing site design data
        ('/designs', DesignsResource(state_manager=state_manager)),
        ('/designs/{design_id}', DesignResource(
            state_manager=state_manager, orchestrator=orchestrator)),
        ('/designs/{design_id}/parts', DesignsPartsResource(
            state_manager=state_manager, ingester=ingester)),
        ('/designs/{design_id}/parts/{kind}', DesignsPartsKindsResource(
            state_manager=state_manager)),
        ('/designs/{design_id}/parts/{kind}/{name}', DesignsPartResource(
            state_manager=state_manager, orchestrator=orchestrator)),

        # API for nodes to discover their bootdata during curtin install
        ('/bootdata/{hostname}/{data_key}', BootdataResource(
            state_manager=state_manager, orchestrator=orchestrator))
    ]

    for path, res in v1_0_routes:
        control_api.add_route('/api/v1.0' + path, res)

    return control_api
