use polars::prelude::*;
use std::path::{Path, PathBuf};

static FILES: &str = "../data/tables/scale-1/";

fn get_ds(name: &str) -> LazyFrame {
    let path = PathBuf::from(FILES).join(Path::new(name));
    LazyFrame::scan_parquet(path, ScanArgsParquet::default()).unwrap()
}

pub fn get_lineitem_ds() -> LazyFrame {
    get_ds("lineitem.parquet")
}
