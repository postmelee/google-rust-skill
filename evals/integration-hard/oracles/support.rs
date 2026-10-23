// SPDX-License-Identifier: MIT
use rhwp_ooxml_chart::data::{scan_chart_values, ChartData};
use rhwp_ooxml_chart::patch::{ChartEdit, EditTarget, PatchError, ValueEdit};

pub fn fixture(left: &str, right: &str) -> Vec<u8> {
    let mut xml = String::from("<c:chartSpace><c:chart><c:plotArea><c:barChart>");
    for series in 0..2 {
        xml.push_str(&format!("<c:ser><c:idx val=\"{series}\"/><c:order val=\"{series}\"/><c:tx><c:v>Series{series}</c:v></c:tx>"));
        xml.push_str("<c:cat><c:strLit><c:ptCount val=\"2\"/><c:pt idx=\"0\"><c:v>Alpha</c:v></c:pt><c:pt idx=\"1\"><c:v>Snow雪</c:v></c:pt></c:strLit></c:cat>");
        xml.push_str(&format!("<c:val><c:numRef><c:f>Sheet1!$B$2:$B$3</c:f><c:numCache><c:ptCount val=\"2\"/><c:pt idx=\"0\"><c:v>{left}</c:v></c:pt><c:pt idx=\"1\"><c:v>{right}</c:v></c:pt></c:numCache></c:numRef></c:val>"));
        xml.push_str(
            "<c:extLst><vendor:opaque>Preserve &amp; spacing</vendor:opaque></c:extLst></c:ser>",
        );
    }
    xml.push_str("</c:barChart></c:plotArea></c:chart></c:chartSpace>");
    xml.into_bytes()
}

pub fn edit(point: usize, text: &str) -> ChartEdit {
    ChartEdit::Value(ValueEdit {
        series: 0,
        point,
        target: EditTarget::Value,
        text: text.into(),
    })
}

pub fn cases() -> Vec<(&'static str, Vec<ChartEdit>)> {
    vec![
        ("empty", vec![]),
        ("values", vec![edit(1, "123456"), edit(0, "7")]),
        (
            "name",
            vec![ChartEdit::SeriesName {
                series: 0,
                text: "Revised雪".into(),
            }],
        ),
        (
            "append-points",
            vec![ChartEdit::AppendPoints {
                series: 0,
                target: EditTarget::Value,
                texts: vec!["3".into(), "4".into()],
            }],
        ),
        (
            "truncate-points",
            vec![ChartEdit::TruncatePoints {
                series: 0,
                target: EditTarget::Value,
                keep: 1,
            }],
        ),
        (
            "append-series",
            vec![ChartEdit::AppendSeries {
                name: Some("New".into()),
                labels: None,
                values: vec!["3".into(), "4".into()],
            }],
        ),
        (
            "truncate-series",
            vec![ChartEdit::TruncateSeries { keep: 1 }],
        ),
        (
            "insert-series",
            vec![ChartEdit::InsertSeries {
                at: 0,
                name: Some("First".into()),
                labels: None,
                values: vec!["5".into(), "6".into()],
            }],
        ),
        ("remove-series", vec![ChartEdit::RemoveSeries { at: 0 }]),
        (
            "mixed-structure",
            vec![
                ChartEdit::TruncatePoints {
                    series: 0,
                    target: EditTarget::Value,
                    keep: 1,
                },
                ChartEdit::AppendPoints {
                    series: 1,
                    target: EditTarget::Value,
                    texts: vec!["8".into()],
                },
            ],
        ),
    ]
}

pub fn expected(name: &str) -> Vec<u8> {
    std::fs::read(
        std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("tests/__golden")
            .join(format!("{name}.xml")),
    )
    .unwrap()
}

// Compile an old consumer without a wildcard: a new variant or non_exhaustive
// attribute on these existing enums is a source-compatibility regression.
pub fn legacy_error(error: PatchError) -> &'static str {
    match error {
        PatchError::SeriesOutOfRange { .. } => "series",
        PatchError::PointOutOfRange { .. } => "point",
        PatchError::DuplicateTarget { .. } => "duplicate",
        PatchError::ValueNotPatchable { .. } => "missing",
        PatchError::UnsafeText { .. } => "text",
        PatchError::SpanOutOfRange { .. } => "span",
        PatchError::OverlappingSpans { .. } => "overlap",
        PatchError::SeriesNameNotPatchable { .. } => "name-missing",
        PatchError::UnsafeName { .. } => "name",
        PatchError::BlockNotResizable { .. } => "block",
        PatchError::EmptyBlockRefused { .. } => "empty-block",
        PatchError::EmptySeriesRefused => "empty-series",
        PatchError::SeriesNotClonable { .. } => "clone",
        PatchError::LengthMismatch { .. } => "length",
        PatchError::OverlappingStructureEdits { .. } => "structure-overlap",
        PatchError::StructureSpanOutOfRange { .. } => "structure-span",
        PatchError::SeriesNotRenumberable { .. } => "renumber",
    }
}

pub fn legacy_edit(edit: ChartEdit) {
    match edit {
        ChartEdit::Value(_)
        | ChartEdit::SeriesName { .. }
        | ChartEdit::AppendPoints { .. }
        | ChartEdit::TruncatePoints { .. }
        | ChartEdit::AppendSeries { .. }
        | ChartEdit::TruncateSeries { .. }
        | ChartEdit::InsertSeries { .. }
        | ChartEdit::RemoveSeries { .. } => {}
    }
}

pub fn legacy_calls() {
    use rhwp_ooxml_chart::patch::{apply_chart_edits, apply_value_edits};
    let _: fn(&[u8], &ChartData, &[ChartEdit]) -> Result<Vec<u8>, PatchError> = apply_chart_edits;
    let _: fn(&[u8], &ChartData, &[ValueEdit]) -> Result<Vec<u8>, PatchError> = apply_value_edits;
    let _ = ChartData {
        series: vec![],
        has_up_down_bars: false,
    };
    let e = ValueEdit {
        series: 0,
        point: 0,
        target: EditTarget::Value,
        text: "42".into(),
    };
    let xml = fixture("1", "2");
    let data = scan_chart_values(&xml).unwrap();
    assert_eq!(
        apply_value_edits(&xml, &data, std::slice::from_ref(&e)).unwrap(),
        apply_chart_edits(&xml, &data, &[ChartEdit::Value(e)]).unwrap()
    );
    legacy_edit(edit(0, "1"));
}
