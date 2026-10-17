cmake_minimum_required(VERSION 3.13)

project(FluidSynthVST VERSION 1.0.0)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(VST3_SDK.cmake)

# FluidSynth installed by the SCons dependency build.
# Override this path when configuring another platform or architecture.
if(NOT DEFINED FLUIDSYNTH_INSTALL_DIR)
    if(WIN32)
        set(_fluidsynth_default "${CMAKE_SOURCE_DIR}/build/deps/fluidsynth/windows-x86_64")
    elseif(APPLE)
        set(_fluidsynth_default "${CMAKE_SOURCE_DIR}/build/deps/fluidsynth/macos-arm64")
    else()
        set(_fluidsynth_default "${CMAKE_SOURCE_DIR}/build/deps/fluidsynth/linux-x86_64")
    endif()

    set(FLUIDSYNTH_INSTALL_DIR "${_fluidsynth_default}" CACHE PATH "FluidSynth installation prefix")
endif()

# Import FluidSynth's static library and its exported dependencies.
find_package(FluidSynth CONFIG REQUIRED PATHS "${FLUIDSYNTH_INSTALL_DIR}/lib/cmake/fluidsynth" NO_DEFAULT_PATH)

set(plug_sources source/fluidsynthvst.h source/fluidsynthvst.cpp)

set(target fluidsynthvst)

smtg_add_vst3plugin(${target} ${plug_sources})

target_link_libraries(${target} PRIVATE sdk FluidSynth::libfluidsynth)

# smtg_dump_plugin_package_variables(${target})
smtg_target_dump_plugin_package_variables(${target})

cmake_print_variables(CMAKE_BUILD_TYPE CMAKE_CONFIGURATION_TYPES FLUIDSYNTH_INSTALL_DIR)
