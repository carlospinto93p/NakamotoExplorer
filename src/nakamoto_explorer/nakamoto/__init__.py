""" Trading bot (minimal version). """

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime as dt
from enum import Enum
from itertools import count
from typing import Callable, Dict, List, Union

from pandas import DataFrame, Series, isna


class RuleAction(Enum):
    """ Enum class to struct rule action types. """
    SALE = 0
    PURCHASE = 1


@dataclass
class RuleData:
    """ RuleData class to handle trading strategies."""
    action: str
    name: str
    parameters: dict
    mask: Series = field(default=None, repr=False)
    apply: Callable[[str, DataFrame], Series] = field(default=None, repr=False)
    first_feasible_index: dt = field(default=dt.max, repr=False)

    def as_dict(self, nested: bool = False) -> dict:
        """
        Get the RuleData as a dictionary using the rule main parameters.
        Useful for representations inside DataFrames.
        """
        if nested:
            return {'name': self.name, 'parameters': self.parameters}
        return {'name': self.name, **self.parameters}

    def get_sorted_parameters(self) -> List[float]:
        return [self.parameters[parameter] for parameter in sorted(self.parameters.keys())]

    def __hash__(self) -> int:
        return hash(tuple(self.get_sorted_parameters()))


class Rule(ABC):
    """
    Rule base class to handle and define Rules.
    Other rules must inherit from this class.
    :param action: Rule action. Can only be 'sale' or 'purchase'.
    :param parameters: Rule specific parameters, as a dictionary.
    """
    rule_class_id: int = 0
    rule_class_id_counter = count(1)
    rule_actions_dict: Dict[RuleAction, str] = {RuleAction.SALE: 'sale',
                                                RuleAction.PURCHASE: 'purchase'}
    parameters: dict = {}

    def __init__(self, rule_action: RuleAction, **parameters):
        self.rule_action: RuleAction = rule_action
        self.action: str = self.rule_actions_dict[rule_action]
        self.name: str = self.__class__.__name__
        self.parameters: dict = parameters

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.rule_class_id = next(cls.rule_class_id_counter)

    def __call__(self, df: DataFrame = None) -> RuleData:
        return self.check(df)

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self) -> int:
        return hash((self.rule_class_id, *self.get_sorted_parameters()))

    def __repr__(self) -> str:
        return self.data.__repr__()

    @property
    def data(self) -> RuleData:
        return RuleData(action=self.action, name=self.name, parameters=self.parameters)

    def as_dict(self) -> dict:
        return self.data.as_dict()

    def check(self, df: DataFrame) -> RuleData:
        mask = self.mask(df)
        return RuleData(action=self.action,
                        name=self.name,
                        parameters=self.parameters,
                        mask=mask,
                        apply=self.apply,
                        first_feasible_index=mask.loc[mask].index[0] if sum(mask) > 0 else dt.max)

    def get_sorted_parameters(self) -> List[float]:
        return [self.parameters[parameter] for parameter in sorted(self.parameters.keys())]

    def mask(self, df: DataFrame) -> Series:
        """
        Apply the defined mask to get the DataFrame rows where the rule can be applied.
        This function is common for all rules, and it includes base conditions that are
        not defined every time in the `define_mask` function.
        :param df: historical DataFrame.
        :return: a boolean pandas Series indicating in which row the rule can be applied.
        """
        base_mask = isna(df['action'])
        specific_mask = self.define_mask(df)
        mask = specific_mask & base_mask
        # Rule tries does NOT comes here. That will be done inside the main simulation
        # function (backtesting).
        # Take for instance the StablePurchase function. It can not be applied to the raw df.
        return mask

    @abstractmethod
    def apply(self, row_index: str, df: DataFrame) -> Union[Series, None]:
        """
        Function to apply the rule. The row_index must be one that fulfill the mask condition.
        :param row_index: row index of the input DataFrame, for reference.
        :param df: historical DataFrame.
        :return: a pandas Series that will be a row containing the result of the applied rule.
        """
        pass

    @abstractmethod
    def define_mask(self, df: DataFrame) -> Series:
        """
        Defines a DataFrame mask based on the rule.
        :param df: historical DataFrame
        :return: a Pandas boolean Series that masks the DataFrame rows where the rule can be applied.
        """
        pass


def select_input_row(row_index: str, df: DataFrame) -> Series:
    """
    Select the `row_index` of the input DataFrame, getting the first DataFrame row
    where its index is equal to row_index.
    """
    input_row = df[df.index == row_index].iloc[0]
    return input_row
