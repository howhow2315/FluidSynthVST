set(vst3sdk_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/library/VST3_SDK" CACHE PATH "Location of VST3 SDK")

if(NOT EXISTS "${vst3sdk_SOURCE_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "VST3 SDK CMakeLists.txt not found: ${vst3sdk_SOURCE_DIR}")
endif()

add_subdirectory("${vst3sdk_SOURCE_DIR}""${CMAKE_CURRENT_BINARY_DIR}/vst3sdk"EXCLUDE_FROM_ALL)

smtg_enable_vst3_sdk()
