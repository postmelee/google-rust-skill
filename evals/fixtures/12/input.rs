pub struct Report { pub title: String }
impl Report {
    pub fn render(&self) -> String {
        self.title.clone()
    }
}
