cmake_minimum_required(VERSION 3.24)
project(PathOfBuildingLauncher LANGUAGES CXX)
add_executable(PathOfBuildingLauncher WIN32 launcher.cpp)
set_target_properties(
  PathOfBuildingLauncher
  PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    OUTPUT_NAME "Path of Building"
)
