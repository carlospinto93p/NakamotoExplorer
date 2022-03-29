from typing import Union

import pandas as pd

from nakamoto_explorer.nakamoto import Rule, RuleAction, select_input_row, settings
from nakamoto_explorer.nakamoto.simulations import simulate_sale, simulate_purchase


class MarginSale(Rule):
    """
    Make a Sale when the accumulated price change (since last action) exceeds some
    threshold (`margin_threshold`). The Sale will be done according to the accumulated
    price change, maintaining a fraction of the current `base_free` (`hold_percent`).
    """

    def __init__(self, margin_threshold: float = settings.SELLING_MARGIN_THRESHOLD,
                 hold_percent: float = settings.HOLD_PERCENT):
        super().__init__(rule_action=RuleAction.SALE,
                         margin_threshold=margin_threshold,
                         hold_percent=hold_percent)

    def apply(self, row_index: str, df: pd.DataFrame) -> Union[pd.Series, None]:
        input_row = select_input_row(row_index, df)
        base_to_sell = input_row['base_free'] * input_row['price_acc_pct_change'] * \
            (1 - self.parameters['hold_percent'])
        return simulate_sale(input_row, base_to_sell, raise_exception=False)

    def define_mask(self, df: pd.DataFrame) -> pd.Series:
        return df['price_acc_pct_change'].ge(self.parameters['margin_threshold'])


class MarginPurchase(Rule):
    """
    Make a Purchase when the accumulated price change (since last action) is inferior
    than some threshold (`margin_threshold`). The Purchase will be done according to
    the accumulated price change, maintaining a fraction of the current `base_free`
    (`hold_percent`).
    """

    def __init__(self, margin_threshold: float = settings.BUYING_MARGIN_THRESHOLD,
                 hold_percent: float = settings.HOLD_PERCENT):
        super().__init__(rule_action=RuleAction.PURCHASE,
                         margin_threshold=margin_threshold,
                         hold_percent=hold_percent)

    def apply(self, row_index: str, df: pd.DataFrame) -> Union[pd.Series, None]:
        input_row = select_input_row(row_index, df)
        base_to_purchase = input_row['base_free'] * (- input_row['price_acc_pct_change']) * \
            (1 - self.parameters['hold_percent'])
        return simulate_purchase(input_row, base_to_purchase, raise_exception=False)

    def define_mask(self, df: pd.DataFrame) -> pd.Series:
        return df['price_acc_pct_change'].le(-self.parameters['margin_threshold'])
