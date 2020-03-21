from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class ScnlibConan(ConanFile):
    name = "scnlib"
    version = "0.3"
    license = "https://github.com/eliaskosunen/scnlib#license"
    description = "Scanf for modern C++"
    url = "https://scnlib.dev/"

    settings = "os", "compiler", "arch"
    exports_sources = ["premake5.lua"]

    build_requires = "premake_installer/5.0.0-alpha14@bincrafters/stable"

    SCNLIB_FOLDER_NAME = "scnlib-{}".format(version)

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.settings.compiler.runtime

    # The the source from github
    def source(self):
        zip_name = "v{}.zip".format(self.version)
        tools.download("https://github.com/eliaskosunen/scnlib/archive/{}".format(zip_name), zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    # Build both the debug and release builds
    def build(self):
        _premake_action = "gmake"

        if self.settings.compiler == "Visual Studio":
            _visuals = {
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017",
                "16": "vs2019",
            }
            _premake_action = "{}".format(_visuals.get(str(self.settings.compiler.version), "vs2019"))

        with tools.chdir(os.path.join(self.source_folder, self.SCNLIB_FOLDER_NAME)):

            copyfile("../premake5.lua", "premake5.lua")

            self.run("premake5 {} --arch={}".format(_premake_action, self.settings.arch))

            if self.settings.compiler == "Visual Studio":
                msbuild = MSBuild(self)
                msbuild.build("scnlib.sln", build_type="Debug")
                msbuild.build("scnlib.sln", build_type="Release")

            if self.settings.compiler == "clang":
                self.run("make config=debug")
                self.run("make config=release")

    def package(self):
        # Copy the license file
        self.copy("LICENSE", src=self.SCNLIB_FOLDER_NAME, dst="LICENSE")

        self.copy("*.h", "include", "%s/include" % self.SCNLIB_FOLDER_NAME, keep_path=True)

        build_dir = os.path.join(self.SCNLIB_FOLDER_NAME, "bin")

        if self.settings.os == "Windows":
            self.copy("*.pdb", "lib", build_dir, keep_path=True)
            self.copy("*.lib", "lib", build_dir, keep_path=True)

        if self.settings.os == "Linux":
            self.copy("*.a", "lib", build_dir, keep_path=True)

    def package_info(self):
        self.cpp_info.debug.libdirs = [ "lib/Debug" ]
        self.cpp_info.release.libdirs = [ "lib/Release" ]
        self.cpp_info.libdirs = []
        self.cpp_info.libs = ["scnlib"]
