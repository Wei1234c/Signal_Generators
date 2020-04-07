# datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ad9833.pdf


try:
    from ..interfaces import *
    from ..register import RegistersMap, Register, Element, array
    from ..adapters import I2C
except:
    from interfaces import *
    from register import RegistersMap, Register, Element, array
    from adapters import I2C

FREQ_MCLK = int(25e6)
POW2_32 = 2 ** 32
POW2_28 = 2 ** 28
POW2_12 = 2 ** 12
POW2_5 = 2 ** 5
BITS_PER_DEG = POW2_12 / DEGREES_IN_PI2



def _get_all_raw_registers():
    registers = []

    registers.append(Register(name = 'Device_Status', address = 0, description = 'Device_Status',
                              elements = [Element(name = 'SYS_INIT', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Initialization Status.'),
                                          Element(name = 'LOL_B', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status.'),
                                          Element(name = 'LOL_A', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLL A Loss Of Lock Status.'),
                                          Element(name = 'LOS_CLKIN', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal (Si5351C Only).'),
                                          Element(name = 'LOS_XTAL', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal'),
                                          Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'REVID', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Revision number of the device.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Interrupt_Status_Sticky', address = 1, description = 'Interrupt_Status_Sticky',
                              elements = [Element(name = 'SYS_INIT_STKY', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Calibration Status Sticky Bit.'),
                                          Element(name = 'LOL_B_STKY', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status Sticky Bit.'),
                                          Element(name = 'LOL_A_STKY', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLLA Loss Of Lock Status Sticky Bit.'),
                                          Element(name = 'LOS_CLKIN_STKY', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal Sticky Bit (Si5351C Only).'),
                                          Element(name = 'LOS_XTAL_STKY', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal Sticky Bit'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Interrupt_Status_Mask', address = 2, description = 'Interrupt_Status_Mask',
                              elements = [Element(name = 'SYS_INIT_MASK', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Initialization Status Mask.'),
                                          Element(name = 'LOL_B_MASK', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status Mask.'),
                                          Element(name = 'LOL_A_MASK', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLL A Loss Of Lock Status Mask.'),
                                          Element(name = 'LOS__CLKIN_MASK', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal Mask (Si5351C Only).'),
                                          Element(name = 'LOS__XTAL_MASK', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal Mask'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Output_Enable_Control', address = 3, description = 'Output_Enable_Control',
                              elements = [Element(name = 'CLK7_OEB', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK7.'),
                                          Element(name = 'CLK6_OEB', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK6.'),
                                          Element(name = 'CLK5_OEB', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK5.'),
                                          Element(name = 'CLK4_OEB', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK4.'),
                                          Element(name = 'CLK3_OEB', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK3.'),
                                          Element(name = 'CLK2_OEB', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK2.'),
                                          Element(name = 'CLK1_OEB', idx_lowest_bit = 1, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK1.'),
                                          Element(name = 'CLK0_OEB', idx_lowest_bit = 0, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK0.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'OEB_Pin_Enable_Control_Mask', address = 9, description = 'OEB_Pin_Enable_Control_Mask',
                 elements = [Element(name = 'OEB_MAS_K7', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK7.'),
                             Element(name = 'OEB_MAS_K6', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK6.'),
                             Element(name = 'OEB_MAS_K5', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK5.'),
                             Element(name = 'OEB_MAS_K4', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK4.'),
                             Element(name = 'OEB_MAS_K3', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK3.'),
                             Element(name = 'OEB_MAS_K2', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK2.'),
                             Element(name = 'OEB_MAS_K1', idx_lowest_bit = 1, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK1.'),
                             Element(name = 'OEB_MAS_K0', idx_lowest_bit = 0, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK0.'),
                             ], default_value = 0))

    registers.append(Register(name = 'PLL_Input_Source', address = 15, description = 'PLL_Input_Source',
                              elements = [Element(name = 'CLKIN_DIV', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'ClKIN Input Divider.'),
                                          Element(name = 'Reserved_4', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'PLLB_SRC', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Input Source Select for PLLB.'),
                                          Element(name = 'PLLA_SRC', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  description = 'Input Source Select for PLLA.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK0_Control', address = 16, description = 'CLK0_Control',
                              elements = [Element(name = 'CLK0_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 0 Power Down.'),
                                          Element(name = 'MS0_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 0 Integer Mode.'),
                                          Element(name = 'MS0_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK0.'),
                                          Element(name = 'CLK0_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 0 Invert.'),
                                          Element(name = 'CLK0_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 0 Input Source.'),
                                          Element(name = 'CLK0_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK0 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK1_Control', address = 17, description = 'CLK1_Control',
                              elements = [Element(name = 'CLK1_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 1 Power Down.'),
                                          Element(name = 'MS1_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 1 Integer Mode.'),
                                          Element(name = 'MS1_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK1.'),
                                          Element(name = 'CLK1_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 1 Invert.'),
                                          Element(name = 'CLK1_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 1 Input Source.'),
                                          Element(name = 'CLK1_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK1 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK2_Control', address = 18, description = 'CLK2_Control',
                              elements = [Element(name = 'CLK2_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 2 Power Down.'),
                                          Element(name = 'MS2_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 2 Integer Mode.'),
                                          Element(name = 'MS2_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK2.'),
                                          Element(name = 'CLK2_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 2 Invert.'),
                                          Element(name = 'CLK2_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 2 Input Source.'),
                                          Element(name = 'CLK2_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK2 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK3_Control', address = 19, description = 'CLK3_Control',
                              elements = [Element(name = 'CLK3_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 3 Power Down.'),
                                          Element(name = 'MS3_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 3 Integer Mode.'),
                                          Element(name = 'MS3_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK3.'),
                                          Element(name = 'CLK3_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 3 Invert.'),
                                          Element(name = 'CLK3_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 3 Input Source.'),
                                          Element(name = 'CLK3_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK3 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK4_Control', address = 20, description = 'CLK4_Control',
                              elements = [Element(name = 'CLK4_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 4 Power Down.'),
                                          Element(name = 'MS4_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 4 Integer Mode.'),
                                          Element(name = 'MS4_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK4.'),
                                          Element(name = 'CLK4_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 4 Invert.'),
                                          Element(name = 'CLK4_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 4 Input Source.'),
                                          Element(name = 'CLK4_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK4 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK5_Control', address = 21, description = 'CLK5_Control',
                              elements = [Element(name = 'CLK5_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 5 Power Down.'),
                                          Element(name = 'MS5_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 5 Integer Mode.'),
                                          Element(name = 'MS5_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK5.'),
                                          Element(name = 'CLK5_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 5 Invert.'),
                                          Element(name = 'CLK5_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 5 Input Source.'),
                                          Element(name = 'CLK5_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK5 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK6_Control', address = 22, description = 'CLK6_Control',
                              elements = [Element(name = 'CLK6_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 7 Power Down.'),
                                          Element(name = 'FBA_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'FBA MultiSynth Integer Mode.'),
                                          Element(name = 'MS6_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK6.'),
                                          Element(name = 'CLK6_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 6 Invert.'),
                                          Element(name = 'CLK6_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 6 Input Source.'),
                                          Element(name = 'CLK6_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK6 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK7_Control', address = 23, description = 'CLK7_Control',
                              elements = [Element(name = 'CLK7_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 7 Power Down.'),
                                          Element(name = 'FBB_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'FBB MultiSynth Integer Mode.'),
                                          Element(name = 'MS7_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK7.'),
                                          Element(name = 'CLK7_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 7 Invert.'),
                                          Element(name = 'CLK7_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 7 Input Source.'),
                                          Element(name = 'CLK7_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK7 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK3–0_Disable_State', address = 24, description = 'CLK3–0_Disable_State',
                              elements = [Element(name = 'CLK3_DIS_STATE', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Clock 3 Disable State.'),
                                          Element(name = 'CLK2_DIS_STATE', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  description = 'Clock 2 Disable State.'),
                                          Element(name = 'CLK1_DIS_STATE', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Clock 1 Disable State.'),
                                          Element(name = 'CLK0_DIS_STATE', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Clock 0 Disable State.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK7–4_Disable_State', address = 25, description = 'CLK7–4_Disable_State',
                              elements = [Element(name = 'CLK7_DIS_STATE', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Clock 7 Disable State.'),
                                          Element(name = 'CLK6_DIS_STATE', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  description = 'Clock 6 Disable State.'),
                                          Element(name = 'CLK5_DIS_STATE', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Clock 5 Disable State.'),
                                          Element(name = 'CLK4_DIS_STATE', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Clock 4 Disable State.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 26, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 27, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 28, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'Unused', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Unused.'),
                                          Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Reserved.'),
                                          Element(name = 'MSNA_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 29, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 30, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 31, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          Element(name = 'MSNA_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 32, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 33, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 34, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 35, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 36, description = 'Multisynth_NB_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 4, n_bits = 4, value = 0, description = ''),
                                  Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          read_only = True, description = 'Reserved.'),
                                  Element(name = 'MSNB_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth NB Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 37, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 38, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 39, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth NB Parameter 3.'),
                                          Element(name = 'MSNB_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 40, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 41, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 42, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 43, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 44, description = 'Multisynth0_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R0_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R0 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS0_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS0 Divide by 4 Enable.'),
                                  Element(name = 'MS0_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth0 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 45, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 46, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 47, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          Element(name = 'MS0_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 48, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 49, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 50, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 51, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 52, description = 'Multisynth1_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R1_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R1 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS1_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS1 Divide by 4 Enable.'),
                                  Element(name = 'MS1_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth1 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 53, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 54, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 55, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          Element(name = 'MS1_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 56, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 57, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 58, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 59, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 60, description = 'Multisynth2_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R2_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R2 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS2_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS2 Divide by 4 Enable.'),
                                  Element(name = 'MS2_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth2 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 61, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 62, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 63, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          Element(name = 'MS2_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 64, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 65, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 66, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 67, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 68, description = 'Multisynth3_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R3_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R3 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS3_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS3 Divide by 4 Enable.'),
                                  Element(name = 'MS3_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth3 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 69, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 70, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 71, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          Element(name = 'MS3_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 72, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 73, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 74, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 75, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 76, description = 'Multisynth4_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R4_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R4 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS4_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS4 Divide by 4 Enable.'),
                                  Element(name = 'MS4_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth4 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 77, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 78, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 79, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          Element(name = 'MS4_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 80, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 81, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 82, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 83, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 84, description = 'Multisynth5_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R5_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R5 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS5_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS5 Divide by 4 Enable.'),
                                  Element(name = 'MS5_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth5 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 85, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 86, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 87, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          Element(name = 'MS5_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 88, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 89, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth6_Parameters', address = 90, description = 'Multisynth6_Parameters',
                              elements = [Element(name = 'MS6_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth6 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth7_Parameters', address = 91, description = 'Multisynth7_Parameters',
                              elements = [Element(name = 'MS7_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth7 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'Clock_6_and_7_Output_Divider', address = 92, description = 'Clock_6_and_7_Output_Divider',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Leave as default.'),
                             Element(name = 'R7_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                     description = 'R7 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                             Element(name = 'Reserved_3', idx_lowest_bit = 3, n_bits = 1, value = 0, read_only = True,
                                     description = 'Leave as default.'),
                             Element(name = 'R6_DIV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                     description = 'R6 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 149, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSC_EN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'Spread Spectrum Enable'),
                             Element(name = 'SSDN_P2_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 150, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 151, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSC_MODE', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'Spread Spectrum Mode.'),
                             Element(name = 'SSDN_P3_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 152, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 153, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 154, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUDP_11_8', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Up/Down Parameter.'),
                             Element(name = 'SSDN_P1_11_8', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 155, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUDP_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up/Down Parameter.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 156, description = 'Spread_Spectrum_Parameters',
                 elements = [
                     Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = 'Unused.'),
                     Element(name = 'SSUP_P2_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                             description = 'PLL A Spread Spectrum Up Parameter 2.'),
                     ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 157, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 158, description = 'Spread_Spectrum_Parameters',
                 elements = [
                     Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = 'Unused.'),
                     Element(name = 'SSUP_P3_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                             description = 'PLL A Spread Spectrum Up Parameter 3.'),
                     ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 159, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 160, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 161, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SS_NCLK', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                     description = 'Must write 0000b to these bits.'),
                             Element(name = 'SSUP_P1_11_8', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 1.'),
                             ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 162, description = 'VCXO_Parameter',
                              elements = [Element(name = 'VCXO_Param_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 163, description = 'VCXO_Parameter',
                              elements = [Element(name = 'VCXO_Param_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 164, description = 'VCXO_Parameter',
                              elements = [Element(name = 'Reserved_6', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  read_only = True,
                                                  description = 'Reserved. Only write 00b to these bits.'),
                                          Element(name = 'VCXO_Param_21_16', idx_lowest_bit = 0, n_bits = 6, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'CLK0_Initial_Phase_Offset', address = 165, description = 'CLK0_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK0_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 0 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK1_Initial_Phase_Offset', address = 166, description = 'CLK1_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK1_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 1 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK2_Initial_Phase_Offset', address = 167, description = 'CLK2_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK2_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 2 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK3_Initial_Phase_Offset', address = 168, description = 'CLK3_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK3_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 3 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK4_Initial_Phase_Offset', address = 169, description = 'CLK4_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK4_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 4 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK5_Initial_Phase_Offset', address = 170, description = 'CLK5_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK5_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 5 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(Register(name = 'PLL_Reset', address = 177, description = 'PLL_Reset',
                              elements = [Element(name = 'PLLB_RST', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'PLLB_Reset.'),
                                          Element(name = 'Reserved_6', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'PLLA_RST', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLLA_Reset.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 5, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Crystal_Internal_Load_Capacitance', address = 183,
                              description = 'Crystal_Internal_Load_Capacitance',
                              elements = [Element(name = 'XTAL_CL', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Crystal Load Capacitance Selection.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 6, value = 0,
                                                  read_only = True,
                                                  description = 'Bits 5:0 should be written to 010010b.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Fanout_Enable', address = 187, description = 'Fanout_Enable',
                              elements = [Element(name = 'CLKIN_FANOUT_EN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of CLKIN to clock output multiplexers. Set this bit to 1b.'),
                                          Element(name = 'XO_FANOUT_EN', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of XO to clock output multiplexers. Set this bit to 1b.'),
                                          Element(name = 'Reserved_5', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Reserved.'),
                                          Element(name = 'MS_FANOUT_EN', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of Multisynth0 and Multisynth4 to all output multiplexers. Set this bit to 1b.'),
                                          ], default_value = 0))

    return registers



def _get_registers_map():
    raw_registers = _get_all_raw_registers()

    names = [reg.name for reg in raw_registers]
    duplicated_names = list((n for n in set(names) if names.count(n) > 1))

    for reg in raw_registers:
        if reg.name in duplicated_names:
            reg.name = '{}_{}'.format(reg.name, reg.address)

    regs_map = RegistersMap(name = 'Si5351', description = 'Si5351 registers.', registers = raw_registers)

    reg = regs_map.registers['Crystal_Internal_Load_Capacitance']
    reg.default_value = 0xC0
    reg.reset()

    return regs_map



class Si535x(Device):
    DEBUG_MODE = False
    FREQ_MCLK = int(25e6)
    I2C_ADDRESS = 0x60

    SHAPES_CONFIG = {'sine': None}


    def __init__(self, i2c, i2c_address = I2C_ADDRESS, pin_oeb = None, pin_ssen = None,
                 freq = FREQ_DEFAULT, freq_correction = 0,
                 phase = PHASE_DEFAULT,
                 shape = SHAPE_DEFAULT,
                 freq_mclk = FREQ_MCLK, commands = None):

        Device.__init__(self, freq = freq, freq_correction = freq_correction, phase = phase, shape = shape,
                        commands = commands)
        self._i2c = I2C(i2c, i2c_address)
        self._i2c_address = i2c_address
        self._pin_oeb = pin_oeb
        self._pin_ssen = pin_ssen
        self.freq_mclk = freq_mclk
        self.register_map = _get_registers_map()
        self.init()


    def init(self):
        self.enable_output(False)
        for i in range(self.REGISTERS_COUNT):
            self.set_frequency(idx = i, freq = self.frequency, freq_mclk = self.freq_mclk)
            self.set_phase(idx = i, phase = self.phase)
        # self.select_freq_source(0)
        # self.select_phase_source(0)
        self.shape = self.shape
        self.start()


    def _update_register(self, register, reset = False):
        if reset:
            register.reset()
        self._i2c.write(register.bytes)
        self._print_register(register)


    def _update_control_register(self, reset = False):
        self._update_register(self.control_register, reset = reset)


    def _update_frequency_register(self, register, reset = False):
        if reset:
            register.reset()
        self._enable_B28(True)
        self._i2c.write(register.lsw)
        self._i2c.write(register.msw)
        self._print_register(register)


    def _update_all_registers(self, reset = False):
        self._update_control_register(reset = reset)
        for i in range(self.REGISTERS_COUNT):
            self._update_frequency_register(self.frequency_registers[i], reset = reset)
            self._update_register(self.phase_registers[i], reset = reset)


    def update(self):
        self._update_all_registers(reset = False)


    def reset(self):
        self._update_all_registers(reset = True)


    def print(self, as_hex = False):
        self.control_register.print(as_hex = as_hex)
        for i in range(self.REGISTERS_COUNT):
            self.frequency_registers[i].print(as_hex = as_hex)
            self.phase_registers[i].print(as_hex = as_hex)


    @property
    def freq_resolution(self):
        return self.freq_mclk / POW2_28


    @property
    def phase_resolution(self):
        return DEGREES_IN_PI2 / POW2_12


    def set_frequency(self, freq, idx = None, freq_correction = None, freq_mclk = None):
        freq_reg = self.frequency_registers[self.active_freq_reg_idx if idx is None else idx]
        freq_reg.frequency = freq + (self.freq_correction if freq_correction is None else freq_correction)
        freq_reg.freq_mclk = self.freq_mclk if freq_mclk is None else freq_mclk
        self._update_frequency_register(freq_reg)


    def set_phase(self, phase, idx = None):
        phase_reg = self.phase_registers[self.active_phase_reg_idx if idx is None else idx]
        phase_reg.phase = phase
        self._update_register(phase_reg)


    def select_freq_source(self, idx):
        self.control_register.elements['FSELECT'].value = idx & 0x1
        self._update_control_register()


    def select_phase_source(self, idx):
        self.control_register.elements['PSELECT'].value = idx
        self._update_control_register()


    @property
    def active_freq_reg_idx(self):
        return self.control_register.elements['FSELECT'].value


    @property
    def active_phase_reg_idx(self):
        return self.control_register.elements['PSELECT'].value


    @property
    def current_frequency_register(self):
        return self.frequency_registers[self.active_freq_reg_idx]


    @property
    def current_frequency(self):
        return self.current_frequency_register.frequency


    @property
    def current_phase_register(self):
        return self.phase_registers[self.active_phase_reg_idx]


    @property
    def current_phase(self):
        return self.current_phase_register.phase


    def apply_signal(self, freq = None, freq_correction = None, freq_mclk = None, phase = None, shape = None):
        self.set_frequency(freq = self.frequency if freq is None else freq,
                           freq_correction = freq_correction,
                           freq_mclk = freq_mclk)
        self.set_phase(phase = self.phase if phase is None else phase)
        self.shape = self.shape if shape is None else shape


    def enable(self, value):
        self.enabled = value
        if value:
            self.shape = self.shape  # restore bit SLEEP12 according to shape.
        # self._enable_internal_clock(value)
        self.enable_output(value)


    def enable_output(self, value = True):
        if self._pin_oeb is not None:
            _ = self._pin_oeb.low() if value else self._pin_oeb.high()


    def enable_spread_spectrum(self, value = True):
        if self._pin_ssen is not None:
            _ = self._pin_ssen.high() if value else self._pin_ssen.low()


    def start(self):
        self.enable(True)


    def pause(self):
        self.enable(False)


    def resume(self):
        self.enable(True)


    def stop(self):
        self.pause()


    def close(self):
        self.stop()
