use std::sync::Arc;
use std::thread;

pub fn count_in_workers(data: Arc<Vec<u8>>) -> usize {
    let handles: Vec<_> = (0..2).map(|_| {
        let data = Arc::clone(&data);
        thread::spawn(move || data.len())
    }).collect();
    handles.into_iter()
        .map(|handle| handle.join().expect("worker only reads immutable data"))
        .sum()
}
