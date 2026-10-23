use std::fs;
use std::path::Path;

pub fn load_config(path: &Path) -> String {
    fs::read_to_string(path).unwrap()
}
