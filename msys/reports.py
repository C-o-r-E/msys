#!/usr/bin/env python3
"""
Helper functions for generating reports
"""

from typing import List

"""
This function returns a list of strings containing the names
of the subcription items associated with a subscription dict
"""
def get_plans_from_subs(sub_data: dict) -> List[str]:
    ret_lst = []
    try:
        #get a list of dict that contain subscription items
        basic_subs = sub_data["items"]["data"]

        for sub_item in basic_subs:
            ret_lst.append(sub_item["plan"]["name"])

    except KeyError as k_err:
        ret_lst.append("KeyError")
    return ret_lst

def main():
    print("This is a lib. exiting")
    return
