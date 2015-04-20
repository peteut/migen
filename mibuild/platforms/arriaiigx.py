# Arria II GX FPGA Developement Board
# Refer to  Arria II GX FPGA Developement Board Reference Manual
from mibuild.generic_platform import (Pins, Subsignal, Misc)
from mibuild.altera import (AlteraPlatform, IOSTD)
import collections


# Table2-7
_epm2210 = [
    # EPM2210
    ("clk_enable", 0, Pins("K14")),
    ("clk_sel", Pins("P2")),
    # Programmable oscillator 1
    ("clk1",
     0,
     Subsignal("ce", Pins("N3")),
     # Output divider
     Subsignal("od", Pins("M2 M1 M3")),
     # Output select
     Subsignal("os", Pins("N1 N2")),
     # Prescaler
     Subsignal("pr", Pins("L2 L1")),
     Subsignal("rstn", Pins("M3"))),
    ("clk100_cp1d", 0, Pins("H12")),
    ("clk155_oe", 0, Pins("E1")),
    # Programmable oscillator 2
    ("clk2",
     0,
     Subsignal("ce", Pins("M14")),
     # Output divider
     Subsignal("od", Pins("N16 N14 N13")),
     # Output select
     Subsignal("os", Pins("M15 M16")),
     # Prescaler
     Subsignal("pr", Pins("P15 P14")),
     Subsignal("rstn", Pins("N15"))),
    # Power monitor
    ("csense",
     0,
     Subsignal("adc_f0", Pins("G16")),
     Subsignal("csn", Pins("J14 H15")),
     Subsignal("sck", Pins("H16")),
     Subsignal("sdi", Pins("H14")),
     Subsignal("sdo", Pins("H13"))),
    # DDR3 SODIMM EEPROM
    ("ddr2",
     0,
     Subsignal("scl", Pins("M7")),
     Subsignal("sda", Pins("M6"))),
    # EEPROM
    ("ep",
     0,
     Subsignal("clk", Pins("J15")),
     Subsignal("cs", Pins("J16")),
     Subsignal("di", Pins("K15")),
     Subsignal("do", Pins("K16"))),
    ("factory_user", 0, Pins("L13")),
    # FSM bus flash memory
    ("flash",
     0,
     Subsignal("advn", Pins("C8")),
     Subsignal("cen", Pins("F15")),
     Subsignal("clk", Pins("C9")),
     Subsignal("oen", Pins("E7")),
     Subsignal("rdy_bsyn", Pins("D8")),
     Subsignal("resetn", Pins("D15")),
     Subsignal("wen", Pins("D7"))),
    # FPGA configuration
    ("fpga",
     0,
     Subsignal("conf_done", Pins("J1")),
     Subsignal("config_d", Pins("B1 A4 A7 B4 B5 A6 A5 B6")),
     Subsignal("dclk", Pins("H4")),
     Subsignal("nconfig", Pins("J2")),
     Subsignal("nstatus", Pins("H3"))),
    # FSM bus
    ("fsm",
     0,
     Subsignal(
         "a",
         Pins("A2 D9 E10 E4 E5 E14 G15 E15 F16 E16 B16 "
              "C15 D16 D10 A15 C11 A12 B12 C12 B13 A13 "
              "B14 D11 E9 D6 C13")),
     Subsignal(
         "d",
         Pins("E11 E12 D12 C14 E8 D4 C6 D5 E6 D14 E13 "
              "D13 C5 C4 C7 C10 C2 D3 E3 D2 E2 D1 F1 "
              "F3 G2 F2 G3 G1 H1 G4 J4 H2"))),
    ("hsma_psnt_n", 0, Pins("A10")),
    ("hsmb_psnt_n", 0, Pins("J13")),
    ("led", 0, Subsignal("config_led", Pins("B8 A8 B7"))),
    ("factory", 0, Pins("B9")),
    ("lcd_pwrmon", 0, Pins("K13")),
    ("reset_confign", 0, Pins("A9")),
    ("max",
     0,
     Subsignal("dip", Pins("L16 L15 L14")),
     # FPGA configuration error LED
     Subsignal("error", Pins("B10")),
     Subsignal("led", Pins("B11")),
     # FPGA configuration active LED
     Subsignal("load", Pins("A11")),
     Subsignal("resetn", Pins("M9"))),
    ("max2",
     0,
     Subsignal("ben", Pins("M11 M10 N12 P12")),
     Subsignal("clk", Pins("N10")),
     Subsignal("csn", Pins("M12")),
     Subsignal("oen", Pins("M8")),
     Subsignal("wen", Pins("N11"))),
    ("sram",
     0,
     Subsignal("mode", Pins("J3")),
     Subsignal("zz", Pins("B3"))),
    ("usb",
     0,
     Subsignal("disablen", Pins("K2")),
     Subsignal("led", Pins("K1"))),
]

_EP2AGX125 = [
    # Table 2-46
    ("flash",
     0,
     Subsignal("advn", Pins("T4")),
     Subsignal("cen", Pins("M3")),
     Subsignal("clk", Pins("N4")),
     Subsignal("oen", Pins("K5")),
     Subsignal("rdy_bsyn", Pins("R3")),
     Subsignal("resetn", Pins("N3")),
     Subsignal("wen", Pins("C7"))),
    # Table 2-7
    ("fpga",
     0,
     Subsignal("conf_done", Pins("AE25")),
     Subsignal("config_d", Pins("N26 N6 G2 P6 L4 K3 M4 K2")),
     Subsignal("dclk", Pins("L25")),
     Subsignal("nconfig", Pins("AC26")),
     Subsignal("nstatus", Pins("AC28"))),
    ("fsm",
     0,
     Subsignal(
         "a",
         Pins("M21 J3 D29 J21 L13 C8 N9 D20 A23 B24 C24 E25 "
              "F21 J19 H19 K21 L21 F25 F26 G23 H21 M13 P7 F10 "
              "R4 K4")),
     Subsignal(
         "d",
         Pins("A19 C18 D28 B19 E19 E18 G19 F19 D21 D23 D24 A25 B26 "
              "C26 A27 R9 R10 R8 A17 D22 T10 P4 R11 A18 B18 C19 D19 "
              "B21 A21 C21 A22"))),
    ("max2",
     0,
     Subsignal("ben", Pins("C15 H16 D14 D14 A9")),
     Subsignal("clk", Pins("J14")),
     Subsignal("csn", Pins("A16")),
     Subsignal("oen", Pins("A14")),
     Subsignal("wen", Pins("B16"))),
    ("sram",
     0,
     Subsignal("zz", Pins("B27"))),
    # Table 2-20
    ("clk155",
     0,
     Subsignal("p", Pins("R29")),
     Subsignal("n", Pins("R30")),
     IOSTD.LVPECL),
    ("clkin_bot",
     0,
     Subsignal("p", Pins("AJ19")),
     Subsignal("n", Pins("AK19")),
     IOSTD.LVDS),
    ("clkin_ref_q2",
     0,
     Subsignal("p", Pins("U29")),
     Subsignal("n", Pins("U30")),
     IOSTD.LVDS),
    ("clkin_top",
     0,
     Subsignal("p", Pins("F18")),
     Subsignal("n", Pins("F17")),
     IOSTD.LVDS),
    ("clk_ref_q1",
     0,
     Subsignal("p", Pins("AA29")),
     Subsignal("n", Pins("AA30")),
     IOSTD.LVDS),
    ("clk_ref_q1",
     1,
     Subsignal("p", Pins("W29")),
     Subsignal("n", Pins("W30")),
     IOSTD.LVDS),
    ("clk_ref_q3",
     0,
     Subsignal("p", Pins("N29")),
     Subsignal("n", Pins("N30")),
     IOSTD.LVDS),
    ("hsma_clkin", 0, Pins("AP17"), IOSTD.LVTTL.level2V5),
    ("hsma_clkin",
     1,
     Subsignal("p", Pins("U6")),
     Subsignal("n", Pins("U5")),
     IOSTD.LVDS),
    ("hsma_clkin",
     2,
     Subsignal("p", Pins("K18")),
     Subsignal("n", Pins("J18")),
     IOSTD.LVDS),
    ("pcie_refclk",
     0,
     Subsignal("p", Pins("AE29")),
     Subsignal("n", Pins("AE30")),
     IOSTD.HCSL,
     Misc(["INPUT_TERMINATION", "OFF"])
     ),
    ("hsmb_clkin", 0, Pins("AP16"), IOSTD.LVTTL.level2V5),
    # Table 2-21
    ("clkout_sma", 0, Pins("F23")),
    ("hsma_clkout", 0, Pins("P10")),
    ("hsma_clkout",
     1,
     Subsignal("p", Pins("AD7")),
     Subsignal("n", Pins("AD6"))),
    ("hsma_clkout",
     2,
     Subsignal("p", Pins("V12")),
     Subsignal("n", Pins("W12"))),
    ("hsmb_clkout", 0, Pins("AG30")),
    # Table 2-29
    ("hsma_led",
     0,
     Subsignal("tx", Pins("C29")),
     Subsignal("rx", Pins("N5"))),
    ("hsmb_led",
     0,
     Subsignal("tx_led", Pins("AE24")),
     Subsignal("rx_led", Pins("AE23"))),
    # Table 2-23
    ("user",
     0,
     Subsignal("pb", Pins("AK9 AL7"), IOSTD.LVCMOS.level1V8),
     Subsignal("cpu_reset", Pins("N10"), IOSTD.LVCMOS.level2V5),
     # Table 2-25
     Subsignal("dip", Pins("N2 U9 V9 U4"), IOSTD.LVCMOS.level2V5),
     # Table 2-27
     Subsignal("led", Pins("G1 J4 J5 R5"), IOSTD.LVCMOS.level2V5)),
    # Table 2-31
    ("lcd",
     0,
     Subsignal("d", Pins("F1 H3 E1 F2 D2 D1 C2 C1 J1 H1 J2")),
     Subsignal("d_cn", Pins("J1")),
     Subsignal("wen", Pins("H1")),
     Subsignal("csn", Pins("J2"))),
    # Table 2-34
    ("pcie_rx",
     0,
     Subsignal("p", Pins("AN33")),
     Subsignal("n", Pins("AN34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     1,
     Subsignal("p", Pins("AL33")),
     Subsignal("n", Pins("AL34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     2,
     Subsignal("p", Pins("AJ33")),
     Subsignal("n", Pins("AJ34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     3,
     Subsignal("p", Pins("AG33")),
     Subsignal("n", Pins("AG34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     4,
     Subsignal("p", Pins("AE33")),
     Subsignal("n", Pins("AE34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     5,
     Subsignal("p", Pins("AC33")),
     Subsignal("n", Pins("AC34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     6,
     Subsignal("p", Pins("AA33")),
     Subsignal("n", Pins("AA34")),
     IOSTD.PCML.level1V5),
    ("pcie_rx",
     7,
     Subsignal("p", Pins("W33")),
     Subsignal("n", Pins("W34")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     0,
     Subsignal("p", Pins("AM31")),
     Subsignal("n", Pins("AM32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     1,
     Subsignal("p", Pins("AK31")),
     Subsignal("n", Pins("AK32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     2,
     Subsignal("p", Pins("AH31")),
     Subsignal("n", Pins("AH32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     3,
     Subsignal("p", Pins("AF31")),
     Subsignal("n", Pins("AF32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     4,
     Subsignal("p", Pins("AD31")),
     Subsignal("n", Pins("AD32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     5,
     Subsignal("p", Pins("AB31")),
     Subsignal("n", Pins("AB32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     6,
     Subsignal("p", Pins("Y31")),
     Subsignal("n", Pins("Y32")),
     IOSTD.PCML.level1V5),
    ("pcie_tx",
     7,
     Subsignal("p", Pins("V31")),
     Subsignal("n", Pins("V32")),
     IOSTD.PCML.level1V5),
    ("pcie_misc",
     0,
     Subsignal("perstn", Pins("N1")),
     Subsignal("waken", Pins("C30")),
     Subsignal("smbclk", Pins("M18")),
     Subsignal("smbdat", Pins("D27")),
     Subsignal("led_x1", Pins("C28")),
     Subsignal("led_x4", Pins("D26")),
     Subsignal("led_x8", Pins("C27")),
     IOSTD.LVTTL.level2V5),
    # Table 2-35
    ("enet",
     0,
     Subsignal("gtx_clk", Pins("D25")),
     Subsignal("inetn", Pins("D18")),
     Subsignal("mdc", Pins("K20")),
     Subsignal("mdio", Pins("N20")),
     Subsignal("resetn", Pins("M20")),
     Subsignal("rx_clk", Pins("V6")),
     Subsignal("rx_d", Pins("E21 E24 E22 F24")),
     Subsignal("rx_dv", Pins("D17")),
     Subsignal("tx_d", Pins("J20 C25 G22 G21")),
     Subsignal("tx_en", Pins("G20")),
     IOSTD.LVCMOS.level2V5),
]

_IO = collections.namedtuple("IO", "epm2210 ep2agx125")(_epm2210, _EP2AGX125)


class Platform(AlteraPlatform):
    default_clk_name = "clkin_bot"
    default_clk_period = 10

    def __init__(self):
        super().__init__("EP2AGX125EF35I5", _IO.ep2agx125)

    def do_finalize(self, fragment):
        super().do_finalize(self, fragment)

        self.add_platform_command("set_global_assignment -name FAMILY "
                                  "\"Arria II GX\"")

if __name__ == "__main__":
    from migen.fhdl import std

    plat = Platform()
    led = plat.request("user").led
    module = std.Module()
    counter = std.Signal(26)
    module.comb += led[0].eq(counter[25])
    module.comb += led[1:].eq(0)
    module.sync += counter.eq(counter + 1)
    plat.build_cmdline(module)
