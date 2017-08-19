<%!
import toolz.curried as toolz
import pyramda as R
from migen.fhdl import vhdl
from migen.fhdl.templates import filters
%>\
<%
merge_ctx = toolz.partial(toolz.merge, context.kwargs)
%>\
if ${vhdl._printexpr(node.cond, merge_ctx(dict(lhs=False, thint=vhdl._THint.boolean, lhint=None)))} then
${vhdl._printnode(node.t, merge_ctx(dict(thint=None, lhint=None))) | filters.indent(1)};
% if node.f:
else
${vhdl._printnode(node.f, merge_ctx(dict(thint=None, lhint=None))) | filters.indent(1)};
% endif
end if\
