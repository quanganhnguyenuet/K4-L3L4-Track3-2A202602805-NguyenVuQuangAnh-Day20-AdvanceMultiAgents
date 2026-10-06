# Lab Report: Self-evolving Agentic

## 1. Student and configuration

- Student: Nguyen Vu Quang Anh
- Student ID: 2A202602805
- Model: `openai:gpt-4.1-mini`; temperature: 0; recursion limit: 60
- Deep Agents: 0.7.21; Python runtime used for the recorded runs: 3.13.5
- Platform: Windows with the local shell backend; Git Unix utilities were added to the sanitized PATH for `which`, `cat`, and `ls` compatibility.
- Recorded runs: 12 task runs plus one curator call; API calls were sequential.
- Freeze tag: to be filled after the evaluation runs.

## 2. Hypotheses (committed before evaluation)

- H1 (subagents vs baseline): The subagents condition will improve or preserve scores on complex code and data tasks because exploration and implementation can be delegated, but it will use more coordination steps and tokens. The gain should be smaller on short log tasks where delegation overhead can exceed the benefit.
- H2 (skills-auto vs baseline): The skills-auto condition will improve adherence to recurring procedural and house-rule checks when a generated skill is read, but the gain will be inconsistent because skill selection depends on the description and the generated skills may not match every task family. It will cost more tokens when the agent inspects skills.
- H3 (learning vs evaluation): Scores will be higher on learning tasks than on evaluation tasks because the evaluation set changes the data and adds a new rule. Any learning improvement that does not transfer to evaluation will indicate overfitting or insufficiently general skills.

## 3. Deep Agents orientation

1. The default agent exposes file tools (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, and `grep`), the shell tool `execute`, and the delegation tool `task`.
2. The `task` tool launches an ephemeral `general-purpose` subagent. It is stateless by default, sees only the delegation prompt, and returns a final report; it does not automatically see the main agent's intermediate context.
3. The `task` description instructs the main agent to provide full context and verify the report. The `execute` description warns that shell commands run in the backend working directory and may access the host through the local backend.

## 4. Baseline learning errors

The learning-only baseline produced the following results before evaluation was opened:

| Task | Score | Failed checks and classification |
|---|---:|---|
| code-learn | 6/10 | `tests_not_modified` (E), `rule_type_hints` (E), `rule_regression_tests` (E), `rule_changelog` (E) |
| data-learn | 5/8 | `rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv` (E) |
| logs-learn | 1/9 | `entry_count`, `timestamps_utc`, `exception_fields`, `repeat_counts`, `counts_by_service` (D); `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` (E) |

The dominant category was E: 10 of the 16 failed learning checks were organizational rules. The remaining technical failures were concentrated in log parsing and normalization. This supports a procedural skill intervention, but the baseline trace also shows that a skill is useful only if the model actually reads and follows it.

## 5. Subagents condition

The custom subagents are:

- `explorer`: inspect files/data and return facts without modifying files.
- `implementer`: make changes, run focused checks, and report the exact changes.
- `reviewer`: independently check requirements and edge cases without modifying files.

Learning results were `6/10`, `1/8`, and `2/9` for code, data, and logs respectively. `subagent_calls` was 0 for code and 1 for data and logs. Mean tokens were 37,041 versus 58,808 for baseline learning runs. The lower score is therefore not explained by token cost alone; delegation quality and the model's choice of when to delegate also mattered.

## 6. Self-evolving skills

The curator was run once on baseline learning feedback and generated three valid skills:

| Skill | Assessment |
|---|---|
| `enforce-type-annotations` | General procedural guidance for public API annotations; relevant to code tasks. |
| `maintain-test-integrity` | General guidance for preserving provided tests and adding regression coverage; relevant to code tasks. |
| `standardize-logging-and-timestamps` | General guidance for UTC timestamps, normalized services, repeated log counts, and schema metadata; relevant to log tasks. |

All three passed `validate_skill`; no evaluation marker was present. In the first skills-auto learning run, `skills_read` was 0/3, so the skills were not demonstrated as used even though the condition loaded them. Scores were `3/10`, `5/8`, and `1/9`, with a mean of 68,701 tokens.

## 7. Results comparison

The final comparison table is stored in `report/table.md` and is generated from `results/`.

## 8. Analysis

1. The learning results show baseline mean score 0.45, subagents 0.32, and skills-auto 0.35. The subagents condition reduced the data score from 5/8 to 1/8, while skills-auto preserved the data score at 5/8. Evaluation results are required before making a transfer claim.
2. Most baseline failures were house rules: formatting, metadata, test integrity, type annotations, and changelog requirements. The generated skills target those recurring procedures, while the log skill targets the technical normalization failures.
3. The learning trace records `skills_read = 0` for all three skills-auto runs. Therefore no learning check can be attributed to following a skill in this sample; the likely issue is that the skill descriptions were not selected by the model or the model answered without reading them.
4. Mean token cost was 58,808 for baseline, 37,041 for subagents, and 68,701 for skills-auto on learning runs. In this sample subagents were cheaper but less accurate, while skills-auto was more expensive without a score increase.
5. The curator filters evaluation roles and rejects evaluation markers before writing skills. The generated files passed validation, which limits leakage risk, but format validation cannot prove that a skill is substantively correct.
6. The learning sample contains one run per task/condition, so the observed differences are noisy. The post-freeze learning rerun will provide a direct comparison of that noise.

## 9. Limitations and validity

1. There are only three tasks per role and one run per condition, so model randomness and task-specific effects can dominate the means.
2. Only one model and one temperature were tested; the result may not generalize to other providers or tool-calling models.
3. The local backend runs shell commands with host permissions; the temporary directory is isolated by convention, not by an operating-system sandbox.
4. The generated skills were validated structurally, but `skills_read` was zero in the learning sample, so their behavioral value is not established until the frozen evaluation runs.

## 10. Conclusion

The harness, subagent mode, runner, curator, and offline tests are complete. On the learning sample, baseline was strongest by score, subagents were cheaper but inconsistent, and skills-auto did not improve results because no skill was read. The frozen evaluation runs will determine whether the procedural skills transfer to unseen tasks or overfit the learning set. A useful next step would be repeated runs with the same frozen skills and a model that reliably follows skill instructions.

## Appendix

Commands used:

```text
pytest -q --basetemp=<fresh-temporary-directory>
python -m lab.runner --condition baseline --tasks learn --recursion-limit 60
python -m lab.runner --condition subagents --tasks learn --recursion-limit 60
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 60
python scripts/check_breakdown.py
python -m lab.compare
```
