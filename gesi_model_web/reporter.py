import json
import os
import pandas as pd
from pyomo.core import value

from gesi_model_web.core.logger import Logger


class Reporter:
    def __init__(self, configuration, data, logger):
        self._result_path = configuration.result_path
        self._data = data
        self._graph_data = dict()
        self._logger = Logger(self.__class__.__name__, logger)

        if not os.path.exists(self._result_path):
            os.mkdir(self._result_path)

        self.t = 8760
        result_set_path = configuration.result_set_path
        with open(result_set_path) as f:
            self.result_sets = json.load(f)

        self.year = configuration.year
        # self.ndc = configuration.ndc
        # self.ratio_pv = configuration.ratio_pv
        # self.ratio_wt = configuration.ratio_wt
        # self.building_retrofit_rate = configuration.building_retrofit_rate
        # self.BEVs_share = configuration.BEVs_share

        self.result_yaml = None
        self.result_xlsx = None
        self.result_json = None

        if self.year < 2035:
            filename = '{}'.format(self.year)

        elif self.year > 2034:
            filename = '{}'.format(self.year)

        else:
            return

        self.result_yaml = os.path.join(self._result_path, '{}.yaml'.format(filename))
        self.result_xlsx = os.path.join(self._result_path, '{}.xlsx'.format(filename))
        self.result_json = os.path.join(self._result_path, '{}.json'.format(filename))

    def save_result(self, instance, result):
        # Report solver result
        result.write(filename=self.result_yaml)

        # Report xlsx results
        self._logger.print_info_line("Start reporting result.")
        index = [i for i in range(1, self.t + 1)]
        index = index + ['total sum']
        scalar_index = ['value']
        year_index = [' ', self.year]

        rep = self.report_rep(instance)
        rep_h = self.report_rep_h(instance)
        rep_g = self.report_rep_g(instance)
        new_invest = self.report_new_invest(instance)
        rep_annual = self.report_rep_annual(instance)
        rep_economic = self.report_rep_economic(instance)
        # energy_demand_index, energy_demand = self.report_energy_demand()
        facility_configuration = self.report_facility_configuration()
        power_generation = self.report_power_generation()
        p2h = self.report_p2h()
        # p2h_extended_index, p2h_extended = self.report_p2h_extended()
        # p2g = self.report_p2g()
        # p2g_extended = self.report_p2g_extended()

        df1 = pd.DataFrame(rep, index=index)
        df2 = pd.DataFrame(rep_h, index=index)
        df3 = pd.DataFrame(rep_g, index=index)
        df4 = pd.DataFrame(new_invest, index=scalar_index)
        df5 = pd.DataFrame(rep_annual, index=scalar_index)
        df7 = pd.DataFrame(rep_economic, index=scalar_index)
        df9 = pd.DataFrame(facility_configuration, index=scalar_index)
        df10 = pd.DataFrame(power_generation, index=scalar_index)


        writer = pd.ExcelWriter(self.result_xlsx, engine='xlsxwriter')

        df1.to_excel(writer, sheet_name='rep')
        df2.to_excel(writer, sheet_name='rep_h')
        df3.to_excel(writer, sheet_name='rep_g')
        df4.to_excel(writer, sheet_name='new_invest')
        df5.to_excel(writer, sheet_name='rep_annual')
        df7.to_excel(writer, sheet_name='rep_economic')
        df9.to_excel(writer, sheet_name='설비구성')
        df10.to_excel(writer, sheet_name='발전량')
 

        writer.save()
        self._logger.print_info_line("Reporting Excel Data Complete")

        with open(self.result_json, 'w') as f:
            json.dump(self._graph_data, f)

        self._logger.print_info_line("Reporting Json Data Complete")

    def report_rep(self, instance):
        rep = dict()
        graph_data = dict()

        sum_el_demand = 0
        sum_pv = 0
        sum_wt = 0
        sum_Waste = 0
        sum_pp = 0
        sum_chp = 0
        sum_fcell = 0
        sum_battery_out = 0
        sum_pumped_out = 0
        sum_p2h = 0
        sum_battery_in = 0
        sum_pumped_in = 0
        sum_e_boiler = 0
        sum_dh_boiler = 0
        sum_ev = 0
        sum_electrolysis = 0
        sum_curtail = 0
        sum_pumped_soc = 0
        sum_battery_soc = 0
        sum_lng = 0
        sum_ng_consumption = 0
        sum_SMR = 0
        sum_National_Grid_in = 0
        sum_National_Grid_out = 0

        for key in self.result_sets['representation']:
            rep[key] = list()
            graph_data[key] = dict()

        for t in range(1, self.t + 1):
            el_demand = value(instance.hourly_demand[t])

            rep['el_demand'].append(el_demand)
            graph_data['el_demand'][t] = el_demand
            sum_el_demand += el_demand

            
            pv = value(instance.h_solar[t] * (instance.specs[('PV', 'cap')] + instance.New['PV']))
            graph_data['PV'][t] = pv
            rep['PV'].append(pv)
            sum_pv += pv

            wt = value(instance.h_wind[t] * (instance.specs[('Wind_on', 'cap')] + instance.New['Wind_on'])
                       + instance.offshore[t] * (instance.specs[('Wind_off', 'cap')] + instance.New['Wind_off']))
            rep['WT'].append(wt)
            graph_data['WT'][t] = wt
            sum_wt += wt

            rep['Waste'].append(value(instance.elp[(t, 'Waste')]))
            graph_data['Waste'][t] = value(instance.elp[(t, 'Waste')]) 
            sum_Waste += value(instance.elp[(t, 'Waste')])

            rep['PP'].append(value(instance.elp[(t, 'PP')]))
            graph_data['PP'][t] = value(instance.elp[(t, 'PP')])
            sum_pp += value(instance.elp[(t, 'PP')])

            rep['CHP'].append(value(instance.elp[(t, 'CHP')]))
            graph_data['CHP'][t] = value(instance.elp[(t, 'CHP')])
            sum_chp += value(instance.elp[(t, 'CHP')])

            rep['Fcell'].append(value(instance.elp[(t, 'Fcell')]))
            graph_data['Fcell'][t] = value(instance.elp[(t, 'Fcell')])
            sum_fcell += value(instance.elp[(t, 'Fcell')])

            rep['battery_out'].append(value(instance.elp[(t, 'b_interface')]))
            graph_data['battery_out'][t] = value(instance.elp[(t, 'b_interface')])
            sum_battery_out += value(instance.elp[(t, 'b_interface')])

            rep['pumped_out'].append(value(instance.elp[(t, 'pumped')]))
            graph_data['pumped_out'][t] = value(instance.elp[(t, 'pumped')])
            sum_pumped_out += value(instance.elp[(t, 'pumped')])

            p2h = value(instance.eld[(t, 'DH_HP')])
            rep['P2H'].append(p2h)
            graph_data['P2H'][t] = p2h
            sum_p2h += p2h

            rep['battery_in'].append(value(instance.eld[(t, 'b_interface')]))
            graph_data['battery_in'][t] = value(instance.eld[(t, 'b_interface')])
            sum_battery_in += value(instance.eld[(t, 'b_interface')])

            rep['pumped_in'].append(value(instance.eld[(t, 'pumped')]))
            graph_data['pumped_in'][t] = value(instance.eld[(t, 'pumped')])
            sum_pumped_in += value(instance.eld[(t, 'pumped')])

            rep['E_boiler'].append(value(instance.eld[(t, 'E_boiler')]))
            graph_data['E_boiler'][t] = value(instance.eld[(t, 'E_boiler')])
            sum_e_boiler += value(instance.eld[(t, 'E_boiler')])

            rep['DH_Boiler'].append(value(instance.eld[(t, 'DH_Boiler')]))
            graph_data['DH_Boiler'][t] = value(instance.eld[(t, 'DH_Boiler')])
            sum_dh_boiler += value(instance.eld[(t, 'DH_Boiler')])

            ev = value(instance.eld[(t, 'EV')])
            rep['EV'].append(ev)
            graph_data['EV'][t] = ev
            sum_ev += ev

            rep['electrolysis'].append(value(instance.eld[(t, 'electrolysis')]))
            graph_data['electrolysis'][t] = value(instance.eld[(t, 'electrolysis')])
            sum_electrolysis += value(instance.eld[(t, 'electrolysis')])

            rep['curtail'].append(value(instance.curtail[t]))
            graph_data['curtail'][t] = value(instance.curtail[t])
            sum_curtail += value(instance.curtail[t])

            rep['pumped_soc'].append(value(instance.SOC[t]))
            graph_data['pumped_soc'][t] = value(instance.SOC[t])
            sum_pumped_soc += value(instance.SOC[t])

            rep['battery_soc'].append(value(instance.SOC_battery[t]))
            graph_data['battery_soc'][t] = value(instance.SOC_battery[t])
            sum_battery_soc += value(instance.SOC_battery[t])

            rep['SMR'].append(value(instance.eld[(t, 'SMR')]))
            graph_data['SMR'][t] = value(instance.eld[(t, 'SMR')])
            sum_SMR += value(instance.eld[(t, 'SMR')])

            rep['National_Grid_out'].append(value(instance.elp[(t, 'National_Grid')]))
            graph_data['National_Grid_out'][t] = value(instance.elp[(t, 'National_Grid')])
            sum_National_Grid_out += value(instance.elp[(t, 'National_Grid')])

            rep['National_Grid_in'].append(value(instance.eld[(t, 'National_Grid')]))
            graph_data['National_Grid_in'][t] = value(instance.eld[(t, 'National_Grid')])
            sum_National_Grid_in += value(instance.eld[(t, 'National_Grid')])


            if t == 1:
                LNG = value(sum([instance.LNG[(t, tech)] for t in instance.t for tech in instance.tech]))
                sum_lng = LNG
                graph_data['LNG'][1] = LNG
            else:
                LNG = ""

            rep['LNG'].append(LNG)

        rep['el_demand'].append(sum_el_demand)
        rep['PV'].append(sum_pv)
        rep['WT'].append(sum_wt)
        rep['Waste'].append(sum_Waste)
        rep['PP'].append(sum_pp)
        rep['CHP'].append(sum_chp)
        rep['Fcell'].append(sum_fcell)
        rep['battery_out'].append(sum_battery_out)
        rep['pumped_out'].append(sum_pumped_out)
        rep['P2H'].append(sum_p2h)
        rep['battery_in'].append(sum_battery_in)
        rep['pumped_in'].append(sum_pumped_in)
        rep['E_boiler'].append(sum_e_boiler)
        rep['DH_Boiler'].append(sum_dh_boiler)
        rep['EV'].append(sum_ev)
        rep['electrolysis'].append(sum_electrolysis)
        rep['SMR'].append(sum_SMR)
        rep['National_Grid_in'].append(sum_National_Grid_in)
        rep['National_Grid_out'].append(sum_National_Grid_out)
        rep['curtail'].append(sum_curtail)
        rep['pumped_soc'].append(sum_pumped_soc)
        rep['battery_soc'].append(sum_battery_soc)
        rep['LNG'].append(sum_lng)
        rep['NG_consumption'].append(sum_ng_consumption)

        graph_data['el_demand']['total'] = sum_el_demand
        graph_data['PV']['total'] = sum_pv
        graph_data['WT']['total'] = sum_wt
        graph_data['Waste']['total'] = sum_Waste
        graph_data['PP']['total'] = sum_pp
        graph_data['CHP']['total'] = sum_chp
        graph_data['Fcell']['total'] = sum_fcell
        graph_data['battery_out']['total'] = sum_battery_out
        graph_data['pumped_out']['total'] = sum_pumped_out
        graph_data['P2H']['total'] = sum_p2h
        graph_data['battery_in']['total'] = sum_battery_in
        graph_data['pumped_in']['total'] = sum_pumped_in
        graph_data['E_boiler']['total'] = sum_e_boiler
        graph_data['DH_Boiler']['total'] = sum_dh_boiler
        graph_data['EV']['total'] = sum_ev
        graph_data['electrolysis']['total'] = sum_electrolysis
        graph_data['SMR']['total'] = sum_SMR
        graph_data['National_Grid_in']['total'] = sum_National_Grid_in
        graph_data['National_Grid_out']['total'] = sum_National_Grid_out
        graph_data['curtail']['total'] = sum_curtail
        graph_data['pumped_soc']['total'] = sum_pumped_soc
        graph_data['battery_soc']['total'] = sum_battery_soc
        graph_data['LNG']['total'] = sum_lng
        graph_data['NG_consumption']['total'] = sum_ng_consumption

        self._graph_data['rep'] = graph_data

        return rep

    def report_rep_h(self, instance):
        rep_h = dict()
        graph_data = dict()

        for key in self.result_sets['H_representation']:
            rep_h[key] = list()
            graph_data[key] = dict()

        sum_heat_demand = 0
        sum_chp_h = 0
        sum_Waste_h = 0
        sum_fcell_h = 0
        sum_dh_hp_h = 0
        sum_dh_boiler = 0
        sum_e_boiler_h = 0
        sum_soc_th = 0
        sum_dis_th = 0
        sum_ch_th = 0

        for t in range(1, self.t + 1):
            rep_h['heat_demand'].append(value(instance.hourly_heat[t]))
            graph_data['heat_demand'][t] = value(instance.hourly_heat[t])
            sum_heat_demand += value(instance.hourly_heat[t])

            rep_h['CHP_h'].append(value(instance.heatP[(t, 'CHP')]))
            graph_data['CHP_h'][t] = value(instance.heatP[(t, 'CHP')])
            sum_chp_h += value(instance.heatP[(t, 'CHP')])

            rep_h['Waste_h'].append(value(instance.heatP[(t, 'Waste')]))
            graph_data['Waste_h'][t] = value(instance.heatP[(t, 'Waste')])
            sum_Waste_h += value(instance.heatP[(t, 'Waste')])

            rep_h['Fcell_h'].append(value(instance.heatP1[(t, 'Fcell')]))
            graph_data['Fcell_h'][t] = value(instance.heatP1[(t, 'Fcell')])
            sum_fcell_h += value(instance.heatP1[(t, 'Fcell')])

            rep_h['DH_HP_h'].append(value(instance.heatP[(t, 'DH_HP')]))
            graph_data['DH_HP_h'][t] = value(instance.heatP[(t, 'DH_HP')])
            sum_dh_hp_h += value(instance.heatP[(t, 'DH_HP')])

            rep_h['DH_Boiler'].append(value(instance.heatP[(t, 'DH_Boiler')]))
            graph_data['DH_Boiler'][t] = value(instance.heatP[(t, 'DH_Boiler')])
            sum_dh_boiler += value(instance.heatP[(t, 'DH_Boiler')])

            rep_h['E_boiler_h'].append(value(instance.heatP[(t, 'E_boiler')]))
            graph_data['E_boiler_h'][t] = value(instance.heatP[(t, 'E_boiler')])
            sum_e_boiler_h += value(instance.heatP[(t, 'E_boiler')])

            rep_h['SOC_th'].append(value(instance.SOC_th[t]))
            graph_data['SOC_th'][t] = value(instance.SOC_th[t])
            sum_soc_th += value(instance.SOC_th[t])

            rep_h['dis_th'].append(value(instance.dis_th[t]))
            graph_data['dis_th'][t] = value(instance.dis_th[t])
            sum_dis_th += value(instance.dis_th[t])

            rep_h['ch_th'].append(value(instance.ch_th[t]))
            graph_data['ch_th'][t] = value(instance.ch_th[t])
            sum_ch_th += value(instance.ch_th[t])

        rep_h['heat_demand'].append(sum_heat_demand)
        rep_h['CHP_h'].append(sum_chp_h)
        rep_h['Waste_h'].append(sum_Waste_h)
        rep_h['Fcell_h'].append(sum_fcell_h)
        rep_h['DH_HP_h'].append(sum_dh_hp_h)
        rep_h['DH_Boiler'].append(sum_dh_boiler)
        rep_h['E_boiler_h'].append(sum_e_boiler_h)
        rep_h['SOC_th'].append(sum_soc_th)
        rep_h['dis_th'].append(sum_dis_th)
        rep_h['ch_th'].append(sum_ch_th)

        graph_data['heat_demand']['total'] = sum_heat_demand
        graph_data['CHP_h']['total'] = sum_chp_h
        graph_data['Waste_h']['total'] = sum_Waste_h
        graph_data['Fcell_h']['total'] = sum_fcell_h
        graph_data['DH_HP_h']['total'] = sum_dh_hp_h
        graph_data['DH_Boiler']['total'] = sum_dh_boiler
        graph_data['E_boiler_h']['total'] = sum_e_boiler_h
        graph_data['SOC_th']['total'] = sum_soc_th
        graph_data['dis_th']['total'] = sum_dis_th
        graph_data['ch_th']['total'] = sum_ch_th

        self._graph_data['rep_h'] = graph_data

        return rep_h

    def report_rep_g(self, instance):
        rep_g = dict()
        graph_data = dict()

        for key in self.result_sets['G_representation']:
            rep_g[key] = list()
            graph_data[key] = dict()

        sum_gas_demand = 0
        sum_electrolysis = 0
        sum_SMR = 0
        sum_chp = 0
        sum_fcell = 0
        sum_pp = 0
        sum_gas_charging = 0
        sum_gas_discharging = 0
        sum_H2_grid_in = 0
        sum_H2_grid_out = 0
        sum_gas_soc = 0
        sum_lng_consumption = 0

        for t in range(1, self.t + 1):
            if self.year < 2035:
                gas_demand = value(instance.industry_gas[t] + sum([instance.gas[(t, gas_all)] for gas_all in instance.gas_all]))
            elif self.year > 2034:
                gas_demand = value(instance.industry_gas[t] + sum([instance.gas[(t, gas_all)] for gas_all in instance.gas_all]))
            else:
                raise ValueError('Wrong year')

            rep_g['gas_demand'].append(gas_demand)
            graph_data['gas_demand'][t] = gas_demand
            sum_gas_demand += gas_demand

            rep_g['electrolysis'].append(value(instance.gasP[(t, 'electrolysis')]))
            graph_data['electrolysis'][t] = value(instance.gasP[(t, 'electrolysis')])
            sum_electrolysis += value(instance.gasP[(t, 'electrolysis')])

            rep_g['SMR'].append(value(instance.gasP[(t, 'SMR')]))
            graph_data['SMR'][t] = value(instance.gasP[(t, 'SMR')])
            sum_SMR += value(instance.gasP[(t, 'SMR')])

            rep_g['CHP'].append(value(instance.gas[(t, 'CHP')]))
            graph_data['CHP'][t] = value(instance.gas[(t, 'CHP')])
            sum_chp += value(instance.gas[(t, 'CHP')])

            rep_g['Fcell'].append(value(instance.gas1[(t, 'Fcell')]))
            graph_data['Fcell'][t] = value(instance.gas1[(t, 'Fcell')])
            sum_fcell += value(instance.gas1[(t, 'Fcell')])

            rep_g['PP'].append(value(instance.gas[(t, 'PP')]))
            graph_data['PP'][t] = value(instance.gas[(t, 'PP')])
            sum_pp += value(instance.gas[(t, 'PP')])

            rep_g['gas_charging'].append(value(instance.ch_gas[t]))
            graph_data['gas_charging'][t] = value(instance.ch_gas[t])
            sum_gas_charging += value(instance.ch_gas[t])

            rep_g['gas_discharging'].append(value(instance.dis_gas[t]))
            graph_data['gas_discharging'][t] = value(instance.dis_gas[t])
            sum_gas_discharging += value(instance.dis_gas[t])

            rep_g['gas_SOC'].append(value(instance.SOC_gas[t]))
            graph_data['gas_SOC'][t] = value(instance.SOC_gas[t])
            sum_gas_soc += value(instance.SOC_gas[t])

            rep_g['H2_grid_out'].append(value(instance.gasP[(t, 'H2_Grid')]))
            graph_data['H2_grid_out'][t] = value(instance.gasP[(t, 'H2_Grid')])
            sum_H2_grid_out += value(instance.gasP[(t, 'H2_Grid')])

            rep_g['H2_grid_in'].append(value(instance.gas[(t, 'H2_Grid')]))
            graph_data['H2_grid_in'][t] = value(instance.gas[(t, 'H2_Grid')])
            sum_H2_grid_in += value(instance.gas[(t, 'H2_Grid')])

            lng_consumption = value(sum([instance.LNG[(t, tech)] for tech in instance.tech]))
            rep_g['LNG_consumption'].append(lng_consumption)
            graph_data['LNG_consumption'][t] = lng_consumption
            sum_lng_consumption += lng_consumption

        rep_g['gas_demand'].append(sum_gas_demand)
        rep_g['electrolysis'].append(sum_electrolysis)
        rep_g['SMR'].append(sum_SMR)
        rep_g['CHP'].append(sum_chp)
        rep_g['Fcell'].append(sum_fcell)
        rep_g['PP'].append(sum_pp)
        rep_g['gas_charging'].append(sum_gas_charging)
        rep_g['gas_discharging'].append(sum_gas_discharging)
        rep_g['gas_SOC'].append(sum_gas_soc)
        rep_g['H2_grid_out'].append(sum_H2_grid_out)
        rep_g['H2_grid_in'].append(sum_H2_grid_in)
        rep_g['LNG_consumption'].append(sum_lng_consumption)

        graph_data['gas_demand']['total'] = sum_gas_demand
        graph_data['electrolysis']['total'] = sum_electrolysis
        graph_data['SMR']['total'] = sum_SMR
        graph_data['CHP']['total'] = sum_chp
        graph_data['Fcell']['total'] = sum_fcell
        graph_data['PP']['total'] = sum_pp
        graph_data['gas_charging']['total'] = sum_gas_charging
        graph_data['gas_discharging']['total'] = sum_gas_discharging
        graph_data['gas_SOC']['total'] = sum_gas_soc
        graph_data['H2_grid_out']['total'] = sum_H2_grid_out
        graph_data['H2_grid_in']['total'] = sum_H2_grid_in
        graph_data['LNG_consumption']['total'] = sum_lng_consumption

        self._graph_data['rep_g'] = graph_data

        return rep_g

    def report_new_invest(self, instance):
        new_invest = dict()

        for expand in instance.expand:
            new_invest[expand] = value(instance.New[expand])

        self._graph_data['new_invest'] = new_invest

        return new_invest

    def report_rep_annual(self, instance):
        rep_annual = dict()

        rep_annual['em_power'] = value(instance.em)
        rep_annual['curtailment'] = value(sum([instance.curtail[t] for t in instance.t]))

        RE_sharp_p = (sum([instance.h_wind[t] * (instance.New['Wind_on'] + instance.specs[('Wind_on', 'cap')])
                           + instance.offshore[t] * (instance.New['Wind_off'] + instance.specs[('Wind_off', 'cap')])
                           + instance.h_solar[t] * (instance.New['PV'] * instance.specs[('PV', 'cap')])
                           for t in instance.t])
                      - (sum([instance.curtail[t] for t in instance.t]) / sum([instance.hourly_demand[t] for t in instance.t])))
        rep_annual['RE_share_p'] = value(RE_sharp_p)

        self._graph_data['rep_annual'] = {
            'em_power': value(instance.em)
        }

        return rep_annual


    def report_rep_economic(self, instance):
        rep_economic = dict()

        investment = (
                sum([instance.New[expand] * instance.annuity[expand] for expand in instance.expand])
                + sum([instance.specs[(f_tech, 'cap')] * instance.annuity[f_tech] for f_tech in instance.f_tech])
        )
        rep_economic['investment'] = value(investment)

        fixed_operation = (
                sum([instance.New[expand] * (instance.annuity[expand] + instance.cost[(expand, 'fixed_OM')]) for expand in instance.expand])
                + sum([instance.specs[(tech, 'cap')] * instance.cost[(tech, 'fixed_OM')] for tech in instance.tech])
        )
        rep_economic['fixed_operation'] = value(fixed_operation)

        v_operation = (
                sum([instance.h_wind[t] * (instance.New['Wind_on'] + instance.specs[('Wind_on', 'cap')]) * instance.cost[('Wind_on', 'variable_OM')] for t in instance.t])
                + sum([instance.offshore[t] * (instance.New['Wind_off'] + instance.specs[('Wind_off', 'cap')]) * instance.cost[('Wind_off', 'variable_OM')] for t in instance.t])
                + sum([instance.h_solar[t] * (instance.New['PV'] + instance.specs[('PV', 'cap')]) * instance.cost[('PV', 'variable_OM')] for t in instance.t])
                + sum([instance.elp[(t, power)] * instance.cost[(power, 'variable_OM')] for t in instance.t for power in instance.power])
                + sum([instance.eld[(t, 'DH_HP')] * instance.cost[('DH_HP', 'variable_OM')] for t in instance.t])
                + sum([instance.dis_gas[t] * instance.cost[('GS_interface', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'electrolysis')] * instance.cost[('electrolysis', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'SMR')] * instance.cost[('SMR', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'National_Grid')] * instance.cost[('National_Grid', 'variable_OM')] for t in instance.t])
                + sum([instance.eld[(t, 'pumped')] * instance.cost[('pumped', 'variable_OM')] for t in instance.t])
        )
        rep_economic['v_operation'] = value(v_operation)

        fuel = (
            sum([instance.LNG[(t, tech)] * instance.fossil[('NG', 'price')] for t in instance.t for tech in instance.tech])
            
        )
        rep_economic['fuel'] = value(fuel)

        em_cost = value(instance.em) * instance.fossil[('emission', 'price')]
        rep_economic['em_cost'] = value(em_cost)

        self._graph_data['rep_economic'] = rep_economic

        return rep_economic

    def report_facility_configuration(self):
        pumped = 6700

      
        facility_configuration = {
            'Wind_on': self._graph_data['new_invest']['Wind_on'],
            'Wind_off': self._graph_data['new_invest']['Wind_off'],
            'PV': self._graph_data['new_invest']['PV'],
            'CHP': self._graph_data['new_invest']['CHP'],
            'Waste': self._graph_data['new_invest']['Waste'],
            'Fcell': self._graph_data['new_invest']['Fcell'],
            # 'Nuke': self._data['specs_extended'].loc['Nuke']['Final'] + self._graph_data['new_invest']['Nuke'],
            'DH_HP': self._graph_data['new_invest']['DH_HP'],
            'DH_boiler': self._graph_data['new_invest']['DH_Boiler'],
            'Electronic boiler': self._graph_data['new_invest']['E_boiler'],
            'Electrolysis': self._graph_data['new_invest']['electrolysis'],
            'Gas_interface': self._graph_data['new_invest']['GS_interface'],
            'b_interface': self._graph_data['new_invest']['b_interface'],
            # 'pumped': self._data['specs_extended'].loc['pumped']['Final'] + self._graph_data['new_invest']['pumped'],
            'pumped': pumped,
            'TES_DH': self._graph_data['new_invest']['TES_DH'],
            'Gas_storage': self._graph_data['new_invest']['Gas_storage'],
            'Battery': self._graph_data['new_invest']['battery'],
            'SMR': self._graph_data['new_invest']['SMR'],
            'National_Grid': self._graph_data['new_invest']['National_Grid']
        }

        self._graph_data['facility_configuration'] = facility_configuration

        return facility_configuration

    def report_power_generation(self):
        power_generation = {
            'WT': self._graph_data['rep']['WT']['total'] / 1000000,
            'PV': self._graph_data['rep']['PV']['total'] / 1000000,
            'CHP': self._graph_data['rep']['CHP']['total'] / 1000000,
            'Fcell': self._graph_data['rep']['Fcell']['total'] / 1000000,
            'Waste': self._graph_data['rep']['Waste']['total'] / 1000000,
            'Electrolysis': self._graph_data['rep']['electrolysis']['total'] / 1000000,
            'SMR': self._graph_data['rep']['SMR']['total'] / 1000000,
            'Electric boiler': self._graph_data['rep']['E_boiler']['total'] / 1000000,
            'EV': self._graph_data['rep']['EV']['total'] / 1000000,
            'Electricity demand': self._graph_data['rep']['el_demand']['total'] / 1000000,
            'P2H': self._graph_data['rep']['P2H']['total'] / 1000000,
            'Curtailment': self._graph_data['rep']['curtail']['total'] / 1000000,
        }

        self._graph_data['power_generation'] = power_generation

        return power_generation

    def report_p2h(self):
        p2h = {
            'F2H_fuel': [
                'fuel',
                self._graph_data['rep_h']['DH_Boiler']['total'] + (self._graph_data['rep_h']['CHP_h']['total'] / 0.4)
            ],
            'F2H_heat': [
                'heat',
                self._graph_data['rep_h']['CHP_h']['total'] + self._graph_data['rep_h']['DH_Boiler']['total']
            ],
            'P2H_elec': [
                'elec',
                self._graph_data['rep']['P2H']['total']
            ],
            'P2H_heat': [
                'heat',
                self._graph_data['rep_h']['DH_HP_h']['total'] 
            ]
        }

        self._graph_data['P2H'] = {
            'F2H': {
                'fuel': p2h['F2H_fuel'][1],
                'heat': p2h['F2H_heat'][1],
            },
            'P2H': {
                'elec': p2h['P2H_elec'][1],
                'heat': p2h['P2H_heat'][1]
            }
        }

        return p2h