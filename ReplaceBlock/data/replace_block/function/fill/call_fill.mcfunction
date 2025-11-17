$data modify storage replace_block:data temp.fill_chunk merge from storage replace_block:data settings.replace_pairs[$(replace_pairs)]
$data modify storage replace_block:data temp.fill_chunk merge from storage replace_block:data settings.dimensions[$(dimensions)]
function replace_block:fill/command with storage replace_block:data temp.fill_chunk
