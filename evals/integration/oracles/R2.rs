// SPDX-License-Identifier: MIT
use rhwp_contracts::ontology;
use serde_json::{json, Value};

fn actions(body: &Value) -> Vec<&Value> {
    body["@graph"].as_array().expect("graph array").iter()
        .filter(|node| node["@type"].as_array().is_some_and(|types| types.iter().any(|t| t == "rhwp:Action")))
        .collect()
}

#[test]
fn first_valid_payload_wins_in_each_namespace() {
    let capabilities = json!({"version":"test", "commands":[
        {"name":"info","summary":"first","flags":["--first"],"available":false},
        {"name":"info","summary":"last","flags":["--last"]},
        {"name":"other","json":true}
    ]});
    let tools = vec![json!({"name":"info","description":"first tool","annotations":{"readOnlyHint":true},"cli":{"command":"info"}}),
        json!({"name":"info","description":"last tool"}),json!({"name":"other"})];
    let saved = (capabilities.clone(), tools.clone());
    let body = ontology::ontology(&capabilities, &tools);
    let found = actions(&body);
    let ids: Vec<_> = found.iter().map(|n| n["@id"].as_str().expect("action id")).collect();
    assert_eq!(ids, ["rhwp:cmd/info","rhwp:cmd/other","rhwp:tool/info","rhwp:tool/other"]);
    assert_eq!(found[0]["rdfs:comment"], "first");
    assert_eq!(found[0]["rhwp:flags"], json!(["--first"]));
    assert_eq!(found[0]["rhwp:available"], false);
    assert_eq!(found[2]["rhwp:annotations"], json!({"readOnlyHint":true}));
    assert_eq!(found[2]["rhwp:implementsCommand"], json!({"@id":"rhwp:cmd/info"}));
    assert_eq!((capabilities.clone(), tools.clone()), saved);
    let envelope = ontology::envelope(&capabilities, &tools);
    assert_eq!(envelope["actionCount"], 4);
    assert_eq!(envelope["ontology"], body);
    assert_eq!(envelope["schemaVersion"], "1.0");
}

#[test]
fn invalid_names_are_skipped_but_valid_bytes_are_not_normalized() {
    let entries = vec![json!(null),json!({}),json!({"name":42}),json!({"name":""}),
        json!({"name":" \t\n"}),json!({"name":"\u{2003}"}),json!({"name":"x"}),json!({"name":"X"}),
        json!({"name":" x "}),json!({"name":"한글"}),json!({"name":"x"})];
    let capabilities = json!({"commands":entries});
    let body = ontology::ontology(&capabilities, &entries);
    let found = actions(&body);
    let labels: Vec<_> = found.iter().map(|n| n["rdfs:label"].as_str().expect("label")).collect();
    assert_eq!(labels, ["x","X"," x ","한글","x","X"," x ","한글"]);
    let empty = ontology::envelope(&json!({}), &[]);
    let actual = ontology::envelope(&capabilities, &entries);
    assert_eq!(actual["classCount"], empty["classCount"]);
    assert_eq!(actual["propertyCount"], empty["propertyCount"]);
    assert_eq!(actual["actionCount"], 8);
    assert_eq!(ontology::ontology(&capabilities, &entries), body);
}
