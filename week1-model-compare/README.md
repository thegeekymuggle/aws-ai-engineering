# Model comparison: support-ticket triage on Amazon Bedrock

Task: classify customer support tickets into JSON (`category`, `priority`, `sentiment`,
`summary`, `needs_human`) using explicit rules in the system prompt. 10 hand-written
tickets including sarcasm, Hinglish, an ambiguous case, and a prompt-injection attempt.
Each ticket run 3 times per model at temperature 0, via the Bedrock Converse API.

## Results

| Model | Valid JSON | Strict JSON | Category | Priority | Needs human | All 3 correct | Consistency | p50 ms | p95 ms | $ / 1k tickets |
|---|---|---|---|---|---|---|---|---|---|---|
| Nova Micro | 100% | 100% | 100% | 90% | 80% | 70% | 100% | 738 | 793 | 0.017 |
| Nova Lite  | 100% | 70%  | 100% | 93% | 80% | 73% | 90%  | 858 | 998 | 0.027 |
| Nova Pro   | 100% | 100% | 100% | 90% | 90% | 80% | 100% | 840 | 1067 | 0.354 |

## Findings
- **Nova Pro costs 21x more than Micro for +1 correct ticket out of 10.** With 10 tickets
  this gap is within noise; a larger eval set is needed to separate them.
- **Nova Lite is dominated:** more expensive than Micro, with no accuracy gain, and worse
  format reliability (70% strict JSON) and consistency.
- **T04 (Hinglish login issue): all models disagreed with my label**, which suggests the
  label or the escalation rule is ambiguous rather than the models being wrong.
- **T05 (prompt injection): partial success on Nova Micro.** It resisted the category change
  but followed the injected "low priority" instruction.
- **T03 (sarcasm): only Nova Micro missed** that the customer was angry.

## Recommendation
Nova Micro as the default (100% valid JSON, sub-second, ~$1.70 per 100k tickets), plus:
Bedrock Guardrails for prompt-attack detection, cascading to Nova Pro for negative-sentiment
tickets, and expanding the eval set to 50+ tickets with clearer escalation rules.

## Note
Claude models were excluded: on an AISPL (India) account, AWS Marketplace subscriptions fail
with `INVALID_PAYMENT_INSTRUMENT` when a card is the default payment method. The fix is
switching to Pay by Invoice via a billing support case.

## Run it
```
pip install boto3
python compare.py
```