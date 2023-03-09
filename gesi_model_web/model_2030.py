from pyomo.core import AbstractModel, Set, Param, Var, Objective, NonNegativeReals

from gesi_model_web.model_component import *


def create_model(name='gesi'):
    M = AbstractModel(name=name)
    M = define_set(M)
    M = define_parameter(M)
    M = define_variable(M)
    M = define_constraints(M)
    M = define_objective(M)

    return M


def define_set(M):
    """

    Set Definition

    """
    # 8760 hours for an year
    M.t = Set(doc='hours in a week', ordered=True)
    
    # technologies : subset by power, storage, thermal, mobile
    M.i_trait = Set(doc='individual power plants specification')
    M.dis = Set(doc='hourly distribution profile')
    M.tech = Set(doc='energy technologies')
    M.f_tech = Set(within=M.tech, doc='for annuity calculation except NG and coal individual plants')
    M.power = Set(within=M.tech, doc='electricity production')
    M.power_stay = Set(within=M.tech, doc='electricity production')
    M.power_ex = Set(within=M.tech, doc='electricity production')
    M.F2P = Set(within=M.tech, doc='electricity production')
    M.G2P = Set(within=M.tech, doc='electricity production from gas')
    M.P2P = Set(within=M.tech, doc='electricity production from electricity storage')
    M.F2H = Set(within=M.tech, doc='heat production from fuel')
    M.G2H = Set(within=M.tech, doc='heat production from gas')
    M.W2P = Set(within=M.tech, doc='electricity production from waste')
    M.W2H = Set(within=M.tech, doc='heat production from waste')
    M.flexible = Set(within=M.tech, doc='storage technologies')
    M.flexible_ex = Set(within=M.tech, doc='flexible technologies')
    M.flexible_stay = Set(within=M.tech, doc='flexible technologies stay')
    M.P2H = Set(within=M.tech, doc='power to heat technlogies')
    M.thermal = Set(within=M.tech, doc='thermal technologies')
    M.mobile = Set(within=M.tech, doc='inputdata technologies')
    M.expand = Set(within=M.f_tech, doc='expandable technologies')
    # M.RE = Set(within=M.tech, doc='renewable power plants')
    M.gas_all = Set(doc='Set for gas calculation')
    M.trait = Set(doc='technology specification')
    M.m = Set(doc='month')
    M.d = Set(doc='day')
    M.w = Set(doc='week')
    M.s = Set(doc='6hours interval')

    M.Upperlimit = Set(within=M.tech, doc='land area restrictions')

    M.fuel = Set(doc='fuels')
    
    M.coeff = Set(doc='coefficiencies')

    M.c = Set(doc='kinds of costs')

    return M


def define_parameter(M):
    """

    Parameter Definition

    """

    M.day = Param(M.t, initialize=init_day)
    M.week = Param(M.t, initialize=init_week)
    M.six = Param(M.t, initialize=init_six)

    M.Distributions = Param(M.t, M.dis, doc="hourly profiles")
    M.cost = Param(M.tech, M.c, doc="cost data from excel ($ per MWh or MW)")
    M.specs = Param(M.tech, M.trait, doc="specs of technology data from excel (GW percentage GWh)")
    M.fossil = Param(M.fuel, M.coeff, doc="price level of fossil fuels and emisson cost")
    M.Potential = Param(M.Upperlimit, doc="Potential of RE")


    M.em_cap = Param(doc="constraints of CO2 emissions")
    M.Solidwaste_cap = Param(doc="constraints of Solidwaste amounts")
    M.Biogas_cap = Param(doc="constraints of Biogas amounts")    
    M.N_grid_cap = Param()

    # M.ratio_PV = Param()
    # M.ratio_WT = Param()
    # M.ratio_WT_off = Param()
    M.hydrogen_import_share = Param()
    M.electricity_import_share = Param()

    M.sum_demand = Param(initialize=init_sum_demand, doc='demand summation')
    M.sum_H_demand = Param(initialize=init_sum_H_demand, doc='heat demand summation')
    M.sum_T_demand = Param(initialize=init_sum_T_demand, doc='summation of inputdata demand')
    M.max_wind = Param(initialize=init_max_wind, doc='max value in hourly wind profile')
    M.max_solar = Param(initialize=init_max_solar, doc='max value in hourl solar profile')
    M.h_demand = Param(M.t, initialize=init_h_demand, doc='hourly profile for electricity demand')
    M.h_H_demand = Param(M.t, initialize=init_h_H_demand, doc='hourly distribution profile for heat demand')
    M.h_wind = Param(M.t, initialize=init_h_wind, doc='hourly wind profile for caculation')
    M.h_solar = Param(M.t, initialize=init_h_solar, doc='hourl pv production profile for calculation')
    M.hourlytr = Param(M.t, initialize=init_hourlytr, doc='hourly transport demand profile')
  
    M.correction_wind = Param()
    M.offshore = Param(M.t, initialize=init_offshore)

    M.N_Evs = Param(doc="assumed number of EVs")
    M.av_distance = Param(doc="average traveling distance of an EV(km)")
    M.bat_cap = Param(doc="battery capacity per a EV (MWh)")
    M.c_rate = Param(doc="battery charging rate")
    M.M_share = Param(doc="max share of driving EVs on road")
    M.C_share = Param(doc="connection share of EVs")
    M.eff_EV = Param(doc="average effency of EVs (km per kwh)")

    M.EL = Param(doc="Annual electricity demand (TWh)")
    M.H = Param(doc="Annual Heating Demand (TWh)")
    M.discount = Param(doc="discount rate (%)")
    M.gas_D = Param(doc="annual gas demand (TWh)")

    M.A_EV = Param(initialize=init_A_EV, doc="annual electricity demand total for inputdata")
    M.ch_cap = Param(initialize=init_ch_cap, doc="charging capacity for a fleet of EVs (MWh)")

    M.hourly_demand = Param(M.t, initialize=init_hourly_demand, doc='hourly electricity demand')
    M.hourly_heat = Param(M.t, initialize=init_hourly_heat, doc='hourly heat demand')
    M.annuity = Param(M.f_tech, initialize=init_annuity, doc="annualized investment cost for technologies")

    # Scalar
    
    M.el_g2v = Param(M.t, initialize=init_el_g2v, doc='hourly inputdata electricity demand')

    M.max_tr_distribution = Param(initialize=init_max_tr_distribution)
    M.hourly_capacity_EV = Param(M.t, initialize=init_hourly_capacity_EV)

    M.industry_gas = Param(M.t, initialize=init_industry_gas, doc="hourly industry gas demand")

    return M


def define_variable(M):
    """

    Variable Definition

    """
    # Positive Variable
    M.elp = Var(M.t, M.tech, within=NonNegativeReals, doc="electricity production by technology", initialize=0.0)
    M.heatP = Var(M.t, M.tech, within=NonNegativeReals, doc="heat production by technology", initialize=0.0)
    M.eld = Var(M.t, M.tech, within=NonNegativeReals, doc="electricity consumption by flexible means such as", initialize=0.0)
    M.SOC_th = Var(M.t, within=NonNegativeReals, doc="themal level in thermal storage", initialize=0.0)
    M.SOC_ind_th = Var(M.t, within=NonNegativeReals, doc="thermal level in individual thermal storage", initialize=0.0)
    M.SOC_gas = Var(M.t, within=NonNegativeReals, doc="gas storage level in gas storage", initialize=0.0)
    M.SOC_EV = Var(M.t, within=NonNegativeReals, doc="electricity charge level in a fleet of EVs", initialize=0.0)
    M.ch_th = Var(M.t, within=NonNegativeReals, doc="hourly charging amount of thermal energy to thermal storage", initialize=0.0)
    M.ch_EV = Var(M.t, within=NonNegativeReals, doc="hourly charging amount to EVs", initialize=0.0)
    M.ch_gas = Var(M.t, within=NonNegativeReals, doc="hourly charging amount of gas", initialize=0.0)
    M.dis_th = Var(M.t, within=NonNegativeReals, doc="hourly discharging thermal energy from thermal storage", initialize=0.0)
    M.dis_gas = Var(M.t, within=NonNegativeReals, doc="hourly discharging gas amount from gas storage", initialize=0.0)
    M.curtail = Var(M.t, within=NonNegativeReals, doc="hourly curtailment amount", initialize=0.0)
    # M.WasteP = Var(M.t, within=NonNegativeReals, doc="hourly W2Hydrogen amount", initialize=0.0)

    M.elp1 = Var(M.t, M.tech, within=NonNegativeReals, doc="electricity production by technology", initialize=0.0)
    M.heatP1 = Var(M.t, M.tech, within=NonNegativeReals, doc="heat production by technology", initialize=0.0)
    M.gas1 = Var(M.t, M.gas_all, within=NonNegativeReals, doc="gas consumption by tech", initialize=0.0)

    M.fu = Var(M.t, M.tech, within=NonNegativeReals, doc="hourly fuel consumption", initialize=0.0)
    M.SOC = Var(M.t, within=NonNegativeReals, doc="storage level in pumped hydro dam", initialize=0.0)
    M.LNG = Var(M.t, M.tech, within=NonNegativeReals, doc="LNG consumption by plants", initialize=0.0)
    M.Solidwaste = Var(M.t, M.tech, within=NonNegativeReals, doc="consumption from plants", initialize=0.0)
    M.Biogas = Var(M.t, M.tech, within=NonNegativeReals, doc="consumption from plants", initialize=0.0)
    
    # M.gas = Var(M.t, M.tech, within=NonNegativeReals, doc="gas consumption by tech", initialize=0.0)
    M.gas = Var(M.t, M.gas_all, within=NonNegativeReals, doc="gas consumption by tech", initialize=0.0)
    M.gasP = Var(M.t, within=NonNegativeReals, doc="gas production", initialize=0.0)
    M.SOC_battery = Var(M.t, within=NonNegativeReals, initialize=0.0)
    M.New = Var(M.tech, within=NonNegativeReals, doc="new added capacity for expandable technologies", initialize=0.0)
    M.em = Var(within=NonNegativeReals, doc="emission amount (tCO2)", initialize=0.0)
    # M.charge = Var(M.t,, within=NonNegativeReals, doc="hourly charging amount into pumped hydro")
    # M.discharge = Var(M.t, within=NonNegativeReals, doc="hourly discharging electricity from pumped hydro")
    M.dis_ind_h = Var(M.t, within=NonNegativeReals, doc="discharing heat in individual heating", initialize=0.0)
    M.charge_ind_h = Var(M.t, within=NonNegativeReals, doc="charging heat in individual heating", initialize=0.0)

    return M


def define_constraints(M):
    """

    Constraint Definition

    """
    M.balance_p = Constraint(M.t, rule=balance_p_rule, doc="balancing electricity demand and supply equation")
    M.balance_th = Constraint(M.t, rule=balance_th_rule, doc="balancing thermal energy demand and supply equation")
    
    # Gas balance equations
    M.balance_gas = Constraint(M.t, rule=balance_gas_rule, doc="balancing gas demand and supply")

    # Conversion
    M.gas_conversion = Constraint(M.t, rule=gas_conversion_rule, doc="hourly gas production eq")
    M.EL_conversion = Constraint(M.t, M.F2P, rule=EL_conversion_rule,
                                 doc="electricity conversion from dispatchable plant")
    M.EL_gas_conversion = Constraint(M.t, M.G2P, rule=EL_gas_conversion_rule,
                                     doc="electricity conversion from dispatchable plant")
    M.Heat_fuel_conversion = Constraint(M.t, M.F2H, rule=Heat_fuel_conversion_rule, doc="Heat converted from fuel")
    M.Heat_gas_conversion = Constraint(M.t, M.G2H, rule=Heat_gas_conversion_rule, doc="Heat converted from gas")
    M.Heat_el_conversion = Constraint(M.t, M.P2H, rule=Heat_el_conversion_rule, doc="Heat converted from electricity")
   
    M.EL_waste_conversion = Constraint(M.t, M.W2P, rule=EL_waste_conversion_rule, doc="electricity conversion from solidwaste")
    M.Heat_waste_conversion = Constraint(M.t, M.W2H, rule=Heat_waste_conversion_rule, doc="Heat converted from solidwaste")


    # EV related equations
    M.EV_battery_SOC = Constraint(M.t, rule=EV_battery_SOC_rule, doc="status of charge equation")
    M.EV_SOC_cap = Constraint(M.t, rule=EV_SOC_cap_rule, doc="capacity constraint for battery SOC")
    M.EV_charging_cap = Constraint(M.t, rule=EV_charging_cap_rule, doc="hourly limitation for charging")
    M.EV_SOC_ini = Constraint(M.t, rule=EV_SOC_ini_rule, doc="initial status of EV SOC(0.5)")
    M.EV_daily = Constraint(M.d, rule=EV_daily_rule, doc="daily charging constraint 28% of driving")
    M.EV_weekly = Constraint(M.w, rule=EV_weekly_rule, doc="weekly charging constraint 80% of driving")
    M.EV_SOC_end = Constraint(M.t, rule=EV_SOC_end_rule, doc="End status of EV SOC(0.5)")

    # Capacity Constraints
    M.capacity_elp = Constraint(M.t, M.power_stay, rule=capacity_elp_rule,
                                doc="capacity constraints for electricity production technologies (no expansion)")
    M.capacity_elp1 = Constraint(M.t, M.power_ex, rule=capacity_elp1_rule,
                                 doc="capacity constraints for electricity production technologies (expansion)")
    M.capacity_eld = Constraint(M.t, M.flexible_stay, rule=capacity_eld_rule,
                                doc="capacity constraints for electricity consumption technologies (no expansion)")
    M.capacity_eld1 = Constraint(M.t, M.flexible_ex, rule=capacity_eld1_rule,
                                 doc="capacity constraints for electricity consumption technologies (expansion)")
    M.capacity_heatP = Constraint(M.t, M.F2H, rule=capacity_heatP_rule,
                                  doc="capacity constraint for heating from fuels")
    # M.capacity_heatP1 = Constraint(M.t, M.P2H, rule=capacity_heatP1_rule,
    #                                doc="capacity constraint for heating from electricity")
    # M.capacity_heatP2 = Constraint(M.t, M.G2H, rule=capacity_heatP2_rule,
    #                                doc="capacity constraint for heating from gas")

    # Storage Constraints
    M.storage_gas_constraint = Constraint(M.t, rule=storage_gas_constraint_rule,
                                          doc="capacity constraint for gas storage capacity")
    M.storage_pumped_constraint = Constraint(M.t, rule=storage_pumped_constraint_rule,
                                             doc="capacity constraint for pumped hydro dam")
    M.storage_thermal_constraint = Constraint(M.t, rule=storage_thermal_constraint_rule,
                                              doc="capacity constraint for thermal storage capacity")
    # M.heat_ind_SOC_cap = Constraint(M.t, rule=heat_ind_SOC_cap_rule,
    #                                 doc="capacity constraint for individual heat storage capacity")

    # Pumped hydro equations
    M.hydro_soc_boundary = Constraint(M.t, rule=hydro_soc_boundary_rule,
                                      doc="initial and final status hydro pumped storage")
    M.hydro_soc = Constraint(M.t, rule=hydro_soc_rule, doc="final status hydro pumped storage")
    M.hydro_charge = Constraint(M.t, rule=hydro_charge_rule, doc="pumped hydro charge equations")
    M.hydro_discharge = Constraint(M.t, rule=hydro_discharge_rule, doc="pumped hydro discharge equation")

    # Conventional fuel plants operation

    # Oper cons PP
    M.oper_cons_pp_f2p = Constraint(M.F2P, rule=oper_cons_pp_f2p_rule)

    # New Equation
    # M.ratio_PV_WT_off1 = Constraint(rule=ratio_PV_WT_off1_rule)
    # M.ratio_PV_WT_off2 = Constraint(rule=ratio_PV_WT_off2_rule)
    # M.ratio_PV_WT_off3 = Constraint(rule=ratio_PV_WT_off3_rule)
    
    # Newly added
    M.new_added_constraints = Constraint(M.Upperlimit, rule=new_added_constraints_rule)

    # Battery equations
    M.battery_SOC_boundary = Constraint(M.t, rule=battery_SOC_boundary_rule)
    M.battery_SOC = Constraint(M.t, rule=battery_SOC_rule)
    M.battery_charge = Constraint(M.t, rule=battery_charge_rule)
    M.battery_discharge = Constraint(M.t, rule=battery_discharge_rule)
    M.battery_storage_cap = Constraint(M.t, rule=battery_storage_cap_rule)
    M.battery_power_energy = Constraint(M.t, rule=battery_power_energy_rule)

    # TES balance heat
    M.heat_SOC = Constraint(M.t, rule=heat_SOC_rule, doc="Heat storage balance equations")
    M.heat_SOC_boundary = Constraint(M.t, rule=heat_SOC_boundary_rule, doc="initial and final heat storage SOC")

    
    # Gas storage balance
    M.gas_SOC = Constraint(M.t, rule=gas_SOC_rule, doc="gas storage SOC equation")
    M.gas_SOC_boundary = Constraint(M.t, rule=gas_SOC_boundary_rule,
                                    doc="initial and final status of SOC in gas storage")
    M.gas_charge_constraint = Constraint(M.t, rule=gas_charge_constraint_rule)
    M.gas_discharge_constraint = Constraint(M.t, rule=gas_discharge_constraint_rule)

    # Emission Constraints
    M.em_amount = Constraint(rule=em_amount_rule)
    M.em_limit = Constraint(rule=em_limit_rule)


    # Biogas Constraints
    # M.Biogas_cap = Constraint(rule=Biogas_limit_rule)
    
    # Solidwaste Constraints
    # M.Solidwaste_cap = Constraint(rule=Solidwaste_limit_rule)


    # Curtailment limit
    M.curtail_limit = Constraint(M.t, rule=curtailment_limit_rule)
    M.SMR_conversion = Constraint(M.t, rule=SMR_conversion_rule)
    M.WtX_conversion_rule = Constraint(M.t, rule=WtX_conversion_rule)
    M.N_grid_rule = Constraint(M.t, rule=N_grid_rule)
    M.N_grid_rule1 = Constraint(M.t, rule=N_grid_rule1)

  
  #  M.National_Grid_limit = Constraint(M.t, rule=National_Grid_limit_rule)

    # Total Cost
    # M.total = Constraint(rule=total_cost, doc="total system cost")

    return M


def define_objective(M):
    """

    Objective

    """
    M.total = Objective(rule=total_rule, doc="total system cost")

    return M
