---
name: BatteryMonitor
short_description: Logs battery voltage and current to GCS, warns on low cell voltage.
vehicle: [copter, plane, rover]
min_firmware: "4.5"
version: "1.0.0"
date: 2026-05-18
status: "broken"
---

# BatteryMonitor

## Description

BatteryMonitor periodically reads the primary battery instance and sends
voltage, per-cell voltage, and current draw to the GCS. It sends an
additional warning message when the per-cell voltage drops below a
configurable threshold.

## Setup

1. Copy `BatteryMonitor.lua` to `APM/scripts/` on your SD card.
2. Ensure a battery monitor is configured (`BATTx_MONITOR` ≠ 0).
3. Adjust the `WARN_VOLTAGE` and `CELL_COUNT` constants at the top of the
   script to match your battery pack.

## Parameters

| Constant | Default | Description |
| -------- | ------- | ----------- |
| `UPDATE_INTERVAL_MS` | 10000 | How often to report (ms). |
| `WARN_VOLTAGE` | 3.5 | Warning threshold in volts per cell. |
| `CELL_COUNT` | 4 | Number of cells in series. |
