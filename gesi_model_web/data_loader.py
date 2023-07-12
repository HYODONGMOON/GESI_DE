import copy
import json
import os
import pandas as pd

from gesi_model_web.core.logger import Logger


class DataLoader:
    def __init__(self, configuration, logger):
        self.logger = Logger(self.__class__.__name__, logger)

        self.data_path = configuration.data_path

        fname, ext = os.path.splitext(self.data_path)

        if ext not in ['.xlsx', '.json']:
            raise TypeError("Not allowed data file format: {}".format(ext))

        self.data_type = ext

        with open(configuration.set_path) as f:
            self.sets = json.load(f)

        self._data = None
        self._control = dict()

        self._result_data = None

    def load_control(self):
        return self._control

    def load_data(self):
        if self.data_type == '.xlsx':
            self.load_data_excel()

        elif self.data_type == '.json':
            self.load_data_json()

    def load_data_json(self):
        pass

    # GESI customized excel format
    def load_data_excel(self):
        self.logger.print_info_line("Load Data")
        init_data = dict()
        result_data = dict()

        df_control = self.extract_control()
        self._control['year'] = df_control.loc['year'][1]
        self._control['ndc'] = df_control.loc['NDC'][1]
        # self._control['ratio_pv'] = df_control.loc['ratio_PV'][1]
        # self._control['ratio_wt'] = df_control.loc['ratio_WT'][1]
        # self._control['ratio_wt_off'] = df_control.loc['ratio_WT_off'][1]
        self._control['hydrogen_import_share'] = df_control.loc['hydrogen_import_share'][1]
        # self._control['electricity_import_share'] = df_control.loc['electricity_import_share'][1]

        # self._control['building_retrofit_rate'] = df_control.loc['building retrofit rate'][1]
        # self._control['bevs_share'] = df_control.loc['BEVs share'][1]

        # Load Set Data
        for k, v in self.sets.items():
            init_data[k] = {None: v}

        # Load Param Data
        
        df_Distributions = self.extract_Distributions()
        df_Distributions.fillna(0., inplace=True)
        Distributions = dict()

        for t in self.sets['t']:
            for dis in self.sets['dis']:
                Distributions[(t, dis)] = df_Distributions.loc[t][dis]

        init_data["Distributions"] = Distributions

        df_cost = self.extract_cost()
        df_cost.fillna(0., inplace=True)
        cost = dict()

        row_costs = df_cost.index.values
        col_costs = df_cost.columns.values

        for tech in self.sets['tech']:
            for c in self.sets['c']:
                if tech in row_costs and c in col_costs:
                    cost[(tech, c)] = df_cost.loc[tech][c]
                else:
                    cost[(tech, c)] = 0.0

        init_data["cost"] = cost

        df_specs = self.extract_specs()
        df_specs.fillna(0., inplace=True)
        specs = dict()

        row_specs = df_specs.index.values
        col_specs = df_specs.columns.values

        for tech in self.sets['tech']:
            for trait in self.sets['trait']:
                if tech in row_specs and trait in col_specs:
                    specs[(tech, trait)] = df_specs.loc[tech][trait]
                else:
                    specs[(tech, trait)] = 0.0

        init_data["specs"] = specs

        df_fossil = self.extract_fossil()
        df_fossil.fillna(0., inplace=True)
        fossil = dict()

        row_fossil = df_fossil.index.values
        col_fossil = df_fossil.columns.values

        for fuel in self.sets['fuel']:
            for coeff in self.sets['coeff']:
                if fuel in row_fossil and coeff in col_fossil:
                    fossil[(fuel, coeff)] = df_fossil.loc[fuel][coeff]
                else:
                    fossil[(fuel, coeff)] = 0.0

        init_data["fossil"] = fossil

        df_Potential = self.extract_Potential()
        Potential = dict()

        for Upperlimit in self.sets['Upperlimit']:
            Potential[Upperlimit] = df_Potential.loc[Upperlimit]['potential'].item()

        init_data["Potential"] = Potential

        # init_data["ratio_PV"] = {None: self._control['ratio_pv']}
        # init_data["ratio_WT"] = {None: self._control['ratio_wt']}
        # init_data["ratio_WT_off"] = {None: self._control['ratio_wt_off']}
        init_data["hydrogen_import_share"] = {None: self._control['hydrogen_import_share']}
        # init_data["electricity_import_share"] = {None: self._control['electricity_import_share']}

        init_data['correction_wind'] = {None: 0.55}


        df_Demand = self.extract_Demand()

        EL = df_Demand.loc['electricity'][0]
        H = df_Demand.loc['heat'][0]
        gas_D = df_Demand.loc['hydrogen'][0]
        # fuelcell = df_Demand.loc['fuelcell'][0]
       
        init_data['EL'] = {None: EL}
        init_data['H'] = {None: H}
        init_data['gas_D'] = {None: gas_D}
        # init_data['fuelcell'] = {None: fuelcell}

        df_General = self.extract_General()

        discount = df_General.loc['discount'][0]
        init_data['discount'] = {None: discount}

        
        df_Building = self.extract_Building()

        el_h_new = df_Building.loc['el_h_new'][0]
        el_h_old = df_Building.loc['el_h_old'][0]
        smart_share = df_Building.loc['smart_share'][0]

        init_data['el_h_new'] = {None: el_h_new}
        init_data['el_h_old'] = {None: el_h_old}
        init_data['smart_share'] = {None: smart_share}


        df_Others = self.extract_Others()       # 유형 선택에 따라 다른 함수가 적용되도록 수정

        Dedicated = df_Others.loc['Dedicated'][0]
        init_data['Dedicated'] = {None: Dedicated}

        export_h = df_Others.loc['export_h'][0]
        init_data['export_h'] = {None: export_h}

        choice_city = df_Others.loc['choice_city'][0]
        init_data['choice_city'] = {None: choice_city}

        choice_industry = df_Others.loc['choice_industry'][0]
        init_data['choice_industry'] = {None: choice_industry}

        choice_rural = df_Others.loc['choice_rural'][0]
        init_data['choice_rural'] = {None: choice_rural}

        choice_port = df_Others.loc['choice_port'][0]
        init_data['choice_port'] = {None: choice_port}


        df_Transportation = self.extract_Transportation()
        
        N_Evs = df_Transportation.loc['N_Evs'][0]
        av_distance = df_Transportation.loc['av_distance'][0]
        bat_cap = df_Transportation.loc['bat_cap'][0]
        c_rate = df_Transportation.loc['c_rate'][0]
        M_share = df_Transportation.loc['M_share'][0]
        C_share = df_Transportation.loc['C_share'][0]
        eff_EV = df_Transportation.loc['eff_EV'][0]

        init_data['N_Evs'] = {None: N_Evs}
        init_data['av_distance'] = {None: av_distance}
        init_data['bat_cap'] = {None: bat_cap}
        init_data['c_rate'] = {None: c_rate}
        init_data['M_share'] = {None: M_share}
        init_data['C_share'] = {None: C_share}
        init_data['eff_EV'] = {None: eff_EV}


        df_Cap = self.extract_Cap()

        em_cap = df_Cap.loc['em_cap'][0]
        Solidwaste_cap = df_Cap.loc['Solidwaste_cap'][0]
        Biogas_cap = df_Cap.loc['Biogas_cap'][0]
        N_grid_cap = df_Cap.loc['N_grid_cap'][0]
        H_grid_cap = df_Cap.loc['H_grid_cap'][0]      
        Off_gas = df_Cap.loc['Off_gas'][0]      
        W_heat = df_Cap.loc['W_heat'][0]      

        init_data["em_cap"] = {None: em_cap}
        init_data["Solidwaste_cap"] = {None: Solidwaste_cap}
        init_data["Biogas_cap"] = {None: Biogas_cap}
        init_data["N_grid_cap"] = {None: N_grid_cap}
        init_data["H_grid_cap"] = {None: H_grid_cap}
        init_data["Off_gas"] = {None: Off_gas}
        init_data["W_heat"] = {None: W_heat}

        self._data = {None: init_data}


        self._result_data = result_data

    def load_model_data(self):
        return self._data

    def load_result_data(self):
        return self._result_data

    def extract_control(self):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name='control', usecols='A:B', nrows=9,
                           index_col=0, header=None)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_table(self, sheet_name, usecols, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, nrows=nrows,
                           index_col=0)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_partial_table(self, sheet_name, usecols, header, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, header=header,
                           nrows=nrows, index_col=0)
        df.fillna(0., inplace=True)
        df.index.name = None

        return df

    def extract_scalar_table(self, sheet_name, usecols, header, nrows):
        df = pd.read_excel(self.data_path, engine='openpyxl', sheet_name=sheet_name, usecols=usecols, header=header,
                           nrows=nrows)
        df.fillna(0., inplace=True)

        return df

    def extract_Distributions(self):
        return self.extract_table('Hourly', 'A:h', 8760)               # 변수추가 망비용추가

    def extract_cost(self):
        return self.extract_table('ES', 'J:N', 22)

    def extract_specs(self):
        return self.extract_table('ES', 'A:h', 22)

    def extract_General(self):
        return self.extract_table('Inputdata', 'A:B', 2)

    def extract_fossil(self):
        return self.extract_partial_table('Inputdata', 'A:C', 13, 7)

    def extract_Cap(self):
        return self.extract_partial_table('Inputdata', 'A:B', 22, 7)
    
    def extract_Building(self):
        return self.extract_partial_table('Inputdata', 'A:B', 31, 3)
    
    def extract_Others(self):
        return self.extract_partial_table('Inputdata', 'A:B', 36, 6)

    def extract_Demand(self):
        return self.extract_table('Demand', 'H:I', 9)

    def extract_Transportation(self):
        return self.extract_partial_table('Inputdata', 'A:B', 4, 7)

    def extract_Potential(self):
        return self.extract_partial_table('ES', 'A:B', 25, 12)