---
name: HelloWorld
short_description: Sends a periodic greeting message to the GCS every 5 seconds.
vehicle: [copter, plane, rover]
min_firmware: "4.5"
version: "1.0.0"
date: 2026-05-18
---

## Description

HelloWorld is the minimal example applet for this repository. It sends a
friendly message to the Ground Control Station every 5 seconds.

Use this as a starting point when writing a new applet.

## Setup

1. Copy `HelloWorld.lua` to the `APM/scripts/` folder on your autopilot SD card
   (or use MAVFTP from Mission Planner).
2. Set `SCR_ENABLE = 1` and reboot if scripting is not already enabled.
3. Open the Messages tab in your GCS — you should see the greeting every 5 s.

## Parameters

None.
