from rest_framework import status

from mayan.apps.documents.permissions import permission_document_type_view
from mayan.apps.documents.tests.mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import Workflow
from ..permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_transition,
    permission_workflow_view
)

from .literals import (
    TEST_WORKFLOW_LABEL, TEST_WORKFLOW_LABEL_EDITED,
    TEST_WORKFLOW_STATE_LABEL, TEST_WORKFLOW_STATE_LABEL_EDITED,
    TEST_WORKFLOW_TRANSITION_LABEL, TEST_WORKFLOW_TRANSITION_LABEL_EDITED
)

from .mixins import (
    DocumentWorkflowAPIViewTestMixin, WorkflowAPIViewTestMixin,
    WorkflowStateAPIViewTestMixin, WorkflowTestMixin,
    WorkflowTransitionAPIViewTestMixin,
    WorkflowTransitionFieldAPIViewTestMixin, WorkflowTransitionFieldTestMixin
)


class DocumentWorkflowsAPIViewTestCase(
    DocumentWorkflowAPIViewTestMixin, DocumentTestMixin, WorkflowTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_workflow_instance_detail_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('workflow' in response.data)

    def test_workflow_instance_detail_view_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('workflow' in response.data)

    def test_workflow_instance_detail_view_with_document_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_document, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse('workflow' in response.data)

    def test_workflow_instance_detail_view_with_full_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )
        self.grant_access(
            obj=self.test_document, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['workflow']['label'],
            TEST_WORKFLOW_LABEL
        )

    def test_workflow_instance_list_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('result' in response.data)

    def test_workflow_instance_list_view_with_document_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_document, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_workflow_instance_list_view_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('result' in response.data)

    def test_workflow_instance_list_view_with_full_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )
        self.grant_access(
            obj=self.test_document, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['workflow']['label'],
            TEST_WORKFLOW_LABEL
        )

    def test_workflow_instance_log_entries_create_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        workflow_instance = self.test_document.workflows.first()
        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # We get bad request because we try to create a transition for which
        # we don't have permission and therefore is not valid for this
        # workflow instance current state
        self.assertEqual(workflow_instance.log_entries.count(), 0)

    def test_workflow_instance_log_entries_create_view_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_transition
        )
        workflow_instance = self.test_document.workflows.first()

        response = self._request_test_workflow_instance_log_entry_create_api_view(
            workflow_instance=workflow_instance
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        workflow_instance.refresh_from_db()
        self.assertEqual(
            workflow_instance.log_entries.first().transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )

    def test_workflow_instance_log_entries_list_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()
        self._create_test_workflow_instance_log_entry()

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_workflow_instance_log_entries_list_view_with_document_access(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_document_stub()
        self._create_test_workflow_instance_log_entry()

        self.grant_access(
            obj=self.test_document, permission=permission_workflow_view
        )

        response = self._request_test_workflow_instance_log_entry_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['transition']['label'],
            TEST_WORKFLOW_TRANSITION_LABEL
        )


class WorkflowAPIViewTestCase(
    WorkflowAPIViewTestMixin, DocumentTestMixin, WorkflowTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_workflow_create_view_no_permission(self):
        response = self._request_test_workflow_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Workflow.objects.count(), 0)

    def test_workflow_create_view_with_permission(self):
        self.grant_permission(permission=permission_workflow_create)

        response = self._request_test_workflow_create_api_view()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['label'], TEST_WORKFLOW_LABEL
        )

        self.assertEqual(Workflow.objects.count(), 1)

    def test_workflow_create_with_document_type_view_no_permission(self):
        response = self._request_test_workflow_create_api_view(
            extra_data={
                'document_types_pk_list': '{}'.format(
                    self.test_document_type.pk
                )
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Workflow.objects.count(), 0)

    def test_workflow_create_with_document_type_view_with_permission(self):
        self.grant_permission(permission=permission_workflow_create)

        response = self._request_test_workflow_create_api_view(
            extra_data={
                'document_types_pk_list': '{}'.format(
                    self.test_document_type.pk
                )
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Workflow.objects.count(), 1)
        workflow = Workflow.objects.first()
        self.assertQuerysetEqual(
            workflow.document_types.all(), (repr(self.test_document_type),)
        )
        self.assertEqual(response.data['id'], workflow.pk)

    def test_workflow_delete_view_no_permission(self):
        self._create_test_workflow()
        response = self._request_test_workflow_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Workflow.objects.count(), 1)

    def test_workflow_delete_view_with_permission(self):
        self._create_test_workflow()
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_delete
        )
        response = self._request_test_workflow_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Workflow.objects.count(), 0)

    def test_workflow_detail_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse('label' in response.data)

    def test_workflow_detail_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], self.test_workflow.label)

    def test_workflow_document_type_create_view_no_permission(self):
        self._create_test_workflow(add_document_type=False)

        response = self._request_test_workflow_document_type_list_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.test_workflow.document_types.count(), 0)

    def test_workflow_document_type_create_view_with_access(self):
        self._create_test_workflow(add_document_type=False)

        self.grant_access(
            permission=permission_workflow_edit, obj=self.test_workflow
        )

        response = self._request_test_workflow_document_type_list_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertQuerysetEqual(
            self.test_workflow.document_types.all(),
            (repr(self.test_document_type),)
        )

    def test_workflow_document_type_delete_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)

        response = self._request_test_workflow_document_type_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.document_types.count(), 1)

    def test_workflow_document_type_delete_view_with_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            permission=permission_workflow_edit, obj=self.test_workflow
        )

        response = self._request_test_workflow_document_type_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.document_types.count(), 0)

    def test_workflow_document_type_detail_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)

        response = self._request_test_workflow_document_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('label' in response.data)

    def test_workflow_document_type_detail_view_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_document_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse('label' in response.data)

    def test_workflow_document_type_detail_view_with_document_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )

        response = self._request_test_workflow_document_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('label' in response.data)

    def test_workflow_document_type_detail_view_with_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_document_type_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['label'], self.test_document_type.label
        )

    def test_workflow_document_type_list_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)

        response = self._request_test_workflow_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_workflow_document_type_list_view_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_workflow_document_type_list_view_with_document_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )

        response = self._request_test_workflow_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_workflow_document_type_list_view_with_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_document_type_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], self.test_document_type.label
        )

    def test_workflow_list_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_workflow_list_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], self.test_workflow.label
        )

    def test_workflow_patch_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_edit_patch_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL)

    def test_workflow_patch_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            permission=permission_workflow_edit, obj=self.test_workflow
        )

        response = self._request_test_workflow_edit_patch_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL_EDITED)

    def test_workflow_put_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_edit_put_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL)

    def test_workflow_put_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_edit_put_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL_EDITED)

    def test_document_type_workflow_list_no_permission(self):
        self._create_test_workflow(add_document_type=True)

        response = self._request_test_document_type_workflow_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_document_type_workflow_list_with_workflow_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_document_type_workflow_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_document_type_workflow_list_with_document_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )

        response = self._request_test_document_type_workflow_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_document_type_workflow_list_with_access(self):
        self._create_test_workflow(add_document_type=True)

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )
        self.grant_access(
            obj=self.test_document_type,
            permission=permission_document_type_view
        )
        response = self._request_test_document_type_workflow_list_api_view()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], self.test_workflow.label
        )


class WorkflowStatesAPIViewTestCase(
    WorkflowStateAPIViewTestMixin, DocumentTestMixin, WorkflowTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_workflow_state_create_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_state_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.states.count(), 0)

    def test_workflow_state_create_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            permission=permission_workflow_edit, obj=self.test_workflow
        )

        response = self._request_test_workflow_state_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.test_workflow.refresh_from_db()
        self.assertEqual(
            self.test_workflow.states.first().label, TEST_WORKFLOW_STATE_LABEL
        )

    def test_workflow_state_delete_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_state_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.states.count(), 1)

    def test_workflow_state_delete_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_state_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.states.count(), 0)

    def test_workflow_state_detail_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_state_detail_api_view()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('label' in response.data)

    def test_workflow_state_detail_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_state_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['label'], TEST_WORKFLOW_STATE_LABEL
        )

    def test_workflow_state_list_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_state_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('label' in response.data)

    def test_workflow_state_list_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        self.grant_access(permission=permission_workflow_view, obj=self.test_workflow)

        response = self._request_test_workflow_state_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], TEST_WORKFLOW_STATE_LABEL
        )

    def test_workflow_state_edit_view_via_patch_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_state_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_state.label, TEST_WORKFLOW_STATE_LABEL
        )

    def test_workflow_state_edit_view_via_patch_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        self.grant_access(permission=permission_workflow_edit, obj=self.test_workflow)

        response = self._request_test_workflow_state_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_state.label, TEST_WORKFLOW_STATE_LABEL_EDITED
        )

    def test_workflow_state_edit_view_via_put_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_state_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_state.label, TEST_WORKFLOW_STATE_LABEL
        )

    def test_workflow_state_edit_view_via_put_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        self.grant_access(permission=permission_workflow_edit, obj=self.test_workflow)

        response = self._request_test_workflow_state_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_state.label, TEST_WORKFLOW_STATE_LABEL_EDITED
        )


class WorkflowTransitionAPIViewTestCase(
    WorkflowTransitionAPIViewTestMixin, DocumentTestMixin, WorkflowTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_workflow_transition_create_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()

        response = self._request_test_workflow_transition_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.transitions.count(), 0)

    def test_workflow_transition_create_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.test_workflow.refresh_from_db()
        self.assertEqual(
            self.test_workflow.transitions.first().label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )

    def test_workflow_transition_delete_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.transitions.count(), 1)

    def test_workflow_transition_delete_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.transitions.count(), 0)

    def test_workflow_transition_detail_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('label' in response.data)

    def test_workflow_transition_detail_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_transition_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['label'], TEST_WORKFLOW_TRANSITION_LABEL
        )

    def test_workflow_transition_list_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_workflow_transition_list_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_transition_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'],
            TEST_WORKFLOW_TRANSITION_LABEL
        )

    def test_workflow_transition_edit_view_via_patch_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )
        self.assertEqual(
            self.test_workflow_transition.origin_state,
            self.test_workflow_state_1
        )
        self.assertEqual(
            self.test_workflow_transition.destination_state,
            self.test_workflow_state_2
        )

    def test_workflow_transition_edit_view_via_patch_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL_EDITED
        )
        self.assertEqual(
            self.test_workflow_transition.origin_state,
            self.test_workflow_state_2
        )
        self.assertEqual(
            self.test_workflow_transition.destination_state,
            self.test_workflow_state_1
        )

    def test_workflow_transition_edit_view_via_put_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_edit_put_api_view_via()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )
        self.assertEqual(
            self.test_workflow_transition.origin_state,
            self.test_workflow_state_1
        )
        self.assertEqual(
            self.test_workflow_transition.destination_state,
            self.test_workflow_state_2
        )

    def test_workflow_transition_edit_view_via_put_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_edit_put_api_view_via()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL_EDITED
        )
        self.assertEqual(
            self.test_workflow_transition.origin_state,
            self.test_workflow_state_2
        )
        self.assertEqual(
            self.test_workflow_transition.destination_state,
            self.test_workflow_state_1
        )


class WorkflowTransitionFieldAPIViewTestCase(
    WorkflowTransitionFieldAPIViewTestMixin, DocumentTestMixin,
    WorkflowTestMixin, WorkflowTransitionFieldTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def test_workflow_transition_field_create_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_test_workflow_transition_field_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            transition_field_count
        )

    def test_workflow_transition_field_create_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_test_workflow_transition_field_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            transition_field_count + 1
        )

    def test_workflow_transition_field_delete_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_test_workflow_transition_field_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            transition_field_count
        )

    def test_workflow_transition_field_delete_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_test_workflow_transition_field_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            transition_field_count - 1
        )

    def test_workflow_transition_field_detail_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        response = self._request_test_workflow_transition_field_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_workflow_transition_field_detail_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_transition_field_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['label'],
            self.test_workflow_transition_field.label
        )

    def test_workflow_transition_field_edit_via_patch_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        transition_field_label = self.test_workflow_transition_field.label

        response = self._request_test_workflow_transition_field_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_workflow_transition_field.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition_field.label, transition_field_label
        )

    def test_workflow_transition_field_edit_via_patch_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        transition_field_label = self.test_workflow_transition_field.label

        response = self._request_test_workflow_transition_field_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflow_transition_field.refresh_from_db()
        self.assertNotEqual(
            self.test_workflow_transition_field.label, transition_field_label
        )

    def test_workflow_transition_field_list_view_no_permission(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        response = self._request_test_workflow_transition_field_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_workflow_transition_field_list_view_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_transition_field_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'],
            self.test_workflow_transition_field.label
        )
