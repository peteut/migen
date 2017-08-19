import operator
import toolz.curried as toolz
import pyramda as R

reg_typename = "{}_reg_t".format

rin_name = "{}_rin".format

r_name = "{}_r".format

v_name = "{}_v".format

architecture_id = "two_process_{}".format

indent = R.curry_n(
    2,
    toolz.comp(
        "\n".join,
        R.apply(map),
        R.unapply(toolz.juxt([
            toolz.comp(R.add, R.multiply("    "), toolz.first),
            toolz.comp(operator.methodcaller("split", "\n"), toolz.second)]))))
