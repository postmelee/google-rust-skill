use std::collections::*;

pub fn make_map() -> HashMap<String, usize> {
    HashMap::new()
}
pub enum Switch { On, Off }
pub fn enabled(value: Switch) -> bool {
    use Switch::*;
    match value { On => true, Off => false }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn map_starts_empty() {
        assert!(make_map().is_empty());
    }
}
