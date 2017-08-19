<%!
import operator
from migen.fhdl import vhdl
import toolz.curried as toolz
import pyramda as R
from migen.fhdl.structure import Constant
%>\
<%
css = toolz.pipe(node.cases.items(), toolz.filter(toolz.comp(R.isinstance(Constant), toolz.first)), tuple, toolz.partial(sorted, key=toolz.comp(operator.attrgetter("value"), toolz.first)))
default = toolz.get("default", node.cases, None)
merge_ctx = toolz.partial(toolz.merge, context.kwargs)
%>\
case ${vhdl._printexpr(node.test, merge_ctx(dict(lhs=False, thint=vhdl._THint.integer, lhint=False)))} is
% for case in css:
when ${vhdl._printexpr(case[0], merge_ctx(dict(lhs=False, thint=vhdl._THint.integer, lhint=None)))} =>
${vhdl._printnode(case[1], merge_ctx(dict(thint=None, lhint=None)))};
% endfor
when others =>
% if default:
${vhdl._printnode(default, merge_ctx(dict(thint=None, lhint=None)))};
% else:
null;
% endif
end case\
