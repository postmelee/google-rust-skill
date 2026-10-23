use std::thread;
pub async fn read_label() -> String {
    "ready".to_owned()
}
pub fn start_worker() -> thread::JoinHandle<()> {
    thread::spawn(|| {})
}
