#!/usr/bin/env python3
"""Run a DPI engine against the bundled PCAP and verify filtering output."""

from __future__ import annotations

import pathlib
import struct
import subprocess
import sys


def count_pcap_packets(path: pathlib.Path) -> int:
    data = path.read_bytes()
    if len(data) < 24:
        raise RuntimeError(f"{path} is too small to be a PCAP file")

    magic = data[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    else:
        raise RuntimeError(f"{path} has an unsupported PCAP magic number")

    offset = 24
    packets = 0
    while offset < len(data):
        if offset + 16 > len(data):
            raise RuntimeError(f"{path} has a truncated packet header")
        _, _, captured_length, _ = struct.unpack_from(endian + "IIII", data, offset)
        offset += 16
        if offset + captured_length > len(data):
            raise RuntimeError(f"{path} has a truncated packet payload")
        offset += captured_length
        packets += 1
    return packets


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: integration_test.py ENGINE SOURCE_DIR OUTPUT_PCAP", file=sys.stderr)
        return 2

    engine = pathlib.Path(sys.argv[1]).resolve()
    source_dir = pathlib.Path(sys.argv[2]).resolve()
    output_path = pathlib.Path(sys.argv[3]).resolve()
    input_path = source_dir / "test_dpi.pcap"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not engine.is_file():
        raise RuntimeError(f"Engine executable not found: {engine}")
    if not input_path.is_file():
        raise RuntimeError(f"Test capture not found: {input_path}")

    result = subprocess.run(
        [str(engine), str(input_path), str(output_path), "--block-app", "YouTube", "--lbs", "2", "--fps", "2"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Engine exited with status {result.returncode}")
    if not output_path.is_file():
        raise RuntimeError("Engine did not create an output PCAP")

    input_count = count_pcap_packets(input_path)
    output_count = count_pcap_packets(output_path)
    if output_count >= input_count:
        raise RuntimeError(
            f"Expected blocking to remove at least one packet; input={input_count}, output={output_count}"
        )

    print(f"Integration test passed: {input_count} input packets, {output_count} forwarded packets")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Integration test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
