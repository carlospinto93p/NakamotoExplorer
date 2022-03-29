from operator import itemgetter
from typing import Dict, Optional

from pandas import Series

from nakamoto_explorer.exceptions import SimulationException, ValidationException
from nakamoto_explorer.nakamoto import settings


def simulate_purchase(input_row: Series, base_to_purchase: float,
                      commission_percent: float = settings.COMMISSION,
                      raise_exception: bool = True) -> Optional[Series]:
    """
    Simulate a purchase operation.
    :param input_row: row that satisfies the conditions for the purchase to be applied.
        It has the `historical_df` index.
    :param base_to_purchase: base to be purchased.
    :param commission_percent: commission percent that will be applied once the operation is done.
    :param raise_exception: whether to raise an exception if the purchase can not be done.
    :return: a new row with te assets quantities updated after the operation.
    """
    if base_to_purchase <= 0:
        if raise_exception:
            raise SimulationException(f'Tried a non-positive {base_to_purchase = }', input_row)
        return None

    # ensure_operation_row(input_row)
    simulation_params = {'base_to_purchase': base_to_purchase, 'input_row': input_row}

    operation_dict = {'base_free': input_row['base_free'] + base_to_purchase,
                      'quote_free': input_row['quote_free'] - base_to_purchase * input_row['base-quote'],
                      'commission': base_to_purchase * commission_percent * input_row['base-commission']}
    operation_dict['commission_free'] = input_row['commission_free'] - operation_dict['commission']

    new_row = update_operation_row(input_row.copy(), operation_dict, action='purchase',
                                   simulation_params=simulation_params,
                                   raise_exception=raise_exception)
    return new_row


def simulate_sale(input_row: Series, base_to_sell: float,
                  commission_percent: float = settings.COMMISSION,
                  raise_exception: bool = True) -> Optional[Series]:
    """
    Simulate a sale operation.
    :param input_row: row that satisfies the conditions for the sale to be applied.
    :param base_to_sell: base to be sold.
    :param commission_percent: commission percent that will be applied once the operation is done.
    :param raise_exception: whether to raise an exception if the purchase can not be done.
    :return: a new row with te assets quantities updated after the operation.
    """
    if base_to_sell <= 0:
        if raise_exception:
            raise SimulationException(f'Tried a non-positive {base_to_sell = }', input_row)
        return None

    # ensure_operation_row(input_row)
    simulation_params = {'base_to_sell': base_to_sell, 'input_row': input_row}

    operation_dict = {'base_free': input_row['base_free'] - base_to_sell,
                      'quote_free': input_row['quote_free'] + base_to_sell * input_row['base-quote'],
                      'commission': base_to_sell * commission_percent * input_row['base-commission']}
    operation_dict['commission_free'] = input_row['commission_free'] - operation_dict['commission']

    new_row = update_operation_row(input_row.copy(), operation_dict, action='sale',
                                   simulation_params=simulation_params,
                                   raise_exception=raise_exception)
    return new_row


def update_operation_row(operation_row: Series, operation_dict: Dict[str, float],
                         action: str, simulation_params: Dict[str, float],
                         # ensure_input_row: bool = True,
                         raise_exception: bool = True) -> Optional[Series]:
    """
    Update an operation row (a list of transactional data in a determined instant).
    :param operation_row: a row of a simulation df
    :param operation_dict: dictionary with the data of the operation that will be done.
        It has the keys: {'base_free', 'quote_free', 'commission_free', 'commission'}
    :param action: name of the action that will be done.
    :param simulation_params: dictionary with the parameters of the order that is being simulated.
        Has to be at least the key `input_row`.
    :param ensure_input_row: whether to add a security layer to ensure that the operation
        row received has the correct format.
    :param raise_exception: whether to raise an exception if the operation can not be done.
    :return: the operation row updated.
    """
    # if ensure_input_row:
    #     ensure_operation_row(operation_row)
    operation_keys = {'base_free', 'quote_free', 'commission_free', 'commission'}
    if not all(operation_key in operation_dict.keys() for operation_key in operation_keys):
        raise ValidationException(f'Not all operation keys {operation_keys} in the operation_dict '
                                  f'{operation_dict}', simulation_params)
    if 'input_row' not in simulation_params:
        raise ValidationException(f'`input_row` not in the simulation params: {simulation_params}')

    base, quote, commission = itemgetter('base_free', 'quote_free', 'commission_free')(operation_dict)
    if base < 0:
        if raise_exception:
            raise SimulationException(f'New base_free {base} < 0', simulation_params)
        return None
    if quote < 0:
        if raise_exception:
            raise SimulationException(f'New quote_free {quote} < 0', simulation_params)
        return None
    if commission < 0:
        if raise_exception:
            raise SimulationException(f'New commission_free {commission} < 0', simulation_params)
        return None

    for key, value in operation_dict.items():
        if key in ['base_free', 'quote_free']:
            operation_row[f'{key}_change'] = value - operation_row[key]
        operation_row[key] = value
    operation_row['action'] = action

    return operation_row

