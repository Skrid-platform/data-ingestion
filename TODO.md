# TODO

## General
- Add a `to_cypher_file` method to graph nodes classes that writes the cypher in a file on the fly ;
- Add a `to_cypher_dump` method to graph nodes classes that dumps the cypher in the database on the fly ;

- Graces notes : they are added as other notes for the moment, with an attribute on the `Fact`.
To be able to ignore them, it could be possible to add a link from the previous `Event` to the following one, skipping the `Event` having the grace note. This way, the grace note would still be in the graph, and searching with it and without it will work.
To implement this, it is needed to change code in `Measure.to_cypher`: check if the current `Event` has only one `Fact`, check that this `Fact` has the `grace` attribute set, and if it is the case, inspire from the way `prev` is already calculated (be careful that the previous `Event` might in the previous `Measure` or event further if there is no note in the previous `Measure` on the given voice) ;

- Add tests ;

## Ideas
- Use multiple threads (divide the files in groups of [nb threads on the current computer] and give a thread to each group) ;
