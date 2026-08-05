-- Call the CombatStyleRarityConfig functions to extract real data
local RS = game:GetService("ReplicatedStorage")
local mod = RS:WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("CombatStyleRarityConfig")
local cfg = require(mod)

local seen = {}
local function ser(v, depth)
  depth = depth or 0
  if depth > 10 then return "..." end
  local t = typeof(v)
  if t == "function" then return "FN" end
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

local result = {}
local ok, rar = pcall(function() return cfg:GetRarities() end)
result.GetRarities_ok = ok
result.GetRarities = ok and ser(rar) or tostring(rar)

local ok2, rs = pcall(function() return cfg:GetRollableStyles() end)
result.GetRollableStyles_ok = ok2
result.GetRollableStyles = ok2 and ser(rs) or tostring(rs)

-- try per-style rarity + color
local styles = ok2 and rs or {}
local perStyle = {}
for _, s in pairs(styles) do
  local r1 = pcall(function() return cfg:GetRarityForStyle(s) end)
  local _, rv = pcall(function() return cfg:GetRarityForStyle(s) end)
  local c1 = pcall(function() return cfg:GetColorForStyle(s) end)
  local _, cv = pcall(function() return cfg:GetColorForStyle(s) end)
  perStyle[tostring(s)] = { rarity = (type(rv)=="table" and ser(rv)) or tostring(rv), color = (type(cv)=="string" and cv) or tostring(cv) }
end
result.perStyle = perStyle

return game:GetService("HttpService"):JSONEncode(result)
