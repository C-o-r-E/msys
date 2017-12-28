#!/usr/bin/env python3
"""
Helper functions for generating reports
"""

from typing import List

def get_total_from_subs(sub_data: dict) -> float:
    """
    Returns a total equal to the sum of all subscription item amounts
    """
    total = 0.0
    try:
        #get a list of dict that contain subscription items
        basic_subs = sub_data["items"]["data"]

        for sub_item in basic_subs:
            plan_amount = sub_item["plan"]["amount"]
            plan_amount = plan_amount / 100.0
            total += plan_amount

    except KeyError:
        total = -1.0
    return total

def get_plans_from_subs(sub_data: dict) -> List[str]:
    """
    This function returns a list of strings containing the names
    of the subcription items associated with a subscription dict
    """
    ret_lst = []
    try:
        #get a list of dict that contain subscription items
        basic_subs = sub_data["items"]["data"]

        for sub_item in basic_subs:
            plan_name = sub_item["plan"]["name"]
            plan_amount = sub_item["plan"]["amount"]
            plan_currency = sub_item["plan"]["currency"]

            plan_amount = plan_amount / 100.0

            line = f"{plan_name} --> ${plan_amount} {plan_currency}"
            ret_lst.append(line)

    except KeyError:
        ret_lst.append("KeyError")
    return ret_lst

def main():
    """ Sentinel to prevent execution as script """
    print("This is a lib. exiting")
    return
