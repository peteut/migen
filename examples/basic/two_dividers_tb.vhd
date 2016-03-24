library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ieee_proposed;
use ieee_proposed.env.all;
use ieee_proposed.std_logic_1164_additions.all;

entity top_tb is end entity;

architecture test of top_tb is

    signal d1_start_i: std_ulogic;
    signal d1_dividend_i: std_logic_vector(15 downto 0);
    signal d1_divisor_i: std_logic_vector(15 downto 0);
    signal d1_ready_o: std_ulogic;
    signal d1_quotient_o: std_logic_vector(15 downto 0);
    signal d1_remainder_o: std_logic_vector(15 downto 0);
    signal d2_start_i: std_ulogic;
    signal d2_dividend_i: std_logic_vector(15 downto 0);
    signal d2_divisor_i: std_logic_vector(15 downto 0);
    signal d2_ready_o: std_ulogic;
    signal d2_quotient_o: std_logic_vector(15 downto 0);
    signal d2_remainder_o: std_logic_vector(15 downto 0);
    signal ce: std_logic;
    signal reset: std_logic;
    signal sys_clk: std_logic := '0';
    signal sys_rst: std_logic := '1';

    constant clk_period: time := 10 ns;

begin
    uut: entity work.top
    port map (d1_start_i,
    d1_dividend_i,
    d1_divisor_i,
    d1_ready_o,
    d1_quotient_o,
    d1_remainder_o,
    d2_start_i,
    d2_dividend_i,
    d2_divisor_i,
    d2_ready_o,
    d2_quotient_o,
    d2_remainder_o,
    ce,
    reset,
    sys_clk,
    sys_rst);

    sys_clk <= not sys_clk after clk_period / 2;

    sys_rst <= '0' after 10 ns;

    verifier: process

        procedure test_divider (signal start: out std_logic;
                                signal dividend: out std_logic_vector;
                                signal divisor: out std_logic_vector;
                                signal ready: in std_logic;
                                signal quotient: in std_logic_vector;
                                signal remainder: in std_logic_vector;
                                s_dividend: in  natural;
                                s_divisor: in natural) is
        begin
            wait until rising_edge(sys_clk);
            ce <= '1';
            dividend <= std_logic_vector(to_unsigned(s_dividend, dividend'length));
            divisor <= std_logic_vector(to_unsigned(s_divisor, divisor'length));
            start <= '1';
            wait until rising_edge(sys_clk);
            start <= '0';
            wait until ready = '1';
            assert to_integer(unsigned(quotient)) = s_dividend / s_divisor and
            to_integer(unsigned(remainder)) = s_dividend mod s_divisor
            report
                "unexpected result: " & to_string(quotient) & ", expected " &
                integer'image(s_dividend / s_divisor) severity error;
            ce <= '0';
            wait until rising_edge(sys_clk);
        end procedure test_divider;

        variable dividend: natural;

    begin
        wait until rising_edge(sys_clk);
        sys_rst <= '0';
        reset <= '0';
        wait until rising_edge(sys_clk);

        dividend := 0;
        while dividend < 2 ** d1_dividend_i'left - 1 loop
            dividend := dividend + 7;
            test_divider(d1_start_i, d1_dividend_i, d1_divisor_i, d1_ready_o,
            d1_quotient_o, d1_remainder_o, dividend,
            (2 ** d1_divisor_i'left - 1) / 2);
        end loop;

        dividend := 0;
        while dividend < 2 ** d2_dividend_i'left - 1 loop
            dividend := dividend + 11;
            test_divider(d2_start_i, d2_dividend_i, d2_divisor_i, d2_ready_o,
            d2_quotient_o, d2_remainder_o, dividend,
            (2 ** d2_divisor_i'left - 1) / 2);
        end loop;

        report "OK, test done" severity note;
        finish(0);

    end process verifier;

end architecture test;
