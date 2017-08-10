### Migen (Milkymist generator)

[![Build Status](https://travis-ci.org/peteut/migen.svg)](
https://travis-ci.org/peteut/migen)
[![Coverage Status](https://coveralls.io/repos/peteut/migen/badge.svg)](
https://coveralls.io/r/peteut/migen)

#### A Python toolbox for building complex digital hardware

Despite being faster than schematics entry, hardware design with Verilog and
VHDL remains tedious and inefficient for several reasons. The event-driven
model introduces issues and manual coding that are unnecessary for synchronous
circuits, which represent the lion's share of today's logic designs. Counter-
intuitive arithmetic rules result in steeper learning curves and provide a
fertile ground for subtle bugs in designs. Finally, support for procedural
generation of logic (metaprogramming) through "generate" statements is very
limited and restricts the ways code can be made generic, reused and organized.

To address those issues, we have developed the **Migen FHDL** library that
replaces the event-driven paradigm with the notions of combinatorial and
synchronous statements, has arithmetic rules that make integers always behave
like mathematical integers, and most importantly allows the design's logic to
be constructed by a Python program. This last point enables hardware designers
to take advantage of the richness of the Python language - object oriented
programming, function parameters, generators, operator overloading, libraries,
etc. - to build well organized, reusable and elegant designs.

Other Migen libraries are built on FHDL and provide various tools such as a
system-on-chip interconnect infrastructure, a dataflow programming system, a
more traditional high-level synthesizer that compiles Python routines into
state machines with datapaths, and a simulator that allows test benches to be
written in Python.

See the doc/ folder for more technical information.

Migen is designed for Python 3.5. Note that Migen is **not** spelled MiGen.

#### Quick Links

Code repository:
https://github.com/m-labs/migen

System-on-chip design based on Migen:
https://github.com/m-labs/misoc

Online documentation:
https://m-labs.hk/gateware.html

#### Quick intro

```python
from migen import *
from migen.build.platforms import m1

plat = m1.Platform()
led = plat.request("user_led")
m = Module()
counter = Signal(26)
m.comb += led.eq(counter[25])
m.sync += counter.eq(counter + 1)
plat.build(m)
```

The module can be exported as HDL like this:

```python
from migen import *
from migen.fhdl import vhdl

def get_readme_module():
    m = Module()
    led = Signal()
    counter = Signal(26)
    m.comb += led.eq(counter[25])
    m.sync += counter.eq(counter + 1)
    return m, ios

example = get_readme_module()
vhdl.convert(example, ios).write("module.vhd")
```

yields:

```vhdl
-- Machine generated using Migen - experimental VHDL backend
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ieee_proposed;
use ieee_proposed.numeric_std_additions.all;
use ieee_proposed.std_logic_1164_additions.all;

entity top is
port (led: out std_ulogic;
      sys_clk: in std_ulogic;
      sys_rst: in std_ulogic);
end entity top;

architecture two_process_top of top is

type sys_reg_t is record
    counter: std_logic_vector(25 downto 0);
end record sys_reg_t;

signal sys_rin: sys_reg_t; -- register input for cd "sys"
signal sys_r: sys_reg_t; -- register for cd "sys"

begin

comb: process (sys_rst, sys_r) is
-- cd variables
variable sys_v: sys_reg_t;  -- variable for cd "sys"
-- buffer variables
variable led_v: std_ulogic;

begin
-- defaults
    sys_v := sys_r;
-- comb statements
    led_v := sys_r.counter(25);
-- sync statements
    sys_v.counter := std_logic_vector(unsigned(sys_r.counter) + 1);
    if \??\(sys_rst) then
        sys_v.counter := (others => '0');
    end if;
-- drive register input
    sys_rin <= sys_v;
-- drive outputs
    led <= led_v;
end process comb;

sys_seq: process (sys_clk)
begin
    if rising_edge(sys_clk) then
        sys_r <= sys_rin;
    end if;
end process;

end architecture two_process_top;
```


#### License

Migen is released under the very permissive two-clause BSD license. Under the
terms of this license, you are authorized to use Migen for closed-source
proprietary designs.
Even though we do not require you to do so, those things are awesome, so please
do them if possible:
* tell us that you are using Migen
* put the Migen logo (doc/migen_logo.svg) on the page of a product using it,
  with a link to http://m-labs.hk
* cite Migen in publications related to research it has helped
* send us feedback and suggestions for improvements
* send us bug reports when something goes wrong
* send us the modifications and improvements you have done to Migen. The use
   of "git format-patch" is recommended. If your submission is large and
   complex and/or you are not sure how to proceed, feel free to discuss it on
   the mailing list or IRC (#m-labs on Freenode) beforehand.

See LICENSE file for full copyright and license info. You can contact us on the
public mailing list devel [AT] lists.m-labs.hk.

  "Electricity! It's like magic!"
