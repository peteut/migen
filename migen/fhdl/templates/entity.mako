<%!
from migen.fhdl.templates import filters
from migen.fhdl.templates import helper
%>\
<%def name="direction(sig)">${"inout" if sig in inouts else "out" if sig in targets else "in"}</%def>\
-- Machine generated using Migen - experimental VHDL backend
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ieee_proposed;
use ieee_proposed.numeric_std_additions.all;
use ieee_proposed.std_logic_1164_additions.all;

entity ${name} is
% for sig in ios:
% if loop.first:
port(
% endif
${ns.get_name(sig) | filters.indent(1)}: ${direction(sig)} ${helper.get_sigtype(sig)}${");" if loop.last else ";"}
% endfor
end entity ${name};
