// SPDX-License-Identifier: MIT
use rhwp_contracts::provenance::{mark_in_place, marked, CommandProvenance, UntrustedField};
use serde_json::{json, Value};

#[test]
fn object_payload_and_declared_order_are_preserved() {
    let input = json!({"title":"hello", "fonts":["A"], "extra":{"nested":[1,2,3]}});
    let expected = json!({"title":"hello", "fonts":["A"], "extra":{"nested":[1,2,3]},
        "untrustedContent":true, "untrustedFields":["title","fonts[]"]});
    let mut value = input.clone();
    mark_in_place(&mut value, "info");
    assert_eq!(value, expected);
    let old_api: fn(Value, &str) -> Value = marked;
    assert_eq!(old_api(input, "info"), expected);
    mark_in_place(&mut value, "info");
    assert_eq!(value, expected);
}

#[test]
fn absence_and_unknown_commands_are_not_marked_as_content() {
    for title in [Value::Null, json!(""), json!([]), json!({})] {
        let mut value = json!({"title":title, "fonts":[], "keep":9});
        mark_in_place(&mut value, "info");
        assert_eq!(value["untrustedContent"], false);
        assert_eq!(value["untrustedFields"], json!([]));
        assert_eq!(value["keep"], 9);
    }
    for title in [json!(false), json!(0), json!(" ")] {
        let mut value = json!({"title":title});
        mark_in_place(&mut value, "info");
        assert_eq!(value["untrustedFields"], json!(["title"]));
    }
    let mut value = json!({"title":"text", "untrustedContent":true, "untrustedFields":["stale"]});
    mark_in_place(&mut value, "unknown-command");
    assert_eq!(value, json!({"title":"text", "untrustedContent":false,"untrustedFields":[]}));
}

#[test]
fn scalar_values_are_untouched_and_existing_structs_are_constructible() {
    for input in [Value::Null, json!(false), json!(17), json!("text"), json!([1,2])] {
        let mut value = input.clone();
        mark_in_place(&mut value, "info");
        assert_eq!(value, input);
        assert_eq!(marked(input.clone(), "info"), input);
    }
    let _: UntrustedField = UntrustedField { path: "title", origin: "consumer" };
    let _: CommandProvenance = CommandProvenance { command: "custom", untrusted: &[], note: "consumer" };
}
