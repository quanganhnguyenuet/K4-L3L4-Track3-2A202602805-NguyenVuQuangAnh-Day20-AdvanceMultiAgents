# Lab Report: Self-evolving Agentic

## 1. Student and configuration

- Student: Nguyen Vu Quang Anh
- Student ID: 2A202602805
- Model: `openai:gpt-4.1-mini`; temperature: 0; recursion limit: 60
- Deep Agents: 0.7.21; recorded runner: Python 3.13.5 (the project venv metadata targets Python 3.11.9)
- Platform: Windows with the local shell backend; Git Unix utilities were added to the sanitized PATH for `which`, `cat`, and `ls` compatibility.
- Experiment budget: 22 task invocations and one curator call; 18 final run records are retained in `results/` because the pre-freeze skills-auto learning records were intentionally replaced by the post-freeze rerun.
- Hypotheses commit: `03e261f`; freeze commit/tag: `758263c` / `freeze`.

## 2. Hypotheses (committed before evaluation)

- H1 (subagents vs baseline): The subagents condition will improve or preserve scores on complex code and data tasks because exploration and implementation can be delegated, but it will use more coordination steps and tokens. The gain should be smaller on short log tasks where delegation overhead can exceed the benefit.
- H2 (skills-auto vs baseline): The skills-auto condition will improve adherence to recurring procedural and house-rule checks when a generated skill is read, but the gain will be inconsistent because skill selection depends on the description and generated skills may not match every task family. It will cost more tokens when the agent inspects skills.
- H3 (learning vs evaluation): Scores will be higher on learning tasks than on evaluation tasks because the evaluation set changes the data and adds a new rule. Any learning improvement that does not transfer to evaluation will indicate overfitting or insufficiently general skills.

## 3. Deep Agents orientation

1. The default agent exposes file tools (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, and `grep`), the shell tool `execute`, and the delegation tool `task`.
2. The `task` tool launches an ephemeral `general-purpose` subagent. It is stateless by default, sees only the delegation prompt, and returns a final report; it does not automatically see the main agent's intermediate context.
3. The `task` description instructs the main agent to provide full context and verify the report. The `execute` tool runs commands in the backend working directory; with the local backend it can access the host, so the experiment uses temporary sandboxes and a sanitized environment.

## 4. Baseline learning errors

The learning-only baseline produced the following results before evaluation was opened:

| Task | Score | Failed checks and classification |
|---|---:|---|
| code-learn | 6/10 | `tests_not_modified` (technical/integrity), `rule_type_hints`, `rule_regression_tests`, `rule_changelog` (house rules) |
| data-learn | 5/8 | `rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv` (house rules) |
| logs-learn | 1/9 | `entry_count`, `timestamps_utc`, `exception_fields`, `repeat_counts`, `counts_by_service` (technical); `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` (house rules) |

There were 15 failed checks in total: 9 house-rule checks and 6 technical/integrity checks. The dominant category was therefore the recurring organizational contract, while the remaining technical failures were concentrated in log parsing and normalization. This supports a procedural skill intervention, but only if the model actually reads and follows the skill.

## 5. Subagents condition

The custom subagents are:

- `explorer`: inspect files/data and return facts without modifying files.
- `implementer`: make changes, run focused checks, and report the exact changes.
- `reviewer`: independently check requirements and edge cases without modifying files.

Learning results were `6/10`, `1/8`, and `2/9` for code, data, and logs. Evaluation results were `6/11`, `5/9`, and `0/10`. `subagent_calls` was 0 for code, 1 for data, and 1 for logs in learning; it was 0, 3, and 1 respectively in evaluation. The mean token cost was 43,323 per final run, lower than baseline's 69,036, but delegation did not consistently improve scores.

## 6. Self-evolving skills

The curator was run once on baseline learning feedback and generated three valid skills:

| Skill | Assessment |
|---|---|
| `enforce-type-annotations` | General procedural guidance for public API annotations; relevant to code tasks. |
| `maintain-test-integrity` | General guidance for preserving provided tests and adding regression coverage; relevant to code tasks. |
| `standardize-logging-and-timestamps` | General guidance for UTC timestamps, normalized services, repeated log counts, and schema metadata; relevant to log tasks. |

All three passed `validate_skill` and contained no evaluation marker. The post-freeze skills-auto scores were `6/10`, `5/8`, and `1/9` on learning, and `6/11`, `5/9`, and `6/10` on evaluation. `skills_read` was 0 in every retained run, so the improvement cannot be attributed to an observed skill-read/tool trace. An initial `logs-learn` run hit the recursion limit; it was rerun at limit 100 and the final retained record completed with score 1/9 and no error.

## 7. Results comparison

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 1/8 | 5/8 |
| logs-learn | 1/9 | 2/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 3/9 | 5/9 | 5/9 |
| logs-eval | 1/10 | 0/10 | 6/10 |
| **Mean score - learning tasks** | 0.45 | 0.32 | 0.45 |
| **Mean score - evaluation tasks** | 0.33 | 0.37 | 0.57 |
| **Mean tokens per run** | 69,036 | 43,323 | 84,667 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

The canonical generated table is also stored in `report/table.md`. All retained runs have `skills_modified = false`; the freeze check reports `OK`.

## 8. Analysis

1. On learning, baseline and post-freeze skills-auto both averaged 0.45, while subagents averaged 0.32. On evaluation, skills-auto was highest at 0.57, ahead of subagents at 0.37 and baseline at 0.33. The strongest transfer signal was logs-eval, where skills-auto scored 6/10 versus 1/10 baseline, while code-eval was unchanged and data-eval improved from 3/9 to 5/9.
2. The breakdown supports the mechanism: evaluation technical checks were 10/18 for baseline, 11/18 for subagents, and 17/18 for skills-auto. House-rule checks were 0/12 for all three conditions, so the generated skills did not visibly improve those rules.
3. The trace counter recorded `skills_read = 0` for all final runs. Thus the skills-auto evaluation gain is correlated with the condition but not proven to come from explicit skill use; it may reflect model variance, prompt/middleware effects, or the task's natural difficulty.
4. Mean token cost was 69,036 for baseline, 43,323 for subagents, and 84,667 for skills-auto. Subagents were the cheapest condition in this sample, while skills-auto had the highest cost despite the best evaluation score.
5. The curator filters evaluation roles and rejects evaluation markers before writing skills. The three generated files passed structural validation, but validation cannot prove substantive correctness; the zero `skills_read` count also limits the strength of any causal claim.
6. One post-freeze skills-auto learning run initially reached the recursion limit; rerunning that task at limit 100 completed successfully, and the final retained artifacts contain no run error.

## 9. Limitations and validity

1. There are only three tasks per role and one run per condition, so model randomness and task-specific effects can dominate the means.
2. Only one model and one temperature were tested; the result may not generalize to other providers or tool-calling models.
3. The local backend runs shell commands with host permissions; the temporary directory is isolated by convention, not by an operating-system sandbox.
4. The generated skills were validated structurally, but no retained run explicitly read a skill according to `skills_read`; behavioral attribution is therefore weak.
5. The initial `logs-learn` retry reached the recursion limit, so the final record uses a higher limit and should be compared with awareness that it had a different budget from the other 60-step runs.

## 10. Conclusion

The harness, subagent mode, runner, curator, tests, experiments, freeze tag, and report artifacts are complete. Skills-auto had the highest evaluation mean (0.57 versus 0.33 baseline) and a large logs-eval improvement, but it used the most tokens and did not improve house-rule checks. The result is promising but not causal because no run recorded an explicit skill read and only one model/run was used. Repeated post-freeze runs would be the next validation step.

## Appendix

Commands used:

```text
pytest -q --basetemp=<fresh-temporary-directory>
python -m lab.runner --condition baseline --tasks learn --recursion-limit 60
python -m lab.runner --condition subagents --tasks learn --recursion-limit 60
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 60
git commit -m "hypotheses"
git commit --allow-empty -m "freeze skills"
git tag freeze
python -m lab.runner --condition baseline --tasks eval --recursion-limit 60
python -m lab.runner --condition subagents --tasks eval --recursion-limit 60
python -m lab.runner --condition skills-auto --tasks all --recursion-limit 60
python -m lab.runner --condition skills-auto --tasks logs-learn --recursion-limit 100
python scripts/verify_freeze.py
python scripts/check_breakdown.py
python -m lab.compare
```
