cmake_minimum_required(VERSION 3.16)
project(DPIEngine VERSION 2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Threads REQUIRED)

set(DPI_COMMON_SOURCES
    src/pcap_reader.cpp
    src/packet_parser.cpp
    src/sni_extractor.cpp
    src/types.cpp
)

# Main multi-threaded pipeline.
add_executable(dpi-engine src/dpi_mt.cpp ${DPI_COMMON_SOURCES})
target_include_directories(dpi-engine PRIVATE include)
target_link_libraries(dpi-engine PRIVATE Threads::Threads)

# Single-threaded pipeline for easier study and debugging.
add_executable(dpi-simple src/main_working.cpp ${DPI_COMMON_SOURCES})
target_include_directories(dpi-simple PRIVATE include)

# Packet header inspection utility.
add_executable(packet-analyzer src/main.cpp src/pcap_reader.cpp src/packet_parser.cpp)
target_include_directories(packet-analyzer PRIVATE include)

# Small SNI/application inspection demo.
add_executable(dpi-simple-demo src/main_simple.cpp ${DPI_COMMON_SOURCES})
target_include_directories(dpi-simple-demo PRIVATE include)

# Reusable modular components and the component-based multi-threaded engine.
add_library(dpi-components STATIC
    src/dpi_engine.cpp
    src/connection_tracker.cpp
    src/fast_path.cpp
    src/load_balancer.cpp
    src/rule_manager.cpp
)
target_include_directories(dpi-components PUBLIC include)
target_link_libraries(dpi-components PUBLIC Threads::Threads)

add_executable(dpi-modular src/main_dpi.cpp ${DPI_COMMON_SOURCES})
target_include_directories(dpi-modular PRIVATE include)
target_link_libraries(dpi-modular PRIVATE dpi-components Threads::Threads)

if(MSVC)
    foreach(target dpi-engine dpi-simple packet-analyzer dpi-simple-demo dpi-components dpi-modular)
        target_compile_options(${target} PRIVATE /W4 /permissive-)
    endforeach()
else()
    foreach(target dpi-engine dpi-simple packet-analyzer dpi-simple-demo dpi-components dpi-modular)
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endforeach()
endif()

include(CTest)
find_package(Python3 COMPONENTS Interpreter QUIET)
if(BUILD_TESTING AND Python3_Interpreter_FOUND)
    add_test(NAME dpi-multithreaded-sample
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/integration_test.py
                $<TARGET_FILE:dpi-engine> ${CMAKE_CURRENT_SOURCE_DIR}
                ${CMAKE_CURRENT_BINARY_DIR}/multithreaded/filtered-test.pcap)
    add_test(NAME dpi-modular-sample
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/integration_test.py
                $<TARGET_FILE:dpi-modular> ${CMAKE_CURRENT_SOURCE_DIR}
                ${CMAKE_CURRENT_BINARY_DIR}/modular/filtered-test.pcap)
endif()

install(TARGETS dpi-engine dpi-simple dpi-modular packet-analyzer RUNTIME DESTINATION bin)
