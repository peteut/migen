<%!
import operator
import toolz.curried as toolz
import pyramda as R
from migen.fhdl import vhdl
from migen.fhdl.templates import filters
from migen.fhdl.templates import helper
%>\
<%
merge_ctx = toolz.partial(toolz.merge, context.kwargs)
get_name = ns.get_name
%>\
architecture ${name | filters.architecture_id} of ${name} is
% for cd, sigs in cd_regs:
type ${cd | filters.reg_typename} is record
% for sig in sigs:
${get_name(sig) | filters.indent(1)}: ${helper.get_sigtype(sig)};
% endfor
end record ${cd | filters.reg_typename};
signal ${cd | filters.rin_name}: ${cd | filters.reg_typename}; -- register input for cd "${cd}"
signal ${cd | filters.r_name}: ${cd | filters.reg_typename}; -- register for cd "${cd}"
% endfor
% for w in wires:
% if loop.first:
-- wires
% endif
signal ${get_name(w)}: ${helper.get_sigtype(w)};
% endfor
begin
% if not len(sensitivity_list):
comb: process
% else:
comb: process (${", ".join(sensitivity_list)}) is
% endif
% for cd in toolz.map(toolz.first, cd_regs):
% if loop.first:
-- cd variables
% endif
variable ${cd | filters.v_name}: ${cd | filters.reg_typename};  -- variable for cd "${cd}"
% endfor
% for v in variables:
% if loop.first:
-- variables
% endif
variable ${get_name(v)}: ${helper.get_sigtype(v)};
% endfor
% for v in buffer_variables:
% if loop.first:
-- buffer variables
% endif
variable ${get_name(v) | filters.v_name}: ${helper.get_sigtype(v)};
% endfor
begin
% for cd in toolz.map(toolz.first, cd_regs):
% if loop.first:
-- defaults
% endif
${cd | filters.v_name,filters.indent(1)} := ${cd | filters.r_name};
% endfor
% for statement in comb_statements:
% if loop.first:
-- comb statements
% endif
${vhdl._printnode(statement, merge_ctx(dict(at=vhdl._AT_BLOCKING, thint=None, lhint=None))) | filters.indent(1)};
% endfor
% for statement in toolz.map(toolz.second, sync_statements):
% if loop.first:
-- sync statements
% endif
${vhdl._printnode(statement, merge_ctx(dict(at=vhdl._AT_BLOCKING, thint=None, lhint=None))) | filters.indent(1)};
% endfor
% for cd in toolz.map(toolz.first, cd_regs):
% if loop.first:
-- drive register input
% endif
${cd | filters.rin_name,filters.indent(1)} <= ${cd | filters.v_name};
% endfor
% for v in buffer_variables:
% if loop.first:
-- drive outputs
% endif
${get_name(v) | filters.indent(1)} <= ${get_name(v) | filters.v_name};
% endfor
% for cd_name, cd_sig in cd_regs:
% for sig in toolz.pipe(cd_sig, toolz.filter(vhdl.contains(ios))):
% if loop.first:
-- drive "${cd_name}" regs
% endif
${get_name(sig) | filters.indent(1)} <= ${cd_name | filters.v_name}.${get_name(sig)};
% endfor
% endfor
end process comb;

% for cd in toolz.pipe(cds, toolz.filter(toolz.comp(vhdl.contains(toolz.map(toolz.first, cd_regs)), operator.attrgetter("name")))):
${cd.name}_seq: process (${get_name(cd.clk)})
begin
${"" | filters.indent(1)}if rising_edge(${get_name(cd.clk)}) then
${cd.name | filters.r_name,filters.indent(2)} <= ${cd.name | filters.rin_name};
${"" | filters.indent(1)}end if;
end process;
% endfor
% for special in specials:
% if loop.first:

-- specials
% endif
${str(special)}
% endfor
end architecture ${name | filters.architecture_id};\
