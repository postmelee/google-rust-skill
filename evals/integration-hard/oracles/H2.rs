// SPDX-License-Identifier: MIT
#[path = "__support.rs"]
mod support;
use rhwp_ooxml_chart::data::scan_chart_values;
use rhwp_ooxml_chart::patch::{
    apply_chart_edits, apply_chart_edits_owned, OwnedPatchError, PatchError,
};
use std::error::Error;
use support::*;

#[test]
fn all_operations_match_frozen_outputs_with_spare_capacity() {
    legacy_calls();
    for (name, edits) in cases() {
        let bytes = fixture("1", "2");
        let mut xml = Vec::with_capacity(bytes.len() * 4);
        xml.extend_from_slice(&bytes);
        let data = scan_chart_values(&xml).unwrap();
        let ptr = xml.as_ptr();
        let capacity = xml.capacity();
        assert_eq!(
            apply_chart_edits(&xml, &data, &edits).unwrap(),
            expected(name),
            "legacy: {name}"
        );
        let output = apply_chart_edits_owned(xml, &data, &edits).unwrap();
        assert_eq!(output, expected(name), "new owned API: {name}");
        assert_eq!(output.as_ptr(), ptr, "allocation: {name}");
        assert_eq!(output.capacity(), capacity, "capacity: {name}");
    }
}

#[test]
fn mixed_growth_and_shrink_do_not_require_transient_extra_capacity() {
    for reverse in [false, true] {
        let large = "1".repeat(1800);
        let growing = "9".repeat(1200);
        let bytes = if reverse {
            fixture("2", &large)
        } else {
            fixture(&large, "2")
        };
        let xml = bytes.into_boxed_slice().into_vec();
        let data = scan_chart_values(&xml).unwrap();
        let edits = if reverse {
            vec![edit(0, &growing), edit(1, "3")]
        } else {
            vec![edit(1, &growing), edit(0, "3")]
        };
        let expected = apply_chart_edits(&xml, &data, &edits).unwrap();
        let ptr = xml.as_ptr();
        let capacity = xml.capacity();
        assert!(expected.len() <= capacity);
        let output = apply_chart_edits_owned(xml, &data, &edits).unwrap();
        assert_eq!(output, expected);
        assert_eq!(output.as_ptr(), ptr);
        assert_eq!(output.capacity(), capacity);
    }
}

#[test]
fn growth_beyond_capacity_and_empty_input_work() {
    let xml = fixture("1", "2").into_boxed_slice().into_vec();
    let data = scan_chart_values(&xml).unwrap();
    let edits = vec![edit(0, &"8".repeat(xml.len() * 2))];
    let expected = apply_chart_edits(&xml, &data, &edits).unwrap();
    assert_eq!(
        apply_chart_edits_owned(xml, &data, &edits).unwrap(),
        expected
    );
    let empty = Vec::with_capacity(32);
    let ptr = empty.as_ptr();
    let data = rhwp_ooxml_chart::data::ChartData::default();
    let output = apply_chart_edits_owned(empty, &data, &[]).unwrap();
    assert!(output.is_empty());
    assert_eq!(output.as_ptr(), ptr);
    assert_eq!(output.capacity(), 32);
}

#[test]
fn errors_return_original_allocation_and_typed_cause_after_borrows_end() {
    for mode in 0..5 {
        let bytes = fixture("1", "222");
        let mut xml = Vec::with_capacity(bytes.len() + 127);
        xml.extend_from_slice(&bytes);
        let ptr = xml.as_ptr();
        let capacity = xml.capacity();
        let (error, expected_kind): (OwnedPatchError, &str) = {
            let mut data = scan_chart_values(&xml).unwrap();
            let mut edits = vec![edit(0, "77777"), edit(1, "8")];
            let kind = match mode {
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
                    edits[1] = edit(0, "8");
                    "duplicate"
                }
            };
            (
                apply_chart_edits_owned(xml, &data, &edits).unwrap_err(),
                kind,
            )
        };
        assert!(!error.to_string().is_empty());
        assert_eq!(legacy_error(error.error().clone()), expected_kind);
        assert_eq!(
            error
                .source()
                .unwrap()
                .downcast_ref::<PatchError>()
                .unwrap(),
            error.error()
        );
        let (recovered, cause) = error.into_parts();
        assert_eq!(recovered, bytes);
        assert_eq!(recovered.as_ptr(), ptr);
        assert_eq!(recovered.capacity(), capacity);
        assert_eq!(legacy_error(cause), expected_kind);
    }
}
