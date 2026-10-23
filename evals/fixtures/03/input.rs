pub fn labels(ids: &[u32]) -> Vec<String> {
    ids.iter().map(|id| format!("item-{id}")).collect()
}
