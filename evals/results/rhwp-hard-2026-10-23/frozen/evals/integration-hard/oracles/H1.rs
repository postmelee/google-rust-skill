// SPDX-License-Identifier: MIT
#[path = "__support.rs"]
mod support;
use rhwp_ooxml_chart::data::scan_chart_values;
use rhwp_ooxml_chart::patch::{apply_chart_edits, write_chart_edits, WritePatchError};
use std::error::Error;
use std::io::{self, Write};
use support::*;

#[derive(Debug)]
struct Payload(u32);
impl std::fmt::Display for Payload {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "payload:{}", self.0)
    }
}
impl Error for Payload {}

struct Sink {
    bytes: Vec<u8>,
    calls: usize,
    fail_at: Option<usize>,
    interrupted: bool,
    zero: bool,
}
impl Sink {
    fn new() -> Self {
        Self {
            bytes: vec![],
            calls: 0,
            fail_at: None,
            interrupted: false,
            zero: false,
        }
    }
}
impl Write for Sink {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        self.calls += 1;
        if self.interrupted {
            self.interrupted = false;
            return Err(io::ErrorKind::Interrupted.into());
        }
        if self.zero {
            return Ok(0);
        }
        if self.fail_at.is_some_and(|limit| self.bytes.len() >= limit) {
            return Err(io::Error::new(io::ErrorKind::BrokenPipe, Payload(73)));
        }
        let size = buf
            .len()
            .min(3)
            .min(self.fail_at.unwrap_or(usize::MAX) - self.bytes.len());
        self.bytes.extend_from_slice(&buf[..size]);
        Ok(size)
    }
    fn flush(&mut self) -> io::Result<()> {
        panic!("caller owns flushing")
    }
}

#[test]
fn all_operations_match_frozen_outputs_and_old_consumers() {
    legacy_calls();
    let xml = fixture("1", "2");
    let original = xml.clone();
    let data = scan_chart_values(&xml).unwrap();
    for (name, edits) in cases() {
        let mut sink = Sink::new();
        sink.interrupted = true;
        let writer: &mut dyn Write = &mut sink;
        write_chart_edits(&xml, &data, &edits, writer).unwrap();
        assert_eq!(sink.bytes, expected(name), "new writer: {name}");
        assert_eq!(
            apply_chart_edits(&xml, &data, &edits).unwrap(),
            expected(name),
            "legacy: {name}"
        );
    }
    assert_eq!(xml, original);
}

#[test]
fn late_validation_failures_never_touch_the_sink() {
    let xml = fixture("1", "222");
    for mode in 0..5 {
        let mut data = scan_chart_values(&xml).unwrap();
        let mut edits = vec![edit(0, "4"), edit(1, "5")];
        let expected_kind = match mode {
            0 => {
                edits[1] = edit(1, "bad&text");
                "text"
            }
            1 => {
                data.series[0].values[1].span = data.series[0].values[0].span.clone();
                "overlap"
            }
            2 => {
                data.series[0].values[1].span = Some(xml.len()..xml.len() + 1);
                "span"
            }
            3 => {
                data.series[0].values[1].span = Some(9..2);
                "span"
            }
            _ => {
                edits[1] = edit(0, "5");
                "duplicate"
            }
        };
        let mut sink = Sink::new();
        sink.fail_at = Some(0);
        let error = write_chart_edits(&xml, &data, &edits, &mut sink).unwrap_err();
        assert_eq!(sink.calls, 0, "validation must finish before any write");
        assert!(sink.bytes.is_empty());
        assert!(error
            .source()
            .unwrap()
            .downcast_ref::<rhwp_ooxml_chart::patch::PatchError>()
            .is_some());
        match error {
            WritePatchError::Patch(cause) => assert_eq!(legacy_error(cause), expected_kind),
            _ => panic!("lost validation cause"),
        }
    }
}

#[test]
fn io_failure_keeps_prefix_and_original_typed_payload() {
    let xml = fixture("1", "2");
    let data = scan_chart_values(&xml).unwrap();
    let edits = vec![edit(0, "44")];
    let output = apply_chart_edits(&xml, &data, &edits).unwrap();
    for limit in [0, 7, 400] {
        let mut sink = Sink::new();
        sink.fail_at = Some(limit);
        let error = write_chart_edits(&xml, &data, &edits, &mut sink).unwrap_err();
        let cause = error.source().unwrap().downcast_ref::<io::Error>().unwrap();
        assert_eq!(cause.kind(), io::ErrorKind::BrokenPipe);
        assert_eq!(
            cause
                .get_ref()
                .unwrap()
                .downcast_ref::<Payload>()
                .unwrap()
                .0,
            73
        );
        assert_eq!(sink.bytes, output[..limit]);
        match error {
            WritePatchError::Io(cause) => assert_eq!(cause.kind(), io::ErrorKind::BrokenPipe),
            _ => panic!("lost I/O cause"),
        }
    }
}

#[test]
fn zero_write_becomes_write_zero() {
    let xml = fixture("1", "2");
    let data = scan_chart_values(&xml).unwrap();
    let mut sink = Sink::new();
    sink.zero = true;
    let error = write_chart_edits(&xml, &data, &[], &mut sink).unwrap_err();
    match error {
        WritePatchError::Io(cause) => assert_eq!(cause.kind(), io::ErrorKind::WriteZero),
        _ => panic!("wrong cause"),
    }
}
