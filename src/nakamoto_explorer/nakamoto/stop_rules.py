from typing import Union

from pandas import DataFrame, Series

from nakamoto_explorer.nakamoto import Rule, RuleAction, select_input_row
from nakamoto_explorer.nakamoto.simulations import simulate_sale
from nakamoto_explorer.exceptions import ValidationException


class StopRule(Rule):

    def apply(self, row_index: str, df: DataFrame) -> Union[Series, None]:
        input_row = select_input_row(row_index, df)
        # TODO 2022.01.28 Add handling actions if there is not enough commission asset to do this.
        base_to_sell = input_row['base_free']
        return simulate_sale(input_row, base_to_sell, raise_exception=False)

    def define_mask(self, df: DataFrame) -> Series:
        raise NotImplementedError('StopRule method needs to be implemented in a child class')


class AbsoluteStopLoss(StopRule):
    """ Stop trading when the Loss is under some absolute threshold. """

    def __init__(self, threshold):
        if threshold <= 0:
            raise ValidationException(f'Negative {threshold = }')
        super().__init__(rule_action=RuleAction.SALE, threshold=threshold)

    def define_mask(self, df: DataFrame) -> Series:
        # TODO 2022.01.26 TODO should be able to set any column or combination of columns
        #  in the init parametrization, with all the StopRules.
        value_col = df['quote_value']
        return value_col.le(self.parameters['threshold'])


class AbsoluteTakeProfit(StopRule):
    """ Stop trading when the Gain surpasses some absolute threshold. """

    def __init__(self, threshold):
        if threshold <= 0:
            raise ValidationException(f'Negative {threshold = }')
        super().__init__(rule_action=RuleAction.SALE, threshold=threshold)

    def define_mask(self, df: DataFrame) -> Series:
        value_col = df['quote_value']
        return value_col.ge(self.parameters['threshold'])
