# Evaluation window decision

## VERIFIED FACTS

- The manuscript declares 2023-01-01 through 2023-07-31.
- The historical Madrid config declared all of 2023 and produced 362 origins.
- The Ireland config ended at 2023-08-01 00:00, yielding origins through 2023-07-31.

## EVIDENCE

`manuscripts/manuscript_main.tex:253`, `code/e2_met_madrid_config.json`,
`code/e2_met_ireland_config_regenerated.json`, and the immutable prior audit.

## CURRENT MANUSCRIPT CONTRACT

2023-01-01 to 2023-07-31.

## CURRENT PIPELINE CONTRACT

Madrid historically used 2023-01-01 to 2023-12-31; Ireland used the declared
January--July window.

## RECOMMENDED CANONICAL WINDOW

Provisional canonical window: 2023-01-01 00:00 through 2023-07-31 00:00 for
24-hour origin candidates. This is now explicit in the Madrid configuration.

## REASON

No evidence sufficient to supersede the manuscript contract was found. This
choice changes configuration, not results: regeneration is gated on inputs.
