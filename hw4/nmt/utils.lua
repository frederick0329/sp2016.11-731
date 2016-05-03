require 'nn'
require 'rnn'
require 'getData'
require 'optim'
require 'cutorch'
require 'cunn'
require 'PrintIdentity'
require 'FastLSTM_padding'

Utils = {}

function Utils.getNextBatch(ds, n, inputs)
    local src_words, tgt_words = torch.CudaTensor(), torch.CudaTensor()
    
    local start_idx = (n-1) * batchSize+1
    local end_idx = n * batchSize
    if end_idx > ds.size then
	end_idx = ds.size
    end

    -- inputs{src_words, tgt_words}  
    src_words:index(ds.src, 1, ds.indices:sub(start_idx, end_idx))
    table.insert(inputs, src_words)
    tgt_words:index(ds.tgt, 1, ds.indices:sub(start_idx, end_idx))
    table.insert(inputs, tgt_words)
end

function Utils.loadData(split, isShuffle)
    local ds = {}
    
    local src = getData.read(split, 'src', rho)
    ds.src = src:cuda()
    if split ~= 'test' then
        local tgt = getData.read(split, 'tgt', rho)
        ds.tgt = tgt:cuda() 
    end
    
    ds.size = src:size(1)

    local indices = torch.LongTensor(ds.size)
	
    if isShuffle then
	indices:randperm(ds.size)
    else
        for i = 1,indices:size(1) do
	    indices[i] = i 
        end
    end	

    ds.indices = indices:cuda()
    return ds
end


return Utils
