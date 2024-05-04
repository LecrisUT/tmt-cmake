cmake_minimum_required(VERSION 3.25...3.30)

project(simple LANGUAGES NONE)

# Check binary dir is in TMT_PLAN_DATA
if (NOT CMAKE_BINARY_DIR PATH_EQUAL "$ENV{TMT_PLAN_DATA}/build")
    message(SEND_ERROR
        "Build directory was not properly set\n"
        "  Expected: $ENV{TMT_PLAN_DATA}/build\n"
        "  Actual: ${CMAKE_BINARY_DIR}"
    )
endif()

add_custom_target(dummy ALL COMMAND ${CMAKE_COMMAND} -E echo dummy_target)
