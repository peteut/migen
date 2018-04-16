library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ieee_proposed;
use ieee_proposed.numeric_std_additions.all;
use ieee_proposed.std_logic_1164_additions.all;


entity ocram_sp is
  generic (
  ABITS, DBITS, WEGRANULARITY : positive;
  FILENAME : string := ""
);
port (
  clk : in std_logic;
  ce : in std_logic;
  we : in std_logic_vector(DBITS / WEGRANULARITY  downto 0);
  a : in std_logic_vector(ABITS-1 downto 0);
  d : in std_logic_vector(DBITS-1 downto 0);
  q : out std_logic_vector(DBITS-1 downto 0)
);
end entity ocram_sp;

architecture rtl of ocram_sp is
  subtype word_t is std_logic_vector(DBITS -1 downto 0);
  type ram_t is array(0 to 2**a'length - 1) of word_t;
  type reg_t is record
  a : std_logic_vector(ABITS-1 downto 0);
  ram : ram_t;
end record reg_t;

impure function init_mem (path : string) return ram_t is
variable index : natural := 0;
variable res : ram_t := (others => (others => '0'));
type init_file_t is file of word_t;
file init_file : init_file_t open read_mode is FILENAME;
begin
  if path'length > 0 then
    while not endfile(path) loop
      read(init_file, res(index));
      index := index + 1;
    end loop;
    return res;
  end if;
end function init_mem;

signal r : reg_t := (a => (others => '0'),
ram => init_mem(FILENAME));
signal rin : reg_t;

begin
  comb : process (r, a, ce, we)
    variable v : reg_t;
  begin
    -- defaults
    v := r;
    -- comb statements
    v.a := a;
    -- sync statements
    if \??\(ce) then
      gen_write_access : for i in DBITS / WEGRANULARITY generate
        if \??\(we(i)) then
          v.ram(to_integer(unsigned(a)))(
          WEGRANULARITY * (i + 1) - 1 downto WEGRANULARITY * i) := d(
          WEGRANULARITY * (i + 1) - 1 downto WEGRANULARITY * i);
        end if;
      end generate;
    end if;
    -- drive register input
    rin <= v;
    -- drive outputs
    q <= r.ram(to_integer(unsigned(r.a)));
  end process;

  seq: process (clk)
  begin
    if rising_edge(clk) then
      r <= rin;
    end if;
  end process;

end architecture ocram_sp;
