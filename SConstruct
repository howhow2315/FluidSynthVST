
import os

from SCons.Script import ARGUMENTS, Default, Dir, Environment, Exit, File

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
fluidsynth_install = os.path.join(
    dependency_root, "fluidsynth", f"{platform}-{arch}"
)
fluidsynth_build = os.path.join(
    dependency_root, "fluidsynth-build", f"{platform}-{arch}"
)

env["FLUIDSYNTH_INSTALL"] = fluidsynth_install
env["FLUIDSYNTH_BUILD"] = fluidsynth_build

# Load the FluidSynth SCons tool.
env.Tool("fluidsynth", toolpath=["tools"])

# FluidSynth installs its public header under include/fluidsynth.
fluidsynth_header = File(
    os.path.join(fluidsynth_install, "include", "fluidsynth.h")
)

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
