use svg::Document;
use svg::node::element::Rectangle;
use std::error::Error;
use std::io;
use std::process;

fn example() -> Result<(), Box<dyn Error>> {
    // Build the CSV Reader and iterate over each record
    let mut rdr = csv::Reader::from_reader(io::stdin());
    for result in rdr.records() {
        // the iterator yeilds Result<StringRecord, Error>, so we check the error here
        let record = result?;
        println!("{:?}", record);
    }
    Ok(())
}

fn main() {


    let rect = Rectangle::new()
        .set("fill", "grey")
        .set("height", 20)
        .set("width", 30);

    let document = Document::new()
        .set("viewBox", (0, 0, 250, 250))
        .add(rect);

    svg::save("image.svg", &document).unwrap();

    if let Err(err) = example() {
        println!("error running example: {}", err);
        process::exit(1);
    }
}
