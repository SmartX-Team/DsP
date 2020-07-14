# swagger_client.DspApi

All URIs are relative to *https://k-post-ip-address/smartx/post/v0.0.1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dspcompose**](DspApi.md#dspcompose) | **POST** /dsp/compose | Trigger boxes composition
[**dsprelease**](DspApi.md#dsprelease) | **DELETE** /dsp/release | Trigger boxes release
[**get_ds_p_installer_by_name**](DspApi.md#get_ds_p_installer_by_name) | **GET** /dsp/installer/{installer_name} | Get all installers supported by the DsP on the post
[**get_ds_p_installer_list**](DspApi.md#get_ds_p_installer_list) | **GET** /dsp/installers | Get all installers supported by the DsP on the post


# **dspcompose**
> dspcompose(topology)

Trigger boxes composition

Trigger boxes composition

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DspApi()
topology = 'topology_example' # str | Pet object that needs to be added to the store

try:
    # Trigger boxes composition
    api_instance.dspcompose(topology)
except ApiException as e:
    print("Exception when calling DspApi->dspcompose: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topology** | **str**| Pet object that needs to be added to the store | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dsprelease**
> dsprelease(topology)

Trigger boxes release

Trigger boxes release

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DspApi()
topology = 'topology_example' # str | Pet object that needs to be added to the store

try:
    # Trigger boxes release
    api_instance.dsprelease(topology)
except ApiException as e:
    print("Exception when calling DspApi->dsprelease: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **topology** | **str**| Pet object that needs to be added to the store | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ds_p_installer_by_name**
> Installer get_ds_p_installer_by_name(installer_name)

Get all installers supported by the DsP on the post

Multiple status values can be provided with comma separated strings

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DspApi()
installer_name = 'installer_name_example' # str | The name of a installer to return

try:
    # Get all installers supported by the DsP on the post
    api_response = api_instance.get_ds_p_installer_by_name(installer_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DspApi->get_ds_p_installer_by_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **installer_name** | **str**| The name of a installer to return | 

### Return type

[**Installer**](Installer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/xml, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ds_p_installer_list**
> list[Installer] get_ds_p_installer_list()

Get all installers supported by the DsP on the post

Multiple status values can be provided with comma separated strings

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DspApi()

try:
    # Get all installers supported by the DsP on the post
    api_response = api_instance.get_ds_p_installer_list()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DspApi->get_ds_p_installer_list: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Installer]**](Installer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/xml, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

