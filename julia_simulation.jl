module HawkDoveSim

using Random

const TYPE_DOVE = 0
const TYPE_HAWK = 1

function fight(types::AbstractVector{<:Integer}, default::Real, nodes::Integer,
    payoff_hh::Real, payoff_hd::Real, payoff_dh::Real, payoff_dd::Real, seed::Integer)
    rng = MersenneTwister(seed)
    total_pop = length(types)
    if nodes < total_pop
        nodes = total_pop
    end

    positions = fill(-1, nodes)
    @inbounds for i in 1:total_pop
        positions[i] = i
    end
    Random.shuffle!(rng, positions)
    usable = nodes - (nodes % 2)
    positions = positions[1:usable]
    pairs = reshape(positions, 2, :)'

    fitness = zeros(Float64, total_pop)
    @inbounds for i in 1:size(pairs, 1)
        a = pairs[i, 1]
        b = pairs[i, 2]
        a_present = a > 0
        b_present = b > 0

        if !a_present && b_present
            fitness[b] = default
        elseif a_present && !b_present
            fitness[a] = default
        elseif a_present && b_present
            ta = types[a]
            tb = types[b]
            if ta == TYPE_HAWK && tb == TYPE_HAWK
                fitness[a] = payoff_hh
                fitness[b] = payoff_hh
            elseif ta == TYPE_HAWK && tb == TYPE_DOVE
                fitness[a] = payoff_hd
                fitness[b] = payoff_dh
            elseif ta == TYPE_DOVE && tb == TYPE_HAWK
                fitness[a] = payoff_dh
                fitness[b] = payoff_hd
            else
                fitness[a] = payoff_dd
                fitness[b] = payoff_dd
            end
        end
    end

    return fitness
end

function food_search(types::AbstractVector{<:Integer}, fitness::AbstractVector{<:Real},
    mean_hawk::Real, shape_hawk::Real, mean_dove::Real, shape_dove::Real, seed::Integer)
    rng = MersenneTwister(seed)
    out = Array{Float64}(fitness)
    @inbounds for i in 1:length(types)
        if types[i] == TYPE_HAWK
            out[i] -= randn(rng) * shape_hawk + mean_hawk
        else
            out[i] -= randn(rng) * shape_dove + mean_dove
        end
    end
    return out
end

function selection2(types::AbstractVector{<:Integer}, ids::AbstractVector{<:Integer},
    fitness::AbstractVector{<:Real}, hawk_to_dove::Real, dove_to_hawk::Real,
    next_id::Integer, seed::Integer)
    rng = MersenneTwister(seed)
    count = length(types)
    keep = falses(count)
    extra_count = zeros(Int, count)

    @inbounds for i in 1:count
        fit = fitness[i]
        if fit > 1.0
            keep[i] = true
            residual = fit - 1.0
            extra = floor(Int, residual)
            if rand(rng) < (residual - extra)
                extra += 1
            end
            extra_count[i] = extra
        elseif fit == 1.0
            keep[i] = true
        else
            if rand(rng) < fit
                keep[i] = true
            end
        end
    end

    total_new = count(keep) + sum(extra_count)
    new_types = Array{Int8}(undef, total_new)
    new_ids = Array{Int64}(undef, total_new)
    pos = 1

    @inbounds for i in 1:count
        if keep[i]
            new_types[pos] = types[i]
            new_ids[pos] = ids[i]
            pos += 1
        end
        extra = extra_count[i]
        if extra > 0
            parent_type = types[i]
            for _ in 1:extra
                if parent_type == TYPE_HAWK
                    mutated = rand(rng) < hawk_to_dove
                    new_types[pos] = mutated ? TYPE_DOVE : TYPE_HAWK
                else
                    mutated = rand(rng) < dove_to_hawk
                    new_types[pos] = mutated ? TYPE_HAWK : TYPE_DOVE
                end
                new_ids[pos] = next_id
                next_id += 1
                pos += 1
            end
        end
    end

    return new_types, new_ids, next_id
end

function purge(types::AbstractVector{<:Integer}, ids::AbstractVector{<:Integer},
    max_pop::Integer, limit_random::Bool, limit_old::Bool, limit_young::Bool, seed::Integer)
    total = length(types)
    if total < max_pop
        return types, ids
    end
    target = max_pop - 1
    if limit_random
        rng = MersenneTwister(seed)
        order = randperm(rng, total)[1:target]
        return types[order], ids[order]
    elseif limit_old
        order = sortperm(ids)
        order = order[1:target]
        return types[order], ids[order]
    elseif limit_young
        order = sortperm(ids, rev=true)
        order = order[1:target]
        return types[order], ids[order]
    else
        error("ERROR : no method selected for purge")
    end
end

end
