"""Enum values for HSA

Note that Python namespacing could be used to avoid the C-like
prefixing, but we choose to keep the same names as found in the C
enums, in order to match the documentation.
"""

import ctypes

# HSA_LARGE_MODEL should be True for 64 bit platforms (make sure of this!)
# Maybe there would be a better test?
HSA_LARGE_MODEL = ctypes.sizeof(ctypes.c_void_p) == 8

# hsa_status_t
HSA_STATUS_SUCCESS                            = 0
HSA_STATUS_INFO_BREAK                         = 0x1
HSA_EXT_STATUS_INFO_ALREADY_INITIALIZED       = 0x4000
HSA_EXT_STATUS_INFO_UNRECOGNIZED_OPTIONS      = 0x4001
HSA_STATUS_ERROR                              = 0x10000
HSA_STATUS_ERROR_INVALID_ARGUMENT             = 0x10001
HSA_STATUS_ERROR_INVALID_QUEUE_CREATION       = 0x10002
HSA_STATUS_ERROR_INVALID_ALLOCATION           = 0x10003
HSA_STATUS_ERROR_INVALID_AGENT                = 0x10004
HSA_STATUS_ERROR_INVALID_REGION               = 0x10005
HSA_STATUS_ERROR_INVALID_SIGNAL               = 0x10006
HSA_STATUS_ERROR_INVALID_QUEUE                = 0x10007
HSA_STATUS_ERROR_OUT_OF_RESOURCES             = 0x10008
HSA_STATUS_ERROR_INVALID_PACKET_FORMAT        = 0x10009
HSA_STATUS_ERROR_RESOURCE_FREE                = 0x1000A
HSA_STATUS_ERROR_NOT_INITIALIZED              = 0x1000B
HSA_STATUS_ERROR_REFCOUNT_OVERFLOW            = 0x1000C
HSA_EXT_STATUS_ERROR_DIRECTIVE_MISMATCH       = 0x14000
HSA_EXT_STATUS_ERROR_IMAGE_FORMAT_UNSUPPORTED = 0x14001
HSA_EXT_STATUS_ERROR_IMAGE_SIZE_UNSUPPORTED   = 0x14002

# hsa_system_info_t
HSA_SYSTEM_INFO_VERSION_MAJOR                 = 0
HSA_SYSTEM_INFO_VERSION_MINOR                 = 1
HSA_SYSTEM_INFO_TIMESTAMP                     = 2
HSA_SYSTEM_INFO_TIMESTAMP_FREQUENCY           = 3
HSA_SYSTEM_INFO_SIGNAL_MAX_WAIT               = 4
                                               
# hsa_agent_feature_t                          
HSA_AGENT_FEATURE_DISPATCH                    = 1
HSA_AGENT_FEATURE_AGENT_DISPATCH              = 2
                                               
# hsa_device_type_t                            
HSA_DEVICE_TYPE_CPU                           = 0
HSA_DEVICE_TYPE_GPU                           = 1
HSA_DEVICE_TYPE_DSP                           = 2
                                               
# hsa_system_info_t                            
HSA_SYSTEM_INFO_VERSION_MAJOR                 = 0
HSA_SYSTEM_INFO_VERSION_MINOR                 = 1
HSA_SYSTEM_INFO_TIMESTAMP                     = 2
HSA_SYSTEM_INFO_TIMESTAMP_FREQUENCY           = 3
HSA_SYSTEM_INFO_SIGNAL_MAX_WAIT               = 4
                                               
# hsa_agent_info_t                             
HSA_AGENT_INFO_NAME                           = 0
HSA_AGENT_INFO_VENDOR_NAME                    = 1
HSA_AGENT_INFO_FEATURE                        = 2
HSA_AGENT_INFO_WAVEFRONT_SIZE                 = 3
HSA_AGENT_INFO_WORKGROUP_MAX_DIM              = 4
HSA_AGENT_INFO_WORKGROUP_MAX_SIZE             = 5
HSA_AGENT_INFO_GRID_MAX_DIM                   = 6
HSA_AGENT_INFO_GRID_MAX_SIZE                  = 7
HSA_AGENT_INFO_FBARRIER_MAX_SIZE              = 8
HSA_AGENT_INFO_QUEUES_MAX                     = 9
HSA_AGENT_INFO_QUEUE_MAX_SIZE                 = 10
HSA_AGENT_INFO_QUEUE_TYPE                     = 11
HSA_AGENT_INFO_NODE                           = 12
HSA_AGENT_INFO_DEVICE                         = 13
HSA_AGENT_INFO_CACHE_SIZE                     = 14
HSA_EXT_AGENT_INFO_IMAGE1D_MAX_DIM            = 15
HSA_EXT_AGENT_INFO_IMAGE2D_MAX_DIM            = 16
HSA_EXT_AGENT_INFO_IMAGE3D_MAX_DIM            = 17
HSA_EXT_AGENT_INFO_IMAGE_ARRAY_MAX_SIZE       = 18
HSA_EXT_AGENT_INFO_IMAGE_RD_MAX               = 19
HSA_EXT_AGENT_INFO_IMAGE_RDWR_MAX             = 20
HSA_EXT_AGENT_INFO_SAMPLER_MAX                = 21

# hsa_queue_type_t
HSA_QUEUE_TYPE_MULTI                          = 0
HSA_QUEUE_TYPE_SINGLE                         = 1