pub fn first(bytes: &[u8]) -> u8 {
    unsafe { *bytes.as_ptr() }
}
