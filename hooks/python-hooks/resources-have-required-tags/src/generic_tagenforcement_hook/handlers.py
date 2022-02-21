import logging
from typing import Any, MutableMapping, Optional
import botocore

from cloudformation_cli_python_lib import (
    BaseHookHandlerRequest,
    HandlerErrorCode,
    Hook,
    HookInvocationPoint,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import HookHandlerRequest, TypeConfigurationModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "Generic::TagEnforcement::Hook"

# LOG.setLevel(logging.debug)

hook = Hook(TYPE_NAME, TypeConfigurationModel)
test_entrypoint = hook.test_entrypoint


def _validate_properties(target_name, target_type, resource_properties, type_configuration, session):
    status = OperationStatus.SUCCESS
    message = f"Successfully invoked required tags hook and found no violations"
    errorCode = None

    try:
        if type_configuration and hasattr(type_configuration, 'requiredTags') and type_configuration.requiredTags is not None and len(type_configuration.requiredTags) > 0:
            required_tag_list = type_configuration.requiredTags.split(',')
        if resource_properties:
            resource_tags_kv = resource_properties.get("Tags", {})
            if not resource_tags_kv:
                status = OperationStatus.FAILED,
                message = f"Missing tags in resource: {', '.join(required_tag_list)}",
                errorCode = HandlerErrorCode.NonCompliant
                logging.warn(f"{message}")
            else:
                resource_tag_keys = []
                for kv in resource_tags_kv:
                    resource_tag_keys.append(kv['Key'])
                missing_tags = []
                for required_tag in required_tag_list:
                    if required_tag not in resource_tag_keys:
                        missing_tags.append(required_tag)
                if len(missing_tags) > 0:
                    status = OperationStatus.FAILED
                    message = f"Missing tags in resource: {', '.join(missing_tags)}"
                    errorCode = HandlerErrorCode.NonCompliant
                    logging.warn(f"{message}")
        else:
            status = OperationStatus.FAILED
            message = f"No properties defined on resource"
            errorCode = HandlerErrorCode.NonCompliant
    except Exception as e:
        status = OperationStatus.FAILED
        message = f"{e}"
        errorCode = HandlerErrorCode.InternalFailure
        logging.warn(str(e))
    return ProgressEvent(
        status=status,
        message=message,
        errorCode=errorCode
    )


@hook.handler(HookInvocationPoint.CREATE_PRE_PROVISION)
def pre_create_handler(
        session: Optional[SessionProxy],
        request: HookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    return _validate_properties(request.hookContext.targetName, request.hookContext.targetType, request.hookContext.targetModel.get("resourceProperties"), type_configuration, session)


@hook.handler(HookInvocationPoint.UPDATE_PRE_PROVISION)
def pre_update_handler(
        session: Optional[SessionProxy],
        request: BaseHookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: MutableMapping[str, Any]
) -> ProgressEvent:
    return _validate_properties(request.hookContext.targetName, request.hookContext.targetType, request.hookContext.targetModel.get("resourceProperties"), type_configuration, session)


@hook.handler(HookInvocationPoint.DELETE_PRE_PROVISION)
def pre_delete_handler(
        session: Optional[SessionProxy],
        request: BaseHookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    return ProgressEvent(
        status=OperationStatus.SUCCESS
    )
