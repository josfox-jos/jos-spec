# Conformance vectors

- `vectors/invalid/*.jos`: documents a conforming validator MUST reject. The expected reason for each is in `expected/invalid.json`.
- `../examples/*.jos`: documents a conforming validator MUST accept.

A validator that accepts everything is not a validator. CI runs both directions.
