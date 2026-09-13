from __future__ import annotations

import pandas as pd

from queries.pandas import utils

Q_NUM = 12


def q() -> None:
    lineitem_ds_fn = utils.get_line_item_ds
    orders_ds_fn = utils.get_orders_ds

    # first call one time to cache in case we don't include the IO times
    lineitem_ds_fn()
    orders_ds_fn()

    def query() -> pd.DataFrame:
        lineitem_ds = lineitem_ds_fn()
        orders_ds = orders_ds_fn()

        var1 = "MAIL"
        var2 = "SHIP"
        var3 = pd.Timestamp("1994-01-01")
        var4 = pd.Timestamp("1995-01-01")

        lineitem_ds = lineitem_ds[lineitem_ds["l_shipmode"].isin([var1, var2])]
        lineitem_ds = lineitem_ds[
            lineitem_ds["l_commitdate"] < lineitem_ds["l_receiptdate"]
        ]
        lineitem_ds = lineitem_ds[
            lineitem_ds["l_shipdate"] < lineitem_ds["l_commitdate"]
        ]
        lineitem_ds = lineitem_ds[
            (lineitem_ds["l_receiptdate"] >= var3)
            & (lineitem_ds["l_receiptdate"] < var4)
        ]

        jn = orders_ds.merge(lineitem_ds, left_on="o_orderkey", right_on="l_orderkey")

        jn["high_line_count"] = jn["o_orderpriority"].isin(["1-URGENT", "2-HIGH"])
        jn["low_line_count"] = ~jn["o_orderpriority"].isin(["1-URGENT", "2-HIGH"])

        gb = jn.groupby("l_shipmode", as_index=False)
        agg = gb.agg(
            high_line_count=pd.NamedAgg(column="high_line_count", aggfunc="sum"),
            low_line_count=pd.NamedAgg(column="low_line_count", aggfunc="sum"),
        )

        result_df = agg.sort_values("l_shipmode")

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
