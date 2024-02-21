use crate::utils::*;
use chrono::NaiveDate;
use polars::prelude::*;

pub fn query() -> PolarsResult<LazyFrame> {
    let q = get_lineitem_ds();
    let var_1 = lit(NaiveDate::from_ymd_opt(1998, 9, 2)
        .unwrap()
        .and_hms_opt(0, 0, 0)
        .unwrap());

    let q = q
        .filter(col("l_shipdate").lt_eq(var_1))
        .groupby([cols(["l_returnflag", "l_linestatus"])])
        .agg([
            sum("l_quantity").alias("sum_qty"),
            sum("l_extendedprice").alias("sum_base_price"),
            (col("l_extendedprice") * (lit(1) - col("l_discount")))
                .sum()
                .alias("sum_disc_price"),
            (col("l_extendedprice") * (lit(1.0) - col("l_discount")) * (lit(1.0) + col("l_tax")))
                .sum()
                .alias("sum_charge"),
            mean("l_quantity").alias("avg_qty"),
            mean("l_extendedprice").alias("avg_price"),
            mean("l_discount").alias("avg_disc"),
            count().alias("count_order"),
        ])
        .sort_by_exprs([cols(["l_returnflag", "l_linestatus"])], &[false], false);

    Ok(q)
}
