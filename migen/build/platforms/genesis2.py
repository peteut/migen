from migen.build.generic_platform import *  # noqa

_io = [
    ("user_btn_w", 0, Pins("M20")),
    ("user_btn_e", 0, Pins("C19")),
    ("user_btn_n", 0, Pins("B19")),
    ("user_btn_s", 0, Pins("M19")),
    ("user_btn_c", 0, Pins("E18")),

    ("user_sw", 0, Pins("G19")),
    ("user_sw", 1, Pins("G25")),
    ("user_sw", 2, Pins("H24")),
    ("user_sw", 3, Pins("K19")),
    ("user_sw", 4, Pins("N19")),
    ("user_sw", 5, Pins("P19")),
    ("user_sw", 6, Pins("P26"), IOStandard("LVCMOS33")),
    ("user_sw", 7, Pins("P27"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("T28"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("V19"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("U30"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("U29"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("V20"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("V26"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("W24"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("W23"), IOStandard("LVCMOS33")),

    ("sysclk", 0,
        Subsignal("p", Pins("AD12")),
        Subsignal("n", Pins("AD11")),
        IOStandard("LVDS")),

    ("cpu_reset", 0, Pins("R19"), IOStandard("LVCMOS33")),

    ("fan", 0,
     Subsignal("pwm", Pins("W19")),
     Subsignal("tach", Pins("V21")),
     IOStandard("LVCMOS33")),

    ("serial", 0,
     Subsignal("rx", Pins("Y20")),
     Subsignal("tx", Pins("AE20")),
     IOStandard("LVCMOS33")),

    ("i2c", 0,
     Subsignal("scl", Pins("AE30")),
     Subsignal("sda", Pins("AF30")),
     IOStandard("LVCMOS33")),

    ("fpga_cfg", 0,
     Subsignal("cclk", Pins("B10")),
     Subsignal("din", Pins("R25")),
     Subsignal("done", Pins("M10")),
     Subsignal("init_b", Pins("A10")),
     Subsignal("program_b", Pins("K10")),
     IOStandard("LVCMOS33")),

    # ("spiflash", 0,
    #  Subsignal("cs_n", Pins("U19")),
    #  Subsingal("dq", Pins("P24 R25 R20 R21")),
    #  IOStandard("LVCMOS33")),

    ("ddram", 0,
     Subsignal("a", Pins(
         "AC12 AE8 AD8 AC10 AD9 AA13 AA10 AA11 "
         "Y10 Y11 AB8 AA8 AB12 AA12 AH9 AG9"), IOStandard("SSTL15_DCI")),
     Subsignal("ba", Pins("AE9 AB10 AC11"), IOStandard("SSTL15_DCI")),
     Subsignal("ras_n", Pins("AE11"), IOStandard("SSTL15_DCI")),
     Subsignal("cas_n", Pins("AF11"), IOStandard("SSTL15_DCI")),
     Subsignal("we_n", Pins("AG13"), IOStandard("SSTL15_DCI")),
     Subsignal("dm", Pins("AD4 AF3 AH4 AF8"),
               IOStandard("SSTL15_DCI"),
               Misc("DATA_RATE=DDR")),
     Subsignal("dq", Pins(
         "AD3 AC2 AC1 AC5 AC4 AD6 AE6 AC7 "
         "AF2 AE1 AF1 AE4 AE3 AE5 AF5 AF6 "
         "AJ4 AH6 AH5 AH2 AJ2 AJ1 AK1 AJ3 "
         "AF7 AG7 AJ6 AK6 AJ8 AK8 AK5 AK4"),
         IOStandard("SSTL15_DCI"),
         Misc("ODT=RTT_40"),
         Misc("DATA_RATE=DDR")),
     Subsignal("dqs_p", Pins("AD2 AG4 AG2 AH7"),
               IOStandard("DIFF_SSTL15_DCI"),
               Misc("ODT=RTT_40"),
               Misc("DATA_RATE=DDR")),
     Subsignal("dqs_n", Pins("AD1 AG3 AH1 AJ7"),
               IOStandard("DIFF_SSTL15_DCI"),
               Misc("ODT=RTT_40"),
               Misc("DATA_RATE=DDR")),
     Subsignal("clk_p", Pins("AB9"),
               IOStandard("DIFF_SSTL15_DCI"),
               Misc("DATA_RATE=DDR")),
     Subsignal("clk_n", Pins("AC9"),
               IOStandard("DIFF_SSTL15_DCI"),
               Misc("DATA_RATE=DDR")),
     Subsignal("cke", Pins("AJ9"), IOStandard("SSTL15_DCI")),
     Subsignal("odt", Pins("AK9")),
     Subsignal("reset_n", Pins("AG5"), IOStandard("SSTL15")),
     Misc("SLEW=TRUE"),
     Misc("OUTPUT_IMPEDANCE=RDRV_40_40")),

    ("audio", 0,
     Subsignal("adr", Pins("AD19 AG19")),
     Subsignal("gpio", Pins("AJ19 AH19 AG18 AJ18")),
     Subsignal("mclk", Pins("AK19")),
     Subsignal("scl", Pins("AE19")),
     Subsignal("sda", Pins("AF18")),
     IOStandard("LVCMOS18")),

    ("oled", 0,
     Subsignal("dc", Pins("AC17"), IOStandard("LVCMOS18")),
     Subsignal("res", Pins("AB17"), IOStandard("LVCMOS18")),
     Subsignal("sclk", Pins("AF17"), IOStandard("LVCMOS18")),
     Subsignal("sdin", Pins("Y15"), IOStandard("LVCMOS18")),
     Subsignal("vbat", Pins("AB22"), IOStandard("LVCMOS33")),
     Subsignal("vdd", Pins("AG17"), IOStandard("LVCMOS18"))),

    ("hdmi", 0,
     Subsignal("tx_clk_p", Pins("AA20"), IOStandard("TMDS_33")),
     Subsignal("tx_clk_n", Pins("AB20"), IOStandard("TMDS_33")),
     Subsignal("tx_p", Pins("AC20 AA22 AB24"), IOStandard("TMDS_33")),
     Subsignal("tx_n", Pins("AC21 AA23 AC25"), IOStandard("TMDS_33")),
     Subsignal("tx_scl", Pins("AF27"), IOStandard("LVCMOS33")),
     Subsignal("tx_sda", Pins("AF26"), IOStandard("LVCMOS33")),
     Subsignal("rx_clk_p", Pins("AE28"), IOStandard("TMDS_33")),
     Subsignal("rx_clk_n", Pins("AF28"), IOStandard("TMDS_33")),
     Subsignal("rx_p", Pins("AJ26 AG27 AH26"), IOStandard("TMDS_33")),
     Subsignal("rx_n", Pins("AK26 AG28 AH27"), IOStandard("TMDS_33")),
     Subsignal("rx_scl", Pins("AJ28"), IOStandard("LVCMOS33")),
     Subsignal("rx_sda", Pins("AJ29"), IOStandard("LVCMOS33"))),

    ("vga", 0,
     Subsignal("r", Pins("AK25 AG25 AH25 AK24 AJ24")),
     Subsignal("g", Pins("AJ23 AJ22 AH22 AK21 AJ21 AK23")),
     Subsignal("b", Pins("AH20 AG20 AF21 AK20 AG22")),
     Subsignal("hsync_n", Pins("AF20")),
     Subsignal("vsync_n", Pins("AG23")),
     IOStandard("LVCMOS33")),

    ("mmc", 0,
     Subsignal("dat", Pins("R26 R30 P29 T30")),
     Subsignal("cmd", Pins("R29")),
     Subsignal("sclk", Pins("R28")),
     Subsignal("reset", Pins("AE24")),
     Subsignal("cd", Pins("P28")),
     IOStandard("LVCMOS33")),


    ("usb_otg",
     Subsignal("d", Pins("AE14 AE15 AC15 AC16 AB15 AA15 AD14 AC14")),
     Subsignal("clk", Pins("AD18")),
     Subsignal("dir", Pins("Y16")),
     Subsignal("stp", Pins("AA17")),
     Subsignal("nxt", Pins("AA16")),
     Subsignal("vbusoc", Pins("AF16")),
     Subsignal("reset_n", Pins("AB14")),
     IOStandard("LVCMOS18")),

    ("eth_clocks", 0,
     Subsignal("tx", Pins("AE10")),
     Subsignal("tx", Pins("AG10")),
     IOStandard("LVCMOS15")),

    ("eth", 0,
     Subsignal("rst_n", Pins("AH24"), IOStandard("LVCMOS18")),
     Subsignal("int_n", Pins("AK16"), IOStandard("LVCMOS18")),
     Subsignal("rx_ctl", Pins("AH11"), IOStandard("LVCMOS15")),
     Subsignal("rx_data", Pins("AJ14 AH14 AK13 AJ13"), IOStandard("LVCMOS15")),
     Subsignal("tx_ctl", Pins("AK14"), IOStandard("LVCMOS15")),
     Subsignal("tx_data", Pins("AJ12 AK11 AJ11 AK10"), IOStandard("LVCMOS15")),
     Subsignal("mdc", Pins("AF12"), IOStandard("LVCMOS15")),
     Subsignal("mdio", Pins("AG12"), IOStandard("LVCMOS15"))),
]

_connectors = [
    ("hpc", {
        "dp1_m2c_p": "Y6",
        "dp1_m2c_n": "Y5",
        "dp2_m2c_p": "W4",
        "dp2_m2c_n": "W3",
        "dp3_m2c_p": "V6",
        "dp3_m2c_n": "V5",
        "dp1_c2m_p": "V2",
        "dp1_c2m_n": "V1",
        "dp2_c2m_p": "U4",
        "dp2_c2m_n": "U3",
        "dp3_c2m_p": "T2",
        "dp3_c2m_n": "T1",
        "dp0_c2m_p": "Y2",
        "dp0_c2m_n": "Y1",
        "dp0_m2c_p": "AA4",
        "dp0_m2c_n": "AA3",
        "la06_p": "D29",
        "la06_n": "C30",
        "la10_p": "B27",
        "la10_n": "A27",
        "la14_p": "C24",
        "la14_n": "B24",
        "la18_cc_p": "D17",
        "la18_cc_n": "D18",
        "la27_p": "A20",
        "la27_n": "A21",
        "ha01_cc_p": "M28",
        "ha01_cc_n": "L28",
        "ha05_p": "J29",
        "ha05_n": "H29",
        "ha09_p": "L30",
        "ha09_n": "K30",
        "ha13_p": "K26",
        "ha13_n": "J26",
        "ha16_p": "M22",
        "ha16_n": "M23",
        "ha20_p": "G27",
        "ha20_n": "F27",
        "clk1_m2c_p": "E28",
        "clk1_m2c_n": "D28",
        "la00_cc_p": "D27",
        "la00_cc_n": "C27",
        "la03_p": "E29",
        "la03_n": "E30",
        "la08_p": "C29",
        "la08_n": "B29",
        "la12_p": "F26",
        "la12_n": "E26",
        "la16_p": "E23",
        "la16_n": "D23",
        "la20_p": "G22",
        "la20_n": "F22",
        "la22_p": "J17",
        "la22_n": "H17",
        "la25_p": "D22",
        "la25_n": "C22",
        "la29_p": "B18",
        "la29_n": "A18",
        "la31_p": "C17",
        "la31_n": "B17",
        "la33_p": "D16",
        "la33_n": "C16",
        "ha03_p": "N25",
        "ha03_n": "N26",
        "ha07_p": "M29",
        "ha07_n": "M30",
        "ha11_p": "P23",
        "ha11_n": "N24",
        "ha14_p": "N27",
        "ha14_n": "M27",
        "ha18_p": "E19",
        "ha18_n": "D19",
        "ha22_p": "D21",
        "ha22_n": "C21",
        "gbtclk1_m2c_p": "N8",
        "gbtclk1_m2c_n": "N7",
        "gbtclk0_m2c_p": "L8",
        "gbtclk0_m2c_n": "L7",
        "la01_cc_p": "D26",
        "la01_cc_n": "C26",
        "la05_p": "B30",
        "la05_n": "A30",
        "la09_p": "B28",
        "la09_n": "A28",
        "la13_p": "E24",
        "la13_n": "D24",
        "la17_cc_p": "F21",
        "la17_cc_n": "E21",
        "la23_p": "G17",
        "la23_n": "F17",
        "la26_p": "B22",
        "la26_n": "A22",
        "pg_m2c": "AH21",
        "ha00_cc_p": "K28",
        "ha00_cc_n": "K29",
        "ha04_p": "M24",
        "ha04_n": "M25",
        "ha08_p": "J27",
        "ha08_n": "J28",
        "ha12_p": "L26",
        "ha12_n": "L27",
        "ha15_p": "J21",
        "ha15_n": "J22",
        "ha19_p": "G29",
        "ha19_n": "F30",
        "prsnt_m2c_b": "AA21",
        "clk0_m2c_p": "F20",
        "clk0_m2c_n": "E20",
        "la02_p": "H30",
        "la02_n": "G30",
        "la04_p": "H26",
        "la04_n": "H27",
        "la07_p": "F25",
        "la07_n": "E25",
        "la11_p": "A25",
        "la11_n": "A26",
        "la15_p": "B23",
        "la15_n": "A23",
        "la19_p": "H21",
        "la19_n": "H22",
        "la21_p": "L17",
        "la21_n": "L18",
        "la24_p": "H20",
        "la24_n": "G20",
        "la28_p": "J19",
        "la28_n": "H19",
        "la30_p": "A16",
        "la30_n": "A17",
        "la32_p": "K18",
        "la32_n": "J18",
        "ha02_p": "P21",
        "ha02_n": "P22",
        "ha06_p": "N29",
        "ha06_n": "N30",
        "ha10_p": "N21",
        "ha10_n": "N22",
        "ha17_cc_p": "C25",
        "ha17_cc_n": "B25",
        "ha21_p": "G28",
        "ha21_n": "F28",
        "ha23_p": "G18",
        "ha23_n": "F18",
    }),
    ("pmoda", "U27 U28 T26 T27 T22 T23 T20 T21"),
    ("pmodb", "V29 V30 V25 W26 T25 U25 U22 U23"),
    ("pmodc", "AC26 AJ27 AH30 AK29 AD26 AG30 AK30 AK28"),
    ("pmodd", "V27 Y30 V24 W22 U24 Y26 V22 W21"),
    ("xadc", {
        "vaux0_p": "J23",
        "vaux0_n": "J24",
        "vaux1_p": "K23",
        "vaux1_n": "K24",
        "vaux8_p": "L22",
        "vaux8_n": "L23",
        "vaux9_p": "L21",
        "vaux9_n": "K21",
    }),
]


class Platform(XilinxPlatform):
    default_clk_name = "sysclk"
    default_clk_period = 5.0

    def __init__(self, toolchain="vivado", **kwargs):
        super().__init__(
            "xc7k325t-2ffg900", _io, _connectors,
            toolchain=toolchain, **kwargs)
        self.toolchain.bitstream_commands.extend([
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]",
            "set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_32BIT_ADDR YES [current_design]",
            "set_property BITSTREAM.CONFIG.SPI_FALL_EDGE YES [current_design]",
            "set_property CFGBVS VCCO [current_design]",
            "set_property CONFIG_VOLTAGE 3.3 [current_design]",
        ])
