# DPI Engine — Deep Packet Inspection System

## The Story Behind the Project

During my third year of engineering, Computer Networks became one of the subjects that genuinely caught my attention. I was fascinated by how data travels across networks, how packets are structured, and how different protocols work together to make communication possible.

As I explored these concepts, my curiosity grew beyond the classroom. I wanted to understand what happens inside network packets and how traffic can be analysed at a deeper level.

Towards the end of my third year, I turned that curiosity into a hands-on project: a **Deep Packet Inspection (DPI) Engine** built with C++.

The project explores packet-level analysis, protocol parsing, application-aware traffic identification, connection tracking, configurable filtering rules, and multithreaded packet processing.

## Project Overview

A Deep Packet Inspection engine examines packet headers and selected payload data to understand network traffic beyond basic IP-address and port filtering. This project reads offline PCAP captures, analyses supported network protocols, classifies application traffic where metadata is available, applies filtering rules, and writes the forwarded packets to another PCAP file.

```text
                    PCAP Input
                        |
                        v
                   Packet Reader
                        |
                        v
                   Packet Parser
                        |
                        v
              Protocol / DPI Inspection
                        |
                        v
              Flow Tracking and Rules
                        |
                        v
                 Forward / Drop
                        |
                        v
              Filtered PCAP + Statistics
```

## Main Features

- **PCAP processing:** read captured network packets and write filtered output captures.
- **Packet parsing:** inspect Ethernet, IPv4, TCP, and UDP headers.
- **Application inspection:** examine DNS, HTTP Host, and TLS SNI metadata when present in the captured packet payload.
- **Application classification:** map recognised hostnames and protocol information to application categories.
- **Connection tracking:** maintain state for network flows using their endpoint information.
- **Traffic filtering:** apply source-IP, application, and domain blocking rules.
- **Multithreaded processing:** distribute packets across load-balancer and fast-path workers.
- **Statistics:** report packet counts, forwarded and dropped traffic, and application classifications.

> **Scope note:** TLS SNI and HTTP Host inspection depend on the relevant handshake or request data being present in the captured packet. This is an offline PCAP analysis project; it is not a kernel firewall or a live network gateway.

## Project Structure

```text
DPI-Engine/
├── include/                    # Header files
│   ├── connection_tracker.h
│   ├── dpi_engine.h
│   ├── fast_path.h
│   ├── load_balancer.h
│   ├── packet_parser.h
│   ├── pcap_reader.h
│   ├── platform.h
│   ├── rule_manager.h
│   ├── sni_extractor.h
│   ├── thread_safe_queue.h
│   └── types.h
├── src/                         # C++ implementation files
│   ├── connection_tracker.cpp
│   ├── dpi_engine.cpp
│   ├── dpi_mt.cpp
│   ├── fast_path.cpp
│   ├── load_balancer.cpp
│   ├── main.cpp
│   ├── main_dpi.cpp
│   ├── main_simple.cpp
│   ├── main_working.cpp
│   ├── packet_parser.cpp
│   ├── pcap_reader.cpp
│   ├── rule_manager.cpp
│   ├── sni_extractor.cpp
│   └── types.cpp
├── tests/
│   └── integration_test.py
├── .github/workflows/ci.yml
├── CMakeLists.txt
├── WINDOWS_SETUP.md
├── generate_test_pcap.py
└── test_dpi.pcap
```

## Build Requirements

- C++17 compiler (GCC, Clang, or MSVC)
- CMake 3.16 or newer
- Python 3 (for the integration tests and PCAP generator)
- No third-party C++ libraries are required

### Build on Linux / macOS

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build --parallel
```

### Build on Windows

```powershell
cmake -S . -B build
cmake --build build --config Release
```

## Available Build Targets

| Target | Purpose |
|---|---|
| `dpi-engine` | Main multithreaded DPI pipeline |
| `dpi-modular` | Component-based multithreaded implementation |
| `dpi-simple` | Single-threaded implementation |
| `dpi-simple-demo` | Small DPI/SNI demonstration |
| `packet-analyzer` | Packet header inspection utility |
| `dpi-components` | Reusable modular components library |

## Run the Engine

Run the multithreaded engine against the bundled capture:

```bash
./build/dpi-engine test_dpi.pcap output.pcap
```

Block selected applications or domains:

```bash
./build/dpi-engine test_dpi.pcap output.pcap \
    --block-app YouTube \
    --block-domain facebook
```

Block a source IP and configure load-balancer / worker counts:

```bash
./build/dpi-engine test_dpi.pcap output.pcap \
    --block-ip 192.168.1.50 \
    --lbs 2 \
    --fps 2
```

Run the component-based implementation:

```bash
./build/dpi-modular test_dpi.pcap output-modular.pcap \
    --block-app YouTube \
    --lbs 2 \
    --fps 2
```

Run the single-threaded implementation:

```bash
./build/dpi-simple test_dpi.pcap output-simple.pcap --block-app YouTube
```

Inspect packet headers:

```bash
./build/packet-analyzer test_dpi.pcap 10
```

## Generate a Test Capture

The repository includes `test_dpi.pcap`. To generate a new synthetic capture:

```bash
python3 generate_test_pcap.py
```

## Run Tests

```bash
ctest --test-dir build --output-on-failure
```

The integration tests run the multithreaded and modular engines against the bundled PCAP, apply a YouTube blocking rule, and verify that the output capture is valid and contains fewer packets than the input.

## Learning Outcomes

This project brings together concepts from Computer Networks, C++ programming, protocol analysis, data structures, flow management, and concurrent programming. It provides a practical way to follow a packet through parsing, inspection, classification, rule evaluation, and forwarding or dropping.
