from __future__ import annotations

import pandas as pd

from queries.pandas import utils

Q_NUM = 14


def q() -> None:
    lineitem_ds_fn = utils.get_line_item_ds
    part_ds_fn = utils.get_part_ds

    # first call one time to cache in case we don't include the IO times
    lineitem_ds_fn()
    part_ds_fn()

    def query() -> pd.DataFrame:
        lineitem_ds = lineitem_ds_fn()
        part_ds = part_ds_fn()

        var1 = pd.Timestamp("1995-09-01")
        var2 = pd.Timestamp("1995-10-01")

        lineitem_ds = lineitem_ds[
            (lineitem_ds["l_shipdate"] >= var1) & (lineitem_ds["l_shipdate"] < var2)
        ]

        jn = lineitem_ds.merge(part_ds, left_on="l_partkey", right_on="p_partkey")

        jn["revenue"] = jn["l_extendedprice"] * (1 - jn["l_discount"])
        jn["promo_revenue"] = jn["revenue"].where(
            jn["p_type"].str.startswith("PROMO"), 0
        )

        promo_revenue = round(
            100.0 * jn["promo_revenue"].sum() / jn["revenue"].sum(), 2
        )

        result_df = pd.DataFrame({"promo_revenue": [promo_revenue]})

        return result_df

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
