-- ExampleDriver: template for a Lua hardware driver.
-- Demonstrates reading a serial port and forwarding data to the GCS.

local SCRIPT_NAME = "ExampleDriver"
local UPDATE_INTERVAL_MS = 100
local BAUD_RATE = 115200

local port = serial:find_serial(0)

local function update()
    if not port then
        gcs:send_text(3, SCRIPT_NAME .. ": serial port not found")
        return update, 5000
    end

    local n = port:available():toint()
    if n > 0 then
        local data = port:readstring(n)
        if data then
            gcs:send_text(6, SCRIPT_NAME .. ": received " .. #data .. " bytes")
        end
    end

    return update, UPDATE_INTERVAL_MS
end

if port then
    port:begin(BAUD_RATE)
end

return update, UPDATE_INTERVAL_MS
