# Generic::TagEnforcement::Hook

This hook will check for the presence of required tags in the resource types listed in the JSON model file.

The resource list is static and must be updated periodically when CloudFormation adds support for more resources. Steps for updating the resource list are included below.

## Getting Started

1. Create a virtual environment and install cfn CLI:
```bash
python3 -m venv env
source env/bin/activate
pip3 install cloudformation-cli cloudformation-cli-python-plugin
pip3 install --upgrade cloudformation-cli cloudformation-cli-python-plugin
```

## Deploying this Hook

1. Clone this repository to your environment where you have the `cfn` CLI installed

2. Run the `cfn submit` command to register the hook with CloudFormation
```bash
cfn submit --set-default # [--region region-name-1]
```

4. Replace <Tag1,Tag2> in the .type_config.json file with your comma-delimited string of required tags and then activate the hook using the following command structure:
```bash
aws cloudformation set-type-configuration \
  --configuration file://type_config.json \
  --type HOOK \
  --type-name Generic::TagEnforcement::Hook
```

## Updating the hook

The hook can be updated at any time using the `cfn submit --set-default` command. The configuration will remain the same even if the version of the schema is updated (eg. due to new resource types being added).

## Updating the resource list

If you would like to maintain the list of resources in a separate file and update the model JSON from there, you can replace all code after the "handlers" property with the following:
```json
    "handlers": {
        "preCreate": {
            "targetNames": [
<TARGET_RESOURCES>
],
            "permissions": []
        },
        "preUpdate": {
            "targetNames": [
<TARGET_RESOURCES>
],
            "permissions": []
        }
    },
    "additionalProperties": false
}
```

...and then run this command to replace the <TARGET_RESOURCES> string with the contents of your file (file name in this example is YOUR_FILE_WITH_A_COMMA_DELIMITED_LIST_OF_STRING_QUOTED_RESOURCE_TYPES):
```bash
sed -e '/<TARGET_RESOURCES>/ {' -e 'r YOUR_FILE_WITH_A_COMMA_DELIMITED_LIST_OF_STRING_QUOTED_RESOURCE_TYPES' -e 'd' -e '}' -i generic-tagenforcement-hook.json
```

Ideally, your resource list file is indented by 16 to match the indenting in the JSON file:
```json
// YOUR_FILE_WITH_A_COMMA_DELIMITED_LIST_OF_STRING_QUOTED_RESOURCE_TYPES
                "AWS::AAService::Aardvark",
                "AWS::AAService::Aardwolf",
                ...
                "AWS::ZZService::Zephyr",
                "AWS::ZZService::Zeppelin"
```

## Other Notes

### Testing instructions

#### Contract testing
If you wish to perform a `submit dry-run` or perform contract tests using the `inputs` folder, you should significantly reduce the number of resources that are in the model JSON file (under 50). After doing so, you can create  test locally using these commands:

```bash
# In a separate instance, create a local Lambda service:
source CloudFormationCLI/env/bin/activate && cd CloudFormationCLI/myhook/
sam local start-lambda
```

```bash
# In the original window NOT running the local Lambda service
cfn generate
cfn submit --dry-run
cfn test -v
```

#### Live testing
The `cfn_templates` folder has some instructions for creating several simple stacks to test hook validity.
