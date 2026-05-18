---
name: ExampleDriver
short_description: Template for a Lua hardware driver that reads from a serial port.
vehicle: [copter, plane, rover]
min_firmware: "4.5"
version: "1.0.0"
date: 2026-05-18
---

## Description

ExampleDriver is a template for writing hardware drivers in Lua. It opens the
first scripting serial port (`SERIALx_PROTOCOL = 28`), reads available bytes,
and forwards a byte-count summary to the GCS every 100 ms.

Use this as a starting point when implementing a driver for a new peripheral.

## Setup

1. Set one of your serial ports to `SERIALx_PROTOCOL = 28` (Scripting).
2. Set `SERIALx_BAUD` to match your device (default 115200).
3. Copy `ExampleDriver.lua` to `APM/scripts/` on your SD card.
4. Reboot. The script will log received byte counts to the Messages tab.

## Parameters

| Parameter | Description |
| --------- | ----------- |
| `BAUD_RATE` | Serial baud rate (hardcoded in script, default 115200). |
