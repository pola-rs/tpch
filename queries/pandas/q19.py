from __future__ import annotations

import pandas as pd

from queries.pandas import utils

Q_NUM = 19


def q() -> None:
    lineitem_ds_fn = utils.get_line_item_ds
    part_ds_fn = utils.get_part_ds

    # first call one time to cache in case we don't include the IO times
    lineitem_ds_fn()
    part_ds_fn()

    def query() -> pd.DataFrame:
        lineitem_ds = lineitem_ds_fn()
        part_ds = part_ds_fn()

        lineitem_ds = lineitem_ds[lineitem_ds["l_shipmode"].isin(["AIR", "AIR REG"])]
        lineitem_ds = lineitem_ds[lineitem_ds["l_shipinstruct"] == "DELIVER IN PERSON"]

        jn = part_ds.merge(lineitem_ds, left_on="p_partkey", right_on="l_partkey")

        # Complex filter conditions
        cond1 = (
            (jn["p_brand"] == "Brand#12")
            & jn["p_container"].isin(["SM CASE", "SM BOX", "SM PACK", "SM PKG"])
            & (jn["l_quantity"] >= 1)
            & (jn["l_quantity"] <= 11)
            & (jn["p_size"] >= 1)
            & (jn["p_size"] <= 5)
        )

        cond2 = (
            (jn["p_brand"] == "Brand#23")
            & jn["p_container"].isin(["MED BAG", "MED BOX", "MED PKG", "MED PACK"])
            & (jn["l_quantity"] >= 10)
            & (jn["l_quantity"] <= 20)
            & (jn["p_size"] >= 1)
            & (jn["p_size"] <= 10)
        )

        cond3 = (
            (jn["p_brand"] == "Brand#34")
            & jn["p_container"].isin(["LG CASE", "LG BOX", "LG PACK", "LG PKG"])
            & (jn["l_quantity"] >= 20)
            & (jn["l_quantity"] <= 30)
            & (jn["p_size"] >= 1)
            & (jn["p_size"] <= 15)
        )

        jn = jn[cond1 | cond2 | cond3]

        revenue = round((jn["l_extendedprice"] * (1 - jn["l_discount"])).sum(), 2)

        result_df = pd.DataFrame({"revenue": [revenue]})

        return result_df

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
