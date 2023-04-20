"""
    Default Gesi Model Example
"""
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_path)
sys.path.append(parent_dir)

web_model_dir = os.path.join(parent_dir, 'gesi_model_web')
sys.path.append(web_model_dir)


from gesi_model_web.run import ModelExecutor

data_path = os.path.join(current_path, 'GESI_DE_1.xlsx')
name = 'gesi_web_jupyter'

executor = ModelExecutor(data_path, name=name, save_result=True, solver='cplex', verbose=1)
solver = executor.run_once()


