// SPDX-License-Identifier: MIT
use rhwp_contracts::schema_registry::{self, write_registry};
use std::io::{self, Write};

#[test]
fn borrowed_writers_and_versions_match_the_existing_registry() {
    for version in ["", "0.8.7", "quotes\" slash\\ newline\n 한글"] {
        let mut bytes = Vec::new();
        let writer: &mut dyn Write = &mut bytes;
        let result: Result<(), serde_json::Error> = write_registry(writer, version);
        result.expect("registry written");
        let expected = serde_json::to_vec(&schema_registry::registry_value_with_crate_version(version))
            .expect("existing registry serializes");
        assert_eq!(bytes, expected);
    }
    assert_eq!(schema_registry::registry_value()["crateVersion"], schema_registry::crate_version());
}

struct FailingWriter { remaining: usize, flushed: bool }
impl Write for FailingWriter {
    fn write(&mut self, bytes: &[u8]) -> io::Result<usize> {
        if self.remaining == 0 { return Err(io::Error::new(io::ErrorKind::BrokenPipe, "consumer closed")); }
        let written = bytes.len().min(self.remaining);
        self.remaining -= written;
        Ok(written)
    }
    fn flush(&mut self) -> io::Result<()> { self.flushed = true; Ok(()) }
}

#[test]
fn io_failure_is_typed_and_not_flushed() {
    for remaining in [0, 7, 40] {
        let mut writer = FailingWriter { remaining, flushed: false };
        let error = write_registry(&mut writer, "0.8.7").expect_err("writer should fail");
        assert!(error.is_io());
        assert_eq!(error.io_error_kind(), Some(io::ErrorKind::BrokenPipe));
        assert!(error.to_string().contains("consumer closed"));
        assert!(!writer.flushed);
    }
}

#[test]
fn successful_writer_is_not_explicitly_flushed() {
    let mut writer = FailingWriter { remaining: usize::MAX, flushed: false };
    write_registry(&mut writer, "0.8.7").expect("enough capacity");
    assert!(!writer.flushed);
}
