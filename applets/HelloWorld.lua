-- HelloWorld: sends a periodic greeting message to the GCS.
-- This is the minimal example applet showing the required script structure.

local SCRIPT_NAME = "HelloWorld"
local UPDATE_INTERVAL_MS = 5000

local function update()
    gcs:send_text(6, SCRIPT_NAME .. ": Hello from ArduPilot Lua!")
    return update, UPDATE_INTERVAL_MS
end

return update, UPDATE_INTERVAL_MS
