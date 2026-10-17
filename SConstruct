import os, shutil

env = Environment(ENV=os.environ.copy())

# Build configuration
platform = ARGUMENTS.get("platform", "linux").lower()
arch = ARGUMENTS.get("arch", "x86_64").lower()

if platform not in ("linux", "windows", "macos"):
    Exit("Unsupported platform: " + platform)

env["platform"] = platform
env["arch"] = arch

# Third-party sources
fluidsynth_source = Dir("#library/fluidsynth")

# Keep dependency build files separate from installed artifacts.
dependency_root = Dir("#build/deps").abspath
fluidsynth_install = os.path.join(dependency_root, "fluidsynth", f"{platform}-{arch}")
fluidsynth_build = os.path.join(
    dependency_root, "fluidsynth-build", f"{platform}-{arch}"
)

env["FLUIDSYNTH_INSTALL"] = fluidsynth_install
env["FLUIDSYNTH_BUILD"] = fluidsynth_build

# Load the FluidSynth SCons tool.
env.Tool("fluidsynth", toolpath=["tools"])

# FluidSynth installs its public header under include/fluidsynth.
fluidsynth_header = File(os.path.join(fluidsynth_install, "include", "fluidsynth.h"))

# Static library naming varies by platform and FluidSynth version.
if platform == "windows":
    fluidsynth_library = File(
        os.path.join(fluidsynth_install, "lib", "libfluidsynth-3.lib")
    )
else:
    fluidsynth_library = File(
        os.path.join(fluidsynth_install, "lib", "libfluidsynth.a")
    )

fluidsynth = env.fluidsynth(
    target=[fluidsynth_library, fluidsynth_header],
    source=[fluidsynth_source],
)

Default(fluidsynth)

project_root = Dir("#").abspath
vst_build = os.path.join(project_root, "build", "vst")
sdk_root = os.path.join(project_root, "library", "VST3_SDK")

cmake_inputs = [
    "#CMakeLists.txt",
    "#VST3_SDK.cmake",
    "#source/fluidsynthvst.cpp",
    "#source/fluidsynthvst.h",
]

configure = env.Command(
    target=os.path.join(vst_build, ".configured"),
    source=cmake_inputs,
    action=[
        f'cmake -S "{project_root}" -B "{vst_build}" '
        f'-DVST3_SDK_ROOT="{sdk_root}" '
        f'-DFLUIDSYNTH_INSTALL_DIR="{fluidsynth_install}" '
        "-DCMAKE_BUILD_TYPE=Release",
        'cmake -E touch "$TARGET"',
    ],
)

plugin = env.Command(
    target=os.path.join(vst_build, ".built"),
    source=configure,
    action=[
        f'cmake --build "{vst_build}" --target fluidsynthvst',
        'cmake -E touch "$TARGET"',
    ],
)

Depends(configure, fluidsynth)


export_dir = os.path.join(project_root, "export")
vst3_bundle = os.path.join(vst_build, "VST3", "Release", "fluidsynthvst.vst3")
export_bundle = os.path.join(export_dir, "fluidsynthvst.vst3")

export = env.Command(
    target=export_bundle,
    source=plugin,
    action=[
        'rm -rf "$TARGET"',
        f'mkdir -p "{export_dir}"',
        f'cp -a "{vst3_bundle}" "$TARGET"',
    ],
)

Depends(export, plugin)
Default(export)
