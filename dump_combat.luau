-- Dump CombatConfig from the live game (real style stats)
local RS = game:GetService("ReplicatedStorage")
local mod = RS:WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("CombatConfig")
local ok, data = pcall(function() return require(mod) end)
if not ok then return "REQUIRE_ERR: " .. tostring(data) end

local seen = {}
local function ser(v, depth)
  depth = depth or 0
  if depth > 12 then return "..." end
  local t = typeof(v)
  if t == "function" then
    local n = debug and debug.info and (pcall(function() return debug.info(v,"n") end))
    return "FN"
  end
  if t == "table" then
    if seen[v] then return "<<cycle>>" end
    seen[v] = true
    local out = {}
    local arr = true; local n = 0
    for k,_ in pairs(v) do n=n+1; if type(k)~="number" then arr=false end end
    if arr and n>0 then
      local i=1
      for _,val in pairs(v) do out[i]=ser(val,depth+1); i=i+1 end
    else
      for k,val in pairs(v) do out[tostring(k)]=ser(val,depth+1) end
    end
    seen[v]=nil
    return out
  elseif t == "Color3" then
    return string.format("Color3(%d,%d,%d)", math.floor(v.R*255+0.5), math.floor(v.G*255+0.5), math.floor(v.B*255+0.5))
  elseif t == "EnumItem" then return tostring(v)
  elseif t == "Instance" then return "Inst:"..v.ClassName..":"..v.Name
  elseif t == "number" or t == "string" or t == "boolean" then return v
  else return tostring(v) end
end

return game:GetService("HttpService"):JSONEncode(ser(data))
