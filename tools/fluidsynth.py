#!/usr/bin/env python3
"""Build static FluidSynth with CMake as an SCons dependency."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path


# https://www.fluidsynth.org/wiki/BuildingWithCMake/#output-library-naming-conventions
# we dont need fluidsynth to have access to any audio servers, midi devices, or anything system level like networking or d-bus/systemd
BUILD_OPTIONS = {
    # Linux
    "alsa": False,  # Linux ALSA audio device backend.
    "jack": False,  # JACK audio server backend.
    "pipewire": False,  # Linux PipeWire audio device backend.
    "pulseaudio": False,  # PulseAudio audio device backend.
    "oss": False,  # OSS audio device backend.
    "systemd": False,  # Linux systemd integration; unnecessary for library use.
    "dbus": False,  # D-Bus integration; unnecessary for library use.
    # Windows
    "dsound": False,  # Windows DirectSound audio device backend.
    "wasapi": False,  # Windows WASAPI audio device backend.
    "waveout": False,  # Windows WaveOut audio device backend.
    "winmidi": False,  # Windows MIDI device backend.
    # Cross-platform
    "portaudio": False,  # PortAudio audio device backend.
    "sdl3": False,  # SDL3 audio device backend.
    "aufile": False,  # Audio-file output driver.
    "libsndfile": False,  # libsndfile audio-file output support.
    "midishare": False,  # MidiShare MIDI backend.
    "network": False,  # Network/MIDI networking support.
    # Android
    "oboe": False,  # Android Oboe audio backend.
    "opensles": False,  # Android OpenSL ES audio backend.
    # Core synthesis
    "threads": True,  # Multithreading, including parallel voice synthesis.
    "openmp": False,  # OpenMP acceleration for synthesis/SoundFont processing.
    "unicode": True,  # Unicode support, particularly relevant on Windows.
    "native-dls": False,  # Native DLS support; unrelated to audio device access.
    "signalsmith": True,  # Signalsmith DSP limiter/reverb; useful for normal DSP.
    # Optional integrations
    "ladspa": False,  # LADSPA plugin/effect support; enable only if needed.
    "readline": False,  # Readline support for the interactive CLI; unnecessary for library use.
    "ipv6": False,  # IPv6 support; only relevant if network functionality is enabled.
}

PLATFORM_BUILD_OPTIONS = {
    "macos": {
        "coreaudio": False,  # macOS/iOS CoreAudio audio device backend.
        "coremidi": False,  # macOS/iOS CoreMIDI MIDI device backend.
        "framework": False,  # Build a normal dylib instead of FluidSynth.framework.
    }
}


def run(*args: str) -> None:
    print("+", shlex.join(args), flush=True)
    subprocess.run(args, check=True)


def cmake_bool(value: bool) -> str:
    return "ON" if value else "OFF"


def target_cmake_args(platform: str, arch: str) -> list[str]:
    """Return CMake target settings, not host settings."""
    args: list[str] = []

    if platform == "macos":
        if arch == "universal":
            args.append("-DCMAKE_OSX_ARCHITECTURES=arm64;x86_64")
        elif arch in ("arm64", "x86_64"):
            args.append(f"-DCMAKE_OSX_ARCHITECTURES={arch}")
        else:
            raise ValueError(f"Unsupported macOS architecture: {arch}")

    elif platform == "windows":
        args.extend(
            [
                "-G",
                "MinGW Makefiles",
                "-DCMAKE_C_COMPILER=gcc",
                "-DCMAKE_CXX_COMPILER=g++",
                # if this doesnt work consider MinGW-w64, im resigning to disable openmp instead for now
                "-DCMAKE_C_FLAGS=-foffload=disable",
                "-DCMAKE_CXX_FLAGS=-foffload=disable",
            ]
        )

    elif platform == "linux":
        linux_arches = {"x86_64", "x86_32", "arm64", "arm32", "rv64", "ppc32", "ppc64"}
        if arch not in linux_arches:
            raise ValueError(f"Unsupported Linux architecture: {arch}")

        if arch == "x86_32":
            args.extend(
                [
                    "-DCMAKE_C_FLAGS=-m32",
                    "-DCMAKE_CXX_FLAGS=-m32",
                    "-DCMAKE_EXE_LINKER_FLAGS=-m32",
                    "-DCMAKE_SHARED_LINKER_FLAGS=-m32",
                    "-DCMAKE_MODULE_LINKER_FLAGS=-m32",
                    "-DCMAKE_SYSTEM_PROCESSOR=i686",
                ]
            )

    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # Optional toolchain override for Linux, Windows, or custom setups.
    # For Android/Web/iOS, set this only if you intentionally want to
    # override the toolchain selected above.
    override = os.environ.get("FLUIDSYNTH_TOOLCHAIN_FILE")
    if override:
        args = [item for item in args if not item.startswith("-DCMAKE_TOOLCHAIN_FILE=")]
        args.append(f"-DCMAKE_TOOLCHAIN_FILE={override}")

    # Additional CMake arguments, supplied by CI or the caller.
    args.extend(shlex.split(os.environ.get("FLUIDSYNTH_CMAKE_ARGS", "")))

    return args


def build_cmake(
    source: Path, build: Path, install: Path, platform: str, arch: str
) -> None:
    build.mkdir(parents=True, exist_ok=True)
    install.mkdir(parents=True, exist_ok=True)

    configure = [
        "cmake",
        "-S",
        str(source),
        "-B",
        str(build),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
        f"-DCMAKE_INSTALL_PREFIX={install}",
        "-DCMAKE_WARN_DEPRECATED=OFF",
        # web seems like it needs this 'error: no member named 'clamp' in namespace 'std'', but it just wont build with EMCC_FORCE_STDLIBS=1 or link without it
        # "-DCMAKE_CXX_STANDARD=17",
        # "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
        # "-DCMAKE_CXX_EXTENSIONS=OFF",
        # "-DCMAKE_CXX_FLAGS=-std=c++17 -include algorithm",
    ]

    build_options = {**BUILD_OPTIONS, **PLATFORM_BUILD_OPTIONS.get(platform, {})}

    configure.extend(
        f"-Denable-{name}={cmake_bool(value)}" for name, value in build_options.items()
    )

    # Pass the target architecture and toolchain settings to CMake.
    configure.extend(target_cmake_args(platform, arch))

    run(*configure)
    run("cmake", "--build", str(build), "--parallel", "--config", "Release")
    run("cmake", "--install", str(build), "--config", "Release")


def build_fluidsynth(target, source, env) -> None:
    source_path = Path(str(source[0])).resolve()
    install = Path(env["FLUIDSYNTH_INSTALL"]).resolve()

    platform = str(env["platform"])
    arch = str(env.get("arch", ""))

    # Include the target in the build directory to prevent incompatible
    # CMake caches from being reused across platforms and architectures.
    build = Path(env["FLUIDSYNTH_BUILD"]).resolve()
    build_cmake(source_path, build, install, platform, arch)

    # Validate the actual artifacts declared by the SCons caller.
    target_paths = [Path(str(node)) for node in target]

    missing = [
        path for path in target_paths if not path.exists() and not path.is_symlink()
    ]

    if missing:
        names = "\n".join(f"  {path}" for path in missing)
        raise RuntimeError(
            f"FluidSynth installation completed, but these declared SCons targets were not produced:\n{names}"
        )


def fluidsynth(env, target, source):
    return env.Command(target, source, build_fluidsynth)


def exists(env) -> bool:
    return env.Detect("cmake") is not None


def generate(env) -> None:
    env.AddMethod(fluidsynth, "fluidsynth")
