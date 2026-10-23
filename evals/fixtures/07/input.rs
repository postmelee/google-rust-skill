#[derive(Clone, Debug)]
pub struct Options {
    pub retries: u32,
    pub label: String,
}
impl Default for Options {
    fn default() -> Self {
        Self { retries: 3, label: String::new() }
    }
}
