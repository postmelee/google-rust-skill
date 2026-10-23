use crate::helpers::label;

pub mod helpers {
    pub fn label() -> &'static str { "ok" }
}
pub fn render() -> &'static str { label() }
