cmake_minimum_required(VERSION 3.25...3.30)

project(simple LANGUAGES NONE)

add_custom_target(dummy ALL COMMAND ${CMAKE_COMMAND} -E echo dummy_target)

enable_testing()
add_test(NAME test_pass
    COMMAND ${CMAKE_COMMAND} -E true
)
add_test(NAME test_fail
    COMMAND ${CMAKE_COMMAND} -E false
)
