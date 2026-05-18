-- BatteryMonitor: logs battery voltage and current to the GCS at a configurable interval.
-- Sends a warning when voltage drops below a threshold.

local SCRIPT_NAME = "BatteryMonitor"
local UPDATE_INTERVAL_MS = 10000
local WARN_VOLTAGE = 3.5   -- volts per cell
local CELL_COUNT = 4

local function update()
    local instance = 0

    if not battery:healthy(instance) then
        gcs:send_text(4, SCRIPT_NAME .. ": battery instance " .. instance .. " not healthy")
        return update, UPDATE_INTERVAL_MS
    end

    local voltage = battery:voltage(instance)
    local current = battery:current_amps(instance)

    if voltage then
        local cell_voltage = voltage / CELL_COUNT
        local msg = string.format("%s: %.2fV (%.2fV/cell)", SCRIPT_NAME, voltage, cell_voltage)
        if current then
            msg = msg .. string.format("  %.1fA", current)
        end
        gcs:send_text(6, msg)

        if cell_voltage < WARN_VOLTAGE then
            gcs:send_text(4, SCRIPT_NAME .. ": WARNING low cell voltage " .. string.format("%.2fV", cell_voltage))
        end
    end

    return update, UPDATE_INTERVAL_MS
end

return update, UPDATE_INTERVAL_MS
