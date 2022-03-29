from typing import Dict, List, Set, Tuple

from pandas import DataFrame, to_datetime

from nakamoto_explorer.nakamoto import Rule, rules, stop_rules
from nakamoto_explorer.files import get_folders_inside_folder, load_csv, load_yaml

from nakamoto_explorer.exceptions import ValidationException
from nakamoto_explorer.settings import DATA_FOLDER


def get_data_idx(data: List[dict], price_list_idx: int, rule_set_idx: int):
    idx, _ = [(idx, elem) for idx, elem in enumerate(data)
              if (elem['identifier']['price_list'] == price_list_idx
                  and elem['identifier']['rule_set'] == rule_set_idx)][0]
    return idx


def get_max_price_list_idx(data: List[dict]):
    return max(x['identifier']['price_list'] for x in data)


def get_max_rule_set_idx(data: List[dict]):
    return max(x['identifier']['rule_set'] for x in data)


def load_rule_set_list(rule_set_list: List[dict]) -> Dict[str, Set[Rule]]:
    """
    Load a raw list of dicts representing a rule set into a one.
    :return a dictionary {'rule_set': Set[Rule], 'stop_rules': Set[Rule]}
    """
    clean_rule_set, clean_stop_rules = [], []
    for rule_dict in rule_set_list:
        rule, is_stop_rule = rule_dict_to_rule(rule_dict)
        if not is_stop_rule:
            clean_rule_set.append(rule)
        else:
            clean_stop_rules.append(rule)
    return {'rule_set': set(clean_rule_set),
            'stop_rules': set(clean_stop_rules)}


def load_simulation_csv(path: str) -> DataFrame:
    # With the use of .csv as intermediate format some properties are lost.
    df = load_csv(path)
    loaded_index = 'Unnamed: 0'
    df[loaded_index] = to_datetime(df[loaded_index])
    df.set_index(loaded_index, inplace=True)
    df.index.name = None
    df.columns.name = 'base_test-quote_test|commission_test'
    return df


def load_data(input_path: str = DATA_FOLDER) -> List[dict]:
    data = []
    for price_list_folder in get_folders_inside_folder(input_path):
        prices_folder = f'{input_path}/{price_list_folder}'
        price_list_idx = int(price_list_folder.split('_')[-1])
        historial_kwargs = load_yaml(f'{prices_folder}/historial_kwargs.yml')
        for rule_set_folder in get_folders_inside_folder(prices_folder):
            data_path = f'{prices_folder}/{rule_set_folder}/'
            rule_set = load_yaml(data_path + 'rule_set.yml')
            rule_set = load_rule_set_list(rule_set)
            rule_set_idx = int(rule_set_folder.split('_')[-1])
            rule_simulation_mock = \
                {'simulation_df': load_simulation_csv(data_path + 'simulation_df.csv'),
                 'metrics': load_yaml(data_path + 'metrics.yml'),
                 'rule_set_kwargs': rule_set,
                 'historial_kwargs': historial_kwargs,
                 'identifier': {'price_list': price_list_idx,
                                'rule_set': rule_set_idx}}
            data.append(rule_simulation_mock)
    data.sort(key=lambda x: (x['identifier']['price_list'], x['identifier']['rule_set']))
    return data


def rule_dict_to_rule(rule_dict: dict) -> Tuple[Rule, bool]:
    """
    Decode a dictionary into a Rule.
    :return a Tuple (Rule, is_stop_rule).
    """
    rule_name = rule_dict['rule_name']
    rule_kwargs = {k: v for k, v in rule_dict.items() if k != 'rule_name'}
    try:
        return getattr(rules, rule_name)(**rule_kwargs), False
    except AttributeError:
        pass
    try:
        return getattr(stop_rules, rule_name)(**rule_kwargs), True
    except AttributeError:
        raise ValidationException(f'Rule {rule_name} not found neither in rules '
                                  f'nor in stop_rules.')
