-- .luacheckrc - luacheck configuration for ArduPilot Lua community scripts
--
-- ArduPilot globals are loaded dynamically from .checks/docs.lua so that
-- luacheck knows about ahrs, gps, battery, vehicle, etc. without false
-- "undefined global" warnings.

-- Suppress warnings that are expected or handled elsewhere:
--   111 - setting an undefined global (handled via stds below)
--   113 - accessing an undefined global (handled via stds below)
--   212/_* - unused argument only when name starts with _
--   611/612/614 - whitespace style (handled by StyLua)
--   631 - line too long (handled by StyLua column_width)
ignore = { "111", "113", "212/_.*", "611", "612", "614", "631" }

-- Dynamically register all ArduPilot bindings from the vendored docs.lua
stds.ArduPilot = {}
stds.ArduPilot.read_globals = {}

local env = setmetatable({}, { __index = _G })
local docs_path = ".checks/docs.lua"
local loader = loadfile(docs_path, "t", env)
if loader then
    pcall(loader)
end

for key, value in pairs(env) do
    local entry = { other_fields = false }
    if type(value) == "table" then
        entry.fields = {}
        for field_key, _ in pairs(value) do
            entry.fields[field_key] = { other_fields = false }
        end
    end
    stds.ArduPilot.read_globals[key] = entry
end

-- Add enum values that are only known at compile time and are not in docs.lua
local function add_enum(singleton, enum)
    if stds.ArduPilot.read_globals[singleton] then
        stds.ArduPilot.read_globals[singleton].fields =
            stds.ArduPilot.read_globals[singleton].fields or {}
        stds.ArduPilot.read_globals[singleton].fields[enum] = { other_fields = false }
    end
end

add_enum("mission", "MISSION_COMPLETE")
add_enum("mission", "MISSION_RUNNING")
add_enum("mission", "MISSION_STOPPED")
add_enum("terrain", "TerrainStatusOK")
add_enum("terrain", "TerrainStatusUnhealthy")
add_enum("terrain", "TerrainStatusDisabled")
add_enum("gps", "GPS_OK_FIX_2D")
add_enum("gps", "GPS_OK_FIX_3D")
add_enum("gps", "GPS_OK_FIX_3D_DGPS")
add_enum("gps", "GPS_OK_FIX_3D_RTK_FLOAT")
add_enum("gps", "GPS_OK_FIX_3D_RTK_FIXED")
add_enum("gps", "NO_GPS")
add_enum("gps", "NO_FIX")

std = "lua53+ArduPilot"

-- Only check files in the script directories
files["applets/*.lua"] = {}
files["drivers/*.lua"] = {}
files["tools/*.lua"] = {}
