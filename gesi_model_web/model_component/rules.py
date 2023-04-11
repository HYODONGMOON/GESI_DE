from pyomo.core import Constraint, value


# from pyomo.core import Constraint

# Balance Constraints
def balance_p_rule(M, t):
    return (               
         (
                    sum([M.elp[(t, power)] for power in M.power])
         # offshore wind + onshore wind + solar + ocean inflexible power
         + M.h_wind[t] * (M.New['Wind_on'] + M.specs[('Wind_on', 'cap')])
         + M.offshore[t] * (M.New['Wind_off'] + M.specs[('Wind_off', 'cap')])
         + M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')])
         # Charge_Discharge_pumped hydro
         # -charge(t)+discharge(t)
         # electricity consumption by flexible technologies
         - sum([M.eld[(t, flexible)] for flexible in M.flexible])
         - M.E_H_ind[t]

         # Curtailment
         - M.curtail[t])
        == (M.hourly_demand[t]
            + value(M.el_h_new) * (1 - value(M.smart_share)) * M.h_H_demand[t]
            - value(M.el_h_old) * value(M.smart_share) * M.h_H_demand[t]))

def balance_th_rule(M, t):
    return (
                   - sum([M.heatP[(t, F2H)] for F2H in M.F2H])
                   - sum([M.heatP[(t, P2H)] for P2H in M.P2H])
                   - sum([M.heatP[(t, G2H)] for G2H in M.G2H])
                   - M.dis_th[t]
                   + M.ch_th[t]) == - M.hourly_heat[t]


def balance_ind_th_rule(M, t):
    # return (M.E_H_ind[t] * 3) + M.dis_ind_h[t] - M.charge_ind_h[t] == M.E_heat_smart[t]
    return (- (M.E_H_ind[t] * 3)
            + M.charge_ind_h[t]
            - M.dis_ind_h[t]) == - M.E_heat_smart[t]


# Conventional Fuel Plants Operation


def oper_cons_pp_f2p_rule(M, F2P):
    return sum([M.elp[(t, F2P)] for t in M.t]) <= (M.New[F2P] * 8760 * 0.8)


# TES balance heat
def heat_SOC_rule(M, t):
    if t > 1:
        return M.SOC_th[t] == (0.9998 * M.SOC_th[t - 1] + M.ch_th[t - 1] - M.dis_th[t - 1])

    return Constraint.Skip


def heat_SOC_boundary_rule(M, t):
    if t == 1 or t == 8760:
        return M.SOC_th[t] == (M.New['TES_DH'] + M.specs[('TES_DH', 'cap')]) * 0.5

    return Constraint.Skip

# TES Individual SOC
def heat_ind_SOC_rule(M, t):
    if t > 1:
        return M.SOC_ind_th[t] == (0.9998 * M.SOC_ind_th[t - 1] - M.dis_ind_h[t] + M.charge_ind_h[t])

    return Constraint.Skip


def heat_ind_SOC_boundary_rule(M, t):
    if t == 1 or t == 8760:
        return M.SOC_ind_th[t] == (value(M.Stor_H_ind) / 2.)

    return Constraint.Skip


# Gas Balance Equations
# def balance_gas_rule(M, t):
#    return (M.ch_gas[t] - M.dis_gas[t] + sum([M.gas[(t, gas_all)] for gas_all in M.gas_all]) - sum([M.gasP[(t, )]) == (- M.industry_gas[t]*(1-M.hydrogen_import_share))

def balance_gas_rule(M, t):
    return (
            sum([M.gas[(t, gas_all)] for gas_all in M.gas_all])
            - sum([M.gasP[(t, RH2)] for RH2 in M.RH2])
            - sum([M.gasP[(t, P2G)] for P2G in M.P2G])
            - M.gasP[(t, 'H2_Grid')]
            - M.dis_gas[t]
            + M.ch_gas[t] 
            - M.hourly_Off_gas[t]) == - M.industry_gas[t]


# Gas Storage Balance
def gas_SOC_rule(M, t):
    if t > 1:
        return M.SOC_gas[t] == (M.SOC_gas[t - 1] + M.ch_gas[t] - M.dis_gas[t])

    return Constraint.Skip


def gas_SOC_boundary_rule(M, t):
    if t == 1 or t == 8760:
        return M.SOC_gas[t] == (M.New['Gas_storage'] + M.specs[('Gas_storage', 'cap')]) * 0.5

    return Constraint.Skip


def gas_charge_constraint_rule(M, t):
    return M.ch_gas[t] <= (M.New['GS_interface'] + M.specs[('GS_interface', 'cap')])


def gas_discharge_constraint_rule(M, t):
    return M.dis_gas[t] <= (M.New['GS_interface'] + M.specs[('GS_interface', 'cap')])


# Conversion
def gas_el_conversion_rule(M, t, P2G):
    return (M.gasP[(t, P2G)] - (M.specs[(P2G, 'eff_de')] * M.eld[(t, P2G)])) == 0

def gas_fuel_conversion_rule(M, t, RH2):
    return (M.gasP[(t, RH2)] - (M.specs[(RH2, 'eff_de')] * M.eld[(t, RH2)])) == 0


    
  # return (- (M.specs[('electrolysis', 'eff_de')] * M.eld[(t, 'electrolysis')]) - (M.specs[('SMR', 'eff_de')] * M.eld[(t, 'SMR')]) + M.gasP[t]) == 0


def EL_conversion_rule(M, t, F2P):
    # return M.elp[(t, F2P)] == M.specs[(F2P, 'eff_pe')] * (M.gas[(t, F2P)] + M.LNG[(t, F2P)])
    return (M.elp[(t, F2P)] - M.specs[(F2P, 'eff_pe')] * (M.gas[(t, F2P)] + M.LNG[(t, F2P)])) == 0

def EL_gas_conversion_rule(M, t, G2P):
    # return M.elp[(t, G2P)] == (M.specs[(G2P, 'eff_pe')] * M.gas[(t, G2P)])
    return (M.elp[(t, G2P)] - (M.specs[(G2P, 'eff_pe')] * M.gas[(t, G2P)])) == 0


def Heat_fuel_conversion_rule(M, t, F2H):
    # return M.heatP[(t, F2H)] == M.specs[(F2H, 'eff_th')] * (M.gas[(t, F2H)] + M.LNG[(t, F2H)])
    return M.heatP[(t, F2H)] == M.specs[(F2H, 'eff_th')] * (M.gas[(t, F2H)] + M.LNG[(t, F2H)])


def Heat_gas_conversion_rule(M, t, G2H):
    # return M.heatP[(t, G2H)] == (M.specs[(G2H, 'eff_th')] * M.gas[(t, G2H)])
    return M.heatP[(t, G2H)] == (M.specs[(G2H, 'eff_th')] * M.gas[(t, G2H)])


def Heat_el_conversion_rule(M, t, P2H):
    # return M.heatP[(t, P2H)] == (M.specs[(P2H, 'eff_th')] * M.eld[(t, P2H)])
    return M.heatP[(t, P2H)] == (M.specs[(P2H, 'eff_th')] * M.eld[(t, P2H)])


def EL_waste_conversion_rule(M, t, W2P):
    return (M.elp[(t, W2P)] - M.specs[(W2P, 'eff_pe')] * (M.Solidwaste[(t, W2P)])) == 0

def Heat_waste_conversion_rule(M, t, W2H):
    return M.heatP[(t, W2H)] == M.specs[(W2H, 'eff_th')] * (M.Solidwaste[(t, W2H)])




# Capacity Constraints
def capacity_elp_rule(M, t, power_stay):
    return M.elp[(t, power_stay)] <= M.specs[(power_stay, 'cap')]


# def capacity_elp1_rule(M, t, power_ex):
    # return M.elp[(t, power_ex)] <= (M.New[power_ex] + M.specs[(power_ex, 'cap')])
    return M.elp[(t, power_ex)] - M.New[power_ex] <= M.specs[(power_ex, 'cap')]


def capacity_eld_rule(M, t, flexible_stay):
    return M.eld[(t, flexible_stay)] <= M.specs[(flexible_stay, 'cap')]


def capacity_eld1_rule(M, t, flexible_ex):
    # return M.eld[(t, flexible_ex)] <= (M.New[flexible_ex] + M.specs[(flexible_ex, 'cap')])
    return M.eld[(t, flexible_ex)] - M.New[flexible_ex] <= M.specs[(flexible_ex, 'cap')]


# Capacity for Heat
def capacity_heatP_rule(M, t, F2H):
    # return M.heatP[(t, F2H)] <= (M.specs[(F2H, 'cap')] + M.New[F2H])
    return M.heatP[(t, F2H)] - M.New[F2H] <= M.specs[(F2H, 'cap')]


# Storage Constraints
def storage_pumped_constraint_rule(M, t):
    # return M.SOC[t] <= M.specs[('pumped', 'storage')]
    return M.SOC[t] <= M.specs[('pumped', 'storage')]


def storage_thermal_constraint_rule(M, t):
    # return M.SOC_th[t] <= (M.New['TES_DH'] + M.specs[('TES_DH', 'cap')])
    return M.SOC_th[t] - M.New['TES_DH'] <= M.specs[('TES_DH', 'cap')]


def storage_gas_constraint_rule(M, t):
    # return M.SOC_gas[t] <= (M.New['Gas_storage'] + M.specs[('Gas_storage', 'cap')])
    return M.SOC_gas[t] - M.New['Gas_storage'] <= M.specs[('Gas_storage', 'cap')]


# EV Related Equations
def EV_battery_SOC_rule(M, t):
    if t > 1:
        # return M.SOC_EV[t] == (M.SOC_EV[t - 1] + (0.9 * M.eld[(t - 1, 'EV')]) - M.el_g2v[t - 1])
        return - (0.9 * M.eld[(t - 1, 'EV')]) - M.SOC_EV[t - 1] + M.SOC_EV[t] == - M.el_g2v[t - 1]

    return Constraint.Skip


def EV_SOC_cap_rule(M, t):
    return (0.1 * value(M.N_Evs) * value(M.bat_cap), M.SOC_EV[t], 0.9 * value(M.N_Evs) * value(M.bat_cap))


def EV_charging_cap_rule(M, t):
    return M.eld[(t, 'EV')] <= M.hourly_capacity_EV[t]


def EV_SOC_ini_rule(M, t):
    if t == 1:
        return M.SOC_EV[t] == (0.5 * value(M.N_Evs) * value(M.bat_cap))

    return Constraint.Skip


def EV_SOC_end_rule(M, t):
    if t == 8760:
        return M.SOC_EV[t] >= (0.5 * value(M.N_Evs) * value(M.bat_cap))

    return Constraint.Skip


def EV_daily_rule(M, d):
    # return sum([M.eld[(t, 'EV')] for t in M.t if M.day[t] == d]) >= (
    #             0.5 * sum([M.el_g2v[t] for t in M.t if M.day[t] == d]))
    return sum([M.eld[(t, 'EV')] for t in M.t if M.day[t] == d]) >= (0.5 * sum([M.el_g2v[t] for t in M.t if M.day[t] == d]))


def EV_weekly_rule(M, w):
    # return sum([M.eld[(t, 'EV')] for t in M.t if M.week[t] == w]) >= (
    #             0.8 * sum([M.el_g2v[t] for t in M.t if M.week[t] == w]))
    return sum([M.eld[(t, 'EV')] for t in M.t if M.week[t] == w]) >= (0.8 * sum([M.el_g2v[t] for t in M.t if M.week[t] == w]))


# Pumped Hydro Equations
def hydro_soc_rule(M, t):
    if t > 1:
        # return M.SOC[t] == (M.SOC[t - 1]
        #                     + (M.specs[('pumped', 'eff_de')] * M.eld[(t - 1, 'pumped')])
        #                     - (M.elp[(t - 1, 'pumped')] / M.specs[('pumped', 'eff_pe')]))
        return (M.elp[(t - 1, 'pumped')] / M.specs[('pumped', 'eff_pe')]) - (M.specs[('pumped', 'eff_de')] * M.eld[(t - 1, 'pumped')]) - M.SOC[t - 1] + M.SOC[t] == 0

    return Constraint.Skip


def hydro_soc_boundary_rule(M, t):
    if t == 1 or t == 8760:
        return M.SOC[t] == (M.specs[('pumped', 'storage')] * 0.5)

    return Constraint.Skip


def hydro_charge_rule(M, t):
    return M.eld[(t, 'pumped')] <= M.specs[('pumped', 'cap')]


def hydro_discharge_rule(M, t):
    return M.elp[(t, 'pumped')] <= M.specs[('pumped', 'cap')]

#New Equation
# def ratio_PV_WT_off1_rule(M):
    # return (value(M.ratio_PV) * sum([(M.h_wind[t] * (M.New['Wind_on'] + M.specs[('Wind_on', 'cap')])
    #                                   + M.offshore[t] * (M.New['Wind_off'] + M.specs[('Wind_off', 'cap')])) for t in M.t])
    #         == value(M.ratio_WT) * sum([M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')]) for t in M.t]))
    # return (sum([(value(M.ratio_PV) * M.h_wind[t] * M.New['Wind_on']) + (value(M.ratio_PV) * M.offshore[t] * M.New['Wind_off']) - (value(M.ratio_WT) * M.h_solar[t] * M.New['PV']) for t in M.t])
        # == sum([(value(M.ratio_WT) * M.h_solar[t] * M.specs[('PV', 'cap')]) - (value(M.ratio_PV) * M.h_wind[t] *  M.specs[('Wind_on', 'cap')]) - (value(M.ratio_PV) * M.offshore[t] * M.specs[('Wind_off', 'cap')]) for t in M.t]))
    return sum([M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')]) for t in M.t])==M.ratio_PV*sum(M.offshore[t] * (M.New['Wind_off']+M.specs[('Wind_off', 'cap')])+M.h_wind[t]*(M.New['Wind_on']+M.specs[('Wind_on','cap')])
      +M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')]) for t in M.t)

# def ratio_PV_WT_off2_rule(M):
    return sum(M.offshore[t] * (M.New['Wind_off']+M.specs[('Wind_off', 'cap')]) for t in M.t)==M.ratio_WT_off*sum(M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')])+M.h_wind[t]*(M.New['Wind_on']+M.specs[('Wind_on','cap')])
      +M.offshore[t] * (M.New['Wind_off']+M.specs[('Wind_off', 'cap')]) for t in M.t)
      
# def ratio_PV_WT_off3_rule(M):
    return sum(M.h_wind[t]*(M.New['Wind_on']+M.specs[('Wind_on','cap')]) for t in M.t)==M.ratio_WT*sum(M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')])+M.h_wind[t]*(M.New['Wind_on']+M.specs[('Wind_on','cap')])
      +M.offshore[t] * (M.New['Wind_off']+M.specs[('Wind_off', 'cap')]) for t in M.t)
    


# Battery Equation
def battery_SOC_rule(M, t):
    if t > 1:
        return M.SOC_battery[t] == (((1 - 0.0001) * M.SOC_battery[t - 1])
                                    + (M.specs[('battery', 'eff_de')] * M.eld[(t - 1, 'b_interface')])
                                    - (M.elp[(t - 1, 'b_interface')] / M.specs[('battery', 'eff_pe')]))

    return Constraint.Skip


def battery_SOC_boundary_rule(M, t):
    if t == 1 or t == 8760:
        return M.SOC_battery[t] == ((M.New['battery'] + M.specs[('battery', 'cap')]) * 0.5)

    return Constraint.Skip


def battery_charge_rule(M, t):
    return M.eld[(t, 'b_interface')] <= (M.New['b_interface'] + M.specs[('b_interface', 'cap')])


def battery_discharge_rule(M, t):
    return M.elp[(t, 'b_interface')] <= (M.New['b_interface'] + M.specs[('b_interface', 'cap')])


def battery_storage_cap_rule(M, t):
    return M.SOC_battery[t] <= (M.New['battery'] + M.specs['battery', 'cap'])


def battery_power_energy_rule(M, t):
    return (M.New['b_interface'] + M.specs[('b_interface', 'cap')]) <= (
                (M.New['battery'] + M.specs[('battery', 'cap')]) / 6.)


def binary_charge_rule(M, t):
    # return M.eld[(t, 'b_interface')] / 10000000000 <= M.bi_battery_ch[t]
    return M.eld[(t, 'b_interface')] <= M.bi_battery_ch[t]


def binary_discharge_rule(M, t):
    # return M.elp[(t, 'b_interface')] / 10000000000 <= M.bi_battery_dis[t]
    return M.elp[(t, 'b_interface')] <= M.bi_battery_dis[t]


def binary_decision_rule(M, t):
    return M.bi_battery_ch[t] + M.bi_battery_dis[t] <= 1.5


# Emission Constraints
def em_amount_rule(M):
    return M.em == ((sum([M.LNG[(t, tech)] for t in M.t for tech in M.tech]) * M.fossil[('NG', 'em')]) 
                    +(sum([M.elp[t, 'National_Grid'] for t in M.t]) * M.fossil[('N_grid', 'em')]))
                


def em_limit_rule(M):
    # return M.em <= value(M.em_cap)
    return M.em == value(M.em_cap)


# Biogas constraints
# def Solidwaste_limit_rule(M, t):
    return M.Solidwaste <= value(M.Solidwaste_cap)/8760

# Newly Added
# def WasteP_limit_rule(M, t):
#     return M.WasteP[t] <= (M.Ncost[t] * (M.New['SMR'] + M.specs[('SMR', 'cap')]))

# Environmental Infra constraints
def SMR_conversion_rule(M, t):
    return M.eld[(t, 'SMR')] == value(M.Biogas_cap)/8760

def WtX_conversion_rule(M, t):
    return M.elp[(t, 'Waste')] == value(M.Solidwaste_cap)/8760/4

def N_grid_rule(M, t):
    return M.elp[(t, 'National_Grid')] == value(M.N_grid_cap)/8760

def N_grid_rule1(M, t):
    return M.eld[(t, 'National_Grid')] <= value(M.N_grid_cap)/8760

# using by hydrogen fuels = excel based constant
def H_grid_rule1(M, t):
    return M.gas[(t, 'H2_Grid')] <= (M.New['H2_Grid'] + M.specs[('H2_Grid', 'cap')])

def H_grid_rule2(M, t):
    return sum([M.gas[(t, gas_all)] for gas_all in M.gas_all]) == value(M.gas_S)

def H_grid_rule(M, t):
    return M.gasP[(t, 'H2_Grid')] == (value(M.H_grid_cap)/8760 + value(M.gas_S) * (M.hydrogen_import_share))/8760

# def binary_H_grid_ch_rule(M, t):
    return M.gas[(t, 'GS_interface')] <= M.bi_H_grid_ch[t]

# def binary_H_grid_dch_rule(M, t):
    return M.gasP[(t, 'GS_interface')] <= M.bi_H_grid_dch[t]

# def binary_H_grid_decision_rule(M, t):
    return M.bi_H_grid_ch[t] + M.bi_H_grid_dch[t] <= 1.5


# National_Grid_in constraints
# def National_Grid_limit_rule(M, t):
    # return sum(M.elp[t, 'National_Grid'] for t in M.t) <= (sum(M.hourly_demand[t] for t in M.t) * M.electricity_import_share)
    return sum(M.elp[t, 'National_Grid'] for t in M.t) == (value(M.EL) * 1000000 * M.electricity_import_share) # 선언하는데 시간이 오래 걸림(180초 이상)
    

# Curtailment Limit
def curtailment_limit_rule(M, t):
    # return M.curtail[t] <= ((M.h_wind[t] * (M.New['Wind_on'] + M.specs[('Wind_on', 'cap')]))
    #                         + M.offshore[t] * (M.New['Wind_off'] + M.specs[('Wind_off', 'cap')])
    #                         + (M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')])))
    return M.curtail[t] <= ((M.h_wind[t] * (M.New['Wind_on'] + M.specs[('Wind_on', 'cap')]))
                            + M.offshore[t] * (M.New['Wind_off'] + M.specs[('Wind_off', 'cap')])
                            + (M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')])))

# Newly Added
def new_added_constraints_rule(M, Upperlimit):
    return M.New[Upperlimit] <= M.Potential[Upperlimit]

def EV_daily_rule(M, d):
    # return sum([M.eld[(t, 'EV')] for t in M.t if M.day[t] == d]) >= (
    #             0.5 * sum([M.el_g2v[t] for t in M.t if M.day[t] == d]))
    return sum([M.eld[(t, 'EV')] for t in M.t if M.day[t] == d]) >= (0.5 * sum([M.el_g2v[t] for t in M.t if M.day[t] == d]))