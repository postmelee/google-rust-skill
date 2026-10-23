pub fn latest() -> u8 {
    let values = vec![1_u8, 2, 3];
    *values.last().unwrap()
}
