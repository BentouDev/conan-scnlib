newoption {
    trigger = "arch",
    description = "Build for the given architecture",
    value = "ARCH"
}

workspace "scnlib"
    configurations { "Debug", "Release" }
    debugformat "C7"

    architecture(_OPTIONS.arch)

    filter { "Debug" }
        symbols "On"

    filter { "Release" }
        optimize "On"

    project "scnlib"
        kind("StaticLib")

        includedirs {
            "include"
        }

        files {
            "src/**.cpp"
        }
