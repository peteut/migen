import toolz.curried as toolz
import pyramda as R

get_sigtype = R.if_else(
    toolz.comp(R.equals(1), len),
    R.always("std_ulogic"),
    toolz.comp("std_logic_vector({} downto 0)".format, R.dec, len))
