from pyomo.core import value


def total_rule(M):
    return (sum([M.New[expand] * M.annuity[expand] for expand in M.expand])
            + sum([M.specs[(f_tech, 'cap')] * M.annuity[f_tech] for f_tech in M.f_tech])
            + sum([M.New[expand] * M.cost[(expand, 'fixed_OM')] for expand in M.expand])
            + sum([M.specs[(tech, 'cap')] * M.cost[(tech, 'fixed_OM')] for tech in M.tech])
            + sum([M.h_wind[t] * (M.New['Wind_on'] + M.specs[('Wind_on', 'cap')]) * M.cost[('Wind_on', 'variable_OM')] for t in M.t])
            + sum([M.offshore[t] * (M.New['Wind_off'] + M.specs[('Wind_off', 'cap')]) * M.cost[('Wind_off', 'variable_OM')] for t in M.t])
            + sum([M.h_solar[t] * (M.New['PV'] + M.specs[('PV', 'cap')]) * M.cost[('PV', 'variable_OM')] for t in M.t])
            + sum([M.elp[(t, power)] * M.cost[(power, 'variable_OM')] for t in M.t for power in M.power])
            + sum([M.eld[(t, 'DH_HP')] * M.cost[('DH_HP', 'variable_OM')] for t in M.t])
            + sum([M.dis_gas[t] * M.cost[('GS_interface', 'variable_OM')] for t in M.t])
            + sum([M.eld[(t, 'electrolysis')] * M.cost[('electrolysis', 'variable_OM')] for t in M.t])
            + sum([M.eld[(t, 'SMR')] * M.cost[('SMR', 'variable_OM')] for t in M.t])
            + sum([M.eld[(t, 'pumped')] * M.cost[('pumped', 'variable_OM')] for t in M.t])
            - sum([M.eld[(t, 'National_Grid')] * M.cost[('National_Grid', 'variable_OM')] for t in M.t])
            + sum([M.elp[(t, 'National_Grid')] * M.cost[('National_Grid', 'variable_OM')] for t in M.t])
            + sum(M.gasP[(t, 'H2_Grid')] * M.cost[('H2_Grid', 'variable_OM')] for t in M.t)  ### 20230412 수정
            - sum(M.gasG[(t, 'H2_Grid')] * M.cost[('H2_Grid', 'variable_OM')] for t in M.t)   ### 20230412 수정
            + sum([M.LNG[(t, tech)] * M.fossil[('NG', 'price')] for t in M.t for tech in M.tech])
            + (value(M.em) * M.fossil[('emission', 'price')]))
