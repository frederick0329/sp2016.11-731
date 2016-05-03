require 'io'
require 'nn'
require 'cunn'
require 'cutorch'

getData = {}

local function tablesize(t)
    local count = 0
    for key, value in pairs(t) do
        count = count + 1
    end
    return count
end

local function copy(original)
    local copy = {}
    for key, value in pairs(original) do
        copy[key] = value
    end
    return copy
end


function getData.read(split, src, rho)
    local sent_path = '/media/iyu/caremedia4/poyaoh/HW4/data/' .. split .. '.' .. src
    local wtoi_path = '/media/iyu/caremedia4/poyaoh/HW4/vocab/' .. src .. '2idx.json' 
    local itow_path = '/media/iyu/caremedia4/poyaoh/HW4/vocab/idx2' .. src .. '.json' 
   
    print(wtoi_path)
    --setting up json
    local cjson = require "cjson"
    local cjson2 = cjson.new()
    local cjson_safe = require "cjson.safe"
    
    local f = io.open(sent_path, "r")
    local corpus = f:read("*all")
    f:close()

    local f = io.open(wtoi_path, "r")
    local wtoi_text = f:read("*all")
    f:close()

    local f = io.open(itow_path, "r")
    local itow_text = f:read("*all")
    f:close()

    local wtoi = cjson.decode(wtoi_text)
    local itow = cjson.decode(itow_text)
    
    local sents = {}
    for s in corpus:gmatch("[^\n]+") do
        local sent = {}
        for w in s:gmatch("[^%s$]+")  do
            if wtoi[w] == nil then
                table.insert(sent, wtoi['<unk>'])
            else    
                table.insert(sent, wtoi[w])
            end
            if #sent >= rho then
                break
            end
        end

        --padding
        for i = #sent+1, rho do
            if src == 'tgt' then
                table.insert(sent, 0)
            else
                table.insert(sent, 1 ,0)
            end
        end
        table.insert(sents, sent)
    end
    sents = torch.DoubleTensor(sents)


    return sents
end

return getData

