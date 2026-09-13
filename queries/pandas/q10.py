from __future__ import annotations

import pandas as pd

from queries.pandas import utils

Q_NUM = 10


def q() -> None:
    customer_ds_fn = utils.get_customer_ds
    lineitem_ds_fn = utils.get_line_item_ds
    nation_ds_fn = utils.get_nation_ds
    orders_ds_fn = utils.get_orders_ds

    # first call one time to cache in case we don't include the IO times
    customer_ds_fn()
    lineitem_ds_fn()
    nation_ds_fn()
    orders_ds_fn()

    def query() -> pd.DataFrame:
        customer_ds = customer_ds_fn()
        lineitem_ds = lineitem_ds_fn()
        nation_ds = nation_ds_fn()
        orders_ds = orders_ds_fn()

        var1 = pd.Timestamp("1993-10-01")
        var2 = pd.Timestamp("1994-01-01")

        orders_ds = orders_ds[
            (orders_ds["o_orderdate"] >= var1) & (orders_ds["o_orderdate"] < var2)
        ]
        lineitem_ds = lineitem_ds[lineitem_ds["l_returnflag"] == "R"]

        jn1 = customer_ds.merge(orders_ds, left_on="c_custkey", right_on="o_custkey")
        jn2 = jn1.merge(lineitem_ds, left_on="o_orderkey", right_on="l_orderkey")
        jn3 = jn2.merge(nation_ds, left_on="c_nationkey", right_on="n_nationkey")

        jn3["revenue"] = jn3["l_extendedprice"] * (1 - jn3["l_discount"])

        gb = jn3.groupby(
            [
                "c_custkey",
                "c_name",
                "c_acctbal",
                "c_phone",
                "n_name",
                "c_address",
                "c_comment",
            ],
            as_index=False,
        )
        agg = gb.agg(revenue=pd.NamedAgg(column="revenue", aggfunc="sum"))

        sel = agg.loc[
            :,
            [
                "c_custkey",
                "c_name",
                "revenue",
                "c_acctbal",
                "n_name",
                "c_address",
                "c_phone",
                "c_comment",
            ],
        ]

        result_df = sel.sort_values("revenue", ascending=False).head(20)

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
